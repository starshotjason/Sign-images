"""Stage 3: rank candidates, fetch source-published ORIGINALS, and assemble a streetzim-style
sign-reader photo set (layout of jasontitus/streetzim tests/fixtures/ocr-signs, docs/ocr-test-set.md).

  python3 -I scripts/build_set.py rank                 # cache/ranked/<ISO>.json
  python3 -I scripts/build_set.py fetch [ISO ...]      # originals into staging/<cc>/ (+ review copies)
  python3 -I scripts/build_set.py assemble             # ocr-signs-world/ from staging + labels/

Labels (visual transcription) live in labels/<cc>.json: {"<key>": {"accept": bool, "reason": "",
"kind": "", "scripts": [], "lines": [...], "expect": {"query": "", "type": ""}, "difficulty": "", "notes": ""}}.
"""
import csv, hashlib, html, io, json, os, re, sys, time, datetime
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from countries import COUNTRIES, priority, target
from wm import UA

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
CAND = os.path.join(ROOT, "cache", "candidates")
RANKED = os.path.join(ROOT, "cache", "ranked")
STAGE = os.path.join(ROOT, "staging")
REVIEW = os.path.join(ROOT, "review")
LABELS = os.path.join(ROOT, "labels")
OUT = os.path.join(ROOT, "ocr-signs-world")
STREETZIM = os.environ.get("STREETZIM", "/home/user/jasontitus/streetzim")
for d in (RANKED, STAGE, REVIEW, LABELS):
    os.makedirs(d, exist_ok=True)
S = requests.Session(); S.headers.clear(); S.headers.update({"User-Agent": UA, "Accept": "*/*"})

# streetzim priority list (docs/ocr-test-set.md) + our own: non-Latin script in a developing country
STREETZIM_PRIORITY = {"BH", "TW", "JP", "KR", "TH", "GR", "CH", "IR", "EG", "RU", "UA", "IN", "CN"}
def labelled_country(iso, script, income):
    return iso in STREETZIM_PRIORITY or (script != "Latin" and income != "H")

SCRIPT_CODES = {"Latin": ["Latn"], "Arabic": ["Arab"], "Ethiopic": ["Ethi"], "Cyrillic": ["Cyrl"], "Han": ["Hani"],
                "Japanese": ["Hani", "Hira", "Kana"], "Devanagari": ["Deva"], "Bengali": ["Beng"], "Tibetan": ["Tibt"],
                "Thaana": ["Thaa"], "Sinhala": ["Sinh"], "Khmer": ["Khmr"], "Lao": ["Laoo"], "Burmese": ["Mymr"],
                "Thai": ["Thai"], "Hangul": ["Hang"], "Hebrew": ["Hebr"], "Greek": ["Grek"], "Armenian": ["Armn"],
                "Georgian": ["Geor"]}
LANG_SCRIPT = {"tamil": "Taml", "telugu": "Telu", "kannada": "Knda", "malayalam": "Mlym", "bengali": "Beng",
               "gujarati": "Gujr", "gurmukhi": "Guru", "punjabi": "Guru", "odia": "Orya", "oriya": "Orya",
               "hindi": "Deva", "marathi": "Deva", "nepali": "Deva", "urdu": "Arab", "persian": "Arab",
               "arabic": "Arab", "chinese": "Hani", "russian": "Cyrl", "english": "Latn", "french": "Latn",
               "tifinagh": "Tfng", "berber": "Tfng", "amazigh": "Tfng", "tigrinya": "Ethi", "amharic": "Ethi",
               "sinhala": "Sinh", "tibetan": "Tibt", "dzongkha": "Tibt", "kurdish": "Arab"}

# ------------------------------------------------------------------ location sanity check
SAME_PLACE = {"PS": {"IL"}, "IL": {"PS"}, "XK": {"RS"}, "HK": {"CN"}, "MO": {"CN"}, "CY": {"CY"}}
ALL_NAMES = None
def geo_country(lat, lon):
    import reverse_geocode
    return reverse_geocode.search([(lat, lon)])[0]["country_code"]
