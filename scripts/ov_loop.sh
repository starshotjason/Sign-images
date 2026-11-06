#!/bin/bash
cd "$(dirname "$0")/.."
for q in "{name} sign" "{name} street sign" "{name} shop sign" "{name} storefront" "{name} signboard" "{name} street name"; do
  OV_QUERY="$q" python3 -u -I scripts/search_openverse.py
done
