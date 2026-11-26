# Overnight Return Anomaly and Calendar Effects (Turn-of-the-Month, Pre-Holiday) as Strategies for a $200 Alpaca Account

Research note on method: this session could not fetch web pages. WebFetch failed with DNS errors for alphaarchitect.com, spintwig.com and benzinga.com, so the findings below come from search-engine extracts of the cited pages, not full-text reads. Numbers are quoted as the extracts gave them. Where an extract was ambiguous or sources conflicted, that is flagged. Anything marked "Inference" is my own arithmetic or reasoning, not a sourced claim.

## 1. Overnight anomaly: what the key papers and later replications find, and magnitudes by period

### Takeaway
Over roughly 1993–2020, close-to-open returns earned essentially all of the US equity premium, and open-to-close returns were near zero or negative. That is well documented academically (Cliff/Cooper/Gulen 2008; Lou/Polk/Skouras 2019; Knuteson 2020; NY Fed). Since about 2021–2022 the effect has been unstable and much weaker. Some years flip (intraday beat overnight in 2022 and 2023, overnight won big in 2024), and the NY Fed's own authors report that their 2–3 a.m. "overnight drift" has averaged about zero since 2021.

### Cited Findings
**Cliff, Cooper & Gulen (2008), "Return Differences between Trading and Non-Trading Hours: Like Night and Day"** (standard citation order is Cliff first; SSRN 1004081)
- The entire US equity premium over the sample accrued overnight. Intraday returns were on average slightly negative. — [ResearchGate listing](https://www.researchgate.net/publication/228461243_Return_Differences_between_Trading_and_Non-Trading_Hours_Like_Night_and_Day); summary in [NY Fed Staff Report 917](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr917.pdf)

**Kelly & Clark (2011)**
- Cited by the NY Fed as also documenting that equities earn "a substantial proportion of their returns during the overnight period." I found no specific numbers or sample details. — [NY Fed Staff Report 917](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr917.pdf)

**Lou, Polk & Skouras (2019), "A Tug of War: Overnight Versus Intraday Expected Returns," JFE 134(1):192–213**
- Across 14 cross-sectional strategies, profits come either entirely overnight or entirely intraday, usually with opposite-signed components in the other session. Momentum profits accrue entirely overnight. Value, profitability, investment and the other strategies earn their premiums intraday. — [RePEc](https://ideas.repec.org/a/eee/jfinec/v134y2019i1p192-213.html); [NBER conference version](https://conference.nber.org/confer/2015/APf15/Lou_Polk_Skouras.pdf)
- Overnight momentum profits partially reverse intraday. The authors link this to clienteles: individuals trade near the open, institutions near the close. Overnight-minus-intraday momentum spreads of roughly 2% per month are tied to institutional momentum trading. — [NBER conference version](https://conference.nber.org/confer/2015/APf15/Lou_Polk_Skouras.pdf); [Internet Appendix](https://personal.lse.ac.uk/loud/ATugofWar_appendix.pdf)
- A third-party replication of a strategy based on the paper by PapersWithBacktest shows about 4.7% per year and Sharpe 0.71 for 2003–2026. These are the site's own numbers, not the paper's. — [PapersWithBacktest](https://paperswithbacktest.com/strategies/a-tug-of-war-overnight-versus-intraday-dong-lou-christopher-polk-and-spyros-skouras)

**Knuteson (2020), "Strikingly Suspicious Overnight and Intraday Returns" (arXiv 2010.01727), plus sequels including "They Chose to Not Tell You" (2021) and "They Still Haven't Told You" (2022)**
- Overnight returns to major indices over recent decades have been "wildly positive" and intraday returns "disturbingly negative." He rejects the explanation that "price discovery happens overnight," because the intraday return distribution is wider than the overnight one. He hypothesises that a large quant portfolio expanding and contracting daily pushes prices up overnight and down intraday. That explanation is his own and not independently validated. — [arXiv 2010.01727](https://arxiv.org/pdf/2010.01727); [arXiv 2107.12516](https://arxiv.org/pdf/2107.12516)
- Using SPY from 1993 to June 2021, Knuteson shows the intraday return distribution is clearly wider than the overnight one. — [arXiv 2107.12516](https://arxiv.org/pdf/2107.12516)

**NY Fed: Boyarchenko, Larsen & Whelan, "The Overnight Drift," RFS 36(9), 2023**
- A large, persistent return to holding US equity (E-mini) futures from 2:00 to 3:00 a.m. ET, around the European open. It averaged about 3.6% annualised over 1998–2019. The authors explain it as compensation to intermediaries for holding inventory after net-selling days. — [CBS accepted version](https://research-api.cbs.dk/ws/portalfiles/portal/101311522/nina_boyarchenko_et_al_the_overnight_drift_acceptedversion.pdf); [Liberty Street 2021](https://libertystreeteconomics.newyorkfed.org/2021/05/the-overnight-drift-in-us-equity-returns)
- **"The Disappearing Overnight Drift" (Liberty Street Economics, July 1, 2026).** The 2–3 a.m. window, previously about 3.7% per year and more than 60% of the contract's 5.9% annualised close-to-close return, has averaged close to zero since 2021. The test covers January 2021 to December 2025, 1,245 trading days. — [Liberty Street 2026](https://libertystreeteconomics.newyorkfed.org/2026/07/the-disappearing-overnight-drift/); [RePEc](https://ideas.repec.org/p/fip/fednls/103479.html)
- Secondary claim, not verified against the Fed post: dispersion of end-of-day signed volume fell from 6.5% to 2.9% as part of the explanation. — [SPY Overnight Swing Trading blog](https://spytomorrow.com/overnight-vs-intraday-returns/)

**Elm Wealth (Haghani, Dewey, Ragulin), "Night Moves: Is the Overnight Drift the Grandmother of All Market Anomalies?"** (data to 2022; JOIM 2024 Harry Markowitz award)
- Over 1993–2022, overnight returns had lower standard deviation than intraday but more negative skew and fatter tails. — [Elm Wealth](https://elmwealth.com/night-moves-overnight-drift/); [award PR](https://www.businesswire.com/news/home/20250304299372/en/Elm-Wealth%E2%80%99s-Haghani-Shares-Award-for-Uncovering-Causes-of-Overnight-Drift-in-Meme-Stocks-Bitcoin)
- Over about 30 years, SPY open-to-close would have turned $1 into about $1.20, below T-bills. Elm reports SPY multiples of 2.07 for the whole day, 1.25 for the daytime and 1.66 for the night-time. The extract was ambiguous on the period and on whether these are annual multiples. — [Elm "Still Working the Night Shift"](https://elmwealth.com/night-shift/)
- Rolling five-year overnight-minus-intraday returns for the S&P 500 were "very high until about ten years ago," meaning the gap narrowed after roughly the mid-2010s. — [Elm Night Moves PDF](https://elmwealth.com/wp-content/uploads/2026/04/Elm-Night-Moves-Overnight-Drift.pdf); [PapersWithBacktest summary](https://paperswithbacktest.com/strategies/night-moves-is-the-overnight-drift-the-grandmother-of-all-market-anomalies)

**SPY magnitudes by period (mostly practitioner sources, which conflict)**
- Across 8,509 SPY trading days from 1993 to Nov 19, 2026, $100 compounded to $1,565 overnight and $103 intraday. — [thetrading.tools weekday analysis](https://www.thetrading.tools/weekday-analysis)
- Since 2000, $1 in SPY during market hours became $1.35, and overnight became $6.22 (blog). — [Substack](https://gurufinanceinsights.substack.com/p/1-in-spy-during-market-hours-since)
- Over 1993–2024, the overnight-only total return was 865.08% and buy-and-hold was 995.98%. — [spintwig](https://spintwig.com/long-spy-day-of-week-equity-backtest) (extract only)
- Over Dec 2014 to Jun 2026, SPY overnight returned +115% and intraday +66%, a much smaller gap. — [Vortex Capital](https://www.vortexcapitalgroup.com/insights/the-night-shift-where-us-equity-returns-actually-accrue-and-why-the-day-session-is-pure-skill)
- By year: 2022 overnight -14.7% vs intraday -5.6%; 2023 intraday +19.2% vs overnight +4.3%; 2024 overnight +22.3% vs intraday +0.8% (blog with unclear method). — [spytomorrow.com](https://spytomorrow.com/spy-overnight-returns-vs-intraday/)
- From 2010 onward the overnight-vs-intraday difference "appears less pronounced." In the 2020 crash and the 2022 decline, the overnight component fell harder than the cash session. — [Benzinga, Nov 2026](https://www.benzinga.com/opinion/26/11/62875511/overnight-trading-on-sp500-returns-drawdowns-in-spy) (extract only)
- In a 2021 Liquidnet analysis, overnight was about 80% of total return for S&P 500 stocks and 65% for Nasdaq-100 listings. — [Liquidnet "Price Discovery and Tactics to Time Trading," Jul 2021](https://static1.squarespace.com/static/5bedbc974eddecbfbb0c217e/t/60f9c66d85ed7357cd00c600/1626981997756/PriceDiscovery-TacticsToTimeTrading-20210714-final.pdf)
- A Quantpedia study covering 2018–2021 found unfiltered SPY overnight returns of 13.62% per year with Sharpe 0.84, gross of costs. — [Quantpedia](https://quantpedia.com/market-sentiment-and-an-overnight-anomaly/)
- PapersWithBacktest flags that the overnight strategy has faded since 2022, with a post-publication Sharpe of -2.46 versus 0.65 for the S&P 500. The window and method were not visible. — [PapersWithBacktest](https://paperswithbacktest.com/strategies/night-moves-is-the-overnight-drift-the-grandmother-of-all-market-anomalies)

### Inferences
- From thetrading.tools ($100 to $1,565 over 8,509 days, about 33.8 years), the average overnight log return is about 0.032% (3.2 bp) per night, roughly 8.5% CAGR gross. The intraday leg is about 0.1% per year. Those 3.2 bp per night are the entire gross edge, and any per-round-trip cost has to come out of them.
- Full-period sources broadly agree that overnight beat intraday for SPY over 1993–2020. They disagree a lot on size, because of dividend handling (SPY goes ex-dividend at the open, which hurts the overnight leg), start dates and data quality.
- Pre-2010: very strong overnight dominance. 2010–2020: still overnight-dominant but narrowing. 2021–2026: unstable, with intraday winning in 2022 and 2023, and the NY Fed's 2–3 a.m. drift is gone. Overnight returns also carry fatter left tails (gap-downs), so "time in market at night" is not a lower-risk way to hold equities.

### Gaps
- No peer-reviewed, sourced breakdown of SPY or QQQ close-to-open vs open-to-close by exact sub-period (pre-2010, 2010–2020, 2020–2026) was found. The period figures above are from blogs and conflict with each other.
- Kelly & Clark (2011): no numbers retrieved.
- No QQQ-specific overnight vs intraday split was found, beyond the Liquidnet 65% figure for Nasdaq-100 constituents.

## 2. Does "buy at the close, sell at the open" on SPY/QQQ survive costs? Break-even cost; MOC/MOO execution

### Takeaway
Gross, yes over 1993–2020. Net, the best-known cost-inclusive test (Alpha Architect, SPY, 1993–Jan 2020) turns a +717% gross cumulative return into -32% after historical bid-ask spreads plus $0.01/share. The gross edge is only about 3 bp per night, so a round trip costing more than about 3 bp kills it. Today's SPY penny spread is well below that, but opening-print slippage and Alpaca's order restrictions for fractional shares matter more for a $200 account. A live product (NightShares NSPY/NIWM) lost money and was liquidated in 2023.

### Cited Findings
- **Alpha Architect, "Trading Costs Wipe Out the Overnight Return Anomaly"**: buy SPY at the close and sell at the next open, Jan 1993 to Jan 2020. Costs were the historical daily bid-ask spread plus $0.01/share commission, the same commission as the original paper, which had ignored spreads. The cumulative return fell from +717% gross to -32% net. The return spread is not significantly different from zero using only post-Reg FD data, i.e. after 2000. — [Alpha Architect](https://alphaarchitect.com/trading-costs-wipe-out-the-overnight-return-anomaly/) (extract; full tables not read)
- Another Alpha Architect summary says overnight-vs-intraday outperformance "still holds gross and net," but with low statistical robustness, "more of a random walk than … a repeatable trading strategy." This partly conflicts with the -32% figure, possibly a different piece or cost assumption. — [Alpha Architect](https://alphaarchitect.com/trading-costs-wipe-out-the-overnight-return-anomaly/)
- Trading in the opening and closing auctions does not cross a bid-ask spread, but price impact remains a cost for large investors. — [Elm Wealth Night Moves PDF](https://elmwealth.com/wp-content/uploads/2026/04/Elm-Night-Moves-Overnight-Drift.pdf)
- The bid-ask spread to the mid is only a lower bound on slippage cost (Falkenblog on overnight ETFs). — [Falkenblog](https://efalken.substack.com/p/the-equity-overnight-anomaly-etfs)
- Quantpedia warns that the transaction costs of this kind of strategy "would be very high." It suggests using the overnight effect as a timing overlay, not a standalone system. — [Quantpedia](https://quantpedia.com/market-sentiment-and-an-overnight-anomaly/); [IBKR Campus repost](https://ibkrcampus.com/?p=155254)
- A general rule from the anomaly literature: net return is roughly gross return minus 2 × turnover × spread. A daily round trip means turnover of about 252x per year. — [Chen, "Accounting for the Anomaly Zoo"](https://jacobslevycenter.wharton.upenn.edu/wp-content/uploads/2019/09/Accounting-for-the-Anomaly-Zoo.pdf)
- **Live-product evidence:** NightShares 500 (NSPY) and NightShares 2000 (NIWM) bought S&P 500 and Russell 2000 futures at the close and sold at the open. They launched in June 2022 and were liquidated, with the last NYSE Arca trading day on July 31, 2023. NSPY returned -6.9% total return since inception versus +22% for the S&P 500 (Bloomberg via WealthManagement), or -4.6% (NSPY) and -4.7% (NIWM) per ETFstream. Assets at closure were about $3.7M. The CEO said the funds launched "just as gains during the day surpassed those of the overnight." — [WealthManagement](https://www.wealthmanagement.com/etfs/-night-effect-etfs-to-shut-down-with-overnight-stock-returns-elusive); [ETFstream](https://www.etfstream.com/articles/blackout-for-night-effect-etfs); [SEC 497 filing](https://www.sec.gov/Archives/edgar/data/1199046/000158064223003676/nightshares497s.htm)
- **Alpaca execution mechanics:** Alpaca supports auction-only orders. Market-on-open and limit-on-open orders use time_in_force = `opg`; market-on-close and limit-on-close use `cls`. — [Alpaca docs: Placing Orders](https://docs.alpaca.markets/docs/orders-at-alpaca); [Alpaca blog](https://alpaca.markets/blog/websocket-moc-cors/)
- Alpaca fractional trading supports market, limit, stop and stop-limit orders with time_in_force = Day. This points to fractional orders not being able to use `opg`/`cls`, and the Broker API docs say fractional orders are market-day only. This should be confirmed in paper or live testing. — [Alpaca Fractional Trading docs](https://docs.alpaca.markets/docs/fractional-trading); [Broker API trading](https://docs.alpaca.markets/docs/brokerapi-trading)
- Alpaca paper trading does not simulate `opg`/`cls` well: they fill as regular market orders at the open or close bid/ask, not at auction prices. A paper backtest of MOC/MOO is therefore not a faithful cost estimate. — [Alpaca forum, via Alpaca docs search](https://forum.alpaca.markets/t/frustration-with-the-execution-of-pre-market-orders/13787)

### Inferences
- **Break-even cost:** with a gross edge of about 3.2 bp per night (from thetrading.tools, 1993–2026) and well under that since 2021, any all-in round-trip cost above about 2–3 bp makes the strategy no better than, or worse than, buy-and-hold. Buy-and-hold already captures the overnight return and avoids the cost. A penny spread on SPY at roughly $600+ is about 0.15–0.2 bp, so the quoted spread alone does not kill it today. The pre-2001 fractional-tick era (1/16 dollar spreads on SPY near $100, about 6 bp) explains the Alpha Architect -32%.
- **What actually kills it for this account:** (a) On Alpaca, a $200 account cannot buy a whole SPY or QQQ share, so it must either use fractional market orders or switch to a low-priced S&P 500 ETF such as SPLG/SPYM for whole-share auction orders (ETF prices not verified here). (b) Fractional orders cannot use the auctions, so the bot would send market orders near 15:59 and just after 09:30. The first minutes after the open have wider spreads and noisy prints, so slippage can plausibly be several bp, but no source quantified this. (c) Short-term capital gains on 252 trades per year, versus no realisation for buy-and-hold.
- **Key point for the user:** the overnight strategy is not "extra return on top of the market." At best it is the market's return compressed into about 17.5 of every 24 hours, with less intraday noise but more gap risk. Its gross CAGR (about 8.5% over 1993–2026, much less recently) is at best similar to buy-and-hold, while it carries 252 round trips a year of cost and tax drag.

### Gaps
- No published measurement was found of MOC/MOO auction slippage versus the midpoint for SPY or QQQ in recent years.
- No source confirmed SEC Section 31 or FINRA TAF fee levels for 2026. They are tiny per trade but non-zero on sells.
- I could not read Alpha Architect's full cost table, including whether it tested post-decimalisation net returns separately.

## 3. Is the overnight return concentrated in certain stocks or days? Decay or reversal after about 2018?

### Takeaway
Yes, it is concentrated. In the cross-section it is tied to momentum and to institutional versus retail clienteles (Lou/Polk/Skouras). Elm Wealth links strong overnight drift to meme stocks and bitcoin, i.e. attention. The index-level effect has decayed: Elm says the gap was very high until about the mid-2010s, intraday beat overnight in 2022 and 2023, and the NY Fed's 2–3 a.m. drift is about zero since 2021. There is also day-of-week structure, with weekend and Monday effects in overnight returns.

### Cited Findings
- Momentum profits accrue entirely overnight and partially reverse intraday. Value, profitability and investment premia are earned intraday. — [Lou, Polk & Skouras, JFE 2019](https://ideas.repec.org/a/eee/jfinec/v134y2019i1p192-213.html)
- Elm Wealth's Haghani shared an award for "uncovering causes of overnight drift in meme stocks [and] bitcoin," linking the drift to attention and retail flows. — [BusinessWire](https://www.businesswire.com/news/home/20250304299372/en/Elm-Wealth%E2%80%99s-Haghani-Shares-Award-for-Uncovering-Causes-of-Overnight-Drift-in-Meme-Stocks-Bitcoin); [Elm podcast](https://podcasts.apple.com/nz/podcast/the-hidden-impact-of-day-traders-overnight-drift/id1656084327?i=1000703037516)
- The overnight share of return was higher for S&P 500 stocks (about 80%) than for Nasdaq-100 listings (about 65%) in 2021 data. — [Liquidnet 2021](https://static1.squarespace.com/static/5bedbc974eddecbfbb0c217e/t/60f9c66d85ed7357cd00c600/1626981997756/PriceDiscovery-TacticsToTimeTrading-20210714-final.pdf)
- In the HYG high-yield ETF (2007–2024), overnight returns are more robust after a negative close-to-close day. A Monday-close-to-Tuesday-open ("Turnaround Tuesday") version cuts turnover and fees. — [Quantpedia](https://quantpedia.com/overnight-reversal-effects-in-the-high-yield-market/)
- For 2018–2021 SPY, sentiment filters (Brain sentiment, VIX, short-term trend) all improved the overnight strategy. Quantpedia discourages the most complex filter as "low added value." — [Quantpedia](https://quantpedia.com/market-sentiment-and-an-overnight-anomaly/)
- Overnight effects show weekly seasonality, i.e. they differ by day of week. — [Redfame journal article](https://redfame.com/journal/index.php/aef/article/download/7705/6965) (no numbers extracted)
- A 2025 paper tests whether public overnight news explains overnight returns. Its conclusions point to microstructure, attention and news rather than Knuteson's hypothesis. — [arXiv 2507.04481](https://arxiv.org/pdf/2507.04481)
- Decay evidence: [Liberty Street 2026](https://libertystreeteconomics.newyorkfed.org/2026/07/the-disappearing-overnight-drift/); [Elm Night Moves](https://elmwealth.com/night-moves-overnight-drift/); [NightShares closure](https://www.wealthmanagement.com/etfs/-night-effect-etfs-to-shut-down-with-overnight-stock-returns-elusive)

### Inferences
- The variants most likely to keep an edge (high-attention or momentum single stocks overnight) are also the ones with the fattest gap risk and the widest spreads. That is a poor fit for a $200 account trying to compound without blow-ups.
- A conditional version (hold overnight only after a down day, or only Monday to Tuesday) reduces turnover, which is the main cost lever. It still rests on in-sample backtests.

### Gaps
- No sourced numbers on overnight return concentration in small caps versus large caps after 2018.
- No sourced day-of-week overnight figures for SPY. spintwig and thetrading.tools have them, but the pages could not be read.

## 4. Turn-of-the-month (TOM) effect: window, size, share of annual return, persistence to 2025

### Takeaway
The classic TOM window is the last trading day plus the first three trading days of the month (McConnell & Xu 2008). It captured essentially all of the US market's excess return in 1926–2005 and 1987–2005, at about 0.15% per day versus roughly zero on other days. The out-of-sample record is mixed: some tests found it vanished in S&P futures after 1990, others say only the first trading day survives, and a 30-country study (1994–2023) still finds about 10 bp per TOM day. As a SPY strategy it typically gives lower CAGR than buy-and-hold (about 3–7% per year) with much smaller drawdowns and about 15–30% time in market.

### Cited Findings
- **McConnell & Xu (2008), FAJ 64(2):49–64.** The window is the last trading day of the month through the first three trading days of the next. On CRSP data for 1926–2005, the average daily return over the 4-day window was 0.15% value-weighted (0.22% equal-weighted). For 1987–2005 it was 0.14% per day value-weighted in the TOM window versus -0.01% on the other roughly 16 days, so the excess market return is concentrated in the 4 days. The effect is not confined to small or low-priced stocks or to quarter-ends, appears in 31 of 35 countries, and is not explained by volume or mutual fund flows. — [Purdue e-Pubs working paper](https://docs.lib.purdue.edu/cgi/viewcontent.cgi?article=1042&context=ciberwp); [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1135217); [RePEc FAJ](https://ideas.repec.org/a/taf/ufajxx/v64y2008i2p49-64.html)
- Earlier foundations: Ariel (1987) and Lakonishok & Smidt (1988), referenced via McConnell & Xu and the CXO review. — [CXO Advisory TOM review](https://www.cxoadvisory.com/calendar-effects/the-turn-of-the-month-effect/) (contents not extracted)
- **2026 international study ("Infrequent rebalancing, risk deferral, and equity returns at the turn of the month," J. Int. Financial Markets):** 30 countries, 1994–2023, mean return of about 10 bp on TOM days versus about 0 on other days, with a return hierarchy tied to rebalancing frequency. — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1042443126000259)
- In S&P 500 futures, turn-of-the-month effects "disappear" after 1990 (1991–1999 out of sample). — [econstor WP 2000-11](https://www.econstor.eu/bitstream/10419/100728/1/wp2000-11.pdf)
- Carchano & Pardo (2011) tested 188 calendar anomalies. The only one significant in both of their sub-periods was the first trading day of the month for S&P 500 futures, which suggests the window shrank to one day. — cited in [atbresearch / search summary](https://atbresearch.substack.com/p/the-turn-of-the-month-effect-tested); original not retrieved
- A walk-forward test on SPY found an out-of-sample (2015–2026) win rate of 61.0% versus 63.5% in sample, but buy-and-hold beat the strategy on raw return (single blog). — [algoedgeinsights](https://algoedgeinsights.beehiiv.com/p/the-turn-of-the-month-effect-is-real-i-tested-it-on-26-years-of-spy-to-prove-it)
- Another current-data test found TOM results not statistically significant, with the TOM window underperforming the rest of the month in ES futures. — [atbresearch](https://atbresearch.substack.com/p/the-turn-of-the-month-effect-tested)
- A February 2025 analysis says the classic 4-day window is no longer statistically significant for US equities and a wider window may still work. A 2026 Kayaçetin study was cited but not verified. — [seasonalpha.ai](https://seasonalpha.ai/en/blog/turn-of-month-effect-still-alive/)
- SPY's first trading day of the month averages about 0.04% more than other days (Quantified Strategies). The extract was ambiguous on whether 0.04% is the excess or the level. — [Quantified Strategies](https://quantifiedstrategies.substack.com/p/the-first-trading-day-of-the-month)
- A post-2024 test is noted by a practitioner site. — [aimytrade](https://aimytrade.io/blog/spy-turn-of-month-pattern-faces-a-post-2024-test) (contents not extracted)

### Inferences
- The mechanism (month-start inflows, payroll and pension contributions, rebalancing) is plausible and not fully arbitraged. The 2026 rebalancing-hierarchy paper supports a flow explanation, which is the main reason to expect partial persistence.
- For a long-only cash account, TOM is cheap to run (about 12 round trips a year). Costs are not the problem. The problem is that the edge is small and noisy and gives up most of the market's return on the other days.

### Gaps
- No sourced figure for the share of SPY's annual return captured by the TOM window after 2008 specifically.
- I could not read the CXO Advisory TOM review or Quantified Strategies' main TOM article for exact rules and post-2008 stats.

## 5. Pre-holiday and other calendar effects: have they persisted?

### Takeaway
The pre-holiday effect (Ariel 1990; Lakonishok & Smidt 1988; Pettengill on 1962–1986) is well established historically. Recent evidence is thin and points to weakening. CXO finds Thanksgiving-adjacent strength positive but "markedly less so in recent data." With about 9 holidays a year, a pre-holiday-only strategy has very low exposure and tiny annual return.

### Cited Findings
- Ariel finds a significant US pre-holiday effect that is not generated by weekend or January effects. Pettengill (S&P 500, 1962–1986) finds higher pre-holiday returns for large and small firms. — [ResearchGate: Influence of Holidays on US Stocks](https://www.researchgate.net/publication/396814315_The_Influence_of_Holidays_on_the_Yield_and_Volatility_of_United_States_Stocks); [IG note citing Lakonishok & Smidt and Ariel](https://www.ig.com/en-ch/news-and-trade-ideas/thanksgiving-stock-market-hours-sp500-effect-261125)
- Thanksgiving (1950–2024): modest strength the day before and after, weakness two days after. The day-before and day-after effects are positive in both subsamples but "markedly less so in recent data." — [CXO Advisory](https://www.cxoadvisory.com/calendar-effects/stock-returns-around-thanksgiving/)
- The Wednesday before Thanksgiving rose in 58 years since 1950, averaging about +0.3% (Motley Fool, Nov 2026). — [Motley Fool](https://www.fool.com/investing/2026/11/21/the-s-and-p-500-heads-into-thanksgiving-below-its-peak-here-s-how-the-holiday-week-has-usually-gone-since-1950/)
- The Tuesday-before to Black Friday window rose in 40 of 50 years (1976–2025). — [IG](https://www.ig.com/en-ch/news-and-trade-ideas/thanksgiving-stock-market-hours-sp500-effect-261125)
- A 2024 conference paper reports S&P 500 holiday effects on return and volatility. It is a weak source. — [Scitepress 2024](https://www.scitepress.org/publishedPapers/2024/132703/pdf/index.html)
- Carchano & Pardo (2011): of 188 calendar anomalies, only the first trading day of the month for S&P futures was significant in both periods, implying the pre-holiday effect was not robustly significant there. — via [atbresearch](https://atbresearch.substack.com/p/the-turn-of-the-month-effect-tested)

### Inferences
- Pre-holiday days could be added as extra "in-market" days to a TOM bot (about 9 per year, partly overlapping month-ends). Expected incremental return is a few tenths of a percent per year at most, and is not reliably positive post-2000.

### Gaps
- No comprehensive post-2000 or post-2015 test of the pre-holiday effect in SPY was found, and no sourced average pre-holiday return for 2010–2025.
- No sourced recent evidence on other calendar effects (Halloween/Sell-in-May, January, FOMC pre-announcement drift).

## 6. Strategy statistics (annual return, drawdown, Sharpe, time in market) and practitioner backtests; implications for $200 to $1,000

### Takeaway
None of these strategies plausibly turns $200 into $1,000 on any reasonable horizon. The overnight strategy's best gross historical CAGR is about 8–14% (and about zero or negative net or since 2021). TOM variants show about 3–7% CAGR with roughly 11–27% max drawdowns and 14–40% time in market. At those rates a 5x takes decades. Their real value is lower drawdown per unit of exposure, not faster growth.

### Cited Findings
| Strategy | Period | CAGR / return | Max DD | Sharpe | Time in market | Costs | Source |
|---|---|---|---|---|---|---|---|
| SPY overnight (close to open) | 1993–Jan 2020 | +717% cumulative gross; **-32% net** | n/a | n/a | about 70% of hours, daily | historical spread + $0.01/sh | [Alpha Architect](https://alphaarchitect.com/trading-costs-wipe-out-the-overnight-return-anomaly/) |
| SPY overnight | 1993–Nov 2026 | $100 to $1,565 (about 8.5% CAGR, my calculation) | n/a | n/a | nightly | gross | [thetrading.tools](https://www.thetrading.tools/weekday-analysis) |
| SPY overnight | 1993–2024 | +865% vs +996% buy-and-hold | n/a | n/a | nightly | unclear | [spintwig](https://spintwig.com/long-spy-day-of-week-equity-backtest) |
| SPY overnight, unfiltered | 2018–2021 | 13.62% p.a. | n/a | 0.84 | nightly | gross | [Quantpedia](https://quantpedia.com/market-sentiment-and-an-overnight-anomaly/) |
| Overnight strategy, post-publication | about 2022+ | negative | n/a | -2.46 (vs 0.65 S&P) | nightly | unclear | [PapersWithBacktest](https://paperswithbacktest.com/strategies/night-moves-is-the-overnight-drift-the-grandmother-of-all-market-anomalies) |
| NightShares NSPY (live ETF) | Jun 2022–Jul 2023 | -6.9% (or -4.6%) vs S&P +22% | n/a | n/a | nightly | real, net | [WealthManagement](https://www.wealthmanagement.com/etfs/-night-effect-etfs-to-shut-down-with-overnight-stock-returns-elusive) |
| TOM "tactical twist" (Quantified Strategies, via a secondary rewrite) | n/a | 6% CAGR, 167 trades, 67% win rate, profit factor 2.8, +1.2% avg/trade | 15% | n/a | about 14% | unverified | [wikidocs rewrite](https://wikidocs.net/blog/@systrader79/17183/) |
| TOM 7-day window, S&P 500 index | 1960–about 2024 | 6.8% vs 7.4% buy-and-hold | 27% vs 56% | n/a | about 33% | n/a | [Quantified Strategies](https://quantifiedstrategies.substack.com/p/the-turn-of-the-month-effect-with) |
| TOM last 3 + first 3 days, SPY | 2000–2026 | 4.83% vs 8.24% buy-and-hold | -19.0% vs -55.2% | n/a | 28.7% | n/a; source tables internally inconsistent | [algoedgeinsights](https://algoedgeinsights.beehiiv.com/p/the-turn-of-the-month-effect-is-real-i-tested-it-on-26-years-of-spy-to-prove-it) |
| TOM SPY (Quantra) | 1993–2023 | 2.87% (2.71% with MA filter) | 11.97% (5.56% filtered) | n/a | n/a | n/a | [Quantra](https://quantra.quantinsti.com/glossary/-Trading-the-Turn-of-the-Month-Effect) |
| TOM SPY, buy at month-end and sell after 3 days (QuantConnect/Quantpedia) | n/a | 3.0% | 24.6% | n/a | n/a | QC default | [Quantpedia screener](https://quantpedia.com/screener/Details/41); [QC backtest](https://www.quantconnect.com/terminal/quantpediaBacktestResult/embedded_backtest_1e06a9be2e68d49a8b0babec5360a840.html) |
| TOM with prior-month-down filter | about 15 yrs | higher per-trade | 18.3% (from 22.3%) | n/a | n/a | n/a | [seasonalpha.ai](https://seasonalpha.ai/en/blog/spy-turn-of-month-down-month-reversal-backtest/) |
| TOM exposure (TradingView config) | n/a | n/a | n/a | n/a | about 7–12 days/month, about 40% | n/a | [TradingView/EdgeTools](https://www.tradingview.com/chart/CL1!/yaZKpqAm-The-Calendar-Anomaly-That-Actually-Works/) |

**Exact rule sets a bot could follow, as described in the sources:**
- *Overnight (academic/Alpha Architect)*: each trading day, buy SPY at the closing price and sell at the next day's opening price. — [Alpha Architect](https://alphaarchitect.com/trading-costs-wipe-out-the-overnight-return-anomaly/)
- *Conditional overnight (Quantpedia, HYG)*: hold overnight only after a negative close-to-close day, or only Monday close to Tuesday open. — [Quantpedia](https://quantpedia.com/overnight-reversal-effects-in-the-high-yield-market/)
- *TOM (McConnell & Xu)*: buy at the close of the second-to-last trading day of the month, which gives exposure to the last day. Sell at the close of the 3rd trading day of the new month. — [McConnell & Xu](https://docs.lib.purdue.edu/cgi/viewcontent.cgi?article=1042&context=ciberwp)
- *TOM (Quantpedia)*: hold the market during the last 4 trading days and the first 3 trading days of each month. — [Quantpedia screener](https://quantpedia.com/screener/Details/41)
- *Alpaca order types*: `cls` (MOC) / `opg` (MOO) for whole shares. Fractional shares appear limited to Day market or limit orders during regular hours. — [Alpaca docs](https://docs.alpaca.markets/docs/orders-at-alpaca); [Fractional docs](https://docs.alpaca.markets/docs/fractional-trading)

### Inferences
- **Time to grow $200 to $1,000 (5x)**: at 3% CAGR about 54 years; at 6% about 28 years; at 8.5% about 20 years; at 13.6% (the 2018–2021 overnight peak, gross) about 12.6 years. Buy-and-hold SPY at about 8–10% historical CAGR is in the same range with zero turnover. No source supports these calendar or overnight strategies reaching 5x in a few years; claiming otherwise would require roughly 40%+ annual returns, far outside any evidence here.
- The honest use for this account: (a) TOM plus pre-holiday as a low-exposure, low-drawdown sleeve, about 12–15 round trips a year, cheap on Alpaca, roughly 3–6% CAGR expected, possibly less. (b) The overnight hold is mostly a way to get beta with fewer hours exposed, with a gross edge of about 3 bp per night that has been unreliable since 2021 and is easily consumed by open-auction or opening-minute slippage. (c) Neither beats simply holding a low-cost S&P 500 ETF on expected total return. Their benefits are drawdown and exposure reduction.
- Because the account is small, whole-share constraints matter. SPY and QQQ cannot be bought whole with $200, so either fractional orders without auction access or a low-priced S&P 500 ETF is required. Whole-share sizing of a roughly $70–80 ETF leaves cash idle, which further drags returns. ETF prices were not verified in this research.
- Fractional shares in amounts like $200 are executed by Alpaca on a principal or riskless-principal basis. Execution quality at 15:59 and 09:30 is unverified and should be measured in live trading before trusting any backtest.

### Gaps
- No sourced Sharpe ratios for TOM on SPY after 2015, and no sourced net-of-cost post-2010 overnight backtest on SPY or QQQ with modern penny spreads. This is the single most useful missing number, and the user should run their own (see task #3, backtest).
- The Quantified Strategies TOM numbers are second-hand via a Korean rewrite; the period and costs are unverified.
- The CXO Advisory calendar-effect reviews and the Alpha Architect full article could not be read because of network restrictions.
