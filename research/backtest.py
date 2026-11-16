#!/usr/bin/env python3
"""Replay Jarvis's opening-range breakout on 60 days of 5-minute bars, rule by rule.

    python3 research/backtest.py --data DATA_DIR            # the comparison tables
    python3 research/backtest.py --data DATA_DIR --json OUT  # also save them for the dashboard

How a trade is replayed (the same way Jarvis trades it, on purpose a little pessimistic):
  * the opening range is the first 15 minutes; the signal is the first later 5-minute bar that CLOSES above
    the range high, between 9:45 and 15:30;
  * Jarvis only sees that bar after it closes, so the buy fills at the NEXT bar's open, plus slippage;
  * the stop and target are planned from the signal bar's close (as exit.py does); if a bar touches both,
    the stop is assumed to come first; a gap through the stop fills at the open, not at the stop;
  * whatever is left is sold at the 15:55 bar's open; slippage is charged on every fill (default 0.05 %).
Results are in R (1R = the planned loss at the stop), so they don't depend on the account size.
"""
import argparse, datetime as dt, json, os, pickle
import numpy as np

SLIP = 0.0005
LAST = 77          # the 15:55 bar: flat by its open
CUTOFF = 72        # a signal bar may close at 15:30 at the latest (bar index 71 closes 15:30)


def load(data):
    t = pickle.load(open(os.path.join(data, "table.pkl"), "rb"))
    return t["rows"], t["bars"]


def signal(b, or_bars=3, vol_x=None):
    """Index of the first bar after the range that closes above the range high (or None), and the range."""
    hi, lo = np.nanmax(b[1, :or_bars]), np.nanmin(b[2, :or_bars])
    c = b[3]
    for i in range(or_bars, CUTOFF):
        if c[i] > hi:  # NaN compares False
            if vol_x and not b[4, i] >= vol_x * np.nanmean(b[4, :or_bars]):
                return None, hi, lo
            return i, hi, lo
    return None, hi, lo


def replay(b, i, stop, target, be_at=None, trail_r=None, time_stop=None, slip=SLIP, limit=None, limit_bars=1):
    """Buy at bar i+1's open (a market order). With limit=L, a limit order at the signal price x (1 + L) instead,
    good for limit_bars bars: it fills at the bar's open if that's at or under the limit, at the limit if the bar
    trades down to it, and not at all otherwise (a missed trade). Returns (R, how, fill, exit price, exit bar) or
    None when there is no fill."""
    plan = float(b[3, i])
    risk = plan - stop
    if risk <= 0 or i + 1 > LAST or np.isnan(b[0, i + 1]):
        return None
    start = i + 1
    if limit is None:
        fill = float(b[0, i + 1]) * (1 + slip)
    else:
        lim, fill = plan * (1 + limit), None
        for k in range(i + 1, min(i + 1 + limit_bars, LAST)):
            o, l = float(b[0, k]), float(b[2, k])
            if np.isnan(o):
                continue
            if o <= lim:
                fill, start = o, k
                break
            if l <= lim:
                fill, start = lim, k
                break
        if fill is None:
            return None  # the order never filled
    if fill <= stop or (target is not None and fill >= target):
        return None  # the price ran away before Jarvis could buy
    s, hi_seen = stop, fill
    for k in range(start, LAST + 1):
        o, h, l, c = (float(x) for x in b[:4, k])
        if np.isnan(o):
            continue
        if k == LAST or (time_stop and k - i >= time_stop and c < fill):
            px = (o if k == LAST else c) * (1 - slip)
            return (px - fill) / risk, "close" if k == LAST else "time", fill, px, k
        if l <= s:
            px = min(s, o) * (1 - slip)
            return (px - fill) / risk, "stop" if s == stop else "trail", fill, px, k
        if target is not None and h >= target:
            px = max(target, o) if o >= target else target
            return (px - fill) / risk, "target", fill, px, k
        hi_seen = max(hi_seen, h)
        if be_at and hi_seen >= plan + be_at * risk:
            s = max(s, plan)                      # stop to break-even once it has run be_at R
        if trail_r and hi_seen - trail_r * risk > s:
            s = hi_seen - trail_r * risk           # trail trail_r R under the high
    return None


