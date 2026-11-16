#!/usr/bin/env python3
"""Walk-forward test of the in-play opening-range breakout: are the rules still good on days they were not picked on?

    python3 research/walkforward.py --data DATA_DIR [--json OUT]

The honest question is not "which settings did best on these 60 days?" (that is curve fitting) but "if, on each day,
Jarvis had picked its settings using ONLY the days before, how would it have done on the days after?"

1. A grid of 384 rule sets, fixed in advance (no peeking at results to choose the grid):
   opening range 5 or 15 min; up >= 2/3/4/5 % on the day; opening volume >= 1/1.5/2/3x normal;
   stop at the range middle or low; target 1.5R/2R/3R/none (sell 15:55); last signal 10:00/10:30/11:00.
   Every rule set also skips stops closer than 1 % (costs eat them). Universe: $5-$40, >= 1M shares a day.
2. Anchored walk-forward: train on days 1-20, pick the rule set with the best (average R - its standard error,
   so a lucky handful of trades can't win), test it on days 21-30; train on 1-30, test 31-40; and so on.
3. Only the test-block trades are reported as out-of-sample. They're compared on the same days with
   the old rules, the current live rules (picked with hindsight on these same days, so NOT out of sample), and
   no filter at all.
4. Costs: slippage on every fill (default 0.05 % a side), then re-run at 0.1 / 0.2 / 0.3 % a side.
5. The out-of-sample trades are walked through a $200 cash account (whole shares and part-shares, 1-3 % risk).
"""
import argparse, itertools, json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backtest import load, subset, trades, portfolio  # noqa: E402

GAINS, RVS = (0.02, 0.03, 0.04, 0.05), (1.0, 1.5, 2.0, 3.0)
STOPS, TARGETS, LASTS, ORS = ("or-mid", "or-low"), (1.5, 2.0, 3.0, None), (6, 12, 18), (1, 3)
LIVE = dict(orb=3, stop="or-low", target=2.0, last=12, gain=0.04, rv=1.5)
OLD = dict(orb=3, stop="or-mid", target=2.0, last=72, gain=None, rv=None)
CLOCK = {6: "10:00", 12: "10:30", 18: "11:00", 72: "15:30"}


def label(c):
    if c["gain"] is None:
        return "%d-min range, %s stop, %s, no filter, signals to %s" % (5 * c["orb"], c["stop"], tgt(c["target"]), CLOCK[c["last"]])
    return "%d-min range, up %d%%+, vol %gx+, %s stop, %s, by %s" % (
        5 * c["orb"], round(100 * c["gain"]), c["rv"], c["stop"], tgt(c["target"]), CLOCK[c["last"]])


def tgt(t):
    return "%gR target" % t if t else "sell 15:55"


def base_trades(rows, bars, slip):
    """Every breakout for each (range, stop, target), signals up to 11:00; the filters are applied afterwards."""
    out = {}
    for orb, stop, target in itertools.product(ORS, STOPS, TARGETS):
        tr = trades(rows, bars, stop=stop, target=target, or_bars=orb, last_signal=18, min_risk_pct=0.01, slip=slip)
        df = pd.DataFrame([{"day": t["day"], "sym": t["sym"], "i": t["i"], "R": t["R"], "gain": t["day_ret"],
                            "rv": t["rv5"] if orb == 1 else t["rv15"], "how": t["how"], "plan": t["plan"], "stop_px": t["stop_px"],
                            "fill": t["fill"], "exit": t["exit"], "k_exit": t["k_exit"], "pc": t["pc"], "avgvol": t["avgvol"]} for t in tr])
        out[(orb, stop, target)] = df
    return out


def pick(base, c, days=None):
    df = base[(c["orb"], c["stop"], c["target"])]
    m = df.i < c["last"]
    if c["gain"] is not None:
        m &= (df.gain >= c["gain"]) & (df.rv >= c["rv"])
    if days is not None:
        m &= df.day.isin(days)
    return df[m]


