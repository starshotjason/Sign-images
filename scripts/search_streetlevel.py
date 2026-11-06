"""Street-level imagery stage: Panoramax and KartaView, both CC BY-SA 4.0, keyless.

  python3 -I scripts/search_streetlevel.py probe [ISO ...]            # coverage -> cache/streetlevel/probe*.json
  python3 -I scripts/search_streetlevel.py run [--cap N] [ISO ...]    # sample, OCR-filter, crop, stage

For each country (non-Latin-script and developing countries first) it probes city-centre points,
samples frames along the sequences found there (every ~10th frame), runs a local PP-OCR text
detector/recogniser (rapidocr-onnxruntime, offline) on a ~1-2k px rendition, scores frames by legible
text area x confidence (favouring fixed signs above street level over vehicle branding and menus),
and for the best ones cuts a crop around the text from the full-size image (a rectilinear view for
360-degree equirectangular panoramas) into staging/<cc>/<key>.jpg with staging/<cc>/<key>.cand.json
for build_set.py assemble(), plus a 1600 px review/<cc>/<key>.jpg.
Keys: p<10 hex of the Panoramax picture id>, k<KartaView photo id>. Existing staged files are never
overwritten; crops staged earlier by this script count toward the per-country cap.
At most 2 crops per sequence within 100 m, and none within 15 m of another crop of this stage.

Politeness: one request at a time, >= 0.6 s between requests to the same host (< 2 req/s),
429/503 Retry-After honoured. Hosts the egress proxy refuses are remembered and reported.
"""
import glob, hashlib, json, math, os, re, shutil, sys, time, random
from urllib.parse import urlparse, urlencode
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from countries import COUNTRIES, priority
from wm import UA
from streetlevel_cities import CITIES

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
_OUT = os.environ.get("SL_DRY_OUT")                        # dry run: write staging/review under this dir
STAGE = os.path.join(_OUT, "staging") if _OUT else os.path.join(ROOT, "staging")
REVIEW = os.path.join(_OUT, "review") if _OUT else os.path.join(ROOT, "review")
WORK = os.path.join(ROOT, "cache", "streetlevel")          # our own cache; downloads in their own dirs
API_CACHE = os.path.join(WORK, "api")
IMG = os.path.join(WORK, "img")
for d in (API_CACHE, IMG):
    os.makedirs(d, exist_ok=True)

PMX = "https://api.panoramax.xyz/api"
KV_API = "https://api.kartaview.org"        # current KartaView API host (kartaview.org front-end config)
MIN_INTERVAL = 0.6
HALF = 0.03                                 # city bbox half-size in degrees (~6 km box)
CAP = [8]                                   # crops staged per country (max); --cap N
STEP = 10                                   # every n-th frame along a sequence
KV_SEQS_PER_CITY = 25                       # KartaView sequences sampled per city
KV_RADIUS_M = 1500                          # keep KartaView frames this close to the city point
LICENSE_URL = "https://creativecommons.org/licenses/by-sa/4.0/"

S = requests.Session(); S.headers["User-Agent"] = UA
_last = {}
BLOCKED = set()


class Blocked(Exception):
    pass


RATE_DIR = os.path.join(WORK, "rate")
os.makedirs(RATE_DIR, exist_ok=True)


def _wait(host):
    """>= MIN_INTERVAL between requests to a host, shared by all worker processes (flock'd timestamp file)."""
    import fcntl
    with open(os.path.join(RATE_DIR, host), "a+") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        fh.seek(0)
        try: last = float(fh.read().strip() or 0)
        except ValueError: last = 0
        w = MIN_INTERVAL - (time.time() - max(last, _last.get(host, 0)))
        if w > 0: time.sleep(w)
        _last[host] = time.time()
        fh.seek(0); fh.truncate(); fh.write(repr(_last[host])); fh.flush()
        fcntl.flock(fh, fcntl.LOCK_UN)


