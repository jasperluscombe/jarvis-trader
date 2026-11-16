# What the backtest found (13–16 Nov 2026)

**Short version:** Jarvis's old rules lost money once realistic fills were counted. Breakouts only paid in stocks
that were already **in play**: up 4 %+ on the day, on 1.5× their normal opening volume, breaking out in the first
hour. Jarvis now trades only those. The improvement is real in this data, but the rules were picked by looking at
the same 59 days, so expect less in the future. The **shadow book** (below) tests them on new days, for free.

## The data

- 997 liquid US stocks (price ≥ $3, ≥ 500k shares a day), every 5-minute bar from **21 Aug to 12 Nov 2026**
  (59 trading days, 58,011 stock-days). Source: Yahoo's free chart data, the same feed Jarvis trades from.
- Two years of daily bars for the same stocks, for the swing-trading check.

## How a trade is replayed (`research/backtest.py`)

The same way Jarvis trades, on purpose a little pessimistic:

- Opening range = the first 15 minutes. Signal = the first 5-minute bar that **closes** above the range high.
- Jarvis only sees that bar after it closes, so the buy fills at the **next bar's open**, plus 0.05 % slippage.
- If one bar touches both the stop and the target, the **stop** is assumed to come first. A gap through the stop
  fills at the open, not the stop. Whatever is left is sold at 3:55 PM. Slippage is charged on every fill.
- Results are in **R**: 1R is what the trade risks at its stop. +0.16R a trade means that, on average, a trade made
  16 % of what it risked.
- The "likely range" resamples whole **days** (trades on the same day move together), giving a 90 % range for the
  average.

## Step by step: old rules → new rules

| Rule (each line adds one) | Trades | Win | Avg per trade | 90 % range |
|---|---:|---:|---:|---|
| **Before:** scanner watchlist, stop at the range middle, 2R target | 945 | 37 % | **−0.16R** | −0.26R to −0.06R |
| Same rules on every liquid $5–$40 stock | 15,408 | 37 % | −0.15R | −0.21R to −0.08R |
| + stop at the range low (wider) | 15,410 | 41 % | −0.10R | −0.16R to −0.05R |
| + skip stops closer than 1 % (costs eat them) | 13,035 | 42 % | −0.07R | −0.13R to −0.02R |
| + only breakouts by 10:30 AM New York | 8,233 | 43 % | −0.06R | −0.13R to +0.01R |
| + stock already up 4 %+ on the day | 1,085 | 51 % | +0.11R | −0.01R to +0.22R |
| **After:** + opening volume ≥ 1.5× normal ("in play") | 340 | 52 % | **+0.16R** | +0.02R to +0.30R |

Both halves of the period were positive for the new rules (+0.04R, then +0.23R), but the first half only barely.

### The same account, walked through both rule sets

2 % of the account risked a trade, whole shares, cash only, at most 10 trades a day:

| Start | Old rules | New rules | New rules' worst dip |
|---:|---:|---:|---:|
| $54 | $50.32 (−6.8 %) | $65.85 (+21.9 %) | −4.2 % |
| $200 | $186.40 (−6.8 %) | $270.50 (+35.2 %) | −4.7 % |
| $5,000 | $4,692.66 (−6.1 %) | $6,965.42 (+39.3 %) | −5.1 % |

**Don't read these as a forecast.** They are in-sample: the thresholds were chosen on these same days.

## Things that did NOT work (so Jarvis doesn't do them)

- **The scanner's daily setups** (20-day breakout, bull flag, reclaim of the 20-day average) made breakouts *worse*,
  not better: −0.18R to −0.23R a trade. They're still in the morning brief as background, but no longer pick trades.
- **The always-watched names** (QQQ, SPY, TSLA, NVDA, AAPL, PSQ, SH) lost −0.34R a trade on the old rules. Under the
  new rules they almost never qualify (they rarely move 4 % in a morning), which is the point.
