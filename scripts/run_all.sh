#!/bin/bash
# (Re)start every background stage; safe to run repeatedly (all stages resume from cache).
cd "$(dirname "$0")/.."
pgrep -f search_commons.py >/dev/null || WM_MIN_INTERVAL=8 setsid nohup python3 -u -I scripts/search_commons.py >> search.log 2>&1 < /dev/null &
pgrep -f ov_loop.sh >/dev/null || setsid nohup scripts/ov_loop.sh >> ov.log 2>&1 < /dev/null &
pgrep -f fetch_loop.sh >/dev/null || setsid nohup scripts/fetch_loop.sh >> fetch.log 2>&1 < /dev/null &
pgrep -f "search_local.py" >/dev/null || WHICH=dest setsid nohup python3 -u -I scripts/search_local.py >> local_dest.log 2>&1 < /dev/null &
pgrep -f ov_city_loop.sh >/dev/null || setsid nohup scripts/ov_city_loop.sh >> ov_city.log 2>&1 < /dev/null &
pgrep -f fetch_zero.sh >/dev/null || setsid nohup scripts/fetch_zero.sh >> fetch.zero.log 2>&1 < /dev/null &
sleep 1; pgrep -af "search_commons|ov_loop|fetch_loop"
