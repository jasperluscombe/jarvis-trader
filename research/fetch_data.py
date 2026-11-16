#!/usr/bin/env python3
"""Download the data the backtest needs from Yahoo's free chart endpoints (the same ones Jarvis trades from).

    python3 research/fetch_data.py --out DATA_DIR            # universe -> liquid list -> 5-minute + daily bars

Writes DATA_DIR/liquid.json (symbols with price >= 3 and volume >= 500k today), DATA_DIR/5m/<SYM>.json.gz
(60 days of 5-minute bars, the most Yahoo gives) and DATA_DIR/1d/<SYM>.json.gz (2 years of daily bars).
Files already there are kept, so a stopped run can be continued.
"""
import argparse, concurrent.futures as cf, gzip, json, os, sys, time, urllib.request, urllib.error

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import scan  # noqa: E402  (the scanner's universe rules)

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
HOSTS = ("https://query2.finance.yahoo.com", "https://query1.finance.yahoo.com")


def get(path, tries=4):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(HOSTS[i % 2] + path, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            last = e
            if e.code == 404:
                return None
            time.sleep(2 + 3 * i)
        except Exception as e:
            last = e
            time.sleep(1 + i)
    print("failed", path[:60], last, file=sys.stderr)
    return None


def universe():
    texts = {}
    for f in scan.NASDAQ_FILES:
        req = urllib.request.Request(scan.NASDAQ_URL + f, headers={"User-Agent": UA})
        texts[f] = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
    built = scan.build_universe(texts)
    syms = built[0] if isinstance(built, tuple) else built
    return sorted(s[0] for s in syms)


def liquid(symbols, min_price, min_volume):
    out = {}

    def one(batch):
        raw = get("/v7/finance/spark?symbols=%s&range=5d&interval=1d" % ",".join(scan.to_yahoo(s) for s in batch))
        res = {}
        if raw:
            for r in (json.loads(raw).get("spark", {}).get("result") or []):
                m = ((r.get("response") or [{}])[0]).get("meta") or {}
                res[r.get("symbol")] = (m.get("regularMarketPrice") or 0, m.get("regularMarketVolume") or 0)
        return res
    batches = [symbols[i:i + 20] for i in range(0, len(symbols), 20)]
    with cf.ThreadPoolExecutor(4) as ex:
        for res in ex.map(one, batches):
            out.update(res)
    return {s: v for s, v in out.items() if v[0] >= min_price and v[1] >= min_volume}


def chart(sym, rng, interval, path):
    if os.path.exists(path):
        return True
    raw = get("/v8/finance/chart/%s?range=%s&interval=%s" % (scan.to_yahoo(sym), rng, interval))
    if not raw:
        return False
    with gzip.open(path, "wb") as f:
        f.write(raw)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--min-price", type=float, default=3)
    ap.add_argument("--min-volume", type=float, default=500000)
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    for d in ("5m", "1d"):
        os.makedirs(os.path.join(a.out, d), exist_ok=True)
    lp = os.path.join(a.out, "liquid.json")
    if os.path.exists(lp):
        liq = json.load(open(lp))
    else:
        u = universe()
        print("universe", len(u))
        liq = liquid(u, a.min_price, a.min_volume)
        for etf in ("SPY", "QQQ", "PSQ", "SH", "IWM"):
            liq.setdefault(etf, (0, 0))
        json.dump(liq, open(lp, "w"))
    syms = sorted(liq)
    print("liquid", len(syms))
    jobs = [(s, "60d", "5m", os.path.join(a.out, "5m", s + ".json.gz")) for s in syms]
    jobs += [(s, "2y", "1d", os.path.join(a.out, "1d", s + ".json.gz")) for s in syms]
    ok = 0
    with cf.ThreadPoolExecutor(a.workers) as ex:
        for i, r in enumerate(ex.map(lambda j: chart(*j), jobs)):
            ok += bool(r)
            if i % 300 == 0:
                print(i, "/", len(jobs), "ok", ok, flush=True)
    print("done", ok, "of", len(jobs))


if __name__ == "__main__":
    main()