def http_get(url, params=None, stream=False, timeout=60):
    host = urlparse(url).hostname
    if host in BLOCKED: raise Blocked(host)
    delay = 10
    for attempt in range(8):
        _wait(host)
        try:
            r = S.get(url, params=params, timeout=timeout, stream=stream, allow_redirects=False)
        except requests.exceptions.ProxyError as e:
            BLOCKED.add(host); raise Blocked(host) from e
        except requests.exceptions.SSLError as e:
            BLOCKED.add(host); raise Blocked(host + " (TLS)") from e
        except requests.RequestException as e:
            print("   net error", host, str(e)[:120], flush=True); time.sleep(delay); delay = min(delay * 2, 120); continue
        if r.status_code in (301, 302, 303, 307, 308):
            url = requests.compat.urljoin(url, r.headers["location"]); params = None
            host = urlparse(url).hostname
            if host in BLOCKED: raise Blocked(host)
            continue
        if r.status_code >= 500 and r.status_code not in (503,) and attempt >= 1:
            print(f"   HTTP {r.status_code} from {host}, giving up on this URL", flush=True)
            return r                                        # a broken asset, not overload: skip it
        if r.status_code == 429 or r.status_code >= 500:
            ra = r.headers.get("retry-after")
            w = (int(ra) if ra and ra.isdigit() else (delay if r.status_code in (429, 503) else 2)) + random.uniform(0.5, 2)
            print(f"   HTTP {r.status_code} from {host}, sleeping {w:.0f}s", flush=True)
            if r.status_code in (520, 521, 522, 523, 525, 526, 530) and attempt >= 1:
                BLOCKED.add(host); raise Blocked(host + f" (HTTP {r.status_code})")
            time.sleep(w); delay = min(delay * 2, 300); continue
        return r
    raise RuntimeError("giving up on " + url)


def get_json(url, params=None, cache=True):
    key = hashlib.sha1((url + "?" + urlencode(sorted((params or {}).items()))).encode()).hexdigest()
    path = os.path.join(API_CACHE, key + ".json")
    if cache and os.path.exists(path):
        return json.load(open(path))
    r = http_get(url, params)
    if r.status_code != 200: return None
    d = r.json()
    json.dump(d, open(path, "w"))
    return d


def download(url, dst):
    if os.path.exists(dst) and os.path.getsize(dst) > 0: return dst
    r = http_get(url, stream=True, timeout=180)
    if r.status_code != 200: return None
    tmp = dst + ".part"
    with open(tmp, "wb") as f:
        for chunk in r.iter_content(1 << 16): f.write(chunk)
    os.replace(tmp, dst)
    return dst


def bbox(lat, lon, half=HALF):
    k = half / max(0.2, math.cos(math.radians(lat)))
    return f"{lon - k:.5f},{lat - half:.5f},{lon + k:.5f},{lat + half:.5f}"


def dist_m(a, b):
    (la1, lo1), (la2, lo2) = a, b
    x = math.radians(lo2 - lo1) * math.cos(math.radians((la1 + la2) / 2)); y = math.radians(la2 - la1)
    return 6371000 * math.hypot(x, y)

# ------------------------------------------------------------------ Panoramax

def via(feature):
    for l in feature.get("links", []):
        if l.get("rel") == "via": return l.get("instance_name"), l.get("href")
    return None, None


def pmx_search(bb, collections=None, limit=100, pages=1):
    params = {"bbox": bb, "limit": limit}
    if collections: params["collections"] = ",".join(collections)
    url, out = PMX + "/search", []
    for _ in range(pages):
        d = get_json(url, params)
        if not d: break
        out += d.get("features", [])
        nxt = [l["href"] for l in d.get("links", []) if l.get("rel") == "next"]
        if not nxt or len(d.get("features", [])) < limit: break
        url, params = nxt[0], None
    return out


def pmx_collections(bb, pages=3):
    url, params, out = PMX + "/collections", {"bbox": bb, "limit": 100}, []
    for _ in range(pages):
        d = get_json(url, params)
        if not d: break
        out += d.get("collections", [])
        nxt = [l["href"] for l in d.get("links", []) if l.get("rel") == "next"]
        if not nxt or len(d.get("collections", [])) < 100: break
        url, params = nxt[0], None
    return out


def hd_host(feature):
    return urlparse(feature["assets"]["hd"]["href"]).hostname


_reach = {}
def probe_reachable(host):
    """One cheap request to learn whether the proxy lets us reach an instance host."""
    if host in BLOCKED: return False
    if host in _reach: return _reach[host]
    try:
        r = http_get(f"https://{host}/api", timeout=30); ok = r.status_code < 500
    except (Blocked, RuntimeError):
        ok = False
    _reach[host] = ok
    if not ok: BLOCKED.add(host)
    return ok