def stop_price(kind, plan, hi, lo, atr):
    if kind == "or-mid":
        return (hi + lo) / 2
    if kind == "or-low":
        return lo
    if kind.startswith("atr:"):
        return plan - float(kind[4:]) * atr
    raise ValueError(kind)


def trades(rows, bars, flt=None, stop="or-mid", target=2.0, or_bars=3, last_signal=CUTOFF, vol_x=None, min_risk_pct=0.0,
           **kw):
    """Every trade the rule would have taken. flt(row, extra) -> bool filters them."""
    out = []
    for r, b in zip(rows, bars):
        i, hi, lo = signal(b, or_bars, vol_x)
        if i is None or i >= last_signal:
            continue
        plan = float(b[3, i])
        s = stop_price(stop, plan, hi, lo, r["atr"])
        risk = plan - s
        if risk <= 0 or risk / plan < min_risk_pct:
            continue
        x = {"i": i, "plan": plan, "hi": hi, "lo": lo, "risk_pct": risk / plan, "ext": (plan - hi) / max(hi - lo, 1e-9),
             "or_pct": (hi - lo) / plan, "or_atr": (hi - lo) / r["atr"], "day_ret": plan / r["pc"] - 1}
        if flt and not flt(r, x):
            continue
        res = replay(b, i, s, None if target is None else plan + target * risk, **kw)
        if res is None:
            continue
        out.append(dict(r, **x, R=res[0], how=res[1], fill=res[2], exit=res[3], k_exit=res[4], stop_px=s))
    return out


