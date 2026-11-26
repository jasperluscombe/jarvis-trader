import json, sys, numpy as np, pandas as pd
D = sys.argv[1]

def load(sym, adj=True):
    j = json.load(open(f"{D}/{sym}.json"))["chart"]["result"][0]
    ts = pd.to_datetime(j["timestamp"], unit="s").normalize()
    q = j["indicators"]
    if adj and "adjclose" in q:
        c = q["adjclose"][0]["adjclose"]
    else:
        c = q["quote"][0]["close"]
    s = pd.Series(c, index=ts, dtype=float).dropna()
    s = s[~s.index.duplicated(keep="last")]
    return s

qqq, spy, tqqq, upro, soxl = (load(x) for x in ["QQQ", "SPY", "TQQQ", "UPRO", "SOXL"])
ndx = load("%5ENDX", False); gspc = load("%5EGSPC", False); sptr = load("%5ESP500TR", False)
irx = load("%5EIRX", False)  # 13w T-bill yield, percent
print("last dates:", qqq.index[-1].date(), tqqq.index[-1].date(), "NDX first", ndx.index[0].date(), "SPTR first", sptr.index[0].date(), "GSPC first", gspc.index[0].date(), "IRX first", irx.index[0].date())

def stats(eq, name):
    eq = eq.dropna()
    yrs = (eq.index[-1] - eq.index[0]).days / 365.25
    cagr = (eq.iloc[-1] / eq.iloc[0]) ** (1 / yrs) - 1
    dd = (eq / eq.cummax() - 1)
    r = eq.pct_change().dropna()
    vol = r.std() * np.sqrt(252)
    return f"{name:45s} {eq.index[0].date()}..{eq.index[-1].date()}  CAGR {cagr*100:6.1f}%  MaxDD {dd.min()*100:6.1f}% (trough {dd.idxmin().date()})  vol {vol*100:5.1f}%  x{eq.iloc[-1]/eq.iloc[0]:.1f}"

# daily rf
rf = (irx.reindex(pd.date_range(irx.index[0], "2027-01-01", freq="D")).ffill() / 100 / 252)

# ---- underlying daily returns for NDX total-return proxy: NDX price before QQQ, QQQ adj after
q_r = qqq.pct_change()
n_r = ndx.pct_change()
under_q = pd.concat([n_r[n_r.index < qqq.index[1]], q_r[q_r.index >= qqq.index[1]]]).dropna()
# S&P TR proxy: SPTR from 1988, GSPC price + 3.5%/yr dividend approx before
g_r = gspc.pct_change()
s_r = sptr.pct_change()
under_s = pd.concat([(g_r[g_r.index < sptr.index[1]] + 0.035 / 252), s_r[s_r.index >= sptr.index[1]]]).dropna()

def lev_sim(ur, L=3, er=0.0095):
    rfd = rf.reindex(ur.index).ffill().fillna(0.04 / 252)
    # L x underlying, minus borrowing on (L-1) at T-bill (+0.5% spread), minus expense ratio
    return L * ur - (L - 1) * (rfd + 0.005 / 252) - er / 252

def sma_strategy(sig_px, asset_r, n=200, band=0.0, lag=1, cash_r=None):
    sma = sig_px.rolling(n).mean()
    above = sig_px > sma * (1 + band)
    below = sig_px < sma * (1 - band)
    st = pd.Series(np.nan, index=sig_px.index)
    st[above] = 1.0; st[below] = 0.0
    st = st.ffill().fillna(0)
    pos = st.shift(lag).reindex(asset_r.index).ffill().fillna(0)
    if cash_r is None:
        cash_r = rf.reindex(asset_r.index).ffill().fillna(0)
    r = pos * asset_r + (1 - pos) * cash_r
    switches = pos.diff().abs().sum()
    yrs = (asset_r.index[-1] - asset_r.index[0]).days / 365.25
    return (1 + r).cumprod(), switches / yrs, r

out = []
P = lambda s: out.append(s)

# validate sim against real TQQQ
sim3n = lev_sim(under_q)
common = tqqq.index[(tqqq.index >= "2010-03-01")]
real_tq = tqqq.pct_change().reindex(common)
simtq = sim3n.reindex(common)
P("=== Simulation check (3x NDX sim vs real TQQQ, 2010-03..now)")
P(stats((1 + real_tq.fillna(0)).cumprod(), "real TQQQ"))
P(stats((1 + simtq.fillna(0)).cumprod(), "simulated 3x NDX"))
sim3s = lev_sim(under_s)
cu = upro.index[upro.index >= "2009-07-01"]
P(stats((1 + upro.pct_change().reindex(cu).fillna(0)).cumprod(), "real UPRO"))
P(stats((1 + sim3s.reindex(cu).fillna(0)).cumprod(), "simulated 3x S&P TR"))

