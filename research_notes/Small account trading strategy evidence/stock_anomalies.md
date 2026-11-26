# Stock-level short-horizon anomalies for a small automated long-only account (reversal, PEAD, gaps, ORB)

Scope note: US equities only. User context is a $200 Alpaca cash account (commission-free, long-only, no margin, fractional shares, free delayed data) aiming for $1,000. Its current ORB strategy (stocks up 4%+ on high volume) was break-even over 2 years before costs and lost money at about 0.3-0.5% slippage per buy.

Method caveat: in this session WebFetch could not reach any host (DNS blocked for cfr.ivo-welch.info, quantconnect.com, anderson-review.ucla.edu), so no full paper was read. Every finding below comes from search-result abstracts and snippets of the cited pages. Exact table values (Sharpe, drawdown, cost break-even) are often missing and are listed under Gaps rather than guessed. "Author-reported" means the paper's own backtest. "Independent" means a third party's replication.

## 1. Short-term (1-week / 1-month) reversal: does it still work after 2010-2015, net of costs, in liquid large caps, long-only?

### Takeaway
The classic 1-month and 1-week reversal was very large in early samples (about 2%/month gross in Jegadeesh 1990). It has since decayed to roughly 0.7%/month gross in later samples and about 3.5%/yr for the factor in 2010-2019. Robeco's 2024 paper says the classic version has "vanished entirely in most regions". The versions that survive are enhanced (residual or industry-relative), long-short, and cost-sensitive. Round-trip costs of about 0.8%/month wipe out most of the gross profit. None of the evidence supports a long-only, retail, single-stock version as a reliable edge after 2015.

