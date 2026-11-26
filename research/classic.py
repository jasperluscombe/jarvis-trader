#!/usr/bin/env python3
"""Experiment E7: classic, published strategies on long daily histories (SPY since 1993, QQQ since 1999).

    python3 research/classic.py --data LONG_DIR [--json OUT]

LONG_DIR holds Yahoo daily chart JSON files (SPY.json, QQQ.json, TQQQ.json, UPRO.json, ...), fetched with
period1/period2 and interval=1d. Prices are adjusted for splits and dividends (Yahoo's adjclose factor), so a
dividend paid overnight is not mistaken for a loss.

Rules, fixed before running (textbook versions from the original papers):
  buy & hold       hold the ETF every day (the benchmark)
  overnight        buy at the close, sell at the next open, every day (Cooper, Cliff & Gulen 2008)
  intraday         buy at the open, sell at the close, every day (the mirror image, for comparison)
  turn of month    hold from the close of the 2nd-last trading day of a month to the close of the 3rd trading day
                   of the next (Lakonishok & Smidt 1988; McConnell & Xu 2008); cash otherwise
  200-day trend    hold while yesterday's close was above its 200-day average, else cash (Faber 2007 style,
                   daily); the leveraged version holds a 3x ETF on the same signal (Gayed & Bilello 2016)
Costs: a fixed % per side every time the position is entered or left (default 0.02 %, re-run at 0.10 %).
Cash earns nothing (conservative).

Outcome measures for a $200 account, over every historical start day:
  share of start days from which $200 reached $1,000 within 1 / 3 / 5 / 10 years, the median years it took,
  and the share of start days from which the account fell to $100 (half) at some point within 5 years.
"""
import argparse, json, os
import numpy as np, pandas as pd