def geo_mismatch(iso, c):
    if c.get("lat") is None or c.get("lon") is None: return False
    try: got = geo_country(float(c["lat"]), float(c["lon"]))
    except Exception: return False
    return got != iso and got not in SAME_PLACE.get(iso, set())
def other_country_named(iso, txt):
    """Another country's name appears as a word in the tags/title (keyword false positives such as 'Chad')."""
    global ALL_NAMES
    if ALL_NAMES is None:
        ALL_NAMES = [(c[0], re.compile(r"\b" + re.escape(c[1].lower()) + r"\b")) for c in COUNTRIES if len(c[1]) > 3]
        ALL_NAMES += [("GB", re.compile(r"\b(england|london|uk|birmingham|manchester|scotland)\b")),
                      ("US", re.compile(r"\b(usa|new york|california|texas|minneapolis|chicago|new mexico|albuquerque|ruidoso|"
                                         r"utah|las vegas|new orleans|disney|epcot|orlando|florida|seattle|atlanta|"
                                         r"kentucky|missouri|massachusetts|peabody|delaware|toronto|ontario|sydney|"
                                         r"melbourne|singapore|american samoa|pago pago|guam|mississippi|lowell|"
                                         r"peachtree|louisiana|hawaii)\b"))]
    return any(rx.search(txt) for code, rx in ALL_NAMES if code != iso)

# ------------------------------------------------------------------ ranking
LIC_OK = re.compile(r"^(cc0|cc by(-sa)? \d|cc-by(-sa)?-\d|public domain|pdm|public domain mark|cc by(-sa)?$)", re.I)

def norm_license(lic, url):
    l = (lic or "").strip(); u = (url or "").lower()
    if re.search(r"\bnc\b|\bnd\b|noncommercial|noderiv", l, re.I) or "/by-nc" in u or "/by-nd" in u:
        return None
    m = re.match(r"(?i)cc[ -]by[ -]sa[ -](\d\.\d)", l) or (re.search(r"/by-sa/(\d\.\d)", u) if "by-sa" in u else None)
    if m: return f"CC BY-SA {m.group(1)}"
    m = re.match(r"(?i)cc[ -]by[ -](\d\.\d)", l) or re.search(r"/licenses/by/(\d\.\d)", u)
    if m: return f"CC BY {m.group(1)}"
    if re.match(r"(?i)cc0", l) or "publicdomain/zero" in u: return "CC0 1.0"
    if re.match(r"(?i)(public domain|pd\b|pd-|pdm)", l) or "publicdomain/mark" in u: return "Public domain"
    return None

LICENSE_URLS = {"CC0 1.0": "https://creativecommons.org/publicdomain/zero/1.0/",
                "Public domain": "https://creativecommons.org/publicdomain/mark/1.0/"}
def license_url(lic, given):
    if lic in LICENSE_URLS: return given or LICENSE_URLS[lic]
    m0 = re.match(r"CC (BY(?:-SA)?) (\d\.\d)", lic or "")
    if m0 and given and f"/licenses/{m0.group(1).lower()}/{m0.group(2)}/" in given:
        return given                        # keep jurisdiction ports such as by/3.0/tw
    m = re.match(r"CC (BY(?:-SA)?) (\d\.\d)", lic)
    return f"https://creativecommons.org/licenses/{m.group(1).lower()}/{m.group(2)}/" if m else given

BAD = re.compile(r"\b(logos?|maps?|diagrams?|flags?|coats? of arms|drawings?|icons?|screenshots?|stamps?|banknotes?|"
                 r"coins?|documents?|scans?|pictograms?|charts?|illustrations?|fonts?|typefaces?|book covers?|"
                 r"posters?|packaging|bottles?|vehicle registration|licen[cs]e plates?|portraits?|people of|"
                 r"selfies?|interiors?|food|dishes|newspapers?|magazines?|calligraphy|manuscripts?|inscriptions?|"
                 r"epigraph|tombstones?|gravestones?|graves|cemeter)", re.I)
