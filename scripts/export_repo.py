"""Sync the assembled set + pipeline into the git repo dir and write README.md with coverage counts."""
import collections, json, os, shutil, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
REPO = sys.argv[1] if len(sys.argv) > 1 else "/home/user/streetzim-ocr-signs"
SRC = os.path.join(ROOT, "ocr-signs-world")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from countries import COUNTRIES, target

dst = os.path.join(REPO, "ocr-signs")
if os.path.exists(dst): shutil.rmtree(dst)
shutil.copytree(SRC, dst)
for sub in ("scripts", "labels"):
    d = os.path.join(REPO, sub)
    if os.path.exists(d): shutil.rmtree(d)
    shutil.copytree(os.path.join(ROOT, sub), d, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
shutil.copy(os.path.join(ROOT, "LABELING.md"), REPO)

recs = [json.loads(l) for l in open(os.path.join(SRC, "manifest.jsonl"))]
by_c = collections.defaultdict(list)
for r in recs: by_c[r["country"]].append(r)
names = {c[0]: (c[1], c[3], c[4]) for c in COUNTRIES}
size = sum(os.path.getsize(os.path.join(SRC, r["file"])) for r in recs)
cnt = lambda key: collections.Counter(key(r) for r in recs)
L = []
L.append("# StreetZim sign-reader photo set (world)\n")
L.append(f"**{len(recs)} openly licensed photos of street signs, address plates, business signs and landmark name boards "
         f"across {len(by_c)} countries**, {sum(1 for r in recs if r['lines'])} of them visually transcribed "
         f"({size/1e6:.0f} MB). Built for the photo search (`--ocr` sign reader) in "
         "[jasontitus/streetzim](https://github.com/jasontitus/streetzim), using the record format of its "
         "`docs/ocr-test-set.md` and `tests/fixtures/ocr-signs/`.\n")
L.append("Score it with streetzim's runner:\n\n```sh\npython3 tools/ocr_photos.py --set <this repo>/ocr-signs --maps <maps folder> --out <out>\n```\n")
L.append("## Layout\n\n- `ocr-signs/manifest.jsonl`: every record. `ocr-signs/<cc>/`: photos, `.source.json` provenance sidecars and the country's `manifest.jsonl`.\n"
         "- `ocr-signs/ATTRIBUTIONS.md`: per-photo credits. **Each photo keeps its own licence** (CC0 / PD / CC BY / CC BY-SA / OGDL-Taiwan); this repo's code licence does not apply to them.\n"
         "- `labels/`: raw review decisions, including rejects with reasons. `scripts/`: the crawl/rank/fetch/assemble pipeline. `LABELING.md`: the transcription rules.\n")
L.append("## Status of labels\n\n- `label_status: visually transcribed`: `lines`, `kind`, `scripts`, `expect.query/type`, `difficulty` written by a reviewer looking at the photo.\n"
         "- `label_status: unlabelled ...`: licence and provenance are complete, but `kind`/`scripts` are guessed from source categories and `lines` is empty.\n"
         "- **No `expect.record`/`expect.near` is map-verified yet** (`map_verification: pending`). `location` is the camera position when the source published one, never the target.\n")
L.append("## Image provenance\n\nThis cloud crawler's IP was throttled by Wikimedia's and Flickr's original-file servers, so some files are the "
         "sources' own published renditions rather than originals; each record's `derivative` field says exactly which (empty = byte-unmodified original):\n")
dv = cnt(lambda r: (r.get("derivative") or "original").split(" (")[0][:90])
for k, v in dv.most_common(): L.append(f"- {v}: {k}")
L.append("\n## Coverage\n\n| Source | Photos |\n|---|---:|")
for k, v in cnt(lambda r: r["source"]).most_common(): L.append(f"| {k} | {v} |")
L.append("\n| Kind | Photos |\n|---|---:|")
for k, v in cnt(lambda r: r["kind"]).most_common(): L.append(f"| {k} | {v} |")
L.append("\n| Licence | Photos |\n|---|---:|")
for k, v in cnt(lambda r: r["license"]).most_common(): L.append(f"| {k} | {v} |")
L.append("\n### By country\n\n| Country | Script | Income | Photos | Transcribed | Target |\n|---|---|---|---:|---:|---:|")
for iso, (nm, sc, inc) in sorted(names.items(), key=lambda x: x[1][0]):
    rs = by_c.get(iso, [])
    L.append(f"| {iso} {nm} | {sc} | {inc} | {len(rs)} | {sum(1 for r in rs if r['lines'])} | {target(sc, inc)} |")
missing = [names[i][0] for i in names if i not in by_c]
L.append(f"\n**No photos yet ({len(missing)}):** " + ", ".join(sorted(missing)) + "\n")
open(os.path.join(REPO, "README.md"), "w").write("\n".join(L) + "\n")
print(f"exported {len(recs)} records, {len(by_c)} countries, {size/1e6:.0f} MB -> {REPO}")
