#!/usr/bin/env python3
"""Experiment E6: five candidate changes to the live rules, fixed before testing, on both datasets.

    python3 research/candidates.py --data DATA_DIR [--json OUT]

Baseline A = the live rules (see EXPERIMENTS.md). Candidates, each ONE change to A:
  B  limit entry at the signal price + 0.1 %, good for one bar (a missed fill = no trade)
  C  the same limit, good for two bars
  D  strong movers: up >= 5 % on the day (instead of 4 %)
  E  very strong movers: up >= 8 %
  F  market mood: SPY up on its previous close at the signal bar
Datasets: 60 days of 5-minute bars (the live setup exactly) and two years of hourly bars (first-hour range,
signals by 12:30, see hourly.py). Every candidate is run at 0.05 % and 0.2 % slippage a side; limit fills pay no
entry slippage (they fill at the limit or better) but the exit still does.
"""
import argparse, json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest import load, subset, trades, portfolio  # noqa: E402
import hourly  # noqa: E402

CANDS = {"A": "baseline (live rules)", "B": "limit +0.1 %, 1 bar", "C": "limit +0.1 %, 2 bars",
         "D": "up 5 %+ (not 4 %)", "E": "up 8 %+", "F": "only when SPY is up on the day"}


def stats(R, days=None):
    R = np.asarray(R, float)
    if len(R) < 5:
        return {"n": int(len(R))}
    w, l = R[R > 0], R[R <= 0]
    out = {"n": int(len(R)), "win": round(float((R > 0).mean()), 3), "avg_R": round(float(R.mean()), 3),
           "pf": round(float(w.sum() / -l.sum()), 2) if l.sum() < 0 else None}
    if days is not None:
        arr = [R[days == d] for d in np.unique(days)]
        rng = np.random.default_rng(11)
        b = [np.concatenate([arr[i] for i in rng.integers(0, len(arr), len(arr))]).mean() for _ in range(1500)]
        out.update(lo=round(float(np.percentile(b, 5)), 3), hi=round(float(np.percentile(b, 95)), 3))
    return out


def fmt(s):
    if s["n"] < 5:
        return "n=%d" % s["n"]
    rng = " [%+.3f, %+.3f]" % (s["lo"], s["hi"]) if "lo" in s else ""
    return "n=%5d win %3.0f%% avg %+.3fR%s PF %s" % (s["n"], 100 * s["win"], s["avg_R"], rng, s["pf"])


# ---------------------------------------------------------------- 5-minute bars
def five_minute(data):
    rows, bars = load(data)
    done = {}
    for r, b in zip(rows, bars):
        done.setdefault(r["day"], []).append(not np.isnan(b[0, 77]))
    complete = {d for d, v in done.items() if np.mean(v) > 0.8}
    spy = {r["day"]: (b, r["pc"]) for r, b in zip(rows, bars) if r["sym"] == "SPY"}
    keep = [i for i, r in enumerate(rows) if r["day"] in complete and 5 <= r["pc"] <= 40 and r["avgvol"] >= 1e6]
    rows, bars = subset(rows, bars, keep)

    def ip(g=0.04):
        return lambda r, x: x["day_ret"] >= g and r["rv15"] >= 1.5

    def spy_up(r, x):
        s = spy.get(r["day"])
        return s is not None and not np.isnan(s[0][3, x["i"]]) and s[0][3, x["i"]] > s[1]
    base = dict(stop="or-low", target=2.0, last_signal=12, min_risk_pct=0.01)
    cfg = {"A": (ip(), {}), "B": (ip(), dict(limit=0.001, limit_bars=1)), "C": (ip(), dict(limit=0.001, limit_bars=2)),
           "D": (ip(0.05), {}), "E": (ip(0.08), {}), "F": (lambda r, x: ip()(r, x) and spy_up(r, x), {})}
    out = {}
    for k, (flt, extra) in cfg.items():
        out[k] = {}
        for sl in (0.0005, 0.002):
            tr = trades(rows, bars, flt=flt, slip=sl, **base, **extra)
            out[k][sl] = tr
    # how many signals a limit order misses
    sig = len(trades(rows, bars, flt=ip(), slip=0.0005, **base))
    return out, sig, len(complete)


