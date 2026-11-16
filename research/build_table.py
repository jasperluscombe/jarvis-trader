#!/usr/bin/env python3
"""Turn the downloaded bars into one table of (stock, day) rows the backtest can replay quickly.

    python3 research/build_table.py --data DATA_DIR      # writes DATA_DIR/table.pkl

Each row is one stock on one session with everything known BEFORE the trade (yesterday's close, 14-day ATR,
20-day average volume, the scanner's daily setups, the opening-range volume against its own 14-day average)
plus that day's 78 five-minute bars, so any entry / stop / target rule can be replayed on it.
Nothing from the future leaks into a row: daily numbers stop at the previous close.
"""
import argparse, datetime as dt, gzip, json, os, pickle, sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import scan  # noqa: E402

NBAR = 78  # 9:30 .. 15:55


def load(path):
    try:
        r = json.load(gzip.open(path))["chart"]["result"][0]
        q = r["indicators"]["quote"][0]
        return r.get("timestamp") or [], q
    except Exception:
        return [], None


def sessions_5m(path):
    """{date: (o,h,l,c,v) arrays of 78 bars, NaN where a bar is missing}"""
    ts, q = load(path)
    if not q:
        return {}
    days = {}
    for i, t in enumerate(ts):
        o, h, l, c, v = q["open"][i], q["high"][i], q["low"][i], q["close"][i], q["volume"][i]
        if None in (o, h, l, c) or t % 300:
            continue
        e = scan.ts_to_eastern(t)
        k = (e.hour * 60 + e.minute - 570) // 5
        if not 0 <= k < NBAR:
            continue
        a = days.get(e.date())
        if a is None:
            a = days[e.date()] = np.full((5, NBAR), np.nan)
        a[:, k] = (o, h, l, c, v or 0)
    return days


def daily(path):
    ts, q = load(path)
    if not q:
        return []
    out = {}
    for i, t in enumerate(ts):
        o, h, l, c, v = q["open"][i], q["high"][i], q["low"][i], q["close"][i], q["volume"][i]
        if None in (o, h, l, c):
            continue
        out[scan.ts_to_eastern(t).date()] = (o, h, l, c, v or 0)
    return sorted(out.items())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    a = ap.parse_args()
    syms = sorted(f[:-8] for f in os.listdir(os.path.join(a.data, "5m")))
    rows, bars = [], []
    for n, s in enumerate(syms):
        d5 = sessions_5m(os.path.join(a.data, "5m", s + ".json.gz"))
        dd = daily(os.path.join(a.data, "1d", s + ".json.gz"))
        if len(d5) < 20 or len(dd) < 40:
            continue
        ddates = [x[0] for x in dd]
        idx = {d: i for i, d in enumerate(ddates)}
        days = sorted(d5)
        for j, day in enumerate(days):
            i = idx.get(day)
            b = d5[day]
            if i is None or i < 35 or np.isnan(b[3, :3]).any():
                continue
            hist = dd[:i]  # strictly before today
            closes = [x[1][3] for x in hist]
            pc = closes[-1]
            tr = [max(hist[k][1][1] - hist[k][1][2], abs(hist[k][1][1] - hist[k - 1][1][3]),
                      abs(hist[k][1][2] - hist[k - 1][1][3])) for k in range(len(hist) - 14, len(hist))]
            atr = float(np.mean(tr))
            avgvol = float(np.mean([x[1][4] for x in hist[-20:]]))
            acr = float(np.mean([abs(closes[k] - closes[k - 1]) for k in range(len(closes) - 14, len(closes))]))
            tags, nums = scan.find_setups(closes[-60:])
            # opening-range volume vs the same 15 minutes (and first 5) over the previous 14 sessions
            prev = [d5[p] for p in days[max(0, j - 14):j]]
            rv15 = rv5 = np.nan
            if len(prev) >= 10:
                m15 = np.mean([np.nansum(p[4, :3]) for p in prev])
                m5 = np.mean([np.nan_to_num(p[4, 0]) for p in prev])
                rv15 = np.nansum(b[4, :3]) / m15 if m15 > 0 else np.nan
                rv5 = np.nan_to_num(b[4, 0]) / m5 if m5 > 0 else np.nan
            rows.append({"sym": s, "day": day, "pc": pc, "atr": atr, "acr": acr, "avgvol": avgvol, "tags": tuple(tags),
                         "rsi": nums.get("rsi"), "rv15": rv15, "rv5": rv5, "gap": b[0, 0] / pc - 1,
                         "ma20": float(np.mean(closes[-20:])), "ma50": float(np.mean(closes[-50:])) if len(closes) >= 50 else np.nan,
                         "ret5": pc / closes[-6] - 1, "ret20": pc / closes[-21] - 1,
                         "hi52": pc / max(closes[-250:]) - 1})
            bars.append(b.astype(np.float32))
        if n % 100 == 0:
            print(n, len(syms), len(rows), flush=True)
    pickle.dump({"rows": rows, "bars": np.stack(bars)}, open(os.path.join(a.data, "table.pkl"), "wb"), protocol=4)
    print("rows", len(rows), "symbols", len({r["sym"] for r in rows}), "days", len({r["day"] for r in rows}))


if __name__ == "__main__":
    main()
