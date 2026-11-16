#!/usr/bin/env python3
"""Swing trades with a fixed 1:2 risk:reward, held for days, on 2 years of daily bars.

    python3 research/swing_rr.py --data DATA_DIR [--json OUT]

Entry (Connors & Alvarez, "Short Term Trading Strategies That Work", 2008): the stock closed above its 200-day
average (an uptrend) and its 2-day RSI fell under 10 (a sharp short dip). Buy at the NEXT day's open.
Stop: 1 x ATR(14) under the entry. Target: 2 x ATR above it (1:2). If neither is hit in 10 trading days, sell at
the next open. On a day whose range touches both, the stop is assumed first; a gap through the stop fills at the
open. 0.05 % slippage a side.

The account: cash only (under $2,000 there is no margin), 3 % of the account at risk a trade, whole shares, each
position at most 90 % of the account and never more than the cash in hand; when more stocks signal than there is
cash for, the deepest dip (lowest RSI 2) goes first.
Caveat: the stock list is today's liquid stocks, so companies that collapsed in the last two years are missing.
"""
import argparse, json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swing import panel, rsi, SLIP  # noqa: E402

ETFS = {"SPY", "QQQ", "IWM", "PSQ", "SH"}


ENTRIES = {
    # Connors & Alvarez: a sharp 2-day dip in a stock above its 200-day average
    "dip": lambda c, ma50, ma200, r2, hi20, i: c[i] > ma200[i] and r2[i] < 10,
    # momentum: a new 20-day closing high in a stock above its 50- and 200-day averages
    "breakout": lambda c, ma50, ma200, r2, hi20, i: c[i] > hi20[i] and c[i] > ma50[i] > ma200[i],
    # baseline: any day in an uptrend (what a coin flip in the same stocks earned)
    "any_uptrend": lambda c, ma50, ma200, r2, hi20, i: c[i] > ma200[i] and i % 5 == 0,
}


def signals(fr, entry="dip", stop_atr=1.0, target_r=2.0, max_days=10, lo=5.0, hi=1e9, exit_ma5=False):
    """exit_ma5: Connors' own exit (sell the day after a close above the 5-day average) instead of the target."""
    out = []
    rule = ENTRIES[entry]
    for s, d in fr.items():
        if s in ETFS or len(d) < 230:
            continue
        c, h, l, o = d.c.values, d.h.values, d.l.values, d.o.values
        tr = np.maximum(d.h - d.l, np.maximum((d.h - d.c.shift()).abs(), (d.l - d.c.shift()).abs()))
        atr = tr.rolling(14).mean().values
        ma200 = d.c.rolling(200).mean().values
        r2 = rsi(d.c, 2).values
        ma50 = d.c.rolling(50).mean().values
        ma5 = d.c.rolling(5).mean().values
        hi20 = d.c.shift(1).rolling(20).max().values
        dv = (d.v * d.c).rolling(20).mean().values
        n = len(d)
        for i in range(200, n - 1):
            if not (rule(c, ma50, ma200, r2, hi20, i) and lo <= c[i] <= hi and dv[i] > 20e6):
                continue
            fill = o[i + 1] * (1 + SLIP)
            risk = stop_atr * atr[i]
            stop, tgt = fill - risk, fill + target_r * risk
            how, j, px = "time", None, None
            for k in range(i + 1, min(n, i + 1 + max_days)):
                if l[k] <= stop:
                    how, j, px = "stop", k, min(stop, o[k]) if k > i + 1 else stop
                    break
                if not exit_ma5 and h[k] >= tgt:
                    how, j, px = "target", k, max(tgt, o[k]) if k > i + 1 else tgt
                    break
                if exit_ma5 and c[k] > ma5[k] and k + 1 < n:
                    how, j, px = "bounce", k + 1, o[k + 1]
                    break
            if j is None:
                j = min(n - 1, i + max_days + 1)
                px = o[j]
                if i + max_days + 1 > n - 1:
                    how = "open"  # still running at the end of the data
            px *= (1 - SLIP)
            out.append({"sym": s, "sig": d.index[i], "in": d.index[i + 1], "out": d.index[j], "fill": fill, "exit": px,
                        "risk": risk, "R": (px - fill) / risk, "how": how, "days": int(np.busday_count(d.index[i + 1].date(), d.index[j].date())),
                        "rsi2": r2[i], "price": c[i]})
    return pd.DataFrame(out).sort_values("in").reset_index(drop=True)