P("\n=== Buy and hold, real ETFs, TQQQ era 2010-02-11 .. 2025-12-31")
for s, nm in [(spy, "SPY"), (qqq, "QQQ"), (tqqq, "TQQQ"), (upro, "UPRO"), (soxl, "SOXL")]:
    x = s[(s.index >= "2010-02-11") & (s.index <= "2025-12-31")]
    P(stats(x, nm + " B&H"))
P("\n=== Buy and hold, real ETFs, through latest date")
for s, nm in [(tqqq, "TQQQ"), (upro, "UPRO"), (soxl, "SOXL")]:
    P(stats(s, nm + " B&H since inception"))

# Strategies on real TQQQ: signal QQQ 200SMA
for (start, end) in [("2010-02-11", "2025-12-31"), ("2010-02-11", "2026-12-31"), ("2016-01-01", "2025-12-31"), ("2021-01-01", "2025-12-31")]:
    P(f"\n=== Real TQQQ with QQQ 200-day SMA filter (signal at close, trade next close, T-bills when out), {start}..{end}")
    ar = tqqq.pct_change()
    ar = ar[(ar.index > start) & (ar.index <= end)]
    for band in [0.0, 0.03]:
        eq, sw, _ = sma_strategy(qqq, ar, 200, band)
        P(stats(eq, f"TQQQ|QQQ>200SMA band {band:.0%}") + f"  switches/yr {sw:.1f}")
    eq, sw, _ = sma_strategy(qqq, qqq.pct_change()[(qqq.index > start) & (qqq.index <= end)], 200, 0)
    P(stats(eq, "QQQ|QQQ>200SMA (1x)") + f"  switches/yr {sw:.1f}")
    P(stats((1 + ar.fillna(0)).cumprod(), "TQQQ B&H same window"))
    ur = upro.pct_change(); ur = ur[(ur.index > start) & (ur.index <= end)]
    eq, sw, _ = sma_strategy(spy, ur, 200, 0)
    P(stats(eq, "UPRO|SPY>200SMA") + f"  switches/yr {sw:.1f}")

# Long simulated history
P("\n=== Simulated 3x Nasdaq-100 (1985-10..now) incl. dot-com")
ndx_sig = pd.concat([ndx[ndx.index < qqq.index[0]], ndx[ndx.index >= qqq.index[0]]])
P(stats((1 + under_q).cumprod(), "NDX TR proxy B&H 1x"))
P(stats((1 + sim3n).cumprod(), "Sim 3x NDX B&H"))
for band in [0.0, 0.03]:
    eq, sw, r = sma_strategy(ndx, sim3n, 200, band)
    P(stats(eq, f"Sim 3x NDX | NDX>200SMA band {band:.0%}") + f"  switches/yr {sw:.1f}")
eq1, sw, _ = sma_strategy(ndx, under_q, 200, 0)
P(stats(eq1, "1x NDX | NDX>200SMA") + f"  switches/yr {sw:.1f}")
# dot-com window
w = (sim3n.index >= "2000-03-10") & (sim3n.index <= "2002-10-09")
P(stats((1 + sim3n[w]).cumprod(), "Sim 3x NDX B&H 2000-03-10..2002-10-09"))
P(stats((1 + under_q[w]).cumprod(), "NDX 1x 2000-03-10..2002-10-09"))
eqf, _, _ = sma_strategy(ndx, sim3n, 200, 0)
P(stats(eqf[(eqf.index >= "1999-12-31") & (eqf.index <= "2009-12-31")], "Sim 3x NDX SMA 2000-2009"))
P(stats((1 + sim3n[(sim3n.index >= "1999-12-31") & (sim3n.index <= "2009-12-31")]).cumprod(), "Sim 3x NDX B&H 2000-2009"))
P(stats(eqf[(eqf.index >= "1985-10-01") & (eqf.index <= "2009-12-31")], "Sim 3x NDX SMA 1985-2009 (pre-TQQQ)"))
# years to recover sim 3x B&H after 2000
eqb = (1 + sim3n).cumprod()
pk = eqb[eqb.index <= "2000-12-31"].max()
rec = eqb[(eqb.index > "2000-03-10") & (eqb >= pk)]
P(f"Sim 3x NDX B&H 2000 peak recovered on: {rec.index[0].date() if len(rec) else 'never'}")