STREET = re.compile(r"street name|street sign|road name|name sign|street plate|nameplate", re.I)
ADDRESS = re.compile(r"house number|address|street number|door number|house numbering|building number", re.I)
TRANSIT = re.compile(r"bus stop|metro station|subway|railway station sign|station sign|tram stop|station name", re.I)
BUSINESS = re.compile(r"shop sign|signboard|storefront|shopfront|shop front|commercial sign|business sign|\bshops?\b|"
                      r"\bstores?\b|restaurant|hotel|pharmac|\bbanks?\b|market|bazaar|\bcaf[eé]|bakery|barber|salon|"
                      r"clinic|advertis|billboard", re.I)
LANDMARK = re.compile(r"museum|temple|mosque|church|cathedral|shrine|pagoda|monastery|school|university|college|"
                      r"hospital|ministry|embassy|park|palace|fort|castle|library|stadium|airport|post office|"
                      r"government|municipal|gate|entrance|zoo|theatre|theater|cinema|mausoleum|tomb of|monument|"
                      r"national park|heritage|citadel|bazaar|souk|medina|old city", re.I)
ROAD = re.compile(r"road signs|traffic signs|warning signs|regulatory signs|speed limit|traffic sign|road sign|"
                  r"no entry|prohibitory|stop signs|direction signs|distance signs", re.I)

PROTEST = re.compile(r"\b(protests?|protesters?|demonstrations?|rally|rallies|placards?|march for|solidarity|"
                     r"vigil|picket|boycott|free palestine|no war|stop the war|graffiti)\b", re.I)
NEWSY = re.compile(r"\b(korea\.net|us navy|navy|army|marines|air force|magharebia|usaid|embassy staff|"
                   r"ceremony|conference|press|summit|delegation|minister|president|visit of|official visit|"
                   r"naturali[sz]ation|citizenship)\b", re.I)
def low_all(t): return t.lower()

def guess_kind(txt):
    if ADDRESS.search(txt): return "address plate"
    if STREET.search(txt): return "street sign"
    if TRANSIT.search(txt): return "transit"
    if BUSINESS.search(txt): return "business sign"
    if LANDMARK.search(txt): return "landmark"
    if re.search(r"bilingual|trilingual|multilingual", txt, re.I): return "bilingual"
    if ROAD.search(txt): return "road sign"
    return "sign"

def score(c, langs, script):
    cats = " | ".join(c["categories"]); title = c["title"]
    txt = f"{title} | {cats} | {c.get('description') or ''}"
    kind = guess_kind(txt)
    s = {"address plate": 7, "street sign": 7, "transit": 6, "business sign": 6, "landmark": 6,
         "bilingual": 3, "sign": 1, "road sign": -1}[kind]
    if BAD.search(cats) or BAD.search(title): s -= 10
    if PROTEST.search(txt): s -= 6
    if NEWSY.search(txt) or NEWSY.search(c.get("author") or ""): s -= 5
    # Flickr matches are only trusted when a city of the country, or its local-script name, is in the tags/title
    if c.get("source") == "openverse" and c.get("_iso"):
        from cities import CITIES
        place_hit = any(ct.lower().split()[0] in low_all(txt) for ct in CITIES.get(c["_iso"], []))
        if place_hit: s += 2
        elif not c.get("found_by", "").startswith("openverse:") or not re.search(r"[^\x00-\u024f]", c.get("found_by", "")): s -= 8
    fb = c.get("found_by", "")
    if fb == "keyword" and c.get("_country") and c["_country"].lower() not in txt.lower(): s -= 8
    if (fb == "keyword" or c.get("source") == "openverse") and c.get("_iso") and other_country_named(c["_iso"], txt.lower()): s -= 8
    if fb.startswith(("deepcat:street_name", "deepcat:house", "deepcat:address")): s += 2
    elif fb.startswith(("deepcat:shop", "deepcat:commercial", "deepcat:signboards", "deepcat:storefronts")): s += 1
    local = [l for l in langs if l != "English"]
    low = txt.lower()
    if fb.startswith("local:") or (fb.startswith("openverse:") and re.search(r"[^\x00-\u024f]", fb)): s += 1
    if any(l.lower() in low for l in local) or re.search(r"bilingual|trilingual|multilingual", low): s += 3
    elif "english-language signs" in low and local: s -= 3
    if script != "Latin" and script.lower() in low: s += 1
    if c.get("lat") is not None: s += 1.5
    long_side = max(c.get("width") or 0, c.get("height") or 0)
    if long_side < 1000: s -= 100           # consumer requires >= 1000 px originals
    b = c.get("bytes") or 0
    if b > 20e6: s -= 100
    elif b > 10e6: s -= 2
    if c.get("mime") not in ("image/jpeg", "image/png"): s -= 100
    if c.get("source") == "openverse":
        s -= 0.5
        if not re.search(r"\bsigns?\b|signboard|signage|street ?name|storefront|shopfront|address", low): s -= 6
    return s, kind