def city_frames(lat, lon):
    """Panoramax frames in a city bbox. Returns (features, {host: count})."""
    bb = bbox(lat, lon)
    feats = pmx_search(bb, limit=100)
    hosts = {}
    for f in feats: hosts[hd_host(f)] = hosts.get(hd_host(f), 0) + 1
    cols = pmx_collections(bb)
    extra = []
    for c in cols:
        name, href = via(c)
        if not href: continue
        h = urlparse(href).hostname
        hosts.setdefault(h, 0)
        if probe_reachable(h) and (c.get("stats:items") or {}).get("count", 0) < 20000:
            extra.append(c["id"])
    if extra:
        seen = {f["id"] for f in feats}
        for i in range(0, len(extra), 20):
            for f in pmx_search(bb, collections=extra[i:i + 20], limit=100, pages=3):
                if f["id"] not in seen:
                    feats.append(f); seen.add(f["id"]); hosts[hd_host(f)] = hosts.get(hd_host(f), 0) + 1
    return feats, hosts


def pmx_is_pano(f):
    p = f.get("properties", {})
    fov = (p.get("pers:interior_orientation") or {}).get("field_of_view")
    proj = (p.get("exif") or {}).get("Xmp.GPano.ProjectionType", "")
    return fov == 360 or proj.lower() == "equirectangular"


def pmx_frame(f, city):
    lon, lat = f["geometry"]["coordinates"][:2]
    return {"src": "panoramax", "id": f["id"], "key": "p" + f["id"].replace("-", "")[:10],
            "seq": f["collection"], "rank": f["properties"].get("geovisio:rank_in_collection", 0),
            "lat": lat, "lon": lon, "pano": pmx_is_pano(f), "city": city,
            "ocr_url": f["assets"]["sd"]["href"], "hd_url": f["assets"]["hd"]["href"], "raw": f}


def pmx_frames(cities, budget):
    feats = []
    for cname, lat, lon in cities:
        try:
            fs, hosts = city_frames(lat, lon)
        except Blocked as e:
            print("   blocked:", e); continue
        reach = [f for f in fs if probe_reachable(hd_host(f))]
        print(f"   panoramax {cname}: {len(fs)} frames, reachable {len(reach)}", flush=True)
        feats += [pmx_frame(f, cname) for f in reach]
    return sample(feats, budget)


