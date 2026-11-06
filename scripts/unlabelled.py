"""Print unlabelled staged photos per country: '<total>' then 'cc:n ...'."""
import json, os, glob, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
rows = []
for d in sorted(glob.glob(os.path.join(ROOT, "staging", "*"))):
    cc = os.path.basename(d); lp = os.path.join(ROOT, "labels", cc + ".json")
    lab = json.load(open(lp)) if os.path.exists(lp) else {}
    un = [f for f in os.listdir(d) if f.endswith(".cand.json") and f[:-10] not in lab]
    if un: rows.append((cc, len(un)))
print(sum(n for _, n in rows)); print(" ".join(f"{c}:{n}" for c, n in rows))