def load(path):
    r = json.load(open(path))["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    adj = r["indicators"]["adjclose"][0]["adjclose"]
    df = pd.DataFrame({"o": q["open"], "c": q["close"], "a": adj},
                      index=pd.to_datetime(r["timestamp"], unit="s").normalize()).dropna()
    df = df[~df.index.duplicated(keep="last")]
    k = df.a / df.c
    df["o"], df["c"] = df.o * k, df.a          # adjusted open and close
    return df[["o", "c"]]


def strat_returns(df, kind, cost, lev=None):
    """Daily strategy returns (decimal), indexed by date. lev: a DataFrame of the leveraged ETF to hold instead."""
    o, c = df.o, df.c
    if kind == "buy_hold":
        r = c.pct_change().fillna(0.0)
        r.iloc[1] -= cost
        return r
    if kind == "overnight":                 # close(t-1) -> open(t), both sides paid every day
        return (o / c.shift(1) - 1 - 2 * cost).dropna()
    if kind == "intraday":                  # open(t) -> close(t)
        return (c / o - 1 - 2 * cost)
    if kind == "turn_of_month":
        idx = df.index
        month = idx.to_period("M")
        pos_in_m = pd.Series(np.arange(len(idx)), index=idx).groupby(month).rank(method="first").astype(int)
        size_m = pd.Series(1, index=idx).groupby(month).transform("size")
        from_end = size_m - pos_in_m            # 0 = last day of the month
        # in the market for the day ending at close(t) when t is the last day of a month or one of the first 3
        hold = (from_end == 0) | (pos_in_m <= 3)
        r = c.pct_change().where(hold, 0.0).fillna(0.0)
        enter = hold & ~hold.shift(1, fill_value=False)
        leave = ~hold & hold.shift(1, fill_value=False)
        return r - cost * (enter.astype(int) + leave.astype(int))
    if kind == "trend200":
        sig = (c > c.rolling(200).mean()).shift(1, fill_value=False)   # decided at yesterday's close
        src = c if lev is None else lev.c.reindex(df.index)
        r = src.pct_change().where(sig, 0.0).fillna(0.0)
        flips = (sig != sig.shift(1, fill_value=False)).astype(int)
        r = r - cost * flips
        return r[r.index >= (df.index[0] if lev is None else lev.index[0])]
    raise ValueError(kind)


def synthetic_3x(df, fee=0.0095, borrow=0.03):
    """A 3x daily-rebalanced fund on df before the real one existed: 3 x the daily return, minus the fund's fee
    and the cost of borrowing the extra 2x (a rough 3 % a year)."""
    r = df.c.pct_change().fillna(0.0)
    r3 = 3 * r - (fee + 2 * borrow) / 252
    out = pd.DataFrame({"c": 100 * (1 + r3).cumprod()})
    out["o"] = out.c
    return out


def metrics(r):
    eq = (1 + r).cumprod()
    yrs = len(r) / 252
    cagr = eq.iloc[-1] ** (1 / yrs) - 1 if eq.iloc[-1] > 0 else -1
    dd = (eq / eq.cummax() - 1).min()
    sh = r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else 0
    return {"cagr": round(100 * cagr, 1), "max_dd": round(100 * dd, 1), "sharpe": round(float(sh), 2),
            "years": round(yrs, 1), "in_market": round(100 * float((r != 0).mean()), 0)}


def five_x(r, start=200.0, goal=1000.0, half=100.0):
    """Over every start day: P(reach goal within 1/3/5/10 years), median years taken, P(hit half within 5 years)."""
    v = np.log1p(r.values)
    cum = np.concatenate([[0.0], np.cumsum(v)])
    n = len(v)
    need, lose = np.log(goal / start), np.log(half / start)
    hit_years, halves, total = [], 0, 0
    within = {1: 0, 3: 0, 5: 0, 10: 0}
    for s in range(0, n - 252 * 5, 5):          # every 5th trading day as a start (plenty, and fast)
        path = cum[s + 1:] - cum[s]
        k = np.argmax(path >= need) if (path >= need).any() else None
        total += 1
        if k is not None:
            y = (k + 1) / 252
            hit_years.append(y)
            for w in within:
                if y <= w:
                    within[w] += 1
        if (path[:252 * 5] <= lose).any():
            halves += 1
    return {"p_within": {w: round(100 * c / total, 1) for w, c in within.items()},
            "median_years": round(float(np.median(hit_years)), 1) if hit_years else None,
            "p_ever": round(100 * len(hit_years) / total, 1), "p_halved_5y": round(100 * halves / total, 1), "starts": total}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--json")
    a = ap.parse_args()
    d = {s: load(os.path.join(a.data, s + ".json")) for s in ("SPY", "QQQ", "TQQQ", "UPRO")}
    out = {"rows": []}
    rows = []
    for und, lev in (("SPY", "UPRO"), ("QQQ", "TQQQ")):
        df = d[und]
        syn = synthetic_3x(df)
        # stitch: synthetic 3x before the real fund started, the real fund after
        real = d[lev]
        stitched = pd.concat([syn[syn.index < real.index[0]].c / syn.c.loc[:real.index[0]].iloc[-1] * real.c.iloc[0], real.c])
        stitched = pd.DataFrame({"c": stitched[~stitched.index.duplicated(keep="last")]}); stitched["o"] = stitched.c
        cases = [("buy & hold %s" % und, "buy_hold", None), ("overnight %s (close to open)" % und, "overnight", None),
                 ("intraday %s (open to close)" % und, "intraday", None), ("turn of month %s" % und, "turn_of_month", None),
                 ("200-day trend %s" % und, "trend200", None),
                 ("hold %s 3x (synthetic before %s)" % (und, real.index[0].year), "buy_hold_lev", stitched),
                 ("200-day trend into %s 3x" % und, "trend200", stitched)]
        for label, kind, lv in cases:
            for cost in (0.0002, 0.001):
                if kind == "buy_hold_lev":
                    r = lv.c.reindex(df.index).pct_change().fillna(0.0)
                else:
                    r = strat_returns(df, kind, cost, lev=lv)
                m = metrics(r)
                row = dict(label=label, cost_pct=100 * cost, **m)
                if cost == 0.0002:
                    row["five_x"] = five_x(r)
                    for era, (s, e) in {"1993-2007": ("1993", "2007"), "2008-2015": ("2008", "2015"), "2016-2026": ("2016", "2026")}.items():
                        sub = r[(r.index >= s) & (r.index <= e + "-12-31")]
                        if len(sub) > 250:
                            row["cagr_" + era] = metrics(sub)["cagr"]
                rows.append(row)
    print("%-44s %5s %7s %7s %6s %5s | %-24s | $200->$1000: ever / within 3y / 5y, median yrs, halved in 5y" % (
        "strategy", "cost", "CAGR", "maxDD", "Sharpe", "inmkt", "CAGR 93-07 / 08-15 / 16-26"))
    for r_ in rows:
        eras = " / ".join("%+.1f" % r_["cagr_" + e] if ("cagr_" + e) in r_ else "  -  " for e in ("1993-2007", "2008-2015", "2016-2026"))
        fx = r_.get("five_x")
        fxs = ("%4.0f%% / %4.0f%% / %4.0f%%, %s, %4.0f%%" % (fx["p_ever"], fx["p_within"][3], fx["p_within"][5],
                                                          fx["median_years"], fx["p_halved_5y"])) if fx else ""
        print("%-44s %4.2f%% %+6.1f%% %6.1f%% %6.2f %4.0f%% | %-24s | %s" % (
            r_["label"][:44], r_["cost_pct"], r_["cagr"], r_["max_dd"], r_["sharpe"], r_["in_market"], eras if fx else "", fxs))
    out["rows"] = rows
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