def score(R):
    """Average R minus its standard error: rewards an edge that holds over many trades, not a lucky few."""
    return R.mean() - R.std(ddof=1) / np.sqrt(len(R)) if len(R) >= 2 else -9


def summ(df, name):
    if not len(df):
        return {"label": name, "n": 0}
    R = df.R.values
    w, l = R[R > 0], R[R <= 0]
    days = sorted(df.day.unique())
    by = df.groupby("day").R.sum()
    rng = np.random.default_rng(3)
    arr = [g.R.values for _, g in df.groupby("day")]
    boots = [np.concatenate([arr[i] for i in rng.integers(0, len(arr), len(arr))]).mean() for _ in range(2000)]
    return {"label": name, "n": int(len(R)), "days_traded": len(days), "win": round(float((R > 0).mean()), 3),
            "avg_R": round(float(R.mean()), 3), "lo": round(float(np.percentile(boots, 5)), 3), "hi": round(float(np.percentile(boots, 95)), 3),
            "pf": round(float(w.sum() / -l.sum()), 2) if l.sum() < 0 else None, "avg_win": round(float(w.mean()), 2) if len(w) else None,
            "avg_loss": round(float(l.mean()), 2) if len(l) else None, "sum_R": round(float(R.sum()), 1)}


def line(s):
    if not s.get("n"):
        return "%-62s no trades" % s["label"]
    return "%-62s n=%4d win %3.0f%% avg %+.3fR [%+.3f, %+.3f] PF %s sum %+.1fR" % (
        s["label"][:62], s["n"], 100 * s["win"], s["avg_R"], s["lo"], s["hi"], s["pf"], s["sum_R"])