def rank():
    for iso, name, variants, script, income, langs in COUNTRIES:
        files = [os.path.join(CAND, iso + x) for x in (".json", ".openverse.json", ".local.json")]
        cands = [c for f in files if os.path.exists(f) for c in json.load(open(f)) if not c.get("placeholder")]
        seen, pool = set(), []
        for c in cands:
            lic = norm_license(c.get("license"), c.get("license_url"))
            key = re.sub(r"\W", "", re.sub(r"\.\w+$", "", c["title"].replace("File:", "")).lower())[:60]
            if not lic or key in seen: continue
            seen.add(key)
            if geo_mismatch(iso, c): continue
            c["_country"] = name; c["_iso"] = iso
            c["license_norm"] = lic; c["key"] = (("c" if c["source"] == "wikimedia_commons" else "f") + str(c["id"]))[:40]
            c["score"], c["kind_guess"] = score(c, langs, script)
            if c["score"] > -50: pool.append(c)
        pool.sort(key=lambda c: -c["score"])
        json.dump(pool, open(os.path.join(RANKED, iso + ".json"), "w"), ensure_ascii=False, indent=0)
        print(f"{iso}: {len(pool)} usable, {sum(1 for c in pool if c['score'] >= 0)} with score>=0")

# ------------------------------------------------------------------ fetching originals
FLICKR_OK = {4: "CC BY 2.0", 5: "CC BY-SA 2.0", 9: "CC0 1.0", 10: "Public domain", 11: "CC BY 4.0", 12: "CC BY-SA 4.0"}
def flickr_original(page_url):
    """Fetch the Flickr photo page and return (original_url, photoModel-ish evidence) or (None, None)."""
    try:
        r = S.get(page_url, timeout=60)
    except requests.RequestException:
        return None, None
    if r.status_code != 200: return None, None
    t = r.text
    m = re.search(r'"o":\{"displayUrl":"(?P<u>[^"]+)","width":(?P<w>\d+),"height":(?P<h>\d+)', t)
    if not m:
        m = re.search(r'"o":\{[^{}]*?"url":"(?P<u>[^"]+_o\.(?:jpg|png))"[^{}]*?\}', t)
        if not m: return None, None
    url = m.group("u").replace("\\/", "/")
    if url.startswith("//"): url = "https:" + url
    lic = re.search(r'"license":(\d+)', t)
    if not lic or int(lic.group(1)) not in FLICKR_OK: return None, None
    g = re.search(r'"hasGeo":true,"latitude":(-?[\d.]+),"longitude":(-?[\d.]+)', t)
    return url, {"flickr_url": r.url, "flickr_license": FLICKR_OK[int(lic.group(1))],
                 "lat": float(g.group(1)) if g else None, "lon": float(g.group(2)) if g else None, "original_url": url, "flickr_license_code": int(lic.group(1)) if lic else None,
                 "retrieved": datetime.datetime.now(datetime.timezone.utc).isoformat()}

