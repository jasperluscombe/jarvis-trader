#!/usr/bin/env python3
"""Two-year check of the in-play idea on 1-hour bars (Yahoo keeps 5-minute bars for only 60 days).

    python3 research/hourly.py --data DATA_DIR [--json OUT]

Rules were FIXED BEFORE LOOKING at this data, copied from the live bot and scaled to hourly bars:
  * opening range = the first hour (9:30-10:30);
  * in play = up >= 4 % on yesterday's close at 10:30, and first-hour volume >= 1.5x its average over the
    previous 14 sessions;
  * signal = the first hourly bar that CLOSES above the first-hour high, by 12:30; buy at the next bar's open;
  * stop = the first-hour low (skipped when closer than 1 %), target = 2R, otherwise sell at the close;
  * a bar touching both stop and target counts as the stop; 0.05 % slippage a side (re-run at 0.2 %).
Universe: $5-$40 on yesterday's close, >= 1M shares a day over 20 days.
Compared, on the same days: every first-hour breakout (no filter), and "buy any in-play stock at 11:30 with
the same stop" (does waiting for the breakout add anything?). Results are split into 6-month periods.
Caveats: the stock list is today's liquid stocks (survivors); hourly bars hide what happened inside the hour.
"""
import argparse, gzip, json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import scan  # noqa: E402

NB = 7  # 9:30, 10:30, ..., 15:30 (the last bar is half an hour)


def load_1h(path):
    try:
        r = json.load(gzip.open(path))["chart"]["result"][0]
        q = r["indicators"]["quote"][0]
    except Exception:
        return {}
    days = {}
    for i, ts in enumerate(r.get("timestamp") or []):
        o, h, l, c, v = (q[k][i] for k in ("open", "high", "low", "close", "volume"))
        if None in (o, h, l, c):
            continue
        e = scan.ts_to_eastern(ts)
        k = (e.hour * 60 + e.minute - 570) // 60
        if 0 <= k < NB and (e.hour * 60 + e.minute - 570) % 60 == 0:
            a = days.setdefault(e.date(), np.full((5, NB), np.nan))
            a[:, k] = (o, h, l, c, v or 0)
    return days


def load_1d(path):
    try:
        r = json.load(gzip.open(path))["chart"]["result"][0]
        q = r["indicators"]["quote"][0]
    except Exception:
        return pd.DataFrame()
    df = pd.DataFrame({"c": q["close"], "v": q["volume"]}, index=[scan.ts_to_eastern(t).date() for t in r["timestamp"]]).dropna()
    return df[~df.index.duplicated(keep="last")]


def run(data, slip=0.0005):
    out = []
    syms = sorted(f[:-8] for f in os.listdir(os.path.join(data, "1h")))
    for n, s in enumerate(syms):
        H, D = load_1h(os.path.join(data, "1h", s + ".json.gz")), load_1d(os.path.join(data, "1d", s + ".json.gz"))
        if len(H) < 40 or len(D) < 40:
            continue
        dd = list(D.index)
        hdays = sorted(H)
        for j, day in enumerate(hdays):
            b = H[day]
            if np.isnan(b[:, 0]).any() or np.isnan(b[0, NB - 1]) or day not in D.index:
                continue
            k = dd.index(day)
            if k < 21:
                continue
            pc, avgv = D.c.iloc[k - 1], D.v.iloc[k - 21:k - 1].mean()
            if not (5 <= pc <= 40 and avgv >= 1e6):
                continue
            prev = [H[p][4, 0] for p in hdays[max(0, j - 14):j] if not np.isnan(H[p][4, 0])]
            if len(prev) < 10 or np.mean(prev) <= 0:
                continue
            rv = b[4, 0] / np.mean(prev)
            gain = b[3, 0] / pc - 1
            hi, lo = b[1, 0], b[2, 0]
            base = {"day": day, "sym": s, "gain": gain, "rv": rv}
            # (a) the breakout: first bar closing above the first-hour high, by 12:30 (bars 1-2)
            for i in (1, 2):
                if b[3, i] > hi:
                    r = trade(b, i + 1, b[3, i], lo, slip)
                    if r:
                        out.append(dict(base, kind="breakout", **r))
                    break
            # (b) control: buy at 11:30 (bar 2 open) with the same stop, whatever the chart did
            r = trade(b, 2, b[0, 2], lo, slip)
            if r:
                out.append(dict(base, kind="buy_1130", **r))
        if n % 200 == 0:
            print("  %d / %d symbols" % (n, len(syms)), flush=True)
    return pd.DataFrame(out)


