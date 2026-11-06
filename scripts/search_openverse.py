"""Stage 2b: Openverse (indexes CC-licensed Flickr etc.). Anonymous quota is ~200 req/day, 20/min,
so one query per country, highest-priority countries first. Writes cache/candidates/<ISO>.openverse.json."""
import json, os, sys, time
import requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from countries import COUNTRIES, priority
from cities import CITIES
from wm import UA

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "cache", "candidates"); os.makedirs(OUT, exist_ok=True)
S = requests.Session(); S.headers["User-Agent"] = UA
QUERY = os.environ.get("OV_QUERY", "{name} sign")
only = sys.argv[1:]
for iso, name, variants, script, income, langs in sorted(COUNTRIES, key=lambda c: -priority(c[3], c[4])):
    if only and iso not in only: continue
    path = os.path.join(OUT, iso + ".openverse.json")
    prev = json.load(open(path)) if os.path.exists(path) else []
    for city in (CITIES.get(iso, [""]) if "{city}" in QUERY else [""]):
      q = QUERY.format(name=name, lang=langs[0], city=city)
      if any(c.get("found_by") == "openverse:" + q for c in prev): continue
      params = {"q": q, "license": "by,by-sa,cc0,pdm", "page_size": "20", "mature": "false",
                "excluded_source": "wikimedia"}
      for attempt in range(5):
          r = S.get("https://api.openverse.org/v1/images/", params=params, timeout=60)
          if r.status_code == 429:
              ra = int(r.headers.get("retry-after", "60") or 60)
              if ra > 3600: print("daily quota exhausted; stop", flush=True); sys.exit(0)
              time.sleep(ra + 2); continue
          break
      if r.status_code != 200: print(iso, "HTTP", r.status_code, flush=True); time.sleep(30); continue
      res = list(prev); have = {c["id"] for c in prev}
      for x in r.json().get("results", []):
          if x["id"] in have: continue
          lic = x["license"].upper(); lic = "CC0" if lic == "CC0" else ("Public Domain Mark" if lic == "PDM" else f"CC {lic} {x.get('license_version') or ''}".strip())
          res.append({"source": "openverse", "provider": x.get("source"), "id": x["id"], "title": x.get("title") or x["id"],
                      "page_url": x.get("foreign_landing_url"), "original_url": x.get("url"), "thumb_url": x.get("url"),
                      "width": x.get("width"), "height": x.get("height"), "mime": "image/" + (x.get("filetype") or "jpeg").replace("jpg", "jpeg"),
                      "license": lic, "license_url": x.get("license_url"), "author": x.get("creator") or "",
                      "credit": x.get("attribution") or "", "description": "", "date": "", "lat": None, "lon": None,
                      "categories": [t["name"] for t in x.get("tags", [])][:40], "found_by": "openverse:" + q})
      json.dump(res, open(path, "w"), ensure_ascii=False, indent=0); prev = res
      print(f"{iso} {name}: {len(res)} openverse candidates  (quota left: {r.headers.get('x-ratelimit-available-anon_sustained')})", flush=True)
      time.sleep(3.5)