def sample(frames, budget):
    """Every ~STEP-th frame along each sequence (by rank), sequences interleaved."""
    by = {}
    for f in frames: by.setdefault(f["seq"], []).append(f)
    total = sum(len(v) for v in by.values())
    step = max(2, min(STEP, total // max(1, budget)))
    seqs = []
    for fs in by.values():
        fs.sort(key=lambda f: f["rank"])
        keep, last = [], None
        for f in fs:
            if last is None or f["rank"] - last >= step: keep.append(f); last = f["rank"]
        seqs.append(keep)
    out, i = [], 0
    while len(out) < budget and any(seqs):
        s = seqs[i % len(seqs)]
        if s: out.append(s.pop(0))
        i += 1
    return out

# ------------------------------------------------------------------ KartaView

def kv_nearby(lat, lon):
    """Nearest photo of each KartaView sequence around a point (API caps radius at 500 m)."""
    d = get_json(KV_API + "/2.0/photo/", {"lat": f"{lat:.5f}", "lng": f"{lon:.5f}", "radius": 500, "itemsPerPage": 100})
    xs = ((d or {}).get("result") or {}).get("data") or []
    return [x for x in xs if dist_m((lat, lon), (float(x["lat"]), float(x["lng"]))) <= 600]


def kv_photo(seq, idx):
    d = get_json(KV_API + "/2.0/photo/", {"sequenceId": seq, "sequenceIndex": idx})
    xs = ((d or {}).get("result") or {}).get("data") or []
    return xs[0] if xs else None


_kv_users = {}
def kv_user(seq):
    if seq not in _kv_users:
        d = get_json(f"{KV_API}/2.0/sequence/{seq}", {"join": "user"})
        data = ((d or {}).get("result") or {}).get("data") or {}
        u = data.get("user") or {}
        _kv_users[seq] = (u.get("username") or u.get("fullName") or "", data.get("countryCode", ""),
                          data.get("userId", ""))
    return _kv_users[seq]


def kv_is_pano(x):
    return x.get("projection") == "SPHERE" or str(x.get("fieldOfView")) == "360"


def kv_frame(x, city):
    return {"src": "kartaview", "id": str(x["id"]), "key": "k" + str(x["id"]), "seq": str(x["sequenceId"]),
            "rank": int(x["sequenceIndex"]), "lat": float(x["lat"]), "lon": float(x["lng"]),
            "pano": kv_is_pano(x), "city": city, "ocr_url": x["imageLthUrl"], "hd_url": x["imageProcUrl"], "raw": x}


def kv_frames(cities, budget):
    """Around each city point (+4 offsets ~900 m away), take each sequence's nearest frame and every
    STEP-th frame either side of it, staying within KV_RADIUS_M of the city point."""
    frames, seen = [], set()
    per_city = max(4, budget // max(1, len(cities)))
    for cname, lat, lon in cities:
        near = {}
        for dy, dx in ((0, 0), (0.008, 0), (-0.008, 0), (0, 0.008), (0, -0.008)):
            try:
                for x in kv_nearby(lat + dy, lon + dx / max(0.2, math.cos(math.radians(lat)))):
                    near.setdefault(str(x["sequenceId"]), x)
            except Blocked as e:
                print("   blocked:", e); return frames
        print(f"   kartaview {cname}: {len(near)} sequences nearby", flush=True)
        got = 0
        for seq, x in list(near.items())[:KV_SEQS_PER_CITY]:
            if got >= per_city: break
            i0 = int(x["sequenceIndex"])
            for k in (0, STEP, -STEP, 2 * STEP, -2 * STEP):
                if got >= per_city: break
                y = x if k == 0 else kv_photo(seq, i0 + k)
                if not y or y["id"] in seen or y.get("status") != "active": continue
                if dist_m((lat, lon), (float(y["lat"]), float(y["lng"]))) > KV_RADIUS_M: continue
                if not y.get("imageProcUrl") or not y.get("imageLthUrl"): continue
                seen.add(y["id"]); frames.append(kv_frame(y, cname)); got += 1
    return frames

# ------------------------------------------------------------------ OCR

_ocr = None
def ocr():
    global _ocr
    if _ocr is None:
        from rapidocr_onnxruntime import RapidOCR
        _ocr = RapidOCR()
    return _ocr

NOISE = re.compile(r"^[\d\s:/.\-,]+$|km/?h|mph|\d{4}[-/.]\d\d[-/.]\d\d|\d\d[-/.]\d\d[-/.]\d{4}|\d\d:\d\d", re.I)


def detect(path, pano):
    """Run PP-OCR; return list of (x0,y0,x1,y1,text,conf) in image pixels, and image size."""
    import numpy as np
    from PIL import Image
    im = Image.open(path).convert("RGB"); W, H = im.size
    cache = path + ".ocr.json"
    if os.path.exists(cache):
        return [tuple(b) for b in json.load(open(cache))], (W, H)
    arr = np.asarray(im)[:, :, ::-1]
    y_off = 0
    if pano:                                           # pitch +-45 deg band: skip sky and the car/rig
        y_off = H // 4; arr = arr[H // 4: 3 * H // 4]
    res, _ = ocr()(arr)
    boxes = []
    for quad, text, conf in res or []:
        xs = [p[0] for p in quad]; ys = [p[1] + y_off for p in quad]
        boxes.append((float(min(xs)), float(min(ys)), float(max(xs)), float(max(ys)), text.strip(), float(conf)))
    json.dump(boxes, open(cache, "w"), ensure_ascii=False)
    return boxes, (W, H)


# PP-OCRv3 "ch" recognises Chinese/Japanese kanji and Latin only. In countries whose script it cannot
# read, a sizeable, text-shaped detection box with an unconfident reading still counts (half weight).
READS_SCRIPT = {"Latin", "Han", "Japanese"}
_script_readable = [True]


def good(b, W, H):
    """Weight of a box: conf for a confident reading, 0.5 for an unread non-Latin-script box, else 0."""
    x0, y0, x1, y1, t, c = b
    bw, bh = x1 - x0, y1 - y0
    if bh < H * 0.012: return 0                         # tiny text
    if (y0 < H * 0.06 or y1 > H * 0.94) and re.search(r"\d", t): return 0   # burned-in captions
    if NOISE.search(t) and len(t) > 4: return 0         # timestamps / speed overlays
    if c >= 0.7 and len(re.sub(r"\W", "", t)) >= 2: return c
    if not _script_readable[0] and bh >= H * 0.018 and bw >= 1.5 * bh and not re.fullmatch(r"[\W\d]*", t):
        return 0.5
    return 0


def frame_score(boxes, W, H, pano):
    """Score = sum over the 8 largest good boxes of weight x area x position factor (/frame area x 1e4).
    Text below the horizon (vehicles, road, hand-held menus) counts 0.35x; frames that look like a
    document or menu (many small lines) are damped; text on the burned-in caption band is dropped."""
    g = [b[:5] + (good(b, W, H),) for b in boxes]
    g = [b for b in g if b[5] > 0]
    horizon = 0.5 if pano else 0.58
    def val(b):
        cy = (b[1] + b[3]) / 2 / H
        pos = 1.0 if cy <= horizon else 0.35
        return b[5] * (b[2] - b[0]) * (b[3] - b[1]) * pos
    top = sorted(g, key=val, reverse=True)[:8]
    s = sum(val(b) for b in top) / (W * H) * 1e4
    hs = sorted(b[3] - b[1] for b in g)
    if len(g) >= 12 and hs[len(hs) // 2] < 0.03 * H:   # menu / notice board / document close-up
        s *= 0.3
    return s, g


def cluster(g, W, pano):
    """The strongest text box plus good boxes near it -> (x0,y0,x1,y1) and the boxes in it."""
    best = max(g, key=lambda b: b[5] * (b[2] - b[0]) * (b[3] - b[1]))
    cx, cy = (best[0] + best[2]) / 2, (best[1] + best[3]) / 2
    reach = max(best[3] - best[1], 1) * 6
    sel = []
    for b in g:
        dx = abs((b[0] + b[2]) / 2 - cx)
        if pano: dx = min(dx, W - dx)
        if dx < reach and abs((b[1] + b[3]) / 2 - cy) < reach: sel.append(b)
    x0 = min(b[0] for b in sel); x1 = max(b[2] for b in sel)
    if pano and x1 - x0 > W / 2:                       # wraps the seam: keep the best box only
        sel = [best]; x0, x1 = best[0], best[2]
    return (x0, min(b[1] for b in sel), x1, max(b[3] for b in sel)), sel

# ------------------------------------------------------------------ crops

def rectilinear(src, yaw, pitch, fov, out_w, out_h):
    """Gnomonic view of an equirectangular panorama. yaw/pitch/fov in degrees (yaw 0 = image centre)."""
    import numpy as np, cv2
    from PIL import Image
    pano = np.asarray(Image.open(src).convert("RGB")); H, W = pano.shape[:2]
    f = (out_w / 2) / math.tan(math.radians(fov) / 2)
    u, v = np.meshgrid(np.arange(out_w) - out_w / 2 + 0.5, np.arange(out_h) - out_h / 2 + 0.5)
    x, y, z = u, -v, np.full_like(u, f)
    p, t = math.radians(pitch), math.radians(yaw)
    y2 = y * math.cos(p) + z * math.sin(p); z2 = -y * math.sin(p) + z * math.cos(p)
    x3 = x * math.cos(t) + z2 * math.sin(t); z3 = -x * math.sin(t) + z2 * math.cos(t)
    lon = np.arctan2(x3, z3); lat = np.arctan2(y2, np.hypot(x3, z3))
    mx = ((lon / (2 * math.pi) + 0.5) * W).astype(np.float32)
    my = ((0.5 - lat / math.pi) * H).astype(np.float32)
    out = cv2.remap(pano, mx, my, cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_WRAP)
    return Image.fromarray(out), (W, H)


def make_crop(fr, box_sd, sd_size, hd_path):
    """Returns (PIL image, derivative sentence) cut from the full-size image around box_sd (OCR-image pixels)."""
    from PIL import Image
    Wsd, Hsd = sd_size
    x0, y0, x1, y1 = box_sd
    what = "HD" if fr["src"] == "panoramax" else "full-size processed (blurred)"
    served = ("Panoramax instance" if fr["src"] == "panoramax" else "KartaView CDN")
    if fr["pano"]:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        yaw = (cx / Wsd - 0.5) * 360; pitch = (0.5 - cy / Hsd) * 180
        wdeg = (x1 - x0) / Wsd * 360; hdeg = (y1 - y0) / Hsd * 180
        fov = max(40.0, min(90.0, 3.0 * max(wdeg, hdeg * 4 / 3)))
        with Image.open(hd_path) as im: Whd = im.size[0]
        native = Whd / 360 * fov
        out_w = int(max(1000, min(2000, round(native / 10) * 10))); out_h = out_w * 3 // 4
        img, (W, H) = rectilinear(hd_path, yaw, pitch, fov, out_w, out_h)
        return img, (f"rectilinear (gnomonic) view, yaw {yaw:+.1f} deg from the panorama centre, pitch {pitch:+.1f} deg, "
                     f"horizontal field of view {fov:.0f} deg, {out_w}x{out_h} px, reprojected from the {W}x{H} {what} "
                     f"equirectangular panorama")
    im = Image.open(hd_path).convert("RGB"); W, H = im.size
    s = W / Wsd
    bx0, by0, bx1, by1 = x0 * s, y0 * s, x1 * s, y1 * s
    cw = max(1200, 4 * (bx1 - bx0), 4 / 3 * 4 * (by1 - by0)); ch = cw * 3 / 4
    cw, ch = min(cw, W), min(ch, H)
    if max(cw, ch) < 1000:
        if max(W, H) < 1000: return None, None
        cw, ch = W, H
    cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
    X0 = int(max(0, min(W - cw, cx - cw / 2))); Y0 = int(max(0, min(H - ch, cy - ch / 2)))
    X1, Y1 = int(X0 + cw), int(Y0 + ch)
    if (X0, Y0, X1, Y1) == (0, 0, W, H):                 # whole frame: keep the bytes as served
        im.info["_copy_from"] = hd_path
        return im, (f"whole {W}x{H} {what} picture as served by the {served} (byte-identical; the service "
                    f"blurs faces and number plates), not cropped")
    return im.crop((X0, Y0, X1, Y1)), f"crop {X0},{Y0},{X1},{Y1} of the {W}x{H} {what} picture"

# ------------------------------------------------------------------ staging

ROADWORDS = re.compile(r"路|街|巷|弄|道|通り|丁目|번길|로\b|길\b|rue|street|\bst\.?\b|road|\brd\b|avenue|ave\b|boulevard|"
                       r"strasse|straße|calle|via\b|ул\.?|улица|просп|шоссе|οδός|odos|شارع|ถนน|ซอย|jalan|\bjl\b|soi\b|"
                       r"đường|phố", re.I)

def kind_guess(texts):
    j = " ".join(texts)
    if ROADWORDS.search(j): return "street sign"
    if texts and all(re.fullmatch(r"[\d\-/A-Za-z]{1,6}", t) for t in texts): return "address plate"
    return "sign"


def cand_meta(fr):
    """Source-specific fields of the .cand.json."""
    if fr["src"] == "panoramax":
        f = fr["raw"]; p = f["properties"]; inst, inst_url = via(f)
        inst_url = (inst_url or "https://" + hd_host(f)).rstrip("/")
        author = p.get("geovisio:producer") or ", ".join(x["name"] for x in f.get("providers", []))
        lic_link = next((l for l in f.get("links", []) if l.get("rel") == "license"), {})
        date = (p.get("datetimetz") or p.get("datetime") or "")[:10]
        return {"title": f"Panoramax picture {fr['id']}" + (f" ({fr['city']}, {date})" if date else f" ({fr['city']})"),
                "page_url": f"{inst_url}/#focus=pic&pic={fr['id']}",
                "api_url": f"{PMX}/collections/{f['collection']}/items/{fr['id']}",
                "license": p.get("license") or lic_link.get("title", ""), "license_ref": lic_link.get("href", ""),
                "author": author, "credit": f"Panoramax, instance {inst or hd_host(f)} ({inst_url})",
                "date": date, "heading": p.get("view:azimuth")}
    x = fr["raw"]; user, country, uid = kv_user(fr["seq"])
    date = (x.get("shotDate") or x.get("dateAdded") or "")[:10]
    return {"title": f"KartaView photo {fr['id']}, sequence {fr['seq']} #{fr['rank']}"
                     + (f" ({fr['city']}, {date})" if date else f" ({fr['city']})"),
            "page_url": f"https://kartaview.org/details/{fr['seq']}/{fr['rank']}/track-info",
            "api_url": f"{KV_API}/2.0/photo/?sequenceId={fr['seq']}&sequenceIndex={fr['rank']}",
            "license": "CC BY-SA 4.0", "license_ref": "https://kartaview.org/terms (imagery under CC BY-SA 4.0)",
            "author": user, "credit": f"KartaView user {user} (user id {uid}); © KartaView contributors",
            "date": date, "heading": x.get("heading"), "kartaview_storage_url": x.get("fileurlProc")}


def stage(cc, fr, img, deriv, score, texts):
    key = fr["key"]
    sdir = os.path.join(STAGE, cc); rdir = os.path.join(REVIEW, cc)
    os.makedirs(sdir, exist_ok=True); os.makedirs(rdir, exist_ok=True)
    dst = os.path.join(sdir, key + ".jpg"); side = os.path.join(sdir, key + ".cand.json")
    rv = os.path.join(rdir, key + ".jpg")
    if os.path.exists(dst) or os.path.exists(side): return False
    m = cand_meta(fr)
    if img.info.get("_copy_from"):
        shutil.copyfile(img.info["_copy_from"], dst)
    else:
        img.save(dst, "JPEG", quality=92)
    w, h = img.size
    if not os.path.exists(rv):
        pv = img.copy(); pv.thumbnail((1600, 1600)); pv.save(rv, "JPEG", quality=85)
    src_name = "Panoramax" if fr["src"] == "panoramax" else "KartaView"
    c = {
        "key": key, "source": fr["src"], "id": fr["id"], "sequence": fr["seq"],
        "title": m["title"], "page_url": m["page_url"], "api_url": m["api_url"],
        "original_url": fr["hd_url"],
        "license": m["license"], "license_norm": "CC BY-SA 4.0", "license_url": LICENSE_URL,
        "license_ref": m["license_ref"], "author": m["author"], "credit": m["credit"],
        "description": (f"{'360-degree panorama' if fr['pano'] else 'Street-level picture'} on {src_name}, taken "
                        f"{m['date']} near {fr['city']} by {m['author']}, sequence {fr['seq']}, heading {m['heading']}. "
                        f"OCR (PP-OCRv3) read: " + " | ".join(texts[:12])),
        "date": m["date"], "categories": [], "width": w, "height": h, "mime": "image/jpeg",
        "lat": fr["lat"], "lon": fr["lon"], "kind_guess": kind_guess(texts), "score": round(score, 2),
        "found_by": f"{fr['src']}-ocr:{fr['city']}", "derivative": deriv, "downloaded_url": fr["hd_url"],
        "ocr_text": texts, "projection": "equirectangular" if fr["pano"] else "flat",
    }
    if m.get("kartaview_storage_url"): c["kartaview_storage_url"] = m["kartaview_storage_url"]
    json.dump(c, open(side, "w"), ensure_ascii=False, indent=1)
    return True


def prior_staged(cc):
    out = []
    for p in glob.glob(os.path.join(STAGE, cc, "[pk]*.cand.json")):
        c = json.load(open(p))
        if c.get("source") not in ("panoramax", "kartaview"): continue
        seq = c.get("sequence") or c.get("api_url", "").split("/collections/")[-1].split("/")[0]
        out.append({"id": str(c["id"]), "seq": seq, "lat": c.get("lat"), "lon": c.get("lon"), "src": c["source"]})
    return out


def too_close(fr, placed):
    """At most 2 crops per sequence within 100 m; none within 15 m of any other crop."""
    if fr["lat"] is None: return False
    same = 0
    for q in placed:
        if q["lat"] is None: continue
        d = dist_m((fr["lat"], fr["lon"]), (q["lat"], q["lon"]))
        if d < 15: return True
        if q["seq"] == fr["seq"] and d < 100: same += 1
    return same >= 2


def run_country(iso, name, script):
    cc = iso.lower(); cities = CITIES.get(iso, [])
    _script_readable[0] = script in READS_SCRIPT
    placed = prior_staged(cc)
    cap = CAP[0]
    if len(placed) >= cap: return {"frames": 0, "panoramax": 0, "kartaview": 0}
    budget = 6 * cap                                # frames sampled per source
    frames = []
    for src, fn in (("panoramax", pmx_frames), ("kartaview", kv_frames)):
        try:
            fs = fn(cities, budget)
        except Blocked as e:
            print("   blocked:", e); fs = []
        print(f"   {src}: {len(fs)} frames sampled", flush=True)
        frames += fs
    # interleave sources so both get OCR time
    a = [f for f in frames if f["src"] == "panoramax"]; b = [f for f in frames if f["src"] == "kartaview"]
    order_ = [x for pair in zip(a, b) for x in pair] + a[len(b):] + b[len(a):]
    done_ids = {q["id"] for q in placed}
    scored, n = [], 0
    for fr in order_:
        if fr["id"] in done_ids: continue
        try:
            if fr["src"] == "panoramax":
                sd = os.path.join(IMG, fr["id"] + "_sd.jpg")
                if not download(fr["ocr_url"], sd): continue
            else:   # KartaView thumbnails are 1280x720 whatever the shape: OCR a local 2048 px copy of the full image
                sd = os.path.join(IMG, "k" + fr["id"] + "_sd.jpg")
                if not os.path.exists(sd):
                    hd = os.path.join(IMG, "k" + fr["id"] + "_hd.jpg")
                    if not download(fr["hd_url"], hd): continue
                    from PIL import Image
                    with Image.open(hd) as im:
                        im = im.convert("RGB"); im.thumbnail((2048, 2048)); im.save(sd, "JPEG", quality=90)
            boxes, size = detect(sd, fr["pano"])
        except Blocked:
            continue
        except Exception as e:
            print("   ocr fail", fr["key"], e); continue
        n += 1
        s, g = frame_score(boxes, *size, fr["pano"])
        if g: scored.append((s, fr, g, size))
        if n >= 40 and sum(1 for x in scored if x[0] >= 5) >= 2 * cap: break    # plenty of strong frames
    scored.sort(key=lambda x: -x[0])
    got = {"panoramax": 0, "kartaview": 0}; seen_text = set()
    for s, fr, g, size in scored:
        if len(placed) >= cap or s < 1.0: break
        if too_close(fr, placed): continue
        box, sel = cluster(g, size[0], fr["pano"])
        texts = [(b[4] if b[5] != 0.5 else "[unread] " + b[4]) for b in sorted(g, key=lambda b: (b[1], b[0]))]
        sig = " ".join(sorted(b[4] for b in sel))
        if sig in seen_text: continue
        hd = os.path.join(IMG, (fr["id"] if fr["src"] == "panoramax" else "k" + fr["id"]) + "_hd.jpg")
        try:
            if not download(fr["hd_url"], hd): continue
            img, deriv = make_crop(fr, box, size, hd)
        except Blocked:
            continue
        except Exception as e:
            print("   crop fail", fr["key"], e); continue
        if img is None or max(img.size) < 1000: continue
        if stage(cc, fr, img, deriv, s, texts):
            got[fr["src"]] += 1; seen_text.add(sig)
            placed.append({"id": fr["id"], "seq": fr["seq"], "lat": fr["lat"], "lon": fr["lon"], "src": fr["src"]})
            print(f"   staged {fr['key']} score {s:.1f} {'pano' if fr['pano'] else 'flat'}: {sig[:60]}", flush=True)
    return {"frames": n, **got}

# ------------------------------------------------------------------ main

def order(only):
    o = sorted(COUNTRIES, key=lambda c: -priority(c[3], c[4]))
    return [(c[0], c[1], c[3]) for c in o if not only or c[0] in only]


def probe(only):
    out = {}
    path = os.path.join(WORK, "probe.json")
    if os.path.exists(path): out = json.load(open(path))
    for iso, name, _ in order(only):
        if iso in out: continue
        rec = []
        for cname, lat, lon in CITIES.get(iso, []):
            try:
                fs, hosts = city_frames(lat, lon)
            except Blocked as e:
                rec.append({"city": cname, "error": str(e)}); continue
            reach = sum(1 for f in fs if probe_reachable(hd_host(f)))
            pano = sum(1 for f in fs if pmx_is_pano(f))
            rec.append({"city": cname, "frames": len(fs), "reachable": reach, "pano": pano, "hosts": hosts})
        out[iso] = rec
        tot = sum(r.get("frames", 0) for r in rec); re_ = sum(r.get("reachable", 0) for r in rec)
        print(f"{iso} {name}: frames {tot}, reachable {re_}", flush=True)
        json.dump(out, open(path, "w"), indent=1)
    print("blocked hosts:", sorted(BLOCKED))


def probe_kv(only):
    """KartaView sequences near each city point (first city point only, one request per city)."""
    path = os.path.join(WORK, "probe_kv.json")
    out = json.load(open(path)) if os.path.exists(path) else {}
    for iso, name, _ in order(only):
        if iso in out: continue
        rec = {}
        for cname, lat, lon in CITIES.get(iso, []):
            rec[cname] = len(kv_nearby(lat, lon))
        out[iso] = rec
        print(f"{iso} {name}: kartaview sequences {rec}", flush=True)
        json.dump(out, open(path, "w"), indent=1)


def run(only):
    summary = {}
    for iso, name, script in order(only):
        print(f"{iso} {name}", flush=True)
        r = run_country(iso, name, script)
        summary[iso] = r
        print(f"{iso} {name}: OCR'd {r['frames']} frames, staged panoramax {r['panoramax']}, kartaview {r['kartaview']}", flush=True)
    path = os.path.join(WORK, "run_summary.json")
    old = json.load(open(path)) if os.path.exists(path) else {}
    old.setdefault("runs", []).append({"summary": summary, "blocked": sorted(BLOCKED), "cap": CAP[0]})
    json.dump(old, open(path, "w"), indent=1)
    print("blocked hosts:", sorted(BLOCKED))


if __name__ == "__main__":
    args = sys.argv[1:]
    cmd = args.pop(0) if args else "probe"
    if "--cap" in args:
        i = args.index("--cap"); CAP[0] = int(args[i + 1]); del args[i:i + 2]
    only = set(a.upper() for a in args)
    {"probe": probe, "probe_kv": probe_kv, "run": run}[cmd](only)
