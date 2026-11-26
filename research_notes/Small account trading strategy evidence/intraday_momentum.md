# Intraday and end-of-day momentum in US index ETFs (SPY, QQQ): evidence for a small automated account

Research note, compiled 2026-11-26. Context: $200 Alpaca cash account (no margin, commission-free), SPY/QQQ plus 1x inverse SH/PSQ, fractional shares, ~5-minute polling from GitHub Actions, possibly delayed data.

**How the sources were read.** Most primary PDFs (SSRN, JFE mirrors, nd.edu, alexandria.unisg.ch, concretumgroup.com, cxoadvisory.com, quantconnect.com, Substack, dev.to, edgelabtrading.com, arxiv.org) could not be fetched: they are outside this session's network allowlist. Figures from those sources come from search-engine summaries and snippets and are marked "(snippet)". GitHub replication READMEs were fetched in full. Where a number could not be pinned to a source, it is listed under Gaps.

---

## Q1. Gao, Han, Li & Zhou (2018) "Market intraday momentum": size, OOS and post-publication fate, replications, gamma link

### Takeaway
The original first-half-hour to last-half-hour effect in SPY (1993-2013) was statistically real but small: R² about 1.6%, and the timing strategy made about 6.7% a year on a last-half-hour-only exposure. Independent replications agree that it has been roughly flat, or even slightly reversed, in SPY since about 2013, and it shows no tradable edge in 2022-2026 data after costs. The gamma-hedging explanation (Baltussen et al. 2021) is well supported in the long futures sample, and it implies the effect is conditional: it appears on negative-dealer-gamma days, not every day.

