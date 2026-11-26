exec(open('bt.py').read().split("out = []")[0])
sim3n = lev_sim(under_q); sim3s = lev_sim(under_s)
eqb=(1+sim3n).cumprod()
p=eqb.loc["2000-03-10"]; lo=eqb[(eqb.index>"2000-03-10")&(eqb.index<="2002-12-31")].min()
print("3x NDX sim B&H peak 2000-03-10 -> min", lo/p-1)
rec=eqb[(eqb.index>"2000-04-30")&(eqb>=p)]
print("recovered", rec.index[0].date() if len(rec) else "never by "+str(eqb.index[-1].date()), "current vs 2000 peak", eqb.iloc[-1]/p)
eqf,_,_=sma_strategy(ndx,sim3n,200,0)
w=eqf[(eqf.index>="2000-03-10")&(eqf.index<="2003-03-31")]
print("SMA 3x NDX 2000-03-10..2003-03-31", w.iloc[-1]/w.iloc[0]-1, "from its own prior peak:", (eqf/eqf.cummax()-1).loc["2003-03-31"])
pk=eqf[eqf.index<="2003-03-31"].cummax().iloc[-1]; r2=eqf[(eqf.index>"2003-03-31")&(eqf>=pk)]
print("SMA 3x NDX recovered prior peak", r2.index[0].date() if len(r2) else "never")
# how many switches 2000-2003
sma=ndx.rolling(200).mean(); st=(ndx>sma).astype(int); s=st[(st.index>="2000-01-01")&(st.index<="2003-04-30")]
print("NDX 200SMA signal changes 2000-01..2003-04:", int(s.diff().abs().sum()))
# QQQ 2026
q=qqq[qqq.index>="2025-12-31"]; print("QQQ 2026 maxDD", (q/q.cummax()-1).min(), "TQQQ 2026 maxDD", ((tqqq[tqqq.index>="2025-12-31"])/(tqqq[tqqq.index>="2025-12-31"]).cummax()-1).min())
# Kelly
for nm,ur in [("S&P TR 1950-now",under_s[under_s.index>="1960-01-01"]),("NDX 1985-now",under_q)]:
    rfd=rf.reindex(ur.index).ffill()
    ex=ur-rfd; mu=ex.mean()*252; s2=ur.var()*252
    print(nm, "excess mu %.3f sigma %.3f kelly L %.2f"%(mu,s2**0.5,mu/s2), "growth over rf at L=1,2,3: ", [round((L*mu-L*L*s2/2)*100,1) for L in (1,2,3)])
# TQQQ max DD including Covid 2020 and 2018
for a,b in [("2018-08-29","2018-12-24"),("2020-02-19","2020-03-20"),("2021-11-19","2022-12-28")]:
    x=tqqq[(tqqq.index>=a)&(tqqq.index<=b)]; print("TQQQ",a,b, x.min()/x.max()-1)
