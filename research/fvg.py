#!/usr/bin/env python3
"""Experiment E8: the "fair value gap" (FVG) from ICT-style trading, against a random-entry control.

    python3 research/fvg.py --data DATA_DIR [--json OUT]

Rules, fixed before running (long only):
  bullish FVG   three consecutive candles where candle 3's low is above candle 1's high by >= 0.2 % of price
  entry         a limit buy at the top of the gap (candle 3's low) if price trades back down to it within the next
                12 bars (5-minute: one hour) / 5 bars (daily); the fill is the limit, or the bar's open if it gaps under
  stop          the bottom of the gap (candle 1's high); a fill whose stop is < 0.2 % away is skipped
  target        2R; a bar touching both counts as the stop; exits pay 0.05 % slippage
  time limit    5-minute: sold at the 15:55 bar's open, gaps formed 9:45-14:00 only; daily: sold after 10 days
  control       for every FVG trade, the same stock and day (5-minute) or period (daily), the same stop distance
                in % and the same 2R target, but bought at the open of a random bar in the same window, with no
                entry slippage either (like the FVG's limit fill): does the gap add
                anything over a random entry?
Universe: $5-$40, >= 1M shares a day (5-minute: 60 days; daily: ~950 stocks, 2 years).
"""
import argparse, json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest import load as load5  # noqa: E402
from swing import panel  # noqa: E402

SLIP, MIN_GAP = 0.0005, 0.002
rng = np.random.default_rng(8)


def run_bars(o, h, l, c, k_in, fill, stop, last, close_px_at, intrabar=False):
    """Walk bars from k_in (the fill bar) to `last`; returns R. close_px_at(k) gives the exit price at the time limit.
    intrabar=True: the fill happened partway through bar k_in (a limit touched), so that bar's high may have come
    BEFORE the fill: on that bar only the stop can count, never the target (no look-ahead)."""
    risk = fill - stop
    tgt = fill + 2 * risk
    for k in range(k_in, last + 1):
        if np.isnan(o[k]):
            continue
        if l[k] <= stop:
            px = (min(stop, o[k]) if k > k_in else stop) * (1 - SLIP)
            return (px - fill) / risk
        if intrabar and k == k_in:
            continue
        if h[k] >= tgt:
            return (max(tgt, o[k]) - fill) / risk
    return (close_px_at(last) * (1 - SLIP) - fill) / risk


def five_minute(data):
    rows, bars = load5(data)
    fv, ctl = [], []
    for r, b in zip(rows, bars):
        if not (5 <= r["pc"] <= 40 and r["avgvol"] >= 1e6) or np.isnan(b[0, 77]):
            continue
        o, h, l, c = b[0], b[1], b[2], b[3]
        k = 5
        while k <= 54:                                   # candle 3 closes by 14:00 (bar 54 starts 14:00)
            if np.isnan(h[k - 2]) or np.isnan(l[k]) or not (l[k] - h[k - 2]) / c[k] >= MIN_GAP or k < 5:
                k += 1
                continue
            top, bot = l[k], h[k - 2]
            if (top - bot) / top < MIN_GAP:
                k += 1
                continue
            fill_k = None
            for j in range(k + 1, min(k + 13, 77)):
                if not np.isnan(l[j]) and l[j] <= top:
                    fill_k, fill = j, min(top, o[j])
                    break
            if fill_k is not None and (fill - bot) / fill >= MIN_GAP:
                R = run_bars(o, h, l, c, fill_k, fill, bot, 77, lambda kk: o[77], intrabar=o[fill_k] > top)
                risk_pct = (fill - bot) / fill
                fv.append({"day": r["day"], "sym": r["sym"], "R": R})
                # control: random entry bar in the same window (k+1 .. k+12), market buy at its open, same stop %
                j = int(rng.integers(k + 1, min(k + 13, 77)))
                if not np.isnan(o[j]):
                    f2 = o[j]
                    ctl.append({"day": r["day"], "sym": r["sym"], "R": run_bars(o, h, l, c, j, f2, f2 * (1 - risk_pct), 77, lambda kk: o[77])})
                k = fill_k + 1                           # one trade at a time per stock
            else:
                k += 1
    return pd.DataFrame(fv), pd.DataFrame(ctl)


def daily(data):
    fr = panel(data)
    fv, ctl = [], []
    for s, d in fr.items():
        if s in ("SPY", "QQQ", "IWM", "PSQ", "SH") or len(d) < 60:
            continue
        o, h, l, c = d.o.values, d.h.values, d.l.values, d.c.values
        dv = (d.v * d.c).rolling(20).mean().values
        n, k = len(d), 22
        while k < n - 16:
            if not (5 <= c[k] <= 40 and dv[k] > 20e6):
                k += 1
                continue
            top, bot = l[k], h[k - 2]
            if (top - bot) / top < MIN_GAP:
                k += 1
                continue
            fill_k = None
            for j in range(k + 1, k + 6):
                if l[j] <= top:
                    fill_k, fill = j, min(top, o[j])
                    break
            if fill_k is not None and (fill - bot) / fill >= MIN_GAP:
                last = fill_k + 10
                R = run_bars(o, h, l, c, fill_k, fill, bot, last, lambda kk: c[kk], intrabar=o[fill_k] > top)
                risk_pct = (fill - bot) / fill
                fv.append({"day": d.index[fill_k], "sym": s, "R": R})
                j = int(rng.integers(k + 1, k + 6))
                f2 = o[j]
                ctl.append({"day": d.index[j], "sym": s, "R": run_bars(o, h, l, c, j, f2, f2 * (1 - risk_pct), j + 10, lambda kk: c[kk])})
                k = last + 1
            else:
                k += 1
    return pd.DataFrame(fv), pd.DataFrame(ctl)


def summ(df, label):
    R = df.R.values
    arr = [g.R.values for _, g in df.groupby("day")]
    b = [np.concatenate([arr[i] for i in rng.integers(0, len(arr), len(arr))]).mean() for _ in range(1000)]
    w, l = R[R > 0], R[R <= 0]
    s = {"label": label, "n": int(len(R)), "win": round(float((R > 0).mean()), 3), "avg_R": round(float(R.mean()), 3),
         "lo": round(float(np.percentile(b, 5)), 3), "hi": round(float(np.percentile(b, 95)), 3),
         "pf": round(float(w.sum() / -l.sum()), 2) if l.sum() < 0 else None}
    print("  %-34s n=%6d win %3.0f%% avg %+.3fR [%+.3f, %+.3f] PF %s" % (label, s["n"], 100 * s["win"], s["avg_R"], s["lo"], s["hi"], s["pf"]))
    return s


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--json")
    a = ap.parse_args()
    out = {}
    print("== 5-minute bars, 60 days (day trades)")
    f, c = five_minute(a.data)
    out["five_minute"] = [summ(f, "fair value gap"), summ(c, "random entry, same stop & target")]
    print("== daily bars, ~2 years (held up to 10 days)")
    f, c = daily(a.data)
    out["daily"] = [summ(f, "fair value gap"), summ(c, "random entry, same stop & target")]
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1)


if __name__ == "__main__":
    main()