def stats(tr, label=""):
    """Win rate, average R, profit factor and a 90 % range for the average from resampling whole DAYS
    (trades on the same day rise and fall together, so days are the honest unit)."""
    if not tr:
        return {"label": label, "n": 0}
    R = np.array([t["R"] for t in tr])
    days = sorted({t["day"] for t in tr})
    by = {d: [] for d in days}
    for t in tr:
        by[t["day"]].append(t["R"])
    rng = np.random.default_rng(7)
    arr = [np.array(by[d]) for d in days]
    boots = []
    for _ in range(2000):
        pick = rng.integers(0, len(arr), len(arr))
        x = np.concatenate([arr[p] for p in pick])
        boots.append(x.mean())
    lo, hi = np.percentile(boots, [5, 95])
    wins, losses = R[R > 0], R[R <= 0]
    day_sum = np.array([sum(v) for v in by.values()])
    how = {}
    for t in tr:
        how[t["how"]] = how.get(t["how"], 0) + 1
    half = days[len(days) // 2]
    h1 = np.array([t["R"] for t in tr if t["day"] < half])
    h2 = np.array([t["R"] for t in tr if t["day"] >= half])
    return {"label": label, "n": len(R), "days": len(days), "per_day": round(len(R) / len(days), 1),
            "win": round(float((R > 0).mean()), 3), "avg_R": round(float(R.mean()), 3),
            "lo": round(float(lo), 3), "hi": round(float(hi), 3),
            "pf": round(float(wins.sum() / -losses.sum()), 2) if losses.sum() < 0 else None,
            "avg_win": round(float(wins.mean()), 2) if len(wins) else 0, "avg_loss": round(float(losses.mean()), 2) if len(losses) else 0,
            "green_days": round(float((day_sum > 0).mean()), 2),
            "h1": round(float(h1.mean()), 3) if len(h1) else None, "h2": round(float(h2.mean()), 3) if len(h2) else None,
            "how": how}


def line(s):
    if not s.get("n"):
        return "%-44s  no trades" % s["label"]
    return "%-44s n=%5d (%4.1f/day) win %4.1f%%  avg %+.3fR [%+.3f, %+.3f]  PF %s  halves %+.3f / %+.3f  %s" % (
        s["label"], s["n"], s["per_day"], 100 * s["win"], s["avg_R"], s["lo"], s["hi"], s["pf"], s["h1"] or 0, s["h2"] or 0,
        " ".join("%s:%d" % kv for kv in sorted(s["how"].items())))


# ---- the universe Jarvis actually hunts in: the scanner's daily setups, $5-$40, >= 1M shares, top 30 by $ volume
WANT = {"breakout_20d", "bull_flag", "reclaim_ma20", "oversold_bounce"}


def jarvis_universe(rows, lo=5, hi=40, top=30, want=WANT):
    keep = set()
    by = {}
    for n, r in enumerate(rows):
        if lo <= r["pc"] <= hi and r["avgvol"] >= 1e6 and (not want or want & set(r["tags"])):
            by.setdefault(r["day"], []).append((r["pc"] * r["avgvol"], n))
    for d, v in by.items():
        v.sort(reverse=True)
        keep.update(n for _, n in v[:top])
    return keep


def subset(rows, bars, keep):
    idx = sorted(keep)
    return [rows[i] for i in idx], bars[idx]


def portfolio(tr, start=50.0, risk_pct=2.0, pos_pct=90.0, buffer_pct=10.0, max_trades=10, rank=None, whole=True, min_order=5.0):
    """Walk an account through the trades the way Jarvis sizes them: 2 % of yesterday's value at risk, one order
    at most 90 % of the account, 10 % cash kept back, whole shares, cash only (a sale frees the cash at once)."""
    eq, curve, taken = start, [], []
    by = {}
    for t in tr:
        by.setdefault(t["day"], []).append(t)
    for d in sorted(by):
        base, cash, open_, n = eq, eq, [], 0
        day = sorted(by[d], key=lambda t: (t["i"], -(rank(t) if rank else 0)))
        for t in day:
            for o in [o for o in open_ if o[0] <= t["i"]]:      # sold before this signal: the cash is back
                cash += o[1]; open_.remove(o)
            if n >= max_trades:
                break
            rps = t["plan"] - t["stop_px"]
            cap = min(base * pos_pct / 100, cash - base * buffer_pct / 100)
            qty = min(base * risk_pct / 100 / rps, cap / t["fill"])
            qty = int(qty) if whole else qty
            if qty <= 0 or qty * t["fill"] < min_order:
                continue
            cost, back = qty * t["fill"], qty * t["exit"]
            cash -= cost; n += 1
            open_.append((t["k_exit"], back))
            eq += back - cost
            taken.append(dict(t, qty=qty, pl=back - cost))
        curve.append((d, round(eq, 2)))
    vals = np.array([start] + [v for _, v in curve])
    peak = np.maximum.accumulate(vals)
    return {"start": start, "end": round(float(vals[-1]), 2), "ret_pct": round(100 * (vals[-1] / start - 1), 1),
            "max_dd_pct": round(float(100 * ((vals - peak) / peak).min()), 1), "trades": len(taken),
            "per_day": round(len(taken) / max(len(curve), 1), 1), "win": round(float(np.mean([t["pl"] > 0 for t in taken])), 3) if taken else None,
            "green_days": round(float(np.mean(np.diff(vals) > 0)), 2), "curve": [[str(d), v] for d, v in curve]}


# ---- the two rule sets
def in_play(min_gain=0.04, min_rv=1.5):
    return lambda r, x: x["day_ret"] >= min_gain and r["rv15"] >= min_rv


V1 = dict(stop="or-mid", target=2.0)                                     # Jarvis before the upgrade
V2 = dict(stop="or-low", target=2.0, last_signal=12, min_risk_pct=0.01)  # signal bar closes by 10:30, stop >= 1 % away


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--json")
    a = ap.parse_args()
    rows, bars = load(a.data)
    last = max(r["day"] for r in rows)            # the newest day is still trading: leave it out
    rows, bars = subset(rows, bars, [i for i, r in enumerate(rows) if r["day"] < last])
    days = sorted({r["day"] for r in rows})
    print("%d stock-days, %d symbols, %s to %s" % (len(rows), len({r["sym"] for r in rows}), days[0], days[-1]))
    jr, jb = subset(rows, bars, jarvis_universe(rows))
    cr, cb = subset(rows, bars, [i for i, r in enumerate(rows) if 5 <= r["pc"] <= 40 and r["avgvol"] >= 1e6])
    wr, wb = subset(rows, bars, [i for i, r in enumerate(rows) if r["sym"] in ("QQQ", "SPY", "TSLA", "NVDA", "AAPL", "PSQ", "SH")])
    steps = [
        ("Before: scanner watchlist, stop at range middle, 2R", jr, jb, V1, None),
        ("Same rules on every liquid $5-$40 stock", cr, cb, V1, None),
        ("+ stop at the range low (wider)", cr, cb, dict(stop="or-low", target=2.0), None),
        ("+ skip stops closer than 1 % (costs eat them)", cr, cb, dict(stop="or-low", target=2.0, min_risk_pct=0.01), None),
        ("+ signals only until 10:30", cr, cb, V2, None),
        ("+ stock already up 4 % on the day", cr, cb, V2, lambda r, x: x["day_ret"] >= 0.04),
        ("After: + opening volume 1.5x normal (in play)", cr, cb, V2, in_play()),
    ]
    out = {"from": str(days[0]), "to": str(days[-1]), "days": len(days), "symbols": len({r["sym"] for r in rows}),
           "slippage_pct": 100 * SLIP, "steps": [], "exits": [], "always": [], "slippage": []}
    keep = {}
    print("\n== step by step (each line adds one rule)")
    for label, R_, B_, kw, flt in steps:
        tr = trades(R_, B_, flt=flt, **kw)
        s = stats(tr, label); out["steps"].append(s); keep[label] = tr
        print(line(s))
    v1, v2 = keep[steps[0][0]], keep[steps[-1][0]]
    print("\n== exits for the in-play signals")
    for stop in ("or-mid", "or-low"):
        for tgt in (1.0, 1.5, 2.0, 3.0, None):
            s = stats(trades(cr, cb, flt=in_play(), **dict(V2, stop=stop, target=tgt)), "%s stop, %s" % (stop, "%gR target" % tgt if tgt else "no target (sell 15:55)"))
            out["exits"].append(s); print(line(s))
    for label, kw in (("or-low, 2R, stop to break-even after 1R", dict(V2, be_at=1.0)), ("or-low, no target, trail 1R under the high", dict(V2, target=None, trail_r=1.0)),
                      ("or-low, 2R, out after 60 min if under entry", dict(V2, time_stop=12))):
        s = stats(trades(cr, cb, flt=in_play(), **kw), label); out["exits"].append(s); print(line(s))
    print("\n== the always-watched names (QQQ SPY TSLA NVDA AAPL PSQ SH)")
    for label, kw, flt in (("before rules", V1, None), ("after rules, no in-play filter", V2, None), ("after rules + in play", V2, in_play())):
        s = stats(trades(wr, wb, flt=flt, **kw), label); out["always"].append(s); print(line(s))
    print("\n== how much slippage matters (after rules)")
    for sl in (0.0, 0.0002, 0.0005, 0.001):
        s = stats(trades(cr, cb, flt=in_play(), slip=sl, **V2), "%.2f %% a side" % (100 * sl)); out["slippage"].append(s); print(line(s))
    print("\n== is it a knife-edge? neighbouring thresholds (after rules)")
    out["sensitivity"] = []
    for g in (0.02, 0.03, 0.04, 0.05):
        for rv in (1.0, 1.5, 2.0, 3.0):
            s = stats(trades(cr, cb, flt=in_play(g, rv), **V2), "up %d %%, volume %.1fx" % (round(100 * g), rv))
            s.update(gain=g, rv=rv); out["sensitivity"].append(s); print(line(s))
    print("\n== walking an account through it (2 % risk, whole shares, cash only)")
    out["accounts"] = []
    out["generated"] = dt.date.today().isoformat()
    for start in (54.0, 200.0, 5000.0):
        for label, tr, rank in (("before", v1, lambda t: t["pc"] * t["avgvol"]), ("after", v2, lambda t: t["rv15"])):
            p = portfolio(tr, start=start, rank=rank)
            out["accounts"].append(dict(p, rules=label))
            print("$%-6.0f %-6s -> $%-9.2f %+6.1f%%  max drawdown %5.1f%%  %3d trades (%.1f/day) win %s  green days %s" % (
                start, label, p["end"], p["ret_pct"], p["max_dd_pct"], p["trades"], p["per_day"], p["win"], p["green_days"]))
    if a.json:
        for k in ("steps", "exits", "always", "slippage"):
            for s in out[k]:
                s.pop("how", None)
        json.dump(out, open(a.json, "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
