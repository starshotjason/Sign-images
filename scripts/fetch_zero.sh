#!/bin/bash
# Fetch countries that have good candidates but < 3 staged photos (they sit late in the main loop's order).
cd "$(dirname "$0")/.."
Z=$(python3 -I -c "
import json,os,sys; sys.path.insert(0,'scripts')
from countries import COUNTRIES
out=[]
for c in COUNTRIES:
  p=f'cache/ranked/{c[0]}.json'
  if not os.path.exists(p): continue
  good=sum(1 for x in json.load(open(p)) if x['score']>=0)
  d=f'staging/{c[0].lower()}'
  st=len([f for f in os.listdir(d) if f.endswith('.cand.json')]) if os.path.isdir(d) else 0
  if good>=3 and st<8: out.append(c[0])
print(' '.join(out))")
[ -n "$Z" ] && python3 -u -I scripts/build_set.py fetch $Z