### Cited Findings
**Original effect sizes (gross, author-reported)**
- Jegadeesh (1990): buying last month's losers and selling winners, held one month, earned "about 2% per month over 1934-1987". The often-quoted figure is 2.49%. Sources disagree on the sample window: one says 1934-1987, another 1965-1989. — [NY Fed SR513, Da, Liu & Schaumburg](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr513.pdf); [Da, Liu & Schaumburg, Management Science 2014](https://academicweb.nd.edu/~zda/Reversal.pdf)
- Jegadeesh also found reversal "much more profitable in the month of January", so a large share of the classic effect is seasonal. — [Alpha Architect summary](https://alphaarchitect.com/quantitative-momentum-research-short-term-return-reversal/)
- Lehmann (1990): prior-week losers outperform prior-week winners at the weekly horizon, and the effect was "most prominent at weekly intervals". No weekly percentage was retrieved. — [Alpha Architect](https://alphaarchitect.com/quantitative-momentum-research-short-term-return-reversal/)

**Decay (later samples)**
- Da, Liu & Schaumburg (Management Science 2014): in their more recent sample of larger stocks, the standard reversal strategy earns a raw 0.67%/month (t = 2.53), "much lower than the 2.49%" of Jegadeesh (1990). Another study reports 0.74%/month (t = 4.44) with January excluded. — [Da, Liu & Schaumburg](https://academicweb.nd.edu/~zda/Reversal.pdf)
- Da, Liu & Schaumburg also argue that reversal "has become less likely recently among all but the smallest stocks". They split the profit into components including across-industry momentum and within-industry variation in expected returns. — [NY Fed SR513](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr513.pdf)
- Da, Liu & Schaumburg (working paper) give a rough cost estimate of about **80.5 bp per month** (46 bp × 90.2% + 43 bp × 90.8% turnover) for the reversal strategy. That is larger than the ~67 bp/month raw return they report for the recent large-stock sample. — [NY Fed SR513](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr513.pdf)
- Robeco reports that the short-term reversal factor (Hou-Xue-Zhang library, not Fama-French) returned about 3.5% over 2010-2019: "below its long-term average, but well above zero". This is gross and long-short. — [Robeco](https://www.robeco.com/en-int/insights/2020/11/factor-investing-going-beyond-fama-and-french)
- Blitz, van der Grient & Honarvar (Robeco; JPM April 2024, 50(6) 89-101; sample 1985-2022): "The classic short-term reversal effect has steadily weakened over time, to the point of now having vanished entirely in most regions." The industry-relative and residual versions held up better on a risk-adjusted basis. The authors note that "any stand-alone STR strategy involves high trading costs and may not be profitable". Benefits come from combining it with other short-term factors. — [SSRN 4575689](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4575689); [PM Research](https://www.pm-research.com/content/iijpormgmt/50/6/89)
- A third-party implementation (paperswithbacktest) of the Blitz et al. strategy shows a negative annual return. This is independent, its method is unverified, and it is low-confidence. — [paperswithbacktest](https://paperswithbacktest.com/strategies/reversing-the-trend-of-short-term-reversal)
- A QuantConnect community reversal backtest over 2016-2021 underperformed the S&P 500. This is an independent single implementation, not a factor study. — [QuantConnect research 15311](https://www.quantconnect.com/research/15311/short-term-reversal-strategy-in-stocks/)

**Residual reversal and large-cap net evidence (older samples)**
- Blitz, Huij, Lansdorp & Verbeek, "Short-Term Residual Reversal" (J. Financial Markets 2013): residual reversal is "statistically and economically significant ... net of trading costs, even when we restrict our sample to large-cap stocks over the post-1990 period". Versions of the paper report >7% or >8% per year net. It earns risk-adjusted returns "twice as large" as conventional reversal, and its costs are "significantly lower". These figures are author-reported, long-short, and the sample ends around 2009. — [EFMA 2012 version](https://www.efmaefm.org/0EFMSYMPOSIUM/2012/papers/017_update.pdf); [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1386418112000468)
- Groot, Huij & Zhou (via Quantpedia): reversal strategies "can generate 30 to 50 basis points per week net of transaction costs" when restricted to large caps. This is author-reported, long-short, with a pre-2010 sample. — [Quantpedia](https://quantpedia.com/strategies/short-term-reversal-in-stocks)
- An EFMA 2011 paper says net reversal profits stay "large and positive among large caps" in the most recent decade of its sample (ending before 2011). — [EFMA 2011](https://efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2011-Braga/papers/0259_update.pdf)
- Medhat & Schmeling (US 1963-2018): short-term reversal is concentrated in the lowest-turnover stocks. Stocks with high turnover show short-term momentum instead. This means a "buy last week's big loser" rule applied to heavily traded stocks (like news-driven movers) can work against the trader. — [CEPR DP15857](https://repec.cepr.org/repec/cpr/ceprdp/DP15857.pdf)
- Blitz et al. (2022, via Alpha Architect): for a composite of short-term signals, transaction costs ate more than two-thirds of the gross alpha. — [Alpha Architect](https://alphaarchitect.com/alpha-from-short-term-signals/)

**Liquidity provision (Nagel 2012)**
- Nagel, "Evaporating Liquidity" (RFS 2012): 5-day reversal returns proxy for the returns to liquidity provision. Expected returns are "strongly time-varying and highly predictable with the VIX index" and are highest when liquidity is withdrawn during market turmoil. — [SSRN 1971476](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1971476); [NBER w17653](https://www.nber.org/system/files/working_papers/w17653/w17653.pdf)

### Inferences
- The post-2010 gross long-short reversal premium in liquid stocks (~3.5%/yr for the factor; ~0.67%/month raw in later large-stock samples) is about the same size as, or smaller than, round-trip costs at weekly or monthly rebalancing (~0.8%/month). The user's measured slippage of 0.3-0.5% per buy, about 0.6-1.0% round trip, would wipe it out at weekly turnover.
- Long-only cuts the edge further. Academic figures are long-short spreads. A long-only loser portfolio carries full market beta, so most of its return would be market return plus a small tilt.
- Nagel's result points to the one regime where reversal pays well: buying liquid stocks after sharp drops when VIX is high. Those are also the periods with the deepest drawdowns. A $200 account gets no diversification benefit from it.
- Medhat & Schmeling suggest that high-volume, news-driven movers are the worst place to expect reversal. That is the same universe the user's ORB bot trades.

### Gaps
- No post-2015 net-of-cost Sharpe or drawdown for any reversal variant was retrieved. The full text of Blitz et al. 2024 (net numbers for the enhanced versions) could not be fetched.
- I did not retrieve Kenneth French ST_Rev data for 2015-2025. Direct factor numbers for the most recent decade are missing.
- No source tested a long-only reversal on large caps specifically.
- No primary source on decimalization and reversal decay was found.

## 2. Post-earnings-announcement drift (PEAD) and the earnings-announcement premium: has it disappeared, and does it survive in small caps after costs?

### Takeaway
PEAD was real and large historically. Martineau (CFR 2022) finds no drift in large stocks since about 2006, and microcap drift has only recently faded. Subrahmanyam (2025, data to Dec 2024) finds drift "does not exist in all but microcaps". Where drift remains (illiquid microcaps), Chordia et al. (2009) estimate that costs absorb 63-100% of paper profits. The US earnings-announcement premium also appears to have shrunk or disappeared after about 2004-2006. A $200 long-only account cannot capture classic SUE-PEAD net of costs. The only open lead is text- or surprise-magnitude-based variants that have not been replicated independently.

### Cited Findings
**Classic effect and costs (pre-2006)**
- Bernard & Thomas (1989) is the classic SUE-decile drift study. Its effect-size figures could not be retrieved in this session (see Gaps).
- Chordia, Goyal, Sadka, Sadka & Shivakumar, "Liquidity and the Post-Earnings-Announcement Drift" (FAJ 2009, 65(4) 18-32): a long-short PEAD strategy earned a value-weighted **0.14%/month in the most liquid stocks** versus **1.60%/month in the most illiquid**. Transaction costs absorb **63-100%** of paper profits (SSRN version) or **70-100%** (published abstract). The authors conclude that "transactions costs could be the source of the drift". — [SSRN 1403342](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1403342); [IDEAS/FAJ](https://ideas.repec.org/a/taf/ufajxx/v65y2009i4p18-32.html)
- Ng, Rusticus & Verdi (2008, JAR) are reported to find that transaction costs "significantly reduce but do not eliminate" PEAD profits. This was cited through a review, not read directly. — [Fink 2020 review, Univ. Graz](https://static.uni-graz.at/fileadmin/sowi/Working_Paper/2020-04_Fink.pdf)
- One blog (TradeWave) claims the drift is "real and tradeable in liquid stocks". That contradicts Chordia et al.'s own abstract, so it should be disregarded. — [TradeWave](http://tradewave.ai/insights/post-earnings-drift.html)

**Disappearance**
- Martineau, "Rest in Peace Post-Earnings Announcement Drift" (Critical Finance Review 2022, 11(3-4)): drift in large stocks has been absent since 2006 and has only recently faded in microcaps. Analyst-based surprises no longer predict post-announcement returns after 2006. His explanation is that announcement-day prices now absorb the surprise fully. In other accounts, drift began disappearing from non-microcaps in 2001 and was gone by 2006. — [Now Publishers CFR-0122](https://nowpublishers.com/article/Details/CFR-0122); [IDEAS](https://ideas.repec.org/a/now/jnlcfr/104.00000122.html)
- Subrahmanyam, "Keeping It Simple: How Post-earnings Return Drift Can Exist and Not Exist Simultaneously" (J. Investment and Management 2026; data Feb 2001-Dec 2024): his recreated "earnings drift factor" shows that drift "does not exist in all but microcaps". He attributes the conflicting papers to research-design choices. — [Science Publishing Group](https://www.sciencepublishinggroup.com/article/10.11648/j.jim.20261501.11)
- UCLA Anderson Review (2025) reports that two accepted papers claim the drift is still present, against Martineau. Their names could not be retrieved because the page was blocked. — [UCLA Anderson Review](https://anderson-review.ucla.edu/is-post-earnings-announcement-drift-a-thing-again/)
- A Columbia working paper argues that short-window PEAD (the first few days after the announcement) has become stronger over time. The overall decline happens later in the quarter. — [Columbia CEASA](https://business.columbia.edu/sites/default/files-efs/imce-uploads/CEASA/Events%20Page/PEAD_Declined_over_time.pdf)
- PEAD.txt (Meursault, Liang, Routledge, Scanlon; JFQA; sample 2010-2019): drift sorted on a text-based surprise (SUE.txt) is "much larger than the classic SUE-based PEAD". This is author-reported. — [Philadelphia Fed WP 21-07](https://www.philadelphiafed.org/-/media/frbp/assets/working-papers/2021/wp21-07.pdf)
- A small-sample study of US tech stocks (2023-2025) found "limited evidence of systematic" PEAD. The journal (Oxford JSS) is of unclear quality. — [Oxford JSS](https://www.oxfordjss.org/oct-2026-vol-12-issue-6/post-earnings-announcement-drift-in-us-technology-stocks-2023-to-2025)
- A self-published GitHub out-of-sample test reports small-cap long-short PEAD earning 6.6%/yr gross and **1.8%/yr net** at 25 bp one-way, with Sharpe 0.26 and worst drawdown 18%. The author calls the costs "illustrative". This is low-confidence and independent. — [GitHub earnings-drift-out-of-sample](https://github.com/guptagaurav-info/earnings-drift-out-of-sample)

**Earnings-announcement premium (Frazzini & Lamont 2007)**
- Frazzini & Lamont show the announcement premium is "quantitatively substantial, especially among large cap securities". Their monthly figure was not retrieved. — [Brock Univ. XBRL paper](https://brocku.scholaris.ca/server/api/core/bitstreams/2b8fe057-36ba-4c6c-993c-827759ace9c1/content)
- Heitz, Narayanamoorthy et al., "The Disappearing Earnings Announcement Premium": the US premium has disappeared since about 2004. They tie this to expanded Form 8-K disclosure pre-empting earnings news. The premium remains robust internationally. — [Rotman seminar paper](https://www-2.rotman.utoronto.ca/userfiles/seminars/files/G_%20Narayanamoorthy%20paper.pdf); [paperswithbacktest](https://paperswithbacktest.com/strategies/the-disappearing-earnings-announcement-premium)
- A conflicting study (1983-2016) finds the premium still positive and significant, but "lowest in the most recent period, 2006-2016". — [Brock Univ.](https://brocku.scholaris.ca/server/api/core/bitstreams/2b8fe057-36ba-4c6c-993c-827759ace9c1/content)
- An options-implied ex-ante announcement risk premium is about 15 bp on average. — [Liu, AEA 2024](https://www.aeaweb.org/conference/2024/program/paper/5GGEki7i)

### Inferences
- Even before 2006, liquid-stock PEAD was only about 0.14%/month gross. The illiquid names where it was large are where 0.3-0.5% slippage per side (or worse in microcaps) is most likely. On this evidence the classic strategy has no realistic net edge for this account in liquid stocks.
- An announcement-premium trade (buy the week before earnings) is worth at most about 15 bp per event ex ante. That is below one side of the user's measured slippage.
- If anything is worth testing, it is the short-window (1-5 day) drift after very large surprises, per the Columbia paper. It needs an independent, cost-inclusive test on current data before any capital goes in.

### Gaps
- Exact Bernard & Thomas (1989) decile spreads were not retrieved.
- Frazzini & Lamont's monthly premium figure was not retrieved.
- Martineau's exact coefficients by size group were not retrieved (PDF host blocked).
- The two "PEAD still exists" papers cited in the UCLA brief could not be identified.
- No post-2015 net-of-cost small-cap PEAD result from a peer-reviewed source was found. The only net figure is the low-confidence GitHub test.

## 3. Overnight vs intraday reversal, gap fills, and "buy the gap-down" evidence

### Takeaway
Peer-reviewed or SSRN papers document stock-level patterns: overnight-intraday reversal, end-of-day reversal concentrated in small stocks and intraday losers, and overnight and intraday continuation with cross-period reversal. All are long-short, gross, and short-holding. Evidence on buying large-cap gap-downs comes almost entirely from blogs and forums with unclear methods. One systematic blog test (QuantRocket) found that selling, not buying, the gap is what works. There is no reliable post-2015 net-of-cost evidence for a retail long-only gap-down rule.

### Cited Findings
- Lou, Polk & Skouras, "A Tug of War: Overnight versus Intraday Expected Returns" (JFE 2019): "strong overnight and intraday firm-level return continuation along with an offsetting cross-period reversal effect". — [LSE PDF](https://personal.lse.ac.uk/polk/research/TugOfWar.pdf)
- Liu, Liu, Wang, Zhou & Zhu, "Overnight-Intraday Reversal Everywhere": buying assets with low past overnight returns and selling those with high ones is robust across asset classes and out-of-sample. They explain it as liquidity provision. — [SSRN 2730304](https://papers.ssrn.com/sol3/Delivery.cfm/2730304.pdf?abstractid=2730304)
- Della Corte et al., "Market Closure and Short-Term Reversal": a daily long-short strategy on past overnight returns earns about **5x** the excess return of conventional reversal in US stocks. This is gross, with daily turnover. — [CICF paper](https://www.cicfconf.org/sites/default/files/paper_357.pdf)
- Baltussen, Da & Soebhag, "End-of-Day Reversal" (SSRN 5039009, EFMA 2024): sharp reversals in the last 30 minutes, stronger in smaller stocks. The effect comes mainly from positive price pressure on intraday losers, driven by attention-induced retail buying and short-seller risk management. — [SSRN 5039009](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5039009); [Notre Dame PDF](https://academicweb.nd.edu/~zda/EOD.pdf)
- A 2025 Finance Research Letters paper finds that overnight price jumps change the pattern. In jump stocks, the overnight leg earns 3.9% lower risk-adjusted return. — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1544612325018458)
- QuantRocket blog on gap-downs: works better on large caps than small caps. Entering 5-10 minutes after the open beats entering at the open. The profitable variant sold the gap rather than buying it. This is an independent blog with no cost details retrieved. — [QuantRocket](https://www.quantrocket.com/blog/buy-or-sell-down-gaps/)
- Engineered Finance blog: buying the weakest gapped-down S&P 500 names at the open, exiting at the close, with a filter for opens above the 20-day average, reported a Sharpe of 2.19 over **2005-Dec 2015**. This is pre-2015, with unclear costs. — [Engineered Finance](https://engineeredfinance.wordpress.com/2016/01/23/intraday-mean-reversion-bog/)
- QuantConnect community "Mind the Gap": buy S&P 500 stocks above their 100-day SMA after a gap-down larger than 1.2× the 14-day ATR, exit 15 minutes after the open. No performance figures were retrieved. — [QuantConnect forum 19075](https://www.quantconnect.com/forum/discussion/19075/mind-the-gap-an-intraday-reversal-strategy-using-gap-downs-and-atr/)
- QuantifiedStrategies (ES futures, not stocks): 68 qualifying gap trades since 2016, 88.2% winners. The sample is small. SPY "shows a lot less mean reversion if opening lower", so they cap gaps at -0.6%. — [QuantifiedStrategies gap fill](https://www.quantifiedstrategies.com/gap-fill-trading-strategies/)
- A blog test of RSI(2) mean reversion on the S&P 500 reports that the edge "lost its lead to costs". — [Quanterlab](https://quanterlab.com/research/navigating-mean-reversion-breaking-down-the-base-mechanism)

### Inferences
- The academic overnight-intraday reversal is a daily long-short liquidity-provision premium. Its per-trade gross edge is presumably measured in basis points. A long-only retail implementation paying 0.3-0.5% per side would very likely lose it.
- The end-of-day reversal is strongest in small stocks' intraday losers. Capturing it means buying near the close and selling around the next open or later, with the same cost problem.
- "Buy the gap-down in an uptrend" has only blog-level support, and one systematic blog test points the other way. It is a hypothesis to test, not an established edge.

### Gaps
- No peer-reviewed paper on buying single-stock gap-downs in US large caps after 2015 was found.
- Per-trade gross edge in bp for the overnight-intraday reversal was not retrieved.
- No cost-break-even figures were found for any gap strategy.

## 4. Opening-range breakout on "stocks in play" (Zarattini/Barbon/Aziz 2024), independent replications, and retail day-trader profitability

### Takeaway
Zarattini, Barbon & Aziz report over 1,600% total net return, Sharpe 2.81 and 36% annual alpha for a 5-minute ORB on the top-20 "stocks in play" over 2016-2023. Their results assume leverage and IBKR-style per-share costs. The plain ORB without the relative-volume filter returned only 29% total (3.2%/yr, Sharpe 0.48). The headline QuantConnect replication (Sharpe 2.40) covers only 2016. A separate QuantConnect backtest for 2023-Apr 2025 showed Sharpe -0.50. Large studies of real retail day traders find that almost all lose money net of costs: 97% of persistent Brazilian day traders lost money, and fewer than 1% of Taiwanese day traders earn reliable positive net returns. The user's own ORB result (break-even gross, negative at 0.3-0.5% slippage) fits this evidence.

### Cited Findings
**The paper (author-reported)**
- Zarattini, Barbon & Aziz, "A Profitable Day Trading Strategy For The U.S. Equity Market" (SSRN 4729284; Swiss Finance Institute RP 24-98): 5-minute ORB on more than 7,000 US stocks, 2016-2023, restricted to "Stocks in Play" (unusually high activity, mostly on company news). The top-20 portfolio reported "total net performance of over 1,600%", Sharpe 2.81 and annualized alpha 36%. Another summary gives 1,637% total and 41.6% annualized. — [SSRN 4729284](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4729284); [Univ. St. Gallen repository](https://www.alexandria.unisg.ch/server/api/core/bitstreams/3c2989c4-688d-4d78-8a71-f02690990d51/content); [Concretum Group](https://concretumgroup.com/a-profitable-day-trading-strategy-for-the-u-s-equity-market/)
- Screens (per CXO Advisory): open price above $5, 14-day average volume of at least 1M shares, ranked by relative volume in the opening window, top 20 taken. — [CXO Advisory](https://www.cxoadvisory.com/individual-investing/intraday-trading-of-overactive-stocks-via-opening-range-breakout/)
- Without the relative-volume filter, ORB on the same universe returned 29% total, 3.2%/yr, Sharpe 0.48, below the S&P 500's 0.78. The unfiltered version had a 13% max drawdown versus 34% for the index. — [QuantifiedStrategies](https://www.quantifiedstrategies.com/stocks-in-play-trading-strategy-day-trading/); [Tradoki blog](https://blog.tradoki.com/posts/opening-range-breakout-stocks-in-play-research)
- A DanFin review agrees that the relative-volume selection "did almost all the work". — [DanFin](https://danfin.net/opening-range-breakout-research)
- Cost assumptions in the related Zarattini/Aziz ORB work (per QuantInsti): $0.0035/share commission each way (IBKR) plus $0.02/share slippage each way, with a 4x leverage cap. QuantInsti's article backtests a different Zarattini & Aziz paper, so treat the parameter attribution to the stocks-in-play paper with care. — [QuantInsti](https://www.quantinsti.com/articles/opening-range-breakout-strategy/)

**Independent replications**
- QuantConnect research post: Sharpe 2.396 and beta -0.042, against 0.836 for SPY buy-and-hold. A volatility-adjusted variant gave Sharpe 2.237 with a 97% Probabilistic Sharpe Ratio. In the parameter sweep, 17 of 25 combinations (68%) beat the benchmark Sharpe. — [QuantConnect research 18444](https://www.quantconnect.com/research/18444/opening-range-breakout-for-stocks-in-play/)
- Critique: the QuantConnect sensitivity tests "are real, but all on the same single year". The research post covers only 2016, the first year of the paper's window. — [GitHub CoursIA issue 16355](https://github.com/jsboige/CoursIA/issues/16355); [Tradoki](https://blog.tradoki.com/posts/opening-range-breakout-stocks-in-play-research)
- A QuantConnect embedded backtest for 2023-Apr 2025 (200-stock universe, 2-minute range, 4x leverage): CAGR 3.942%, drawdown 6.6%, Sharpe -0.502. The configuration differs from the paper, so this is not a direct replication. — [QuantConnect embedded backtest](https://www.quantconnect.com/terminal/cache/embedded_backtest_01b8fa640b519cbc4a61330ce572c66c.html)
- The paper itself frames day-trading viability as "a matter of debate". No live-trading track record was found. — [IDEAS RePEc rp2498](https://ideas.repec.org/p/chf/rpseri/rp2498.html)

**Retail day-trader profitability**
- Chague, De-Losso & Giovannetti ("Day Trading for a Living?", Brazil, cohort of 19,646 new day traders): of those who persisted more than 300 days, 97% lost money and only 1.1% earned more than the minimum wage. Some sources give 3.0% profitable. — [Does It Pay summary](https://doesitpay.org/day-trading/); [Tradeedgealpha summary](https://tradeedgealpha.com/day-trading-success-rate.html)
- Barber, Lee, Liu & Odean (all Taiwan Stock Exchange trades 1992-2006): fewer than 1% of day traders predictably and reliably earn positive abnormal returns net of fees. About 13-20% are profitable in a given year net of costs, and sources differ on the exact share. — [Scalpeltrade summary](https://scalpeltrade.com/blog/day-trading-statistics); [Tradewink summary](https://www.tradewink.com/learn/how-many-day-traders-are-profitable)

### Inferences
- The paper's edge depends on (a) relative-volume selection and (b) costs of a few cents per share on liquid, $5+ stocks with 1M+ volume. For a $20 stock, $0.02 + $0.0035 per side is about 0.12%. That is several times smaller than the 0.3-0.5% per buy the user measured, which explains why the bot's break-even gross turned negative net.
- The paper uses leverage of up to 4x, assumed rather than confirmed for this specific paper. A no-margin cash account cannot replicate that sizing. Under Alpaca cash-account rules (settled funds, possibly PDT limits; not verified here), the paper's return path is out of reach.
- Independent out-of-sample evidence after 2023 is negative (Sharpe -0.50 in a differing configuration). The headline replication is a single year in-sample. The strategy should be treated as unproven after publication.
- The retail studies are not tests of this strategy, but they set a strong prior that discretionary or retail intraday trading loses after costs.

### Gaps
- Exact rules of the paper (stop placement, ATR use, risk per trade, the 4x leverage claim, short side) were not verified because the PDF could not be fetched.
- Max drawdown of the top-20 portfolio was not retrieved.
- No independent full-period (2016-2023) replication or post-2024 out-of-sample test with realistic slippage was found.
- No cost break-even level (the slippage at which the Sharpe goes to zero) was found.
- The primary Barber/Lee/Liu/Odean and Chague et al. papers were not read directly. The figures come from secondary summaries that broadly agree with each other.

## Cross-cutting magnitude check for a $200 to $1,000 goal (inference only)

### Takeaway
Growing $200 to $1,000 is a +400% return. None of the post-2015 evidence above supports a net-of-cost long-only edge large enough to do that on a reasonable horizon. The surviving effects are long-short, measured in basis points per trade, and smaller than the user's measured slippage.

### Cited Findings
- Costs absorb 63-100% of PEAD profits even in the classic sample. — [SSRN 1403342](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1403342)
- A stand-alone short-term reversal strategy "may not be profitable" after costs. — [SSRN 4575689](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4575689)
- The reversal factor returned about 3.5% in total over 2010-2019, gross, long-short. — [Robeco](https://www.robeco.com/en-int/insights/2020/11/factor-investing-going-beyond-fama-and-french)

### Inferences
- At 0.4% slippage per side, a strategy trading once a day round trip pays about 0.8%/day, roughly 200%/yr in cost drag at 250 trades. Any viable approach for this account must trade rarely, in very liquid names, with limit orders or another way to cut slippage.
- The math: 5x takes about 17 years at 10%/yr, about 6 years at 30%/yr, and about 2.3 years at 100%/yr. Nothing in this evidence base credibly supports the last two for a long-only retail implementation after 2015.
- Deposits are a far more reliable way to reach $1,000 than strategy returns on $200.

### Gaps
- Alpaca execution quality for fractional and odd-lot orders, and how its cash-account settlement and PDT rules affect day trading, were not researched here (outside this scope).
