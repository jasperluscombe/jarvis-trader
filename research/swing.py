#!/usr/bin/env python3
"""Daily-bar check of classic swing rules on 2 years of data (about 1,000 liquid US stocks).

    python3 research/swing.py --data DATA_DIR

Rules are taken as published, not tuned here. Buys fill at the NEXT day's open, sells at the next open after the
exit signal, 0.05 % slippage a side. Caveat: the stock list is today's liquid stocks, so companies that collapsed
or were delisted in the last two years are missing; that flatters dip-buying rules in particular.
"""
import argparse, gzip, json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import scan  # noqa: E402
SLIP = 0.0005


def panel(data):
    fr = {}
    for f in sorted(os.listdir(os.path.join(data, "1d"))):
        try:
            r = json.load(gzip.open(os.path.join(data, "1d", f)))["chart"]["result"][0]
            q = r["indicators"]["quote"][0]
            adj = (r["indicators"].get("adjclose") or [{}])[0].get("adjclose")
            df = pd.DataFrame({"o": q["open"], "h": q["high"], "l": q["low"], "c": q["close"], "v": q["volume"], "a": adj or q["close"]},
                              index=pd.to_datetime([scan.ts_to_eastern(t).date() for t in r["timestamp"]])).dropna()
            df = df[~df.index.duplicated(keep="last")]
            k = df.a / df.c   # split/dividend adjustment
            for col in "ohlc":
                df[col] *= k
            if len(df) > 260:
                fr[f[:-8]] = df
        except Exception:
            pass
    return fr


def rsi(c, n):
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn)


def run(fr, rule):
    tr = []
    for s, df in fr.items():
        if s in ("SPY", "QQQ", "IWM", "PSQ", "SH"):
            continue
        c, o = df.c, df.o
        liquid = (c > 5) & ((df.v.rolling(20).mean() * c) > 20e6)
        ent, ext, maxhold = rule(df)
        ent = (ent & liquid).values; ext = ext.values
        i, n = 0, len(df)
        while i < n - 2:
            if ent[i]:
                j = i + 1
                while j < n - 1 and not ext[j] and j - i < maxhold:
                    j += 1
                buy, sell = o.iloc[i + 1] * (1 + SLIP), o.iloc[min(j + 1, n - 1)] * (1 - SLIP)
                tr.append({"sym": s, "in": df.index[i + 1], "out": df.index[min(j + 1, n - 1)], "ret": sell / buy - 1, "days": j - i,
                           "mae": df.l.iloc[i + 1:j + 2].min() / buy - 1})
                i = j + 1
            else:
                i += 1
    return pd.DataFrame(tr)


def rep(t, label, spy):
    if len(t) < 30:
        print("%-46s n=%d" % (label, len(t))); return None
    t = t.copy(); t["m"] = t["in"].dt.to_period("M")
    mm = t.groupby("m").ret.mean()
    mk = np.array([spy.o.asof(b) / spy.o.asof(a) - 1 for a, b in zip(t["in"], t["out"])])
    yrs = sorted(t["in"].dt.year.unique()); half = t["in"].sort_values().iloc[len(t) // 2]
    s = {"label": label, "n": int(len(t)), "win": float((t.ret > 0).mean()), "avg": float(t.ret.mean()), "med": float(t.ret.median()),
         "vs_spy": float((t.ret - mk).mean()), "days": float(t.days.mean()), "pos_months": float((mm > 0).mean()), "months": int(len(mm)),
         "h1": float(t[t["in"] < half].ret.mean()), "h2": float(t[t["in"] >= half].ret.mean()), "worst": float(t.ret.min()),
         "avg_win": float(t.ret[t.ret > 0].mean()), "avg_loss": float(t.ret[t.ret <= 0].mean()), "t": float(mm.mean() / mm.std() * np.sqrt(len(mm)))}
    print("%-46s n=%5d win %4.1f%% avg %+.2f%% (vs SPY %+.2f%%) med %+.2f%% hold %.1fd  halves %+.2f/%+.2f  +months %d/%d t=%.1f  avgW %+.1f%% avgL %+.1f%% worst %+.0f%%" % (
        label, s["n"], 100 * s["win"], 100 * s["avg"], 100 * s["vs_spy"], 100 * s["med"], s["days"], 100 * s["h1"], 100 * s["h2"],
        int((mm > 0).sum()), len(mm), s["t"], 100 * s["avg_win"], 100 * s["avg_loss"], 100 * s["worst"]))
    return s


RULES = {
    # Connors & Alvarez, "Short Term Trading Strategies That Work" (2008): RSI(2) pullback in an uptrend
    "RSI(2)<10 above 200-day avg, exit > 5-day avg": lambda d: ((d.c > d.c.rolling(200).mean()) & (rsi(d.c, 2) < 10), d.c > d.c.rolling(5).mean(), 10),
    "RSI(2)<5 above 200-day avg, exit > 5-day avg": lambda d: ((d.c > d.c.rolling(200).mean()) & (rsi(d.c, 2) < 5), d.c > d.c.rolling(5).mean(), 10),
    # 3 down closes in an uptrend, exit on first up close (classic "three down days")
    "3 down days above 200-day avg, exit first up day": lambda d: ((d.c > d.c.rolling(200).mean()) & (d.c < d.c.shift(1)) & (d.c.shift(1) < d.c.shift(2)) & (d.c.shift(2) < d.c.shift(3)), d.c > d.c.shift(1), 5),
    # the scanner's own setups, held 5 days
    "20-day closing high, hold 5 days": lambda d: (d.c > d.c.shift(1).rolling(20).max(), pd.Series(False, index=d.index), 5),
    "reclaim 20-day avg, hold 5 days": lambda d: ((d.c.shift(1) < d.c.shift(1).rolling(20).mean()) & (d.c > d.c.rolling(20).mean()), pd.Series(False, index=d.index), 5),
    "RSI(14)<30 then up day (oversold bounce), hold 5": lambda d: ((rsi(d.c, 14).shift(1) < 30) & (d.c > d.c.shift(1)), pd.Series(False, index=d.index), 5),
    # Donchian / turtle-style trend: 55-day high, exit 20-day low
    "55-day high, exit 20-day low (trend)": lambda d: (d.c > d.c.shift(1).rolling(55).max(), d.c < d.c.shift(1).rolling(20).min(), 120),
    # baseline: any day, hold 5 (what 'just being in stocks' paid)
    "baseline: every 5th day, hold 5 days": lambda d: (pd.Series(np.arange(len(d)) % 5 == 0, index=d.index), pd.Series(False, index=d.index), 5),
}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--data", required=True); ap.add_argument("--json")
    a = ap.parse_args()
    fr = panel(a.data)
    spy = fr["SPY"]
    print(len(fr), "stocks,", spy.index[0].date(), "to", spy.index[-1].date(), " SPY %+.1f%%" % (100 * (spy.c.iloc[-1] / spy.c.iloc[0] - 1)))
    out = []
    for name, rule in RULES.items():
        s = rep(run(fr, rule), name, spy)
        if s: out.append(s)
    if a.json:
        json.dump({"from": str(spy.index[0].date()), "to": str(spy.index[-1].date()), "stocks": len(fr), "rules": out}, open(a.json, "w"), indent=1)