P("\n=== Simulated 3x S&P 500 (1928..now; pre-1988 dividends approximated at 3.5%/yr, pre-1960 T-bill at 4%)")
P(stats((1 + under_s).cumprod(), "S&P TR proxy 1x B&H"))
P(stats((1 + sim3s).cumprod(), "Sim 3x S&P B&H"))
eqs, sws, _ = sma_strategy(gspc, sim3s, 200, 0)
P(stats(eqs, "Sim 3x S&P | S&P>200SMA") + f"  switches/yr {sws:.1f}")
eqs2, sws2, _ = sma_strategy(gspc, lev_sim(under_s, 2), 200, 0)
P(stats(eqs2, "Sim 2x S&P | S&P>200SMA") + f"  switches/yr {sws2:.1f}")
eqs1, sws1, _ = sma_strategy(gspc, under_s, 200, 0)
P(stats(eqs1, "1x S&P | S&P>200SMA") + f"  switches/yr {sws1:.1f}")
for a, b in [("1929-09-01", "1932-07-01"), ("1973-01-01", "1974-12-31"), ("2007-10-09", "2009-03-09"), ("1987-08-25", "1987-12-04")]:
    w = (sim3s.index >= a) & (sim3s.index <= b)
    P(stats((1 + sim3s[w]).cumprod(), f"Sim 3x S&P B&H {a}..{b}") + "  | SMA: " + f"{(eqs[w].iloc[-1]/eqs[w].iloc[0]-1)*100:.0f}%")

# Rolling outcome distributions: $200 start
P("\n=== Rolling-window outcome distribution for $200 (all daily start dates; overlapping windows)")
def rolling_dist(eq, years, label):
    eq = eq.dropna()
    n = int(round(252 * years))
    v = eq.values
    mult = v[n:] / v[:-n]
    # path min / hit 5x
    hit5 = []; dd50 = []
    for i in range(0, len(v) - n, 5):
        path = v[i:i + n + 1] / v[i]
        hit5.append((path >= 5).any())
        dd50.append((path <= 0.5).any())
    q = np.percentile(mult, [5, 25, 50, 75, 95])
    return (f"{label:38s} {years}y  n={len(mult):5d}  $200 -> p5 ${200*q[0]:.0f} p25 ${200*q[1]:.0f} median ${200*q[2]:.0f} p75 ${200*q[3]:.0f} p95 ${200*q[4]:.0f}"
            f"  P(end>=$1000) {np.mean(mult>=5)*100:4.1f}%  P(touch $1000) {np.mean(hit5)*100:4.1f}%  P(end<$200) {np.mean(mult<1)*100:4.1f}%  P(touch<=$100) {np.mean(dd50)*100:4.1f}%")

sp_bh = (1 + under_s[under_s.index >= "1950-01-01"]).cumprod()
nd_bh = (1 + under_q).cumprod()
tq_sma_sim = eqf
tq_bh_sim = (1 + sim3n).cumprod()
for yrs in [1, 3, 5, 10]:
    P(rolling_dist(sp_bh, yrs, "S&P 500 TR B&H (1950-now)"))
    P(rolling_dist(nd_bh, yrs, "Nasdaq-100 B&H (1985-now)"))
    P(rolling_dist(tq_bh_sim, yrs, "Sim 3x NDX B&H (1985-now)"))
    P(rolling_dist(tq_sma_sim, yrs, "Sim 3x NDX + 200SMA (1985-now)"))
    P(rolling_dist(eqs[eqs.index >= "1950-01-01"], yrs, "Sim 3x S&P + 200SMA (1950-now)"))

# same but only post-2010 real TQQQ+SMA
ar = tqqq.pct_change()[tqqq.index > "2010-02-11"]
eqr, _, _ = sma_strategy(qqq, ar, 200, 0)
for yrs in [1, 3, 5]:
    P(rolling_dist(eqr, yrs, "REAL TQQQ + QQQ200SMA (2010-now)"))
    P(rolling_dist(tqqq[tqqq.index > "2010-02-11"], yrs, "REAL TQQQ B&H (2010-now)"))

# calendar-year returns of real TQQQ SMA vs QQQ
P("\n=== Calendar-year returns: real TQQQ+SMA | TQQQ B&H | QQQ | SPY")
for y in range(2011, 2027):
    def yr(eq):
        e = eq[(eq.index.year == y)]
        prev = eq[eq.index.year < y]
        if len(e) == 0 or len(prev) == 0: return float('nan')
        return (e.iloc[-1] / prev.iloc[-1] - 1) * 100
    P(f"{y}: {yr(eqr):7.1f}% | {yr(tqqq):7.1f}% | {yr(qqq):6.1f}% | {yr(spy):6.1f}%")

# compounding math
P("\n=== Years to 5x at given CAGR")
for c in [0.07, 0.10, 0.15, 0.20, 0.30, 0.40, 0.60, 1.0]:
    P(f"CAGR {c:.0%}: {np.log(5)/np.log(1+c):.1f} years")
print("\n".join(out))