- **Bigger targets** (3R, or no target) didn't help under the wide stop: about the same as 2R. Most trades end at
  the 3:55 PM close, not at the target.
- **The paper's own version** (Zarattini, Barbon & Aziz 2024: buy the high of a green first 5-minute bar, stop 10 %
  of the daily range) lost badly here. A stop that tight gets hit by normal noise, and 5-minute bars can't tell
  which came first inside the entry bar.
- **Breakouts after 10:30 AM** and **afternoon momentum** lost money.
- **Slippage matters:** at 0.10 % a side the new rules' edge shrinks to +0.13R and the range touches zero.

## Is it a knife-edge?

Average per trade for neighbouring settings (all with the wide stop, 2R, signals by 10:30):

| Up on the day | volume ≥ 1× | ≥ 1.5× | ≥ 2× | ≥ 3× |
|---|---:|---:|---:|---:|
| 2 %+ | +0.06R | +0.06R | +0.03R | +0.15R |
| 3 %+ | +0.10R | +0.09R | +0.05R | +0.15R |
| **4 %+** | +0.17R | **+0.16R** | +0.13R | +0.24R |
| 5 %+ | +0.17R | +0.17R | +0.12R | +0.23R |

Every cell is positive and the numbers change smoothly, which is what a real effect looks like. The strongest
driver is **how far the stock is already up**. Heavier volume helps at 3×, but with fewer trades.

## Swing trading (holding for days), first look

Day trading with under $25,000 in a US margin account runs into the pattern-day-trader limit, so real money would
probably need trades that last a few days. Published swing rules on 957 stocks, Nov 2024–Nov 2026, buying at the
next open, 0.05 % slippage (`research/swing.py`):

| Rule | Trades | Win | Avg | vs. S&P 500 same days | Held |
|---|---:|---:|---:|---:|---:|
| RSI(2) < 5, price above its 200-day average, sell above the 5-day average (Connors) | 3,186 | 61 % | +0.51 % | +0.23 % | 4.1 d |
| RSI(2) < 10, same | 6,130 | 62 % | +0.48 % | +0.18 % | 4.0 d |
| 3 down days above the 200-day average, sell the first up day | 7,333 | 57 % | +0.24 % | +0.11 % | 1.9 d |
| Baseline: buy any day, hold 5 days | 36,935 | 49 % | +0.04 % | −0.09 % | 5 d |

Promising, but the stock list is **today's** survivors (companies that collapsed are missing), which flatters
dip-buying. Not built into Jarvis yet: it's the obvious next project.

## The shadow book: the honest test

From now on, after every close Jarvis replays **every** breakout it saw that day, bought or not, under both the old
and the new rules, and keeps score (dashboard → Lab → Shadow book). These are days the rules have never seen.
Give it **a few hundred in-play signals** (a couple of months) before trusting the new rules with real money.

## Sources

- Zarattini, Barbon & Aziz (2024), *A Profitable Day Trading Strategy for the U.S. Equity Market*, SSRN 4729284:
  5-minute opening-range breakouts on "stocks in play" (top relative opening volume). The idea behind the in-play
  filter. Summaries report the unfiltered breakout returned 29 % over 2016–2023, against 1,600 %+ for the filtered one.
- Zarattini, Aziz & Barbon (2024), *Beat the Market: An Effective Intraday Momentum Strategy for S&P500 ETF (SPY)*,
  Swiss Finance Institute 24-97. Independent re-tests found weaker results than the paper.
- Connors & Alvarez (2008), *Short Term Trading Strategies That Work*: the RSI(2) pullback rules.
- Chague, De-Losso & Giovannetti (2019), *Day Trading for a Living?*: 97 % of people who day traded futures for
  300+ days in Brazil lost money.

## Re-running it

```
python3 research/fetch_data.py --out DATA        # ~10 min, ~200 MB
python3 research/build_table.py --data DATA
python3 research/backtest.py --data DATA --json docs/research.json
python3 research/swing.py --data DATA --json docs/swing.json
```
