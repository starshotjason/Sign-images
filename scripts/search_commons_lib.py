"""Shared search helpers (Commons CirrusSearch; Openverse record conversion)."""
import html, re
from wm import api
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


def commons(query, how):
    return run(query, how)[0]

def from_openverse(x, q):
    lic = x["license"].upper()
    lic = "CC0" if lic == "CC0" else ("Public Domain Mark" if lic == "PDM" else f"CC {lic} {x.get('license_version') or ''}".strip())
    return {"source": "openverse", "provider": x.get("source"), "id": x["id"], "title": x.get("title") or x["id"],
            "page_url": x.get("foreign_landing_url"), "original_url": x.get("url"), "thumb_url": x.get("url"),
            "width": x.get("width"), "height": x.get("height"),
            "mime": "image/" + (x.get("filetype") or "jpeg").replace("jpg", "jpeg"),
            "license": lic, "license_url": x.get("license_url"), "author": x.get("creator") or "",
            "credit": x.get("attribution") or "", "description": "", "date": "", "lat": None, "lon": None,
            "categories": [t["name"] for t in x.get("tags", [])][:40], "found_by": "openverse:" + q}