def commons_urls(c):
    """Commons media: upload.wikimedia.org throttles this client, but thumb.wikimedia.org (the host the
    Commons API itself returns for thumbnails) serves the standard renditions. Use the largest standard
    step >= 1000 px; fall back to the original on upload.wikimedia.org."""
    o = c["original_url"].split("?")[0]; w, h = c.get("width") or 0, c.get("height") or 0
    base = o.replace("://upload.wikimedia.org/wikipedia/commons/", "://thumb.wikimedia.org/wikipedia/commons/thumb/")
    fn = o.rsplit("/", 1)[1]
    out = []
    for step in (1920, 1280):
        if w > step and max(step, step * h / max(w, 1)) >= 1000:
            out.append((f"{base}/{step}px-{fn}", f"Wikimedia Commons standard {step}px-wide rendition (thumb.wikimedia.org)"))
    out.append((o, ""))
    return out

WM_BLOCKED_UNTIL = [0.0]
FLICKR_BLOCKED_UNTIL = [0.0]
HOST_INTERVAL = {"thumb.wikimedia.org": 1.5, "live.staticflickr.com": float(os.environ.get("FLICKR_INTERVAL", "31")), "api.openverse.org": 3.0}
_host_last = {}
BAD_PATH = os.path.join(ROOT, "cache", "geo_rejected.json")
def mark_bad(cc, key):
    d = json.load(open(BAD_PATH)) if os.path.exists(BAD_PATH) else {}
    d.setdefault(cc, []).append(key); json.dump(d, open(BAD_PATH, "w"))
def load_bad(cc):
    return set((json.load(open(BAD_PATH)) if os.path.exists(BAD_PATH) else {}).get(cc, []))

def get(url, path, patient=True):
    """Download url to path. Honour short Retry-After waits; give up on long ones."""
    wm = "upload.wikimedia.org" in url
    if wm and time.time() < WM_BLOCKED_UNTIL[0]: return None
    host = url.split("/")[2]
    if host == "live.staticflickr.com":
        if time.time() < FLICKR_BLOCKED_UNTIL[0]: return None
        patient = False
    for i in range(3):
        wait = HOST_INTERVAL.get(host, 0) - (time.time() - _host_last.get(host, 0))
        if wait > 0: time.sleep(wait)
        _host_last[host] = time.time()
        try:
            r = S.get(url, timeout=120)
            if r.status_code == 200 and len(r.content) > 10000:
                open(path, "wb").write(r.content); return r.content
            if r.status_code in (429, 503):
                ra = int(r.headers.get("retry-after") or 30)
                if wm:  # Wikimedia media: never wait in-line; skip Commons-native files for a while
                    WM_BLOCKED_UNTIL[0] = time.time() + max(ra, 60); return None
                if host == "live.staticflickr.com":
                    FLICKR_BLOCKED_UNTIL[0] = time.time() + 900; return None
                print(f"   {r.status_code} retry-after {ra}s from {url.split('/')[2]}", flush=True)
                if ra > 90 or not patient: return None
                time.sleep(min(ra, 30) + 3); continue
            print("   fail", r.status_code, url[:120], flush=True); return None
        except requests.RequestException as e:
            print("   err", e, flush=True); time.sleep(10)
    return None

def review_copy(src, dst):
    from PIL import Image, ImageOps
    im = Image.open(src); im = ImageOps.exif_transpose(im).convert("RGB")
    im.thumbnail((1600, 1600)); im.save(dst, "JPEG", quality=85)

