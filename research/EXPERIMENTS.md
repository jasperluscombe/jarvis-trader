# Experiment log

Every strategy test, what it was meant to show, and what it showed. Newest first. Numbers are copied from the
scripts' output; the scripts and the exact commands are listed so anyone can re-run them.

**Baseline (live, paper):** `in_play` v1 (since 16 Nov 2026): 15-minute opening range; buy the first 5-minute
close above it by 10:30 AM New York in a $5–$40 stock up ≥ 4 % on the day with opening volume ≥ 1.5× normal; stop
at the range low (≥ 1 % away); target 2R; sell everything at 3:55 PM; 3 % of the account at risk a trade.

**Experimental:** none promoted. A new version replaces the baseline only if it passes the promotion rules below.

## Promotion rules (fixed 16 Nov 2026, before the tests below)

A candidate must, against the baseline on the same days:
1. be better out of sample: walk-forward on 5-minute bars **and** the 2-year hourly test, by ≥ 0.05R a trade;
2. stay positive with 0.2 % slippage a side;
3. have ≥ 200 out-of-sample trades;
4. not have a worse worst-dip on a $200 account.
Then it runs in the shadow book for ≥ 20 trading days before it can trade.

---

## E5 · 16 Nov 2026 · Two-year check on hourly bars (`research/hourly.py`)

*Question:* does the in-play idea hold up over two years and several market moods, not just the last 60 days?
Rules copied from the live bot and fixed before looking: first hour as the opening range, in play = up ≥ 4 % and
first-hour volume ≥ 1.5× its 14-day average, buy the first hourly close above the first-hour high by 12:30, stop at
the first-hour low, 2R target, sell at the close. 0.05 % slippage a side.
Data: 13 Dec 2024 – 13 Nov 2026, 475 trading days, 698 stocks ($5–$40, ≥ 1M shares a day).

| | Trades | Win | Avg per trade | 90 % range |
|---|---:|---:|---:|---|
| **In play + breakout (the live idea)** | 1,866 | 49 % | **−0.009R** | −0.029 to +0.012 |
| Every first-hour breakout, no filter | 43,542 | 45 % | −0.051R | −0.069 to −0.035 |
| Breakout, up 4 %+ only | 4,776 | 50 % | −0.004R | −0.025 to +0.018 |
| In play, bought at 11:30 with no breakout | 5,252 | 47 % | −0.013R | −0.038 to +0.014 |
| In play + breakout at 0.2 % slippage | 1,866 | 43 % | −0.057R | −0.077 to −0.037 |

Quarter by quarter, the in-play filter beat no filter in **9 of 9 quarters** (by 0.01R to 0.10R), but was itself
only between −0.04R and +0.02R.

*Verdict:* **the in-play filter reliably makes breakouts less bad; it did not make them profitable over two years.**
The +0.16R from the 60-day test (E2) was not repeated. Caveat: hourly bars are a rough stand-in (a one-hour opening
range and later entries than the live bot's 15 minutes), so this doesn't rule out an edge in the faster version.
But it means the 60-day result can't be taken at face value.

## E4 · 16 Nov 2026 · Walk-forward on 5-minute bars (`research/walkforward.py`)

*Question:* if Jarvis had picked its settings using only past days, how would it have done on the days after?
384 rule sets × 2 opening-range lengths (768) fixed in advance; anchored walk-forward: train on days 1–20, test
21–30; train 1–30, test 31–40; and so on (40 test days, 21 Sep – 13 Nov 2026). Picked by average R minus its standard
error.

| Fold | Picked on the training days | Train | Test |
|---|---|---:|---:|
| 21 Sep – 2 Oct | 5-min range, up 5 %+, vol 1.5×+, mid stop, 3R, by 10:00 | +1.15R (31) | **−0.17R** (24) |
| 5 – 16 Oct | same | +0.58R (55) | **−0.34R** (32) |
| 19 – 30 Oct | 15-min range, up 5 %+, vol 1×+, mid stop, 3R, by 10:00 | +0.34R (109) | +0.08R (24) |
| 2 – 13 Nov | same | +0.29R (133) | +0.37R (125) |

Same 40 days: walk-forward **+0.160R** (205 trades, 90 % range **−0.155 to +0.445**), old rules −0.007R,
no in-play filter −0.034R, live rules +0.147R (but those were chosen with hindsight on these days).
Slippage: +0.121R at 0.1 %, +0.043R at 0.2 %, **−0.035R at 0.3 %** a side.
$200 cash account through the out-of-sample trades: 1 % risk −1.4 % (worst dip −10 %), 2 % risk −1.7 %
(−14 %), 3 % risk +8.7 % (−19 %); part-shares made no real difference.

Across all 768 rule sets the ingredient that mattered most was **how far the stock was already up**
(median +0.06R at 2 %+ up, +0.16R at 5 %+); the volume threshold made no consistent difference.

*Verdict:* positive on average but **not distinguishable from zero**; two of four folds lost; most of the profit came
from the last two weeks. The edge vanishes at 0.3 % slippage a side.

## E3 · 16 Nov 2026 · Swing trades with a 1:2 stop and target (`research/swing_rr.py`)

Dip buying (Connors RSI 2) and 20-day breakouts, held for days, on ~950 stocks Sep 2025 – Nov 2026: every
version within ±0.05R of a random entry in an uptrend (+0.01R). *Verdict:* no edge. Not adopted.

## E2 · 13 Nov 2026 · In-play filter on 60 days of 5-minute bars (`research/backtest.py`)

Old rules −0.16R a trade; in-play rules +0.16R (340 trades). In sample: the rules were chosen on these days.
Adopted as `in_play` v1 (PR #2) on the strength of this test and the published research. **E4 and E5 have since
weakened this result.**

## E1 · 13 Nov 2026 · The original rules (`research/backtest.py`)

Scanner watchlist, stop at the range middle, 2R: −0.158R a trade over 945 trades (90 % range −0.26 to −0.06).
*Verdict:* lost money after costs. Replaced.
