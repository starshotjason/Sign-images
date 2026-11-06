"""Stage 2c: local-language searches on Commons and Openverse (Flickr). Writes cache/candidates/<ISO>.local.json."""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from countries import COUNTRIES, priority
from local_terms import LOCAL, DEST, DEST_LANG
import search_commons_lib as scl
import requests
from wm import UA
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "cache", "candidates")
S = requests.Session(); S.headers["User-Agent"] = UA
which = os.environ.get("WHICH", "both")

def openverse(q):
    params = {"q": q, "license": "by,by-sa,cc0,pdm", "page_size": "20", "mature": "false", "excluded_source": "wikimedia"}
    for attempt in range(4):
        r = S.get("https://api.openverse.org/v1/images/", params=params, timeout=60)
        if r.status_code == 429:
            ra = int(r.headers.get("retry-after", "60") or 60)
            if ra > 3600: return None
            time.sleep(ra + 2); continue
        if r.status_code != 200: time.sleep(20); continue
        return [scl.from_openverse(x, q) for x in r.json().get("results", [])]
    return []

for iso, name, variants, script, income, langs in sorted(COUNTRIES, key=lambda c: -priority(c[3], c[4])):
    if iso not in LOCAL: continue
    lname, street, shop, sign = LOCAL[iso]
    path = os.path.join(OUT, iso + ".local.json")
    res = json.load(open(path)) if os.path.exists(path) else []
    done = {c["found_by"] for c in res}; have = {c["id"] for c in res}
    queries = []
    if which in ("both", "openverse"):
        queries += [("ov", f"{lname}"), ("ov", f"{shop} {name}"), ("ov", f"{street} {name}"), ("ov", f"{sign} {lname}")]
    if which in ("both", "openverse", "dest"):
        queries += [("ov", f"{w} {name}") for w in DEST.get(DEST_LANG.get(iso, ""), [])]
    if which == "dest": queries = [q for q in queries if any(q[1].startswith(w) for w in DEST.get(DEST_LANG.get(iso, ""), []))]
    if which in ("both", "commons"):
        queries += [("wm", f'{street} {lname} filetype:bitmap'), ("wm", f'{shop} {lname} filetype:bitmap'),
                    ("wm", f'{sign} {lname} filetype:bitmap')]
    for kind, q in queries:
        tag = ("openverse:" if kind == "ov" else "local:") + q
        if tag in done: continue
        rs = openverse(q) if kind == "ov" else scl.commons(q, tag)
        if rs is None: print("openverse quota exhausted", flush=True); which = "commons"; continue
        for r in rs:
            if r["id"] not in have: have.add(r["id"]); res.append(r)
        # record the query as done even when it returned nothing
        res.append({"id": "__q__" + tag, "found_by": tag, "placeholder": True}) if not rs else None
        json.dump(res, open(path, "w"), ensure_ascii=False, indent=0)
        if kind == "ov": time.sleep(3.5)
    print(f"{iso} {name}: {sum(1 for c in res if not c.get('placeholder'))} local-language candidates", flush=True)
