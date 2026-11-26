# ETF Trend Following, Leveraged-ETF Trend Strategies, and the Realistic Odds of Turning $200 into $1,000

Context: $200 US cash account at Alpaca (commission-free, no margin, fractional shares, can buy 3x ETFs such as TQQQ/UPRO/SOXL and 1x inverse ETFs, automated bot). Goal: $200 -> $1,000 (5x).

**About the "own backtest" citations.** Many numbers below come from a backtest I ran in this session on Yahoo Finance daily data (adjusted closes) downloaded on 2026-11-26, with data through 2026-11-25. The script and full output are saved next to this file:
- `research_notes/Small account trading strategy evidence/backtest_code/trend_leverage_backtest.py`
- `research_notes/Small account trading strategy evidence/backtest_code/trend_leverage_extra.py`
- `research_notes/Small account trading strategy evidence/backtest_code/trend_leverage_backtest_output.txt`

Method:
- **Data.** Real ETF prices are used where the ETF exists. The "NDX TR proxy" is the ^NDX price index before 10 Mar 1999 and QQQ adjusted close after. The "S&P TR proxy" is ^SP500TR from 1988, and ^GSPC price plus an assumed 3.5%/yr dividend before that.
- **Simulated 3x funds.** Daily return = 3 x underlying − 2 x (13-week T-bill + 0.5%) − 0.95%/yr expense ratio.
- **Signal and trading.** The signal is the close versus the 200-day SMA. Trades execute at the next day's close (one-day lag). Money earns T-bills while out of the market.
- **Not modelled:** taxes, bid/ask spread, slippage.
- **Simulator check.** The simulator tracks the real funds closely. Over Mar 2010 to Nov 2026, simulated 3x NDX returned 37.2% CAGR with a −81.5% max drawdown; real TQQQ returned 37.1% with −81.7%. Over Jul 2009 to Nov 2026, simulated 3x S&P returned 30.9% with −76.7%; real UPRO returned 30.5% with −76.8%. Source: [Own backtest on Yahoo Finance data](https://query1.finance.yahoo.com/v8/finance/chart/TQQQ).

Pre-2010 leveraged results are simulations. Results from 2010 onward use real fund prices. Everything from 2010 to 2025 sits inside one of the strongest Nasdaq bull markets on record, so treat it as a favourable, effectively in-sample window. None of these rules is new: Faber's 10-month and 200-day SMA rules were public by 2007, and Gayed and Bilello published in 2016. In that sense 2007 onward (Faber) and 2016 onward (Gayed and Bilello) are post-publication periods. But the TQQQ-plus-SMA combination itself became popular on retail forums because of how well it did in 2010-2021, so selection bias is high.

---

## 1. Time-series momentum / trend following on ETFs: what the evidence says, in-sample vs post-publication

### Takeaway
Trend following has strong long-run academic support, from 58 futures markets and more than a century of data. Its main benefit is cutting deep drawdowns, not raising returns. For a single equity index with a 200-day or 10-month SMA, the long-run return is roughly equal to buy-and-hold (S&P 1928-2026: 9.8% vs 9.4% CAGR), with about half the maximum drawdown. After publication it has mostly lagged buy-and-hold in strong bull markets, mainly through whipsaws. Dual momentum (GEM) has done noticeably worse out of sample than in its original backtest.

### Cited Findings
**Moskowitz, Ooi & Pedersen (2012), "Time Series Momentum"**
- Published in the *Journal of Financial Economics* 104(2), 228-250. It found significant time-series momentum in equity index, currency, commodity and bond futures, across each of 58 liquid instruments. — [EconPapers/RePEc](https://econpapers.repec.org/RePEc:eee:jfinec:v:104:y:2012:i:2:p:228-250); [SSRN](https://papers.ssrn.com/abstract=2089463)
- Returns persist for 1-12 months and then partly reverse over longer horizons. An instrument's past 12-month excess return predicts its future return. — [EconPapers/RePEc](https://econpapers.repec.org/RePEc:eee:jfinec:v:104:y:2012:i:2:p:228-250)
- A diversified time-series momentum portfolio "delivers substantial abnormal returns with little exposure to standard asset pricing factors and performs best during extreme markets". — [EconPapers/RePEc](https://econpapers.repec.org/RePEc:eee:jfinec:v:104:y:2012:i:2:p:228-250)
- The original data cover January 1985 to December 2009. AQR keeps publishing a monthly updated TSMOM factor series, which can be used to check post-publication results. — [AQR dataset page](https://www.aqr.com/Insights/Datasets/Time-Series-Momentum-Original-Paper-Data); [AQR TSMOM factors monthly](https://www.aqr.com/Insights/Datasets/Time-Series-Momentum-Factors-Monthly)
- The strategy is diversified, long/short and volatility-targeted, run on futures. It is not a single-ETF long/cash rule, and it cannot be reproduced in a $200 cash account, which has no futures and no shorting. — inference from the paper design above.

**Hurst, Ooi & Pedersen, "A Century of Evidence on Trend-Following Investing"**
- Published in the *Journal of Portfolio Management*, Fall 2017. The authors build a time-series momentum strategy back to 1880 and find it "consistently profitable" over the following 110+ years. The paper also discusses higher asset levels in the strategy and higher cross-market correlations after the credit crisis. — [AQR](https://www.aqr.com/Insights/Research/Journal-Article/A-Century-of-Evidence-on-Trend-Following-Investing); [PDF copy](https://fairmodel.econ.yale.edu/ec439/hurst.pdf)
- AQR's "You Can't Always Trend When You Want" says trend strategies suffered a significant drawdown and delivered lower returns in the 2010s than in their multi-decade history. It cites the SG Trend Index and puts the weakness down mainly to smaller-than-usual market moves. — [AQR](https://www.aqr.com/Insights/Research/Journal-Article/You-Cant-Always-Trend-When-You-Want)

**Faber (2007), "A Quantitative Approach to Tactical Asset Allocation" (10-month SMA)**
- The rule: hold an asset when its monthly close is above its 10-month SMA, otherwise hold cash. It was tested in-sample on US stocks from 1900, then out of sample on 20 other markets. — [quantstrat stratFaber documentation](https://rdrr.io/rforge/quantstrat/man/stratFaber.html); [Scribd copy of SSRN 962461](https://www.scribd.com/doc/116881446/SSRN-id962461)
- Summaries report that after transaction costs the timing rule fell short of buy-and-hold on absolute return but gave better risk-adjusted returns. — [quantstrat stratFaber documentation](https://rdrr.io/rforge/quantstrat/man/stratFaber.html)
- A February 2013 update added 2008-2012 data, and a 2018 JPM paper revisited the model "10 years later". Per Swedroe's summary, the out-of-sample period was "remarkably consistent", including 2008. The model's goal is roughly equity-like returns with much lower volatility. — [Swedroe, ETF.com](https://www.etf.com/sections/index-investor-corner/swedroe-why-financial-trends-persist) (summary as seen in search results; the page could not be fetched from this environment)
- An independent replication (Concretum Group) ran Faber's 5-asset, 200-day SMA GTAA unchanged through March 2025 and found returns below the in-sample period. — [Concretum Group](https://concretumgroup.substack.com/p/global-tactical-asset-allocation) (search-snippet level only; exact figures not retrieved)

**Own backtest of the 200-day SMA on single equity indices (1x)**
- S&P 500, 1928-2026: 1x buy-and-hold returned 9.4% CAGR with a −84.8% max drawdown. The 1x S&P 200-day SMA timing rule returned 9.8% CAGR with a −50.6% max drawdown and about 6.0 position switches per year. — [Own backtest on Yahoo data](https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC)
- Nasdaq-100, 1985-2026: 1x buy-and-hold returned 14.6% CAGR with −83.0%. 1x NDX with the 200-day SMA returned 12.2% CAGR with −58.2% and 6.8 switches per year. The SMA lowered the CAGR. — [Own backtest](https://query1.finance.yahoo.com/v8/finance/chart/%5ENDX)
- QQQ with its 200-day SMA, Feb 2010 to Dec 2025 (real ETF): 13.8% CAGR with −23.3% max drawdown, against QQQ buy-and-hold at 19.2% with −35.1%. In this bull market the filter gave up about 5.4 points of CAGR a year. — [Own backtest](https://query1.finance.yahoo.com/v8/finance/chart/QQQ)

**Antonacci dual momentum / GEM**
- Resolve Asset Management replicated GEM with out-of-sample periods of 1950-1973 and 2012-2018; the original in-sample period was 1974-2011. They found attractive absolute and risk-adjusted performance overall, but the "Original" specification "regressed to the median out of sample". They attributed its in-sample edge over other specifications to "random luck". — [Advisor Perspectives, "Global Equity Momentum: A Craftsman's Perspective" (2019)](https://files.advisorperspectives.com/articles/2019/05/06/global-equity-momentum-a-craftsmans-perspective)
- Newfound's examples:
  - In Q4 2018, dual momentum stayed mostly in equities and only signalled defensive in early January 2019, when the S&P 500 was already down 14%. — [Newfound Research blog (GEM tag)](https://blog.thinknewfound.com/tag/gem/)
  - In 2020 the strategy moved into bonds just as equities were recovering and stayed there. — [Freefloat Substack](https://freefloat.substack.com/p/global-equities-momentum)
- Price Action Lab says dual momentum's annualized return after 2018 fell to about one third of its pre-publication level. It points to a regime change, including stock-bond correlation turning positive after 2020. — [Price Action Lab](https://www.priceactionlab.com/Blog/?p=68274) (a blog; methodology not checked)
- Antonacci's own writing says GEM's long-run edge comes from avoiding bear-market losses. This is promotional and comes from the author. — [Seeking Alpha, "Why Does Dual Momentum Outperform?"](https://seekingalpha.com/article/3768586-why-does-dual-momentum-outperform)

### Inferences
- For one equity ETF, a 200-day SMA is a drawdown-control tool, not a return enhancer. Over 98 years of S&P data it added about 0.4 points of CAGR and halved the worst drawdown. In the 2010-2025 bull market it cost about 5 points a year on QQQ.
- In-sample vs post-publication. Faber's in-sample period ends in 2005 and the rule held up reasonably well afterwards, mainly by sidestepping 2008, per the secondary sources. GEM (published 2014) has clearly deteriorated out of sample. TSMOM on diversified futures had a weak 2010s per AQR.
- Trade frequency of the 200-day rule on daily data: about 5-7 position changes a year with no band, and about 1.5 a year with a ±3% band (own backtest). That is low turnover, well suited to a bot.

### Gaps
- No verified year-by-year GEM returns for 2014-2025 or Faber GTAA returns for 2007-2025 were retrieved. Antonacci's site and the Concretum/ETF.com pages could not be fetched: hosts concretumgroup.substack.com, www.etf.com and www.cxoadvisory.com were not reachable from this session.
- Faber's original in-sample CAGR, volatility and drawdown tables, and Hurst-Ooi-Pedersen's headline return and volatility numbers, were not checked against the primary PDFs in this session, so they are not quoted.
- SG Trend Index returns for 2022-2025 were not retrieved. 2022 is widely reported as a strong trend year, but that was not verified here.

---

## 2. Leveraged ETFs: volatility decay, trend filters, and risk of ruin

### Takeaway
3x daily-reset ETFs compound well in smooth bull markets but are destroyed by long bear markets and choppy markets. A simulated 3x Nasdaq-100 lost 99.95% from March 2000 to October 2002 and, as of November 2026, was still at about 22% of its March 2000 peak. A 200-day SMA filter does not prevent catastrophic drawdowns. The simulated 3x NDX with the SMA still fell 96% in 2000-2003, and the simulated 3x S&P with the SMA fell 93.5% in 1929-1935. Its long-run edge over buy-and-hold comes from avoiding the worst extended crashes. From 2010 to 2025, TQQQ with a QQQ 200-day filter returned about 32% a year with a −56% drawdown, below buy-and-hold TQQQ's 42%. That result depends heavily on the bull market.

### Cited Findings
**Volatility decay, regulatory warnings and real-fund drawdowns**
- The SEC/FINRA joint alert (2009, still the reference) says leveraged and inverse ETFs reset daily and that "performance over a period longer than one day can differ significantly from their stated daily performance objectives", with possible "significant and sudden losses". — [Investor.gov SEC/FINRA alert](https://www.investor.gov/news-alerts/investor-alerts/sec-finra-investor-alert-leveraged-inverse-etfs); [FINRA news release 2009](https://finra.org/media-center/news-releases/2009/finra-sec-warn-retail-investors-about-investing-leveraged-or-inverse)
- FINRA Regulatory Notice 09-31 says daily-reset leveraged and inverse ETFs are typically unsuitable for retail investors who plan to hold them longer than one session. — [FINRA RN 09-31](https://www.finra.org/industry/notices/09-31); [FINRA non-traditional ETF FAQ](https://www.finra.org/rules-guidance/key-topics/etf/non-traditional-etf-faq)
- Real-world decay in 2026, a choppy year (own backtest, real prices, year to 2026-11-25):
  - QQQ +3.5%, TQQQ −13.6%. TQQQ's 2026 max drawdown was −52.6%, against −19.9% for QQQ.
  - Underlying flat-to-up while the 3x fund is down is classic volatility decay.
  - Source: [Own backtest](https://query1.finance.yahoo.com/v8/finance/chart/TQQQ)
- Real 3x fund drawdowns (own backtest):

| Fund | Period | Drawdown |
|---|---|---|
| TQQQ | Aug-Dec 2018 | −58% |
| TQQQ | Feb-Mar 2020 | −70% |
| TQQQ | Nov 2021 to Dec 2022 | −81.7% |
| UPRO | to Mar 2020 trough | −76.8% |
| SOXL | to Oct 2022 trough | −90.5% |

  Source: [Own backtest](https://query1.finance.yahoo.com/v8/finance/chart/SOXL). Other trackers also put TQQQ's max drawdown at about −81.7% (Dec 28, 2022). — [YCharts TQQQ max drawdown](https://ycharts.com/companies/TQQQ/max_drawdown_5y)

**Gayed & Bilello (2016), "Leverage for the Long Run" (Dow Award winner)**
- Method: S&P 500 total return with leverage (1.25x, 2x, 3x, rebalanced daily, with an assumed 1%/yr cost of leverage) when the index is above its 200-day SMA, and T-bills when below. — [QuantConnect write-up](https://www.quantconnect.com/research/15351/leveraged-etfs-with-systematic-risk-management/); [CXO Advisory summary](https://www.cxoadvisory.com/volatility-effects/leveraging-the-u-s-stock-market-based-on-sma-rules/) (search-snippet level; page not fetchable here)
- Per CXO's summary of the October 1928 to October 2015 sample:
  - 2x SMA timing had a gross Sharpe of 0.51 and a −78% max drawdown.
  - Unleveraged SMA timing had a Sharpe of 0.60 and a −50% drawdown.
  - Leverage increased cumulative return but lowered risk-adjusted return.
  - The SMA rule beat buy-and-hold in only about 49% of rolling 3-year periods.
  - Over much of the sample, trading frictions and leverage costs would have hurt.
  - Source: [CXO Advisory](https://www.cxoadvisory.com/volatility-effects/leveraging-the-u-s-stock-market-based-on-sma-rules/) (secondary; figures not checked against the paper)
- My replication broadly matches. Simulated 2x S&P with the 200-day SMA, 1928-2026: 13.4% CAGR, −79.3% max drawdown. 1x SMA: −50.6%. — [Own backtest](https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC)

**Own backtest: real TQQQ with a QQQ 200-day SMA (out = T-bills), Feb 2010 to Dec 2025**

| Strategy | CAGR | Max DD | Switches/yr | Growth |
|---|---|---|---|---|
| TQQQ + SMA, no band | 32.1% | −55.6% (trough Jun 2019) | 6.2 | x83 |
| TQQQ + SMA, ±3% band | 30.9% | −65.9% | 1.5 | — |
| TQQQ buy-and-hold | 41.8% | −81.7% | — | x255 |
| QQQ buy-and-hold | 19.2% | −35.1% | — | — |
| SPY buy-and-hold | 14.3% | −33.7% | — | — |
| UPRO + SPY 200-day SMA | 22.9% | −51.2% | — | — |
| UPRO buy-and-hold | 30.1% | −76.8% | — | — |

Source: [Own backtest](https://query1.finance.yahoo.com/v8/finance/chart/TQQQ)
- Through 2026-11-25: TQQQ + SMA 28.7% CAGR, TQQQ buy-and-hold 37.9%. — [Own backtest](https://query1.finance.yahoo.com/v8/finance/chart/TQQQ)
- Calendar-year returns of real TQQQ + SMA show the whipsaw cost (TQQQ buy-and-hold / QQQ in brackets):

| Year | TQQQ + SMA | TQQQ B&H | QQQ |
|---|---|---|---|
| 2011 | −33.8% | −8.0% | +3.5% |
| 2015 | −0.7% | +17.2% | — |
| 2016 | −6.2% | +11.4% | — |
| 2018 | −22.3% | −19.8% | — |
| 2019 | +52.7% | +133.8% | — |
| 2022 | −42.2% | −79.1% | −32.6% |
| 2023 | +113.8% | +198% | — |
| 2026 YTD | −17.4% | −13.6% | +3.5% |

  Source: [Own backtest](https://query1.finance.yahoo.com/v8/finance/chart/QQQ)
- Community backtests agree on the rough range:
  - TQQQ held when SPY is above its 200-day SMA (2010-2024): about 62% max drawdown, $10k to about $312k. — [r/LETFs mirror](https://libreddit.app.runonflux.io/r/LETFs/comments/mdb4n4/backtesting_tqqqs_hypothetical_performance_over/l84fj27/?context=3)
  - A Composer version (TQQQ above the QQQ 200-day SMA, else short-term bonds) lists a −31.6% max drawdown with no period stated. — [Composer](https://www.composer.trade/trading-strategies/tqqq-based-on-200d-ma-X3BQchFSANrGzrIKnDO6)
  - These are unverified retail sources. Their lower drawdowns probably come from different windows, signals or execution.

**Own backtest: long simulated history (before the funds existed)**
- Simulated 3x NDX buy-and-hold, 1985-2026: 13.6% CAGR, below 1x NDX at 14.6%, with a −99.95% max drawdown. From 2000-03-10 to 2002-10-09 it fell 99.95% (1x NDX: −83%). At 2026-11-25 it stood at only 22% of its March 2000 peak, so it had not recovered after 26 years. — [Own backtest](https://query1.finance.yahoo.com/v8/finance/chart/%5ENDX)
- Simulated 3x NDX with the NDX 200-day SMA, 1985-2026:
  - Full period: 18.7% CAGR, −96.1% max drawdown (trough March 2003), 6.8 switches per year.
  - The SMA did not save it in the dot-com bust: −95.9% from March 2000 to March 2003, with 34 signal changes between January 2000 and April 2003 as bear-market rallies kept pulling it back in.
  - It did not regain its 2000 peak until August 2018.
  - 1985-2009 (before TQQQ existed): 12.9% CAGR. 2000-2009: −15.1% a year.
  - Source: [Own backtest](https://query1.finance.yahoo.com/v8/finance/chart/%5ENDX)
- Simulated 3x S&P 500, 1928-2026:
  - Buy-and-hold: 5.8% CAGR, −100% (−99.9% from September 1929 to July 1932).
  - With the 200-day SMA: 16.1% CAGR, −93.5% max drawdown (trough 1935).
  - Crash windows, buy-and-hold vs SMA:

| Crash window | 3x B&H | 3x + SMA |
|---|---|---|
| 1929-32 | −99.9% | −50% |
| 1973-74 | −89.5% | −22% |
| Oct 2007 to Mar 2009 | −95.6% | −24% |
| Aug-Dec 1987 | about −80% | −32% |

  - The filter's long-run value is almost entirely in these slow bear markets.
  - Source: [Own backtest](https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC)

**Kelly view of leverage (own calculation, i.i.d. normal approximation with growth ≈ L·μ − L²σ²/2)**
- S&P TR, 1960-2026: excess return about 6.8%/yr, volatility 16.3%, full-Kelly leverage about 2.6x. Growth over cash: 5.5% at 1x, 8.3% at 2x, 8.5% at 3x.
- NDX, 1985-2026: excess return 13.7%, volatility 25.6%, Kelly about 2.1x. Growth over cash: 10.5% at 1x, 14.4% at 2x, 11.8% at 3x.
- So 3x is above Kelly for the Nasdaq-100: expected growth falls even before fees, fat tails and volatility clustering. NDX's sample mean is also inflated by hindsight, since it is the index that won.
- Source: [Own calculation on Yahoo data](https://query1.finance.yahoo.com/v8/finance/chart/%5ENDX)

### Inferences
- The TQQQ-plus-SMA record for 2010-2025 (about 32%/yr) is mostly bull-market beta. QQQ itself returned 19% a year, about 5 points above its 1985-2026 average. Over the full 1985-2026 simulation the same rule returned 18.7%, with a decade (2000-2009) of −15%/yr and an 18-year wait to recover.
- Risk of ruin is real even with the filter. Over 1928-2026 and 1985-2026, both 3x SMA strategies had at least one drawdown above 93%. A −56% to −66% drawdown happened even inside the 2010-2025 bull market (2018-2020).
- Fast crashes are the specific weakness: 1987, February-March 2020 and 2018. The 200-day SMA reacts too slowly, so a 3x fund can lose 50-80% before the signal flips.
- Long choppy periods are the second weakness (2000-2003, 2011, 2015-16, 2026). Each whipsaw costs a few percent, and 3x leverage triples it.
- SOXL is a 3x fund on a single, highly volatile sector (−90.5% max drawdown). Its ruin risk is clearly higher than TQQQ or UPRO.
- Holding 1x inverse ETFs for long periods also decays, per the SEC/FINRA alert. Rotating into them when below the SMA adds whipsaw losses in bear-market rallies. Not backtested here.

### Gaps
- The full Gayed-Bilello paper was not retrieved. Its 3x CAGR and drawdown numbers are not cited from the primary source.
- The ProShares prospectus wording on compounding was not fetched. The SEC/FINRA alert covers the same point.
- Backtests ignore slippage, taxes, fund closure or reverse-split risk, and the possibility of a single-day −33% index move, which would wipe out a 3x fund. (ProShares disclosures discuss this, but they were not retrieved here.)

---

## 3. Realistic odds and time frame for $200 -> $1,000

### Takeaway
A 5x takes about 17 years at 10%, 9 years at 20%, and 4.8 years at 40% CAGR. Historically, S&P buy-and-hold almost never turned $200 into $1,000 in under 10 years (about 5% of 10-year windows). A 3x Nasdaq + 200-day SMA strategy did it in about 4-5% of 3-year windows, about 20% of 5-year windows, and about 55% of 10-year windows (1985-2026 simulation), with a real chance of losing half the money along the way. High-risk day trading has much worse odds. In a fair game the gambler's-ruin chance of 5x before going broke is 20%. Real retail day traders face a negative edge, and 97% of persistent Brazilian day traders lost money.

### Cited Findings
**Compounding math** (own calculation: years = ln 5 / ln(1+r)) — [Own calculation](https://query1.finance.yahoo.com/v8/finance/chart/SPY)

| CAGR | Years to 5x |
|---|---|
| 7% | 23.8 |
| 10% | 16.9 |
| 15% | 11.5 |
| 20% | 8.8 |
| 30% | 6.1 |
| 40% | 4.8 |
| 60% | 3.4 |
| 100% | 2.3 |

**Gambler's ruin** (own calculation from the standard formula)
- In a fair game, P(reach $1,000 before $0 | start $200) = 200/1000 = 20%. This holds for any bet size.
- With a small negative edge (49/51 even-money bets):
  - $10 bets: about 2.3%.
  - $50 bets: about 14%.
  - Bold play (all-in bets) is optimal in an unfair game and gets closest to 20%.
- With a positive edge, smaller bets increase the probability. Retail evidence below points to a negative edge after costs.
- Source: [Own calculation](https://query1.finance.yahoo.com/v8/finance/chart/SPY); formula P = (1 − (q/p)^i) / (1 − (q/p)^N)

**Historical distribution of outcomes for $200** (own backtest)

Method:
- Every daily start date, with overlapping windows, so the effective number of independent samples is much smaller than n.
- "Touch $1,000" means it hit $1,000 at any point in the window. "Touch $100" means it lost half at some point.
- 3x NDX + SMA history before 2010 is simulated.

Percentiles are dollar values of the $200 at the end of the window.

| Strategy, window | p5 | median | p95 | P(end ≥ $1k) | P(touch $1k) | P(end < $200) | P(touch ≤ $100) |
|---|---|---|---|---|---|---|---|
| S&P TR B&H (1950-2026), 1y | $169 | $227 | $276 | 0% | 0% | 20.8% | 0.2% |
| S&P TR B&H, 3y | $168 | $279 | $402 | 0% | 0% | 10.2% | 1.5% |
| S&P TR B&H, 5y | $190 | $352 | $538 | 0% | 0% | 7.4% | 1.5% |
| S&P TR B&H, 10y | $257 | $584 | $1,004 | 5.1% | 7.1% | 2.8% | 1.6% |
| Sim 3x NDX + 200SMA (1985-2026), 1y | $110 | $233 | $493 | 0.5% | 1.8% | 37.2% | 3.0% |
| Sim 3x NDX + 200SMA, 3y | $114 | $367 | $976 | 4.5% | 15.7% | 21.0% | 10.7% |
| Sim 3x NDX + 200SMA, 5y | $113 | $499 | $1,910 | 20.4% | 38.9% | 14.2% | 11.8% |
| Sim 3x NDX + 200SMA, 10y | $97 | $1,108 | $5,756 | 55.2% | 81.5% | 8.9% | 14.3% |
| Sim 3x NDX B&H (1985-2026), 1y | $32 | $273 | $602 | 0.7% | 2.1% | 28.2% | 20.0% |
| Sim 3x NDX B&H, 3y | $7 | $443 | $1,769 | 12.5% | 23.6% | 24.9% | 36.9% |
| Sim 3x NDX B&H, 5y | $3 | $598 | $4,123 | 34.8% | 56.5% | 30.4% | 47.9% |
| Sim 3x S&P + 200SMA (1950-2026), 3y | $163 | $337 | $796 | 2.6% | 4.5% | 11.1% | 1.5% |
| Sim 3x S&P + 200SMA, 5y | $176 | $489 | $1,498 | 12.4% | 17.3% | 7.3% | 2.5% |
| REAL TQQQ + QQQ 200SMA (2010-2026 only), 1y | $132 | $278 | $461 | 0% | 0% | 27.0% | 2.1% |
| REAL TQQQ + SMA, 3y | $309 | $477 | $873 | 1.1% | 8.6% | 1.5% | 2.7% |
| REAL TQQQ + SMA, 5y | $413 | $841 | $1,827 | 39.7% | 58.3% | 0% | 2.9% |

Source: [Own backtest](https://query1.finance.yahoo.com/v8/finance/chart/TQQQ); full table in `backtest_code/trend_leverage_backtest_output.txt`.

**Retail day-trading evidence**
- Chague, De-Losso & Giovannetti, "Day Trading for a Living?":
  - Sample: all 19,646 individuals who began day trading mini-Ibovespa futures in Brazil in 2013-2015.
  - 97% of those who persisted more than 300 days lost money.
  - Of the 1,551 persistent traders, only 1.1% earned more than the Brazilian minimum wage and 0.5% more than a bank teller's starting salary.
  - No evidence of learning.
  - Sources: [SSRN 3423101](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3423101); [IDEAS/RePEc](https://ideas.repec.org/p/fgv/eesptd/525.html); [Quantpedia summary](https://quantpedia.com/retail-day-trading-is-an-uphill-battle/)
- Barber, Lee, Liu & Odean (2014, *Journal of Financial Markets*), Taiwan 1992-2006: "less than 1% of the day trader population is able to predictably and reliably earn positive abnormal returns net of fees". — [EconPapers](https://econpapers.repec.org/RePEc:eee:finmar:v:18:y:2014:i:c:p:1-24); [Berkeley working paper](https://faculty.haas.berkeley.edu/odean/papers/day%20traders/Day%20Trading%20Skill%20110523.pdf)
- A related Barber/Lee/Liu/Odean draft ("Learning Fast or Slow") reports that 97% of day traders, and over 90% of day-trading volume, are linked to losses. — [PUC-Rio copy](https://www.econ.puc-rio.br/uploads/adm/seminarios/Learning_fast_or_slow_180606.pdf) (working-paper version)
- Barber, Lee, Liu & Odean, "Just How Much Do Individual Investors Lose by Trading?" (RFS 2009), Taiwan. — [Berkeley PDF](https://faculty.haas.berkeley.edu/odean/papers%20current%20versions/justhowmuchdoindividualinvestorslose_rfs_2009.pdf) (the headline loss figures were not checked in this session)
- Beckmeyer, Branger & Gayda (2023), "Retail Traders Love 0DTE Options... But Should They?":
  - Retail traders lost about $70 million in aggregate on S&P 500 0DTE options over about two years. More than $50 million of that was transaction costs.
  - Average daily retail losses were about $358,000 after daily expirations began in May 2022.
  - About 75% of retail S&P options trades were 0DTE.
  - Sources: [Bloomberg](https://www.bloomberg.com/news/articles/2023-04-21/day-traders-lose-358-000-per-day-gambling-on-zero-day-options); [WealthManagement](https://www.wealthmanagement.com/equities/retail-investors-are-in-love-with-same-day-options); SSRN abstract 4404704
  - Options are not available in this account setup; the study is included as general evidence on retail lottery-seeking.

### Inferences
- **Time frame.** Reaching $1,000 from $200 within about 1 year has essentially no historical precedent for any of the trend or buy-and-hold strategies tested: at most 0.5-2% of windows, and only for 3x NDX variants. Within 3 years it is unlikely (about 5-16% "touch" for 3x NDX + SMA). The most realistic route is 5-10 years of a leveraged trend strategy, or simply adding new money, with at least a 1-in-10 chance of a 50% loss along the way.
- **Fixed-target framing.** Under a fixed target, any rule that "doubles down" raises the chance of hitting $1,000 but also raises the chance of losing most of the $200. In a fair game, 20% is the ceiling for any betting scheme. Since day trading is negative-edge on average after costs, the realistic chance for a high-risk day-trading bot is below 20%, plausibly in the low single digits. This is an inference from gambler's-ruin math combined with the retail studies, not a measured number.
- **Scale effect.** At $200, a 40% CAGR adds about $80 in the first year. Monthly contributions dominate: $200 a month at 10% reaches $1,000 in about 4-5 months. This is the overwhelmingly most reliable path to a $1,000 balance (inference, simple arithmetic).
- **Real TQQQ data overstates the odds.** The "REAL TQQQ" rows (2010-2026: 0% chance of ending below $200 after 5 years) come from a single bull market and should not be read as forward-looking odds. The 1985-2026 simulation, which includes the dot-com crash, is the more honest base rate, and even it benefits from hindsight about which index won.

### Gaps
- FINRA/SEC statistics on retail losses specifically in leveraged ETFs were not found. Only general warnings were located.
- No study measuring outcomes for small automated retail trading bots was found.
- The Brazil and Taiwan studies cover futures and stock day trading, not leveraged-ETF swing trading. Applying them to this account is an analogy.
- The Barber & Odean (2000) "Trading Is Hazardous to Your Wealth" headline figures were not checked in this session, so they are not quoted.

---

## 4. Small-account practicalities (Alpaca cash account)

### Takeaway
The pattern-day-trader rule and its $25,000 minimum were removed by FINRA effective June 4, 2026, with broker phase-in allowed to October 20, 2027. The old rule applied to margin accounts anyway. In a cash account, the binding constraint is settled cash: T+1 settlement and good-faith/free-riding rules. A low-turnover SMA rule (about 1.5-6 switches a year) never runs into these limits.

### Cited Findings
- The SEC approved FINRA's SR-FINRA-2025-017 on April 14, 2026. It replaces the Rule 4210 day-trading margin requirements with "intraday margin standards" and eliminates the pattern-day-trader designation and its $25,000 minimum equity. Effective date June 4, 2026; phase-in ends October 20, 2027. — [FINRA Regulatory Notice 26-10](https://www.finra.org/rules-guidance/notices/26-10); [Federal Register filing](https://www.federalregister.gov/documents/2026/04/17/2026-07485/self-regulatory-organizations-financial-industry-regulatory-authority-inc-notice-of-filing-of)
- Brokers implement on their own timelines; for example, Schwab planned to stop counting day trades from June 8. — [Schwab](https://www.schwab.com/learn/story/sec-approves-scrapping-25000-day-trader-minimum); [Firstrade guide](https://blog.firstrade.com/blog/2026/6/3/the-complete-guide-to-the-pdt-rule-elimination-everything-investors-need-to-know-on-day-one)
- Leveraged and inverse ETFs can be less tax-efficient, partly because daily resets can generate short-term gains. — [Investor.gov SEC/FINRA alert](https://www.investor.gov/news-alerts/investor-alerts/sec-finra-investor-alert-leveraged-inverse-etfs)

### Inferences
- Fractional shares let a $200 account hold TQQQ, QQQ or SPY in any proportion. The minimum trade size is not the constraint (inference; Alpaca's fractional-share minimums were not verified this session).
- T+1 settlement: sale proceeds in a cash account are usable for new purchases once settled, the next business day. A daily-signal SMA bot that switches TQQQ to T-bills/cash and back within a day could hit good-faith violations if it buys with unsettled funds. A band (e.g. ±3%) or a monthly check (Faber-style) cuts this risk and roughly quarters the switch count (1.5 vs 6.2 a year in the backtest).
- The cash leg: the backtest assumes T-bill yield while out. In practice that means holding cash, which may earn nothing at Alpaca, or a T-bill ETF such as BIL or SGOV. At $200 the yield difference is cents.

### Gaps
- Alpaca-specific rules (fractional-share eligibility of TQQQ/SOXL, cash-account good-faith-violation handling, interest on idle cash, any leveraged-ETF acknowledgement requirement) were not verified in this session.
- The SEC T+1 rule (compliance date May 28, 2024) is from background knowledge and was not re-fetched this session.