def fetch(only):
    shard = os.environ.get("SHARD")  # "i/n": this worker takes every n-th country
    order = sorted(COUNTRIES, key=lambda c: -priority(c[3], c[4]))
    for idx, (iso, name, variants, script, income, langs) in enumerate(order):
        if only and iso not in only: continue
        if shard and idx % int(shard.split("/")[1]) != int(shard.split("/")[0]): continue
        p = os.path.join(RANKED, iso + ".json")
        if not os.path.exists(p): continue
        pool = [c for c in json.load(open(p)) if c["score"] >= 0]
        def quick(c):
            return True
        pool = [c for c in pool if quick(c)] + [c for c in pool if not quick(c)]
        tgt = target(script, income)
        accepted = sum(1 for v in load_labels(iso.lower()).values() if v.get("accept"))
        n = (2 * tgt if labelled_country(iso, script, income) else tgt + 5) + (tgt - min(accepted, tgt)) // 2  # reviewers reject ~half
        cc = iso.lower(); sdir = os.path.join(STAGE, cc); rdir = os.path.join(REVIEW, cc)
        os.makedirs(sdir, exist_ok=True); os.makedirs(rdir, exist_ok=True)
        rejected = {k for k, v in load_labels(cc).items() if not v.get("accept", True)} | load_bad(cc)
        per_author, got = {}, 0
        for c in pool:
            if got >= n: break
            if c["key"] in rejected: continue
            a = (c.get("author") or "?")[:40]
            if per_author.get(a, 0) >= 4: continue
            ext = ".png" if c.get("mime") == "image/png" else ".jpg"
            dst = os.path.join(sdir, c["key"] + ext); side = os.path.join(sdir, c["key"] + ".cand.json")
            if not os.path.exists(dst):
                if c["source"] == "wikimedia_commons":
                    ok = False
                    urls = commons_urls(c)
                    if time.time() < WM_BLOCKED_UNTIL[0]:
                        urls = [u for u in urls if "thumb.wikimedia.org" in u[0]]
                        if not urls: continue
                    for url, deriv in urls:
                        if url.startswith("flickr:"):
                            fu, ev = flickr_original("https://www.flickr.com/photo.gne?id=" + url[7:]); time.sleep(1)
                            if not fu: continue
                            c["flickr_evidence"] = ev; url = fu
                            if ev.get("lat") is not None and c.get("lat") is None:
                                c["lat"], c["lon"], c["location_from"] = ev["lat"], ev["lon"], "flickr"
                            if geo_mismatch(iso, c): mark_bad(cc, c["key"]); break
                        if get(url, dst, patient=not url == c["original_url"].split("?")[0]):
                            c["downloaded_url"] = url; c["derivative"] = deriv; ok = True; break
                    if not ok: continue
                else:
                    if c.get("provider") not in (None, "flickr") or "flickr.com" not in (c.get("page_url") or ""):
                        continue                  # only Flickr items from Openverse (others are stock/aggregators)
                    try:
                        url, ev = flickr_original(c["page_url"]); time.sleep(1)
                    except requests.RequestException as e:
                        print("   flickr page error", e.__class__.__name__, flush=True); continue
                    if not url: continue          # licence no longer open on Flickr, or no original
                    c["original_url"] = url; c["flickr_evidence"] = ev
                    if ev.get("lat") is not None:
                        c["lat"], c["lon"], c["location_from"] = ev["lat"], ev["lon"], "flickr"
                        if geo_mismatch(iso, c):
                            mark_bad(cc, c["key"]); print(f"   {iso}: {c['key']} geotagged outside the country, skipped", flush=True); continue
                    if time.time() >= FLICKR_BLOCKED_UNTIL[0] and get(url, dst, patient=False):
                        c["downloaded_url"] = url; c["derivative"] = ""
                    else:
                        FLICKR_BLOCKED_UNTIL[0] = time.time() + 1800
                        pu = f"https://api.openverse.org/v1/images/{c['id']}/thumb/?full_size=true&compressed=false"
                        if not get(pu, dst): continue
                        c["downloaded_url"] = pu
                        c["derivative"] = ("Flickr's published 1024 px 'large' rendition, served by the Openverse image "
                                           "API (Flickr originals were throttled for this client)")
                time.sleep(4)
            try:
                from PIL import Image
                with Image.open(dst) as im: w, h = im.size
                if max(w, h) < 1000: os.remove(dst); continue
                c["width"], c["height"] = w, h
                rv = os.path.join(rdir, c["key"] + ".jpg")
                if not os.path.exists(rv): review_copy(dst, rv)
            except Exception as e:
                print("   bad image", dst, e); os.remove(dst); continue
            json.dump(c, open(side, "w"), ensure_ascii=False, indent=1)
            per_author[a] = per_author.get(a, 0) + 1; got += 1
        print(f"{iso} {name}: staged {got}/{n}", flush=True)