def trade(b, k, plan, stop, slip, target_r=2.0):
    risk = plan - stop
    if risk <= 0 or risk / plan < 0.01 or k >= NB or np.isnan(b[0, k]):
        return None
    fill = b[0, k] * (1 + slip)
    tgt = plan + target_r * risk
    if fill <= stop or fill >= tgt:
        return None
    for m in range(k, NB):
        o, h, l, c = b[:4, m]
        if l <= stop:
            return {"R": (min(stop, o) * (1 - slip) - fill) / risk, "how": "stop"}
        if h >= tgt:
            return {"R": (max(tgt, o) - fill) / risk, "how": "target"}
    return {"R": (b[3, NB - 1] * (1 - slip) - fill) / risk, "how": "close"}


def summ(df, name):
    if len(df) < 5:
        return {"label": name, "n": int(len(df))}
    R = df.R.values
    arr = [g.R.values for _, g in df.groupby("day")]
    rng = np.random.default_rng(5)
    boots = [np.concatenate([arr[i] for i in rng.integers(0, len(arr), len(arr))]).mean() for _ in range(1000)]
    w, l = R[R > 0], R[R <= 0]
    return {"label": name, "n": int(len(R)), "win": round(float((R > 0).mean()), 3), "avg_R": round(float(R.mean()), 3),
            "lo": round(float(np.percentile(boots, 5)), 3), "hi": round(float(np.percentile(boots, 95)), 3),
            "pf": round(float(w.sum() / -l.sum()), 2) if l.sum() < 0 else None}


def line(s):
    if s["n"] < 5:
        return "%-46s n=%d" % (s["label"], s["n"])
    return "%-46s n=%5d win %3.0f%% avg %+.3fR [%+.3f, %+.3f] PF %s" % (s["label"], s["n"], 100 * s["win"], s["avg_R"], s["lo"], s["hi"], s["pf"])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--json")
    a = ap.parse_args()
    df = run(a.data)
    df["period"] = pd.to_datetime(df.day).dt.to_period("Q").astype(str)
    ip = (df.gain >= 0.04) & (df.rv >= 1.5)
    out = {"from": str(df.day.min()), "to": str(df.day.max()), "days": int(df.day.nunique()), "symbols": int(df.sym.nunique())}
    print("\n%s to %s, %d trading days, %d stocks" % (out["from"], out["to"], out["days"], out["symbols"]))
    br, ctl = df.kind == "breakout", df.kind == "buy_1130"
    rows = [summ(df[br & ip], "IN PLAY + breakout (the live idea)"), summ(df[br], "every first-hour breakout (no filter)"),
            summ(df[br & (df.gain >= 0.04)], "breakout, up 4%+ only (no volume check)"), summ(df[ctl & ip], "in play, bought at 11:30, no breakout needed")]
    print("\n== the whole period"); [print("  " + line(s)) for s in rows]
    out["overall"] = rows
    print("\n== quarter by quarter: in play + breakout vs no filter")
    out["periods"] = []
    for p, g in df.groupby("period"):
        a1, a2 = summ(g[(g.kind == "breakout") & (g.gain >= 0.04) & (g.rv >= 1.5)], p), summ(g[g.kind == "breakout"], p)
        print("  %s  in play: %s   |   no filter: %s" % (p, ("n=%4d %+.3fR" % (a1["n"], a1["avg_R"])) if a1["n"] >= 5 else "n=%d" % a1["n"],
                                                       ("n=%5d %+.3fR" % (a2["n"], a2["avg_R"])) if a2["n"] >= 5 else ""))
        out["periods"].append({"period": p, "in_play": a1, "no_filter": a2})
    print("\n== threshold neighbours (breakout), whole period")
    out["grid"] = []
    for g_ in (0.02, 0.03, 0.04, 0.05, 0.08):
        cells = []
        for rv in (1.0, 1.5, 2.0, 3.0):
            s = summ(df[br & (df.gain >= g_) & (df.rv >= rv)], "up %d%% vol %gx" % (round(100 * g_), rv))
            cells.append(s); out["grid"].append(dict(s, gain=g_, rv=rv))
        print("  up %2d%%+: " % round(100 * g_) + "  ".join("vol %gx %+.3f (%d)" % (rv, c.get("avg_R", float("nan")), c["n"]) for rv, c in zip((1.0, 1.5, 2.0, 3.0), cells)))
    print("\n== costs")
    out["slippage"] = []
    for sl in (0.002,):
        d2 = run(a.data, slip=sl)
        s = summ(d2[(d2.kind == "breakout") & (d2.gain >= 0.04) & (d2.rv >= 1.5)], "in play + breakout at %.1f %% a side" % (100 * sl))
        out["slippage"].append(s); print("  " + line(s))
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