def walk(base, days, first=20, step=10):
    grid = [dict(orb=o, stop=s, target=t, last=l, gain=g, rv=r)
            for o, s, t, l, g, r in itertools.product(ORS, STOPS, TARGETS, LASTS, GAINS, RVS)]
    folds, oos = [], []
    for k in range(first, len(days), step):
        train, test = days[:k], days[k:k + step]
        best, bs = None, -9
        for c in grid:
            R = pick(base, c, train).R
            if len(R) < 30:           # too few trades to judge
                continue
            sc = score(R)
            if sc > bs:
                best, bs = c, sc
        te = pick(base, best, test)
        folds.append({"train": "%s to %s (%d days)" % (train[0], train[-1], len(train)), "test": "%s to %s (%d days)" % (test[0], test[-1], len(test)),
                      "picked": label(best), "train_avg_R": round(float(pick(base, best, train).R.mean()), 3), "train_n": int(len(pick(base, best, train))),
                      "test_n": int(len(te)), "test_avg_R": round(float(te.R.mean()), 3) if len(te) else None})
        oos.append(te.assign(rule=label(best)))
    return folds, pd.concat(oos), grid


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--json")
    a = ap.parse_args()
    rows, bars = load(a.data)
    # a day counts only once it is over: most stocks have their 15:55 bar
    done = {}
    for r, b in zip(rows, bars):
        done.setdefault(r["day"], []).append(not np.isnan(b[0, 77]))
    complete = {d for d, v in done.items() if np.mean(v) > 0.8}
    keep = [i for i, r in enumerate(rows) if r["day"] in complete and 5 <= r["pc"] <= 40 and r["avgvol"] >= 1e6]
    rows, bars = subset(rows, bars, keep)
    days = sorted({r["day"] for r in rows})
    print("%d stock-days, %d days, %s to %s" % (len(rows), len(days), days[0], days[-1]))
    base = base_trades(rows, bars, 0.0005)
    out = {"from": str(days[0]), "to": str(days[-1]), "days": len(days)}

    print("\n== anchored walk-forward (settings picked on earlier days only)")
    folds, oos, grid = walk(base, days)
    for f in folds:
        print("train %s -> test %s\n   picked: %s (train %+.3fR over %d)  ->  test %s over %d trades" % (
            f["train"], f["test"], f["picked"], f["train_avg_R"], f["train_n"],
            "%+.3fR" % f["test_avg_R"] if f["test_avg_R"] is not None else "-", f["test_n"]))
    oos_days = sorted(oos.day.unique()) if len(oos) else []
    test_days = days[20:]
    rep = [summ(oos, "WALK-FORWARD (out of sample)"),
           summ(pick(base, OLD, test_days), "old rules, same days"),
           summ(pick(base, dict(LIVE, gain=None), test_days), "live exits, NO in-play filter, same days"),
           summ(pick(base, LIVE, test_days), "live rules, same days (picked with hindsight!)")]
    print("\nsame %d test days (%s to %s):" % (len(test_days), test_days[0], test_days[-1]))
    for s in rep:
        print("  " + line(s))
    out.update(folds=folds, compare=rep)

    print("\n== the whole 60 days: how many of the %d rule sets made money, and does the in-play filter matter?" % len(grid))
    allr = [(c, pick(base, c)) for c in grid]
    good = [x for x in allr if len(x[1]) >= 30]
    pos = [x for x in good if x[1].R.mean() > 0]
    print("  %d of %d rule sets with 30+ trades averaged above 0R" % (len(pos), len(good)))
    filt = {}
    for g in GAINS:
        v = [x[1].R.mean() for x in good if x[0]["gain"] == g]
        filt["up %d%%+" % round(100 * g)] = round(float(np.median(v)), 3)
    for r in RVS:
        v = [x[1].R.mean() for x in good if x[0]["rv"] == r]
        filt["volume %gx+" % r] = round(float(np.median(v)), 3)
    for o in ORS:
        v = [x[1].R.mean() for x in good if x[0]["orb"] == o]
        filt["%d-min range" % (5 * o)] = round(float(np.median(v)), 3)
    for s_ in STOPS:
        v = [x[1].R.mean() for x in good if x[0]["stop"] == s_]
        filt["%s stop" % s_] = round(float(np.median(v)), 3)
    for t_ in TARGETS:
        v = [x[1].R.mean() for x in good if x[0]["target"] == t_]
        filt[tgt(t_)] = round(float(np.median(v)), 3)
    for l_ in LASTS:
        v = [x[1].R.mean() for x in good if x[0]["last"] == l_]
        filt["signals by %s" % CLOCK[l_]] = round(float(np.median(v)), 3)
    for k, v in filt.items():
        print("  median avg R of rule sets with %-18s %+.3f" % (k, v))
    out["medians"] = filt
    out["share_positive"] = [len(pos), len(good)]

    print("\n== costs: the walk-forward picks re-run with more slippage")
    out["slippage"] = []
    for sl in (0.0005, 0.001, 0.002, 0.003):
        b2 = base if sl == 0.0005 else base_trades(rows, bars, sl)
        pieces = []
        for f, k in zip(folds, range(20, len(days), 10)):
            c = next(c for c in grid if label(c) == f["picked"])
            pieces.append(pick(b2, c, days[k:k + 10]))
        s = summ(pd.concat(pieces), "%.2f %% a side" % (100 * sl)); out["slippage"].append(s)
        print("  " + line(s))

    print("\n== a $200 cash account through the out-of-sample trades only")
    out["accounts"] = []
    tr = [dict(r._asdict()) for r in oos.itertuples(index=False)]
    for whole in (True, False):
        for risk in (1.0, 2.0, 3.0):
            p = portfolio(tr, start=200.0, risk_pct=risk, whole=whole, rank=lambda t: t["rv"], min_order=1.0)
            p.pop("curve")
            p.update(risk_pct=risk, shares="whole" if whole else "part-shares")
            out["accounts"].append(p)
            print("  %-11s risk %.0f%%: $200 -> $%.2f (%+.1f%%), worst dip %.1f%%, %d trades, win %s, green days %s" % (
                p["shares"], risk, p["end"], p["ret_pct"], p["max_dd_pct"], p["trades"], p["win"], p["green_days"]))
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
