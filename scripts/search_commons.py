"""Stage 2: per country, pull candidate files from the sign categories via CirrusSearch deepcat,
plus keyword fallbacks. Writes cache/candidates/<ISO>.json (one record per file)."""
import json, os, re, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from countries import COUNTRIES, priority, target
from wm import api

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CATS = json.load(open(os.path.join(ROOT, "cache", "categories.json")))
OUT = os.path.join(ROOT, "cache", "candidates"); os.makedirs(OUT, exist_ok=True)
ORDER = ["street_name_signs", "house_numbers", "address_signs", "shop_signs", "commercial_signs",
         "signboards", "storefronts", "street_signs", "signs"]
META = "LicenseShortName|LicenseUrl|Artist|Credit|ImageDescription|DateTimeOriginal|GPSLatitude|GPSLongitude|ObjectName"

def strip(s):
    s = re.sub(r"<[^>]+>", " ", s or ""); return re.sub(r"\s+", " ", html.unescape(s)).strip()

def run(query, how, limit=50, offset=0):
    p = {"action": "query", "generator": "search", "gsrnamespace": "6", "gsrlimit": str(limit),
         "gsrsearch": query, "prop": "imageinfo|categories|coordinates", "cllimit": "max", "clshow": "!hidden",
         "iiprop": "url|size|extmetadata|mime", "iiurlwidth": "1280", "iiextmetadatafilter": META,
         "coprimary": "all"}
    if offset: p["gsroffset"] = str(offset)
    d = api(p)
    res = []
    for pg in d.get("query", {}).get("pages", []):
        ii = (pg.get("imageinfo") or [{}])[0]
        if not ii or ii.get("mime") not in ("image/jpeg", "image/png", "image/webp", "image/tiff"):
            continue
        em = {k: v.get("value") for k, v in ii.get("extmetadata", {}).items()}
        co = (pg.get("coordinates") or [{}])[0]
        lat = co.get("lat") or em.get("GPSLatitude"); lon = co.get("lon") or em.get("GPSLongitude")
        res.append({
            "source": "wikimedia_commons", "id": pg["pageid"], "title": pg["title"],
            "page_url": ii.get("descriptionurl"), "original_url": ii.get("url"),
            "thumb_url": ii.get("thumburl"), "width": ii.get("width"), "height": ii.get("height"), "bytes": ii.get("size"),
            "mime": ii.get("mime"),
            "license": strip(em.get("LicenseShortName")), "license_url": em.get("LicenseUrl"),
            "author": strip(em.get("Artist"))[:200], "credit": strip(em.get("Credit"))[:200],
            "description": strip(em.get("ImageDescription"))[:500],
            "date": strip(em.get("DateTimeOriginal"))[:40],
            "lat": float(lat) if lat not in (None, "") else None, "lon": float(lon) if lon not in (None, "") else None,
            "categories": [c["title"][9:] for c in pg.get("categories", [])],
            "found_by": how,
        })
    return res, d.get("warnings")

todo = sys.argv[1:] or None
for iso, name, variants, script, income, langs in sorted(COUNTRIES, key=lambda c: -priority(c[3], c[4])):
    if todo and iso not in todo: continue
    path = os.path.join(OUT, iso + ".json")
    if os.path.exists(path): continue
    tgt = target(script, income); cands = {}
    def add(rs):
        for r in rs: cands.setdefault(r["id"], r)
    cats = CATS.get(iso, {})
    for kind in ORDER:
        if kind in cats:
            rs, w = run(f'deepcat:"{cats[kind]["cat"]}" filetype:bitmap', "deepcat:" + kind)
            add(rs)
            if kind == "signs" and len(rs) == 50 and priority(script, income) >= 2:
                add(run(f'deepcat:"{cats[kind]["cat"]}" filetype:bitmap', "deepcat:signs", offset=50)[0])
    if len(cands) < 3 * tgt:
        for q in [f'"street sign" "{name}" filetype:bitmap', f'shop sign "{name}" filetype:bitmap',
                  f'signboard "{name}" filetype:bitmap']:
            add(run(q, "keyword")[0])
    json.dump(list(cands.values()), open(path, "w"), ensure_ascii=False, indent=0)
    print(f"{iso} {name}: {len(cands)} candidates (cats: {', '.join(cats) or 'none'})", flush=True)