# ------------------------------------------------------------------ regions
def load_regions():
    groups = {}
    for line in open(os.path.join(STREETZIM, "cloud", "m49-countries.tsv"), encoding="utf-8"):
        if line.startswith("#") or not line.strip(): continue
        f = line.rstrip("\n").split("\t")
        for g in f[1:]:
            if g: groups.setdefault(g, set()).add(f[0])
    maps = []
    for line in open(os.path.join(STREETZIM, "cloud", "region-places.tsv"), encoding="utf-8"):
        if line.startswith("#") or not line.strip(): continue
        f = (line.rstrip("\n").split("\t") + [""] * 5)[:5]
        rid, countries, sub = f[0], f[1], f[2]
        if sub or "light" in rid or "border" in rid: continue
        cs = set()
        for x in countries.split(";"):
            x = x.strip()
            if x.startswith("@"): cs |= groups.get(x[1:], set())
            elif x: cs.add(x)
        maps.append((rid, cs))
    return maps

ALIASES = {"Ivory Coast": "Côte d'Ivoire", "Republic of the Congo": "Congo", "Czech Republic": "Czechia",
           "Cape Verde": "Cabo Verde", "Sao Tome and Principe": "São Tomé and Príncipe", "Vatican City": "Holy See",
           "Micronesia": "Micronesia", "Palestine": "Palestine", "Eswatini": "Eswatini", "Timor-Leste": "Timor-Leste"}
def region_for(name, maps):
    n = ALIASES.get(name, name)
    hits = [(len(cs), rid) for rid, cs in maps if n in cs or name in cs]
    return min(hits)[1] if hits else ""

# ------------------------------------------------------------------ assembling
def load_labels(cc):
    p = os.path.join(LABELS, cc + ".json")
    return json.load(open(p)) if os.path.exists(p) else {}

def attribution(c, lic, lurl):
    via = SOURCE_NAMES.get(c["source"], c["source"])
    tail = ("Unmodified original." if not c.get("derivative") else c["derivative"] + ".")
    extra = " © KartaView contributors." if c["source"] == "kartaview" else ""
    return (f"Photo: {c.get('author') or 'unknown'}, {lic}, via {via}.{extra} Source: {c['page_url']}. "
            f"License: {lurl}. {tail}")
SOURCE_NAMES = {"wikimedia_commons": "Wikimedia Commons", "openverse": "Flickr", "flickr": "Flickr",
                "panoramax": "Panoramax", "kartaview": "KartaView"}
SOURCE_IDS = {"wikimedia_commons": "commons", "openverse": "flickr"}

