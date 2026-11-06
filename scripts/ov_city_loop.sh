#!/bin/bash
cd "$(dirname "$0")/.."
for q in "{city} sign" "{city} shop" "{city} street sign" "{city} hotel sign" "{city} museum sign" "{city} station sign" \
         "{city} restaurant sign" "{city} market sign" "{city} signboard" "{city} temple sign" "{city} mosque sign" \
         "{city} church sign" "{city} university sign" "{city} hospital sign" "{city} bank sign" "{city} pharmacy sign" \
         "{city} cafe sign" "{city} entrance sign" "{city} metro station"; do
  OV_QUERY="$q" python3 -u -I scripts/search_openverse.py
done
