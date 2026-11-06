"""Stage 1: find which per-country sign categories exist on Commons (and how many direct files they hold)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from countries import COUNTRIES
from wm import api

KINDS = {
    "street_name_signs": "Street name signs in {}",
    "house_numbers": "House numbers in {}",
    "address_signs": "Address signs in {}",
    "shop_signs": "Shop signs in {}",
    "commercial_signs": "Commercial signs in {}",
    "signboards": "Signboards in {}",
    "storefronts": "Storefronts in {}",
    "street_signs": "Street signs in {}",
    "signs": "Signs in {}",
}
titles = {}
for iso, name, variants, *_ in COUNTRIES:
    for v in variants:
        for kind, pat in KINDS.items():
            titles["Category:" + pat.format(v)] = (iso, kind)
tl = list(titles)
found = {}
for i in range(0, len(tl), 50):
    d = api({"action": "query", "titles": "|".join(tl[i:i+50]), "prop": "categoryinfo", "redirects": "1"})
    q = d.get("query", {})
    redir = {r["from"]: r["to"] for r in q.get("redirects", [])}
    norm = {n["from"]: n["to"] for n in q.get("normalized", [])}
    pages = {p["title"]: p for p in q.get("pages", [])}
    for t in tl[i:i+50]:
        tt = norm.get(t, t); tt = redir.get(tt, tt)
        p = pages.get(tt)
        if p and not p.get("missing"):
            iso, kind = titles[t]
            ci = p.get("categoryinfo", {})
            found.setdefault(iso, {})[kind] = {"cat": tt, "files": ci.get("files", 0), "subcats": ci.get("subcats", 0)}
    print(f"{i+50}/{len(tl)} checked, {sum(len(v) for v in found.values())} found", flush=True)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cache", "categories.json")
json.dump(found, open(out, "w"), indent=1, ensure_ascii=False)
missing = [c[1] for c in COUNTRIES if c[0] not in found]
print("countries with no sign categories:", missing)