def assemble():
    maps = load_regions()
    os.makedirs(OUT, exist_ok=True)
    allrecs = []
    for iso, name, variants, script, income, langs in COUNTRIES:
        cc = iso.lower(); sdir = os.path.join(STAGE, cc)
        if not os.path.isdir(sdir): continue
        labels = load_labels(cc); tgt = target(script, income)
        is_labelled = labelled_country(iso, script, income)
        rank_order = {c["key"]: i for i, c in enumerate(json.load(open(os.path.join(RANKED, iso + ".json"))))}
        staged = []
        for f in os.listdir(sdir):
            if f.endswith(".cand.json"):
                c = json.load(open(os.path.join(sdir, f)))
                lab = labels.get(c["key"])
                if lab is not None and not lab.get("accept", True): continue
                if geo_mismatch(iso, c): print(f"   {iso}: dropping {c['key']} (camera location outside the country)"); continue
                if is_labelled and lab is None: continue         # priority countries: reviewed photos only
                staged.append((c, lab))
        staged.sort(key=lambda x: (x[1] is None, rank_order.get(x[0]["key"], 1e9)))  # reviewed first
        staged = staged[:tgt]
        odir = os.path.join(OUT, cc); os.makedirs(odir, exist_ok=True)
        for f in os.listdir(odir): os.remove(os.path.join(odir, f))
        recs = []
        for i, (c, lab) in enumerate(staged, 1):
            ext = ".png" if c.get("mime") == "image/png" else ".jpg"
            rid = f"{cc}-{5000 + i}"; fn = rid + ext
            src = os.path.join(sdir, c["key"] + ext); data = open(src, "rb").read()
            dst = os.path.join(odir, fn)
            try: os.link(src, dst)
            except OSError: open(dst, "wb").write(data)
            lic = c.get("license_norm") or norm_license(c.get("license"), c.get("license_url"))
            lurl = license_url(lic, c.get("license_url"))
            txt = " | ".join(c["categories"]).lower()
            scripts = list(SCRIPT_CODES.get(script, ["Latn"]))
            for word, code in LANG_SCRIPT.items():
                if f"{word}-language" in txt and code not in scripts: scripts.append(code)
            lab = lab or {}
            loc = [c["lat"], c["lon"]] if c.get("lat") is not None else None
            rec = {
                "id": rid, "file": f"{cc}/{fn}", "sha256": hashlib.sha256(data).hexdigest(),
                "source": SOURCE_IDS.get(c["source"], c["source"]),
                "source_url": c["page_url"], "author": c.get("author") or "", "license": lic, "license_url": lurl,
                "attribution": attribution(c, lic, lurl), "country": iso, "region": region_for(name, maps),
                "kind": lab.get("kind") or c["kind_guess"],
                "scripts": lab.get("scripts") or scripts,
                "lines": lab.get("lines") or [],
                "expect": {"query": (lab.get("expect") or {}).get("query", ""), "record": "",
                           "type": (lab.get("expect") or {}).get("type", ""), "near": None, "in_map": None},
                "location": loc, "location_source": (c.get("location_from") or ("commons" if c["source"] == "wikimedia_commons" else "manual")) if loc else "",
                "difficulty": lab.get("difficulty", ""),
                "notes": lab.get("notes", ""),
                "original_url": c["original_url"], "width": c.get("width"), "height": c.get("height"),
                "derivative": c.get("derivative", ""),
                "map_verification": "pending",
                "label_status": "visually transcribed" if lab.get("lines") else "unlabelled (kind/scripts guessed from source categories)",
                "source_title": c["title"], "source_categories": c["categories"][:30],
            }
            if loc: rec["notes"] = (rec["notes"] + " " if rec["notes"] else "") + "location is where the photo was taken (Commons camera coordinates), not the target."
            ev = {"source": rec["source"], "source_url": c["page_url"], "original_url": c["original_url"],
                  "license_as_published": c.get("license"), "license_url_as_published": c.get("license_url"),
                  "author_as_published": c.get("author"), "credit_as_published": c.get("credit"),
                  "title": c["title"], "description": c.get("description"), "date": c.get("date"),
                  "categories": c["categories"], "camera_location": loc, "found_by": c.get("found_by"),
                  "bytes": len(data), "width": c.get("width"), "height": c.get("height")}
            ev["downloaded_url"] = c.get("downloaded_url", c["original_url"]); ev["derivative"] = c.get("derivative", "")
            if c.get("flickr_evidence"): ev["flickr"] = c["flickr_evidence"]; ev["openverse_id"] = c["id"]
            json.dump(ev, open(dst + ".source.json", "w"), ensure_ascii=False, indent=2)
            recs.append(rec)
        with open(os.path.join(odir, "manifest.jsonl"), "w") as f:
            for r in recs: f.write(json.dumps(r, ensure_ascii=False) + "\n")
        allrecs += recs
        print(f"{iso}: {len(recs)}/{tgt}")
    with open(os.path.join(OUT, "manifest.jsonl"), "w") as f:
        for r in allrecs: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(os.path.join(OUT, "ATTRIBUTIONS.md"), "w") as f:
        f.write("# Photo attributions\n\nThese photographs are third-party works, each under its own licence (below), "
                "not the licence of any software they ship with. Keep these credits, the manifests and the "
                "`.source.json` evidence with redistributed copies. Files are the source-published originals, byte-unmodified.\n")
        for r in allrecs:
            f.write(f"\n## {r['id']}\n\nFile: [{r['file']}]({r['file']})\n\n{r['attribution']}\n")
    print("total", len(allrecs))

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "rank": rank()
    elif cmd == "fetch": fetch(set(sys.argv[2:]))
    elif cmd == "assemble": assemble()