# ---------------------------------------------------------------- hourly bars
def hourly_run(data):
    """hourly.py's breakout, plus the limit entry and SPY's move at the signal bar."""
    spyH = hourly.load_1h(os.path.join(data, "1h", "SPY.json.gz"))
    spyD = hourly.load_1d(os.path.join(data, "1d", "SPY.json.gz"))
    spy_pc = {d: spyD.c.iloc[i - 1] for i, d in enumerate(spyD.index) if i}
    out = []
    syms = sorted(f[:-8] for f in os.listdir(os.path.join(data, "1h")))
    for s in syms:
        H, D = hourly.load_1h(os.path.join(data, "1h", s + ".json.gz")), hourly.load_1d(os.path.join(data, "1d", s + ".json.gz"))
        if len(H) < 40 or len(D) < 40:
            continue
        dd = {d: i for i, d in enumerate(D.index)}
        hdays = sorted(H)
        for j, day in enumerate(hdays):
            b = H[day]
            if np.isnan(b[:, 0]).any() or np.isnan(b[0, hourly.NB - 1]) or day not in dd or dd[day] < 21:
                continue
            k = dd[day]
            pc, avgv = D.c.iloc[k - 1], D.v.iloc[k - 21:k - 1].mean()
            if not (5 <= pc <= 40 and avgv >= 1e6):
                continue
            prev = [H[p][4, 0] for p in hdays[max(0, j - 14):j] if not np.isnan(H[p][4, 0])]
            if len(prev) < 10 or np.mean(prev) <= 0:
                continue
            rv, gain = b[4, 0] / np.mean(prev), b[3, 0] / pc - 1
            if gain < 0.04 or rv < 1.5:
                continue
            hi, lo = b[1, 0], b[2, 0]
            for i in (1, 2):
                if b[3, i] > hi:
                    sb = spyH.get(day)
                    spy_ret = (sb[3, i] / spy_pc[day] - 1) if sb is not None and day in spy_pc and not np.isnan(sb[3, i]) else np.nan
                    rec = {"day": day, "sym": s, "gain": gain, "spy_ret": spy_ret}
                    for sl in (0.0005, 0.002):
                        m = hourly.trade(b, i + 1, b[3, i], lo, sl)
                        rec["R_mkt_%g" % sl] = m["R"] if m else np.nan
                        rec["R_lim_%g" % sl] = lim_trade(b, i + 1, b[3, i], lo, sl)
                    out.append(rec)
                    break
    return pd.DataFrame(out)


def lim_trade(b, k, plan, stop, slip, limit=0.001):
    """Hourly limit entry: fills in bar k at its open if at or under plan x (1 + limit), or at the limit if bar k
    trades down to it; otherwise no trade."""
    if k >= hourly.NB or np.isnan(b[0, k]):
        return np.nan
    lim = plan * (1 + limit)
    o, l = b[0, k], b[2, k]
    fill = o if o <= lim else (lim if l <= lim else None)
    if fill is None:
        return np.nan
    risk = plan - stop
    if risk <= 0 or risk / plan < 0.01 or fill <= stop or fill >= plan + 2 * risk:
        return np.nan
    tgt = plan + 2 * risk
    for m in range(k, hourly.NB):
        o_, h_, l_ = b[0, m], b[1, m], b[2, m]
        if l_ <= stop:
            return (min(stop, o_) * (1 - slip) - fill) / risk
        if h_ >= tgt:
            return (max(tgt, o_) - fill) / risk
    return (b[3, hourly.NB - 1] * (1 - slip) - fill) / risk


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--json")
    a = ap.parse_args()
    res = {"candidates": CANDS, "five_minute": {}, "hourly": {}}
    fm, nsig, ndays = five_minute(a.data)
    print("== 60 days of 5-minute bars (%d days; the live rules were picked on these days)" % ndays)
    for k, v in fm.items():
        r1 = [t["R"] for t in v[0.0005]]; d1 = np.array([t["day"] for t in v[0.0005]])
        r2 = [t["R"] for t in v[0.002]]
        s1, s2 = stats(r1, d1), stats(r2)
        res["five_minute"][k] = {"slip_0.05": s1, "slip_0.2": s2}
        print("  %s %-30s %s   | at 0.2%%: %s" % (k, CANDS[k], fmt(s1), ("avg %+.3fR" % s2["avg_R"]) if s2["n"] >= 5 else "-"))
    print("  (limit orders: B filled %d and C %d of the %d baseline signals)" % (len(fm["B"][0.0005]), len(fm["C"][0.0005]), nsig))
    H = hourly_run(a.data)
    print("\n== two years of hourly bars (%d in-play breakouts, %s to %s)" % (len(H), H.day.min(), H.day.max()))
    days = H.day.values
    sel = {"A": (np.ones(len(H), bool), "mkt"), "B": (np.ones(len(H), bool), "lim"), "D": (H.gain.values >= 0.05, "mkt"),
           "E": (H.gain.values >= 0.08, "mkt"), "F": (H.spy_ret.values > 0, "mkt")}
    for k, (m, kind) in sel.items():
        R1, R2 = H["R_%s_0.0005" % kind].values, H["R_%s_0.002" % kind].values
        ok1, ok2 = m & ~np.isnan(R1), m & ~np.isnan(R2)
        s1, s2 = stats(R1[ok1], days[ok1]), stats(R2[ok2])
        res["hourly"][k] = {"slip_0.05": s1, "slip_0.2": s2}
        print("  %s %-30s %s   | at 0.2%%: %s" % (k, CANDS[k], fmt(s1), ("avg %+.3fR" % s2["avg_R"]) if s2["n"] >= 5 else "-"))
    H["year"] = pd.to_datetime(H.day).dt.year
    print("\n  by year (avg R at 0.05 %, market entry): " + "  ".join(
        "%d: A %+.3f (%d) F %+.3f (%d)" % (y, np.nanmean(g["R_mkt_0.0005"]), g["R_mkt_0.0005"].notna().sum(),
                                           np.nanmean(g.loc[g.spy_ret > 0, "R_mkt_0.0005"]), g.loc[g.spy_ret > 0, "R_mkt_0.0005"].notna().sum())
        for y, g in H.groupby("year")))
    if a.json:
        json.dump(res, open(a.json, "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
