#!/bin/bash
# Re-rank, then fetch with 4 parallel workers (disjoint country shards); repeat as searches fill in.
cd "$(dirname "$0")/.."
while true; do
  python3 -I scripts/build_set.py rank > /dev/null
  for i in 0 1 2; do SHARD="$i/3" python3 -u -I scripts/build_set.py fetch > "fetch.$i.log" 2>&1 & done
  wait
  echo "=== pass done $(date)"; sleep 120
done
