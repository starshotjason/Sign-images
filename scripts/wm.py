"""Polite Wikimedia Commons API client: one request at a time, min interval, 429 backoff, disk cache."""
import hashlib, json, os, time, random
import requests

UA = "SignAddressTestset/0.1 (open-license street-sign test set builder; python-requests)"
API = "https://commons.wikimedia.org/w/api.php"
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cache", "api")
os.makedirs(CACHE, exist_ok=True)
S = requests.Session()
S.headers.update({"User-Agent": UA, "Accept-Encoding": "gzip"})
MIN_INTERVAL = float(os.environ.get("WM_MIN_INTERVAL", "5"))
_last = [0.0]

def api(params, use_cache=True):
    params = dict(params, format="json", formatversion="2", maxlag="5")
    key = hashlib.sha1(json.dumps(params, sort_keys=True).encode()).hexdigest()
    path = os.path.join(CACHE, key + ".json")
    if use_cache and os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    delay = 20
    for attempt in range(12):
        wait = MIN_INTERVAL - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        try:
            r = S.get(API, params=params, timeout=60)
        except requests.RequestException as e:
            print("  net error", e, flush=True); time.sleep(delay); delay = min(delay * 2, 300); continue
        if r.status_code == 429 or r.status_code >= 500:
            ra = r.headers.get("retry-after")
            w = (int(ra) if ra and ra.isdigit() else delay) + random.uniform(1, 4)
            print(f"  HTTP {r.status_code}, sleeping {w:.0f}s", flush=True)
            time.sleep(w); delay = min(delay * 2, 300); continue
        delay = 20
        d = r.json()
        if d.get("error", {}).get("code") == "maxlag":
            time.sleep(10); continue
        with open(path, "w") as f:
            json.dump(d, f)
        return d
    raise RuntimeError("giving up on " + json.dumps(params)[:200])