def account(t, start=200.0, risk_pct=3.0, pos_pct=90.0, whole=True, max_open=10):
    """Walk a cash account day by day. Returns (taken trades, daily equity series)."""
    t = t[t.how != "open"]
    days = sorted(set(t["in"]) | set(t["out"]))
    cash, open_, taken, curve = start, [], [], []
    by_in = {d: g.sort_values("rsi2") for d, g in t.groupby("in")}
    for d in days:
        for p in [p for p in open_ if p["out"] == d]:       # exits first (they free the cash)
            cash += p["qty"] * p["exit"]; open_.remove(p)
        eq = cash + sum(p["qty"] * p["fill"] for p in open_)  # value positions at cost: simple and fair
        for _, x in (by_in.get(d, pd.DataFrame()).iterrows() if d in by_in else []):
            if len(open_) >= max_open or any(p["sym"] == x.sym for p in open_):
                continue
            qty = min(eq * risk_pct / 100 / x.risk, eq * pos_pct / 100 / x.fill, cash / x.fill)
            qty = int(qty) if whole else qty
            if qty <= 0:
                continue
            cash -= qty * x.fill
            p = dict(x, qty=qty); taken.append(p)
            if p["out"] == d:          # stopped (or hit the target) the same day it was bought
                cash += qty * p["exit"]
            else:
                open_.append(p)
        curve.append((d, cash + sum(p["qty"] * p["fill"] for p in open_)))
    for p in taken:
        p["pl"] = p["qty"] * (p["exit"] - p["fill"])
    return pd.DataFrame(taken), pd.Series(dict(curve))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--json")
    a = ap.parse_args()
    fr = panel(a.data)
    print("== setups compared (every signal, R = the stop distance)")
    rows = []
    for label, kw in (("Dip, 1:2, stop 1 ATR, 10 days", dict(entry="dip")),
                      ("Dip, 1:2, stop 2 ATR, 15 days", dict(entry="dip", stop_atr=2.0, max_days=15)),
                      ("Dip, sell on the bounce (Connors), stop 2 ATR", dict(entry="dip", stop_atr=2.0, exit_ma5=True)),
                      ("Breakout, 1:2, stop 1.5 ATR, 15 days", dict(entry="breakout", stop_atr=1.5, max_days=15)),
                      ("Breakout, 1:2, stop 2 ATR, 20 days", dict(entry="breakout", stop_atr=2.0, max_days=20)),
                      ("Baseline: any uptrend day, 1:2, stop 1.5 ATR", dict(entry="any_uptrend", stop_atr=1.5, max_days=15))):
        x = signals(fr, **kw); x = x[x.how != "open"]
        half = x["in"].sort_values().iloc[len(x) // 2]
        print("%-48s n=%5d win %2.0f%% avg %+.3fR  avg win %+.2fR loss %+.2fR  hold %4.1fd  years %+.2f / %+.2f" % (
            label, len(x), 100 * (x.R > 0).mean(), x.R.mean(), x.R[x.R > 0].mean(), x.R[x.R <= 0].mean(), x.days.mean(),
            x[x["in"] < half].R.mean(), x[x["in"] >= half].R.mean()))
        rows.append({"label": label, "n": len(x), "win": float((x.R > 0).mean()), "avg_R": float(x.R.mean()), "hold": float(x.days.mean())})
    print()
    t = signals(fr, entry="breakout", stop_atr=1.5, max_days=15)
    done = t[t.how != "open"]
    print("%d stocks, %d signals (%s to %s)" % (len(fr), len(t), t["in"].min().date(), t["in"].max().date()))
    R = done.R
    print("every signal: win %.0f%%, avg %+.2fR, avg win %+.2fR, avg loss %+.2fR, held %.1f days" % (
        100 * (R > 0).mean(), R.mean(), R[R > 0].mean(), R[R <= 0].mean(), done.days.mean()))
    for h in ("target", "stop", "time"):
        x = done[done.how == h]
        print("  %-6s %5d (%2.0f%%) avg %+.2fR" % (h, len(x), 100 * len(x) / len(done), x.R.mean()))
    half = done["in"].sort_values().iloc[len(done) // 2]
    print("  first year %+.2fR, second year %+.2fR" % (done[done["in"] < half].R.mean(), done[done["in"] >= half].R.mean()))
    out = {"setups": rows, "signals": len(done), "win": float((R > 0).mean()), "avg_R": float(R.mean()), "hold_days": float(done.days.mean()),
           "how": {h: int((done.how == h).sum()) for h in ("target", "stop", "time")}, "accounts": []}
    for start in (200.0, 1000.0):
        tk, eq = account(t, start=start)
        pk = eq.cummax(); dd = float(((eq - pk) / pk).min())
        two = eq.iloc[10:].values / eq.iloc[:-10].values - 1 if len(eq) > 10 else np.array([0])
        m = eq.resample("ME").last(); mr = m.pct_change().dropna()
        last59 = eq.iloc[-1] / eq[eq.index <= eq.index[-1] - pd.Timedelta(days=84)].iloc[-1] - 1
        print("\n$%.0f account, 3%% risk: $%.2f by the end (%+.0f%%), worst dip %.0f%%, %d trades, win %.0f%%" % (
            start, eq.iloc[-1], 100 * (eq.iloc[-1] / start - 1), 100 * dd, len(tk), 100 * (tk.pl > 0).mean()))
        print("  any 2 weeks: median %+.1f%%, up %.0f%% of the time, best %+.1f%%, worst %+.1f%%" % (
            100 * np.median(two), 100 * (two > 0).mean(), 100 * two.max(), 100 * two.min()))
        print("  months up: %d of %d, average month %+.1f%%; last 12 weeks %+.1f%%" % ((mr > 0).sum(), len(mr), 100 * mr.mean(), 100 * last59))
        out["accounts"].append({"start": start, "end": round(float(eq.iloc[-1]), 2), "max_dd_pct": round(100 * dd, 1), "trades": len(tk),
                                "win": float((tk.pl > 0).mean()), "two_week_median_pct": round(100 * float(np.median(two)), 2),
                                "two_week_up": float((two > 0).mean()), "months_up": int((mr > 0).sum()), "months": len(mr),
                                "curve": [[str(k.date()), round(float(v), 2)] for k, v in eq.items()]})
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