### Cited Findings
**Original paper (author-reported, in-sample 1993-2013)**
- Published as Gao, Han, Li, Zhou, *Journal of Financial Economics* 129(2), 2018, pp. 394-414. Uses S&P 500 ETF (SPY) high-frequency data, 1993-2013. The first half-hour return, measured from the previous close, predicts the last half-hour return — [EconPapers/RePEc](https://econpapers.repec.org/RePEc:eee:jfinec:v:129:y:2018:i:2:p:394-414); [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0304405X18301351)
- Working-paper draft (March 2014): predictive R² is about 1.6% using the first half-hour alone and rises to about 2.6% when the 12th (penultimate) half-hour return is added. The authors say predictability holds both in and out of sample (snippet). Not verified that the JFE version uses identical figures — [SSRN 2440866 draft via search](https://www.researchgate.net/publication/272303487_Intraday_Momentum_The_First_Half-Hour_Return_Predicts_the_Last_Half-Hour_Return); [Scribd copy](https://www.scribd.com/document/568229114/Indatray-Momentum)
- Timing strategy: go long (short) in the last half-hour if the first half-hour return is positive (negative). It earns 6.67% per annum, and the authors say it beats always-long and buy-and-hold benchmarks (snippet) — [paper mirror on mql5](https://c.mql5.com/forextsd/forum/173/intraday_momentum_-_the_first_half-hour_return_predicts_the_last_half-hour_return.pdf); [Alpha Architect 2014 summary](https://alphaarchitect.com/2014/08/attention-prop-traders-the-first-half-hour-of-trading-predicts-the-last-half-hour/)
- Alpha Architect's summary: the effect is strongest on high-volatility days, recession periods, high-volume days and news days — [Alpha Architect](https://alphaarchitect.com/attention-prop-traders-the-first-half-hour-of-trading-predicts-the-last-half-hour/)

**Post-sample and post-publication evidence on SPY (independent, mostly non-peer-reviewed)**
- Temperance Capital (Substack, Nov 2026). On SPY over 2000-2019, the slope is 0.060 with t = 3.30. Split by period, it is positive in 2000-2012 and flat in 2013-2019 (slope 0.003, t = 0.20). The last half-hour moves only about 20 bps on average, which is small relative to costs (snippet) — [Temperance Capital](https://temperancecapital.substack.com/p/market-intraday-momentum-replicates)
- Dead Signals Lab, "Replication: Intraday Momentum, Eight Years Later" (Substack, ~Oct 2026). The net result is negative in all four cells tested. SPY and DIA show a slight intraday *reversal* rather than momentum. Only IWM showed gross momentum, and only before 2018 (snippet) — [Dead Signals Lab](https://deadsignalslab.substack.com/p/replication-intraday-momentum-eight)
- GitHub study, QQQ and SPY, 1-minute bars, Oct 2024 to Oct 2026, 501 sessions each. The 09:30-10:00 return vs the 15:30-16:00 return gives correlation 0.04 (QQQ) and 0.05 (SPY); the slope's confidence interval includes zero, and sign agreement is below 50%. The slope is positive in the exploration split, negative in validation and about zero in holdout; positive in 2025 and negative in 2026. The "last half-hour" trade (enter 15:30, exit at close) is negative in every split for both symbols, slightly negative even before costs. Verdict: "No tradeable edge found." — [hongfu12321/trading-backtest PR #3](https://github.com/hongfu12321/trading-backtest/pull/3)
- dev.to/FirmTape analysis of 1,085 SPX sessions, 2022-2026 (0DTE era). The unconditional rest-of-day to last-30-minute slope is near zero overall and alternates in sign by year. The exception is closes in dealer short gamma, where the slope adds +0.055 (t = +3.1) (snippet; informal and non-peer-reviewed) — [dev.to/firmtape](https://dev.to/firmtape/intraday-momentum-is-dead-in-the-0dte-era-we-measured-it-on-1085-spx-sessions-43g0)
- A QuantConnect replication of Gao et al. on ETFs reports that the pattern "produces lower returns over our testing period" (snippet) — [QuantConnect research 15348](https://www.quantconnect.com/research/15348/intraday-etf-momentum/)

**Baltussen, Da, Lammers & Martens (2021, JFE 142(1):377-403), "Hedging demand and market intraday momentum"**
- Covers more than 60 futures on equities, bonds, commodities and FX, 1974-2020. The return over the rest of the day predicts the last 30 minutes in every asset class, and the effect is "economically and statistically highly significant". It reverts over the following days — [Erasmus Pure](https://pure.eur.nl/en/publications/hedging-demand-and-market-intraday-momentum/); [RePEc](https://econpapers.repec.org/RePEc:eee:jfinec:v:142:y:2021:i:1:p:377-403)
- Mechanism: hedging short-gamma positions (option market makers; leveraged and inverse ETF rebalancing into the close) means trading in the direction of the day's move. In the S&P 500, momentum appears when the negative-gamma-exposure proxy is negative and grows stronger as it gets more negative. On positive-gamma days there is no significant intraday momentum (snippet of summaries) — [Alpha Architect summary](https://alphaarchitect.com/hot-topic-does-gamma-hedging-actually-affect-stock-prices/); [paper PDF (nd.edu)](https://www3.nd.edu/~zda/intramom.pdf)
- A follow-up, Baltussen, Da & Soebhag, "End-of-Day Reversal" (2024/2025), finds a *reversal* at the end of the day in individual stocks that liquidity or gamma effects do not explain. It is distinct from the market-level momentum — [EFMA 2024 PDF](http://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2024-Lisbon/papers/EndofDayReversal_withnames.pdf)

**Other-market replications**
- Elaut, Frömmel & Lampaert: in RUB-USD on the Moscow exchange (2005-2014 tick data), the first half-hour predicts the last half-hour. They attribute this to liquidity providers' aversion to overnight risk — [ScienceDirect (J. Financial Markets)](https://www.sciencedirect.com/science/article/abs/pii/S1386418116300313)
- Li, Sakkas & Urquhart, *Journal of Financial Markets* 57 (2021), 100619. Across 16 developed markets, intraday time-series momentum is "economically sizeable and statistically significant both in- and out-of-sample in most" markets. It is stronger when liquidity is low, volatility is high and information is dispersed (snippet) — [Reading repository](https://centaur.reading.ac.uk/95566)
- China: the effect is significant, with a reversal effect, and stronger on high-volume, high-volatility and high-attention days. I could not confirm which paper is "Zhang, Ma & Zhu" — [ResearchGate: Intraday time-series momentum: Evidence from China](https://www.researchgate.net/publication/337792455_Intraday_time-series_momentum_Evidence_from_China); [ScienceDirect: Intraday momentum and reversal in Chinese stock market](https://www.sciencedirect.com/science/article/abs/pii/S1544612318307414)
- Sweden: intraday momentum is weak and not robust across most stocks (thesis) — [DiVA thesis](https://www.diva-portal.org/smash/get/diva2:1878991/FULLTEXT01.pdf)

### Inferences
- Since about 2013 the plain Gao et al. signal looks dead in SPY. Three independent replications point the same way: flat in 2013-2019, slight reversal in recent data, null with correct sign only about half the time in 2024-2026. That is consistent with post-publication decay or a change of regime. None of these replications is peer-reviewed, but none of them contradicts the others.
- The economic size was always small. An effect with R² of about 1.6%, on a window that moves about 20 bps on average, leaves very little after even 1-2 bps of round-trip cost. The original 6.67%/yr comes from holding only the last 30 minutes. On a $200 account that is about $13/yr *gross*, before any decay.
- If any piece survives, the gamma-conditional version is the candidate (one informal source: t = 3.1 on short-gamma closes in 2022-2026). Dealer-gamma estimates are not free or easy to compute for a GitHub Actions bot, so this is a research lead, not a rule.

### Gaps
- I could not fetch the JFE paper's exact Sharpe ratio, out-of-sample R², or timing-strategy breakdown (long vs short, by subperiod). The 1.6% and 2.6% R² figures come from the 2014 draft.
- I could not retrieve Baltussen et al.'s exact coefficients or R² for the S&P 500, their subperiod results, or a timing-strategy Sharpe.
- No source found for "Komarov" intraday momentum.
- "Zhang, Ma & Zhu" could not be matched with certainty.
- There is no peer-reviewed post-2013 out-of-sample test of Gao et al. on SPY. All the post-publication evidence found is from blogs, GitHub or Substack.

---

## Q2. Zarattini, Aziz & Barbon (2024) "Beat the Market" (noise-area momentum): rules, reported results, costs, independent replications, shorting and leverage

### Takeaway
The paper reports 19.6%/yr, Sharpe 1.33, and about 1,985% total return net of commissions for 2007 to early 2024 in SPY. That result *requires* up to 4x intraday leverage and shorting. Independent code replications reproduce the in-sample numbers closely (Sharpe about 1.1-1.34). Out of sample since May 2024, Sharpe falls to about 0.39 (4.8%/yr, below SPY buy-and-hold), and recent Sharpe is about 0 in another replication. One test found the short side was never a real edge on Nasdaq. Break-even extra slippage is only about 2 bps. Unlevered and long-only in a cash account, the expected return is a small fraction of the headline.

### Cited Findings
**Paper identity and reported results (author-reported, in-sample)**
- SSRN 4824172; Swiss Finance Institute Research Paper 24-97 (May 2024); Concretum Research, Peak Capital Trading and Bear Bull Traders — [SFI](https://www.sfi.ch/en/publications/n-24-97-beat-the-market-an-effective-intraday-momentum-strategy-for-s-p500-etf-spy); [SSRN](https://ssrn.com/abstract=4824172)
- Reports 1,985% total return net of costs, 19.6% annualized and Sharpe 1.33, May 2007 to April 2024 (snippet) — [Concretum Group page](https://concretumgroup.com/beat-the-market-an-effective-intraday-momentum-strategy-for-sp500-etf-spy/); [Delgado SSRN abstract restating the paper's figures](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7323419)
- Paper figures as tabulated by an independent replicator: annualized return 19.6%, volatility 14.3%, Sharpe 1.33, hit ratio 43%, max drawdown 25% — [PazSheimy/spy-intraday-momentum-oos](https://github.com/PazSheimy/spy-intraday-momentum-oos)
- Costs assumed: commission of $0.0035/share (Interactive Brokers) plus slippage of $0.001/share — [svettelnova/intraday-momentum-spy](https://github.com/svettelnova/intraday-momentum-spy); [PazSheimy repo](https://github.com/PazSheimy/spy-intraday-momentum-oos)

**Exact rules (as implemented by replicators and summarized by CXO)**
- Noise band: σ(t,T) is the average absolute move from the open at time of day T over the previous 14 days. The upper band is max(Open_t, Close_{t-1}) × (1 + σ) and the lower band is min(Open_t, Close_{t-1}) × (1 − σ). The max/min with the prior close adjusts for overnight gaps. The volatility multiplier is 1 — [svettelnova repo](https://github.com/svettelnova/intraday-momentum-spy)
- Entry: go long if price is above the upper band, short if below the lower band. Signals are checked only at HH:00 and HH:30, from 10:00 to 15:30. All positions close at 16:00; nothing is held overnight — [svettelnova repo](https://github.com/svettelnova/intraday-momentum-spy)
- Trailing stop: for longs, the higher of the upper boundary and the intraday VWAP; for shorts, the lower of the lower boundary and VWAP. One replicator implements entry plus stop as one combined check at half-hour marks (close beyond both band and VWAP) and calls it equivalent — [CXO Advisory (snippet)](https://www.cxoadvisory.com/momentum-investing/complex-intraday-time-series-momentum-strategy-applied-to-spy/); [PazSheimy repo](https://github.com/PazSheimy/spy-intraday-momentum-oos)
- Sizing: shares = floor(AUM × L / Open), with L = min(4, 0.02 / σ_SPY), where σ_SPY is the standard deviation of the last 14 daily returns. That is a 2% daily volatility target with a 4x leverage cap — [svettelnova repo](https://github.com/svettelnova/intraday-momentum-spy); [CXO (snippet)](https://www.cxoadvisory.com/momentum-investing/complex-intraday-time-series-momentum-strategy-applied-to-spy/)

**Independent replications and out-of-sample results**
- Paz Serpa (GitHub and SSRN 7290621):
  - In-sample replication 2015-2024: 19.8%/yr, volatility 14.3%, Sharpe 1.34, max drawdown 26.2%.
  - Out of sample, May 2024 to March 2026: 4.8%/yr, volatility 14.7%, Sharpe 0.39, hit ratio 45%, max drawdown 18.5%. It underperformed SPY buy-and-hold, and the Sharpe decline is reported as significant (p < 0.001).
  - Uses the same costs ($0.0035 + $0.001/share), 2% volatility target, 4x cap and 30-minute checks.
  - [PazSheimy repo](https://github.com/PazSheimy/spy-intraday-momentum-oos); [SSRN 7290621](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7290621)
- Brusco (GitHub, SPY July 2020 to July 2026 on the free Alpaca IEX feed; ES May 2024 to July 2026):
  - Sharpe 1.11, alpha +16.7%/yr (t = 2.85), beta ≈ 0, win rate 41%, payoff ratio 1.69, about +2.6 bps per trade, costs about 0.4 bps per round trip.
  - Sharpe 1.4-2.0 each year in 2020-2024. In 2022 the strategy made +25.8% while SPY fell 19.5%.
  - "Recent Sharpe roughly 0 on both instruments." The author says the decline is "not the feed, not the costs".
  - Quarterly walk-forward parameter re-selection gave Sharpe 0.57, against 0.92 for the fixed configuration.
  - Verdict: "Not allocable today, not dismissible as dead either."
  - [giovannibrusco/zarattini-2024-momentum-spy](https://github.com/giovannibrusco/zarattini-2024-momentum-spy)
- Delgado (SSRN 7323419, Aug 2026): independent replication and statistical audit on about 2.6M one-minute SPY bars, Jan 2000 to Aug 2026, including Probability of Backtest Overfitting and Deflated Sharpe Ratio tests. The findings could not be retrieved — [SSRN 7323419](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7323419)
- Francesco-Nicolo, replicating the blackswan-quants band/VWAP variants on SPY on QuantConnect over 8 years:
  - Best variant: +271% at 0 bps extra slippage, Sharpe 1.075, max drawdown 9%, beta −0.05.
  - Break-even extra slippage *beyond the quoted spread* is about 2.1-2.5 bps; the 271% falls to zero at 2.2 bps.
  - About 3,388 orders over 8 years (≈ 420/yr).
  - Leveraged buy-and-hold made 350% with a 40% drawdown.
  - [francesco-nicolo/intraday-momentum-replication](https://github.com/francesco-nicolo/intraday-momentum-replication)
- EdgeLab (vendor blog), Nasdaq-100. The long side held up out of sample (Sharpe 0.68 on a business-day basis, 1.18 per trading day). The short side was negative in-sample (short-only Sharpe −0.21) and profitable only out of sample, which the author calls "regime luck, not an edge" (snippet) — [EdgeLab](https://edgelabtrading.com/blog/zarattini-intraday-momentum-nasdaq/)
- Search summaries mention further replications: one reporting the strategy "loses in all four instruments and in every sub-window" net of costs, and one (VigorTas, NQ/ES futures, 16 years) finding NQ profitable after costs but ES flat. I could not verify either: the VigorTas repo returned 404 — [VigorTas (404)](https://github.com/VigorTas/beat-the-market-replication)
- A TradingView reimplementation author: "results are good, but not as good as they are stated in the paper" (snippet) — [TradingView script](https://br.tradingview.com/script/gJeM3LZ5-Out-of-the-Noise-Intraday-Strategy-with-VWAP-YuL)
- A Substack review notes the hit ratio is about 43%, low for a strategy with such a high Sharpe (snippet) — [QuantMacro review](https://quantmacro.substack.com/p/paper-review-an-effective-intraday)
- Maróy (2025, SSRN 5095349) claims further gains from parameter optimization and alternative exits. Brusco's 27-variant grid found the paper's original configuration was the in-sample winner and promoted no variant, and reports the follow-up's claimed Sharpe as above 3 — [Bear Bull Traders forum](https://forums.bearbulltraders.com/topic/4002-improvements-to-intraday-momentum-strategies-using-parameter-optimization-and-different-exit-strategies/); [Brusco repo](https://github.com/giovannibrusco/zarattini-2024-momentum-spy)

### Inferences
- **Leverage is integral.** With L = min(4, 0.02/σ) and SPY daily volatility often around 1% or less, the strategy usually runs at 2-4x intraday. A no-margin cash account is capped at 1x, so returns and volatility scale down roughly in proportion. My rough estimate: an unlevered in-sample return of perhaps 5-10%/yr. This is an inference; I found no source with the paper's average leverage or unlevered results. Out of sample, 4.8%/yr *levered* (Paz) implies low single digits or less unlevered.
- **Shorting.** The strategy is long/short. A cash account cannot short, but buying SH (1x inverse S&P) or PSQ (1x inverse Nasdaq-100) is a mechanical substitute for an intraday short. Daily-reset decay does not matter within a single day. Not verified here: SH and PSQ have wider spreads in bps than SPY and QQQ, and lower liquidity. The EdgeLab finding that the short side carried no in-sample edge argues for a long-only version anyway, which simplifies things.
- **Long-only.** Long-only means about half the trades, at 1x exposure. The long leg's out-of-sample Sharpe of about 0.7 (Nasdaq, vendor source) is the most optimistic figure for a cash-account version.
- **What $200 could plausibly earn.** At 1x, long-only, with post-2024 out-of-sample performance, a realistic expectation is roughly 0-8%/yr, about $0-16 a year on $200. Getting to $1,000 (+400%) from this strategy alone is not plausible on any reasonable horizon.
- **Trades and time in market.** Roughly one entry per day, with several stop-outs and re-entries on some days (≈ 420 orders/yr in one variant). The bot is never in the market overnight and often flat intraday.

### Gaps
- I could not access the paper's own tables: time-in-market, long vs short contribution, unlevered results, average leverage, or results by trade frequency (1-minute vs 30-minute).
- I could not retrieve Delgado's audit results or the Larry Swedroe write-up.
- I found no QuantConnect or TradingView replication with full net-of-cost statistics.
- I found no data on SH and PSQ spreads, slippage or expense ratios.

---

## Q3. Other Zarattini/Aziz papers: opening range breakout (ORB) on QQQ/TQQQ and on "stocks in play"

### Takeaway
The 5-minute QQQ ORB ("Can Day Trading Really Be Profitable?", 2023) reports a Sharpe of about 1.1-1.2 and large returns, but these rely on up to 4x leverage (or TQQQ) and zero slippage. An independent replication reproduces it gross. Its Sharpe collapses to 0.23 with 2¢/share entry slippage, and it breaks even at about 2.2¢/share. A separate out-of-sample test (2023-2026) shows a small positive edge in R-multiples that is statistically inconclusive, with 2026 negative. The "stocks in play" ORB paper (Sharpe 2.81) relies on picking individual stocks, not SPY/QQQ.

### Cited Findings
- Zarattini & Aziz, SSRN 4416622, "Can Day Trading Really Be Profitable?", QQQ, Jan 2016 to Feb 2023.
  - Rule: if the first 5-minute bar is up (down), buy (sell) at the start of the second bar. The stop is at the other end of the first bar, the target is 10× the risk, and the position exits at the close otherwise.
  - A secondary source reports 676% on QQQ vs 1,484% on TQQQ from the same signals (snippet).
  - [CXO Advisory](https://www.cxoadvisory.com/technical-trading/day-trading-with-an-opening-range-breakout-strategy/); [QuantInsti](https://www.quantinsti.com/articles/opening-range-breakout-strategy/)
- Paper figures as cited by the Brusco replication: $25k → $192,806, 1,795 trades, Sharpe 1.12, max drawdown 22%, CAGR about 31-33%. Sizing is min(1% equity risk / R, 4 × equity / price), which reflects the 4x FINRA day-trading cap — [giovannibrusco/zarattini-2023-orb-qqq](https://github.com/giovannibrusco/zarattini-2023-orb-qqq)
- Brusco replication (QQQ 5-minute, 2016 to Feb 2023):
  - With zero slippage: Sharpe 1.06, CAGR 30.4%, max drawdown 22.4%, t-stat 1.79, $0.070/share.
  - With $0.02/share entry slippage and $0.04/share on stops: Sharpe 0.23, CAGR 2.7%, max drawdown 43.9%. Break-even is at about 2.2¢/share, about two QQQ spreads.
  - About 75% of trades exit at the −1R stop, about 22% at the close, and only 2-3% hit the 10R target.
  - 2022 provides 38% of the replication's PnL.
  - QQQ buy-and-hold over the same period: Sharpe 0.72, CAGR 15.3%.
  - [Brusco ORB repo](https://github.com/giovannibrusco/zarattini-2023-orb-qqq)
- Mericck (GitHub), QQQ ORB, out of sample Jan 2023 to Sep 2026:
  - Before costs: 906 trades, win rate 42.6%, +0.074R per trade, profit factor 1.15.
  - Annual R: 2023 +20.8, 2024 +18.9, 2025 +35.3, 2026 YTD −7.7.
  - At $0.04/share round-trip cost: +0.054R per trade, but the 95% bootstrap confidence interval includes zero. No Sharpe is reported.
  - [mericck/QQQ-Opening-Range-Breakout](https://github.com/mericck/QQQ-Opening-Range-Breakout)
- Zarattini, Barbon & Aziz, SSRN 4729284, "A Profitable Day Trading Strategy For The U.S. Equity Market". A top-20 "Stocks in Play" ORB portfolio reports more than 1,600% total net and Sharpe 2.81. A summary says a plain ORB was weak and that selecting unusually active stocks did most of the work (snippet) — [SSRN 4729284](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4729284); [danfin.net summary](https://danfin.net/opening-range-breakout-research)

### Inferences
- The ORB entry must fill at about 09:35:00, right after the first 5-minute bar. A bot polling every 5 minutes from GitHub Actions, whose scheduled runs can start several minutes late, will often enter minutes after the breakout. Given the 2.2¢ break-even, that lateness alone could remove the edge. This is the worst fit of the strategies here for the user's infrastructure.
- The headline returns come from 4x leverage or TQQQ. A no-margin $200 account at 1x QQQ would see roughly a quarter of the paper's volatility and return, before any slippage.

### Gaps
- I could not access the ORB paper's own QQQ-only Sharpe, its TQQQ Sharpe (a snippet shows "Sharpe Ratio was 1.18", but which series it refers to is unclear), or its commission assumptions.
- I found no out-of-sample Sharpe or CAGR for the QQQ ORB after Feb 2023.

---

## Q4. Trading costs, delayed or 5-minute-polled data, late entry

### Takeaway
SPY and QQQ quoted spreads are about 1¢, well under 1 bp. But every intraday momentum strategy reviewed has a thin per-trade edge, about +2-3 bps for noise-area momentum, so it breaks even at only about 2 bps of extra slippage, or about 2¢/share for ORB. A 1-minute entry delay alone cost about 0.4-0.7 bps per trade in one test. Alpaca's free plan gives real-time IEX data, and only the latest 15 minutes of SIP data are blocked. Data latency is therefore less of a problem than GitHub Actions scheduling jitter.

### Cited Findings
- QQQ's bid-ask spread is about 1¢. The ORB break-even is about 2.2¢/share of entry slippage — [Brusco ORB repo](https://github.com/giovannibrusco/zarattini-2023-orb-qqq)
- Noise-area momentum variants on SPY break even at about 2.1-2.5 bps of slippage beyond the quoted spread. The best variant's 271% falls to zero at 2.2 bps, and returns at +0.25 / +0.5 bps fall to about 219% / 175% — [francesco-nicolo repo](https://github.com/francesco-nicolo/intraday-momentum-replication)
- Average return per trade is about +2.6 bps (SPY noise-area replication), with costs modelled at about 0.4 bps per round trip — [Brusco SPY repo](https://github.com/giovannibrusco/zarattini-2024-momentum-spy)
- A one-minute entry delay (10:01 instead of 10:00) reduced the mean return by about 0.4-0.7 bps per trade on SPY and QQQ, using a 2 bps round-trip base-cost assumption — [hongfu12321 PR #3](https://github.com/hongfu12321/trading-backtest/pull/3)
- One replication of the 30-minute noise-area check fills at the close of the 30-minute bar ending at the check time. Another used the free Alpaca IEX feed (about 3% of consolidated volume) for SPY and still matched ES results (correlation 0.97) — [svettelnova repo](https://github.com/svettelnova/intraday-momentum-spy); [Brusco SPY repo](https://github.com/giovannibrusco/zarattini-2024-momentum-spy)
- Alpaca's free Basic plan has real-time IEX-only equities data. Historical data is unrestricted, but the latest 15 minutes of SIP data cannot be queried, and the end parameter must be at least 15 minutes old. Real-time SIP requires Algo Trader Plus (listed at $99/month) — [Alpaca Market Data docs](https://docs.alpaca.markets/us/docs/about-market-data-api); [Alpaca Market Data FAQ](https://docs.alpaca.markets/docs/market-data-faq)

### Inferences
- If the bot uses 15-minute-delayed SIP bars instead of real-time IEX, a half-hour check would act on prices 15 minutes old. That is far worse than the 1-minute delay measured above and would likely erase a 2-3 bps edge. The bot should use the real-time IEX feed or latest quotes.
- GitHub Actions cron is best-effort: runs are delayed, sometimes by many minutes, and occasionally skipped (general knowledge, not sourced here). For the noise-area strategy, which acts only at HH:00 and HH:30 and closes at 16:00, a missed 15:30 or close-out run is a real risk. The bot needs a "flat by close" safeguard, such as a market-on-close order or a late-day close-out order placed early.
- On a $200 account, fractional SPY orders lose nothing to per-share rounding. Alpaca charges no commissions, so the paper's $0.0035/share commission does not apply. Spread plus slippage, and timing, become the whole cost.
- Inverse ETFs (SH, PSQ) are likely to cost more per trade in bps than SPY and QQQ. A long-only variant avoids that.

### Gaps
- I found no direct measurement of how Zarattini noise-area performance degrades with 5-, 10- or 15-minute execution delay.
- I found no sourced SH or PSQ spread data.
- I found no published measurement of GitHub Actions scheduling latency.

---

## Q5. Typical annual return, max drawdown, Sharpe, trades per year, time in market (summary table)

### Takeaway
The headline numbers (19.6%/yr, Sharpe 1.33; ORB CAGR about 30%) are in-sample, levered up to 4x, and come from the authors. Independent out-of-sample figures are much lower: Sharpe 0-0.4 for SPY noise-area since 2024, about 0.7 for the long-only Nasdaq leg, and an inconclusive ORB edge. The plain Gao et al. signal has no tradable edge in SPY since about 2013.

### Cited Findings
| Strategy / source | Period | Ann. return | Sharpe | Max DD | Notes |
|---|---|---|---|---|---|
| Gao et al. timing (author) | 1993-2013 | 6.67% | n/a found | n/a | Last 30 min only, long/short, gross — [mql5 mirror](https://c.mql5.com/forextsd/forum/173/intraday_momentum_-_the_first_half-hour_return_predicts_the_last_half-hour_return.pdf) |
| Gao et al. signal on SPY (Temperance) | 2013-2019 | — | — | — | Slope 0.003, t = 0.20 (flat) — [Temperance](https://temperancecapital.substack.com/p/market-intraday-momentum-replicates) |
| Gao et al. on SPY/QQQ (hongfu12321) | Oct 2024-Oct 2026 | negative | — | — | No edge, even gross — [PR #3](https://github.com/hongfu12321/trading-backtest/pull/3) |
| Beat the Market (author) | 2007-2024 | 19.6% | 1.33 | 25% | ≤4x leverage, long/short, net of $0.0035+$0.001/sh — [PazSheimy](https://github.com/PazSheimy/spy-intraday-momentum-oos) |
| Beat the Market OOS (Paz Serpa) | May 2024-Mar 2026 | 4.8% | 0.39 | 18.5% | Trails SPY buy-and-hold — [PazSheimy](https://github.com/PazSheimy/spy-intraday-momentum-oos) |
| Beat the Market (Brusco) | 2020-2026 | alpha 16.7% | 1.11 (recent ≈ 0) | n/a | Beta ≈ 0; +25.8% in 2022 — [Brusco](https://github.com/giovannibrusco/zarattini-2024-momentum-spy) |
| Noise-band variant (francesco-nicolo) | 8 yrs | 271% total | 1.075 | 9% | ≈ 420 orders/yr; break-even at +2.2 bps — [repo](https://github.com/francesco-nicolo/intraday-momentum-replication) |
| Noise-band long-only Nasdaq (EdgeLab) | OOS | n/a | 0.68 (bus.-day) | n/a | Short side no edge — [EdgeLab](https://edgelabtrading.com/blog/zarattini-intraday-momentum-nasdaq/) |
| QQQ 5-min ORB (paper, via Brusco) | 2016-Feb 2023 | 31-33% CAGR | 1.12 | 22% | 1,795 trades (≈ 250/yr), ≤4x — [Brusco ORB](https://github.com/giovannibrusco/zarattini-2023-orb-qqq) |
| QQQ ORB with 2¢/4¢ slippage (Brusco) | 2016-Feb 2023 | 2.7% CAGR | 0.23 | 43.9% | — [Brusco ORB](https://github.com/giovannibrusco/zarattini-2023-orb-qqq) |
| QQQ ORB OOS (mericck) | 2023-Sep 2026 | +0.054R/trade net at 4¢ | n/a | 30.8R | Confidence interval includes 0; 2026 negative — [mericck](https://github.com/mericck/QQQ-Opening-Range-Breakout) |

### Inferences
- **Trades.** Expect about 250 trades a year (one per day) for ORB, and 250-420 orders a year for noise-area strategies.
- **Time in market.** Intraday only. Never overnight; for noise-area strategies, often flat for much of the session.
- **Return at the user's scale.** The realistic 1x, long-only, out-of-sample expectation is low single-digit percent a year, with a material chance of zero or negative. On $200 that is single-digit dollars a year. None of this evidence supports growing $200 to $1,000 through these strategies. Their honest appeal is low beta and crisis convexity (for example 2022), not fast growth.
- **Minimal noise-area bot rules a cash account could follow (long-only).**
  1. Compute σ(T) as the 14-day average |close(T)/open − 1| at each half-hour mark T.
  2. At 10:00, 10:30, …, 15:30 ET, if the last price is above max(open, prior close) × (1 + σ(T)) and above VWAP, hold SPY at 1x cash (optionally scaled by min(1, 0.02/σ_daily14), since the cash account caps it at 1x).
  3. Exit at the next check where the price is below max(upper band, VWAP).
  4. Always be flat by 15:55-16:00.
  5. Optional: buy SH instead of shorting on lower-band breaks. The evidence suggests skipping this.
  These rules are assembled from the replications above. Treat them as a hypothesis to paper-trade, not a validated edge.

### Gaps
- The paper's own time-in-market and trade-count statistics were not accessible.
- No independent source reports results for a fully unlevered, long-only, SPY-only variant over 2024-2026.
- Cash-account settlement (T+1) and good-faith-violation rules for multiple same-day round trips were not researched here. They could matter for re-entries after stop-outs and should be checked with Alpaca's documentation.
