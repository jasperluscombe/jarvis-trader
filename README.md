# Jarvis HQ

Jasper's always-on paper-trading buddy. It runs on GitHub's servers (free), messages you on
Telegram, and shows a live dashboard of its bot crew. Your laptop can stay closed.

## What happens on a US trading day (Sydney time, Nov–Mar)

| Your time | Jarvis |
|---|---|
| ~12:00 AM | **Morning brief**: scans ~6,000 US stocks, reads the news, sends the watchlist and when to be awake |
| 1:30 AM | US market opens. Jarvis waits 15 min for the opening range |
| 1:45 AM – 2:10 AM | **Hunting**: every ~5 min it finds the stocks **in play** (up 4%+ today on 1.5× normal opening volume) and checks them for a breakout above the opening range. For each one: stop, target, replays, sizing to your limits, risk check |
| | **High or medium confidence + paper account**: buys by itself and tells you |
| | **Real money**: always asks you first: Buy / Skip (expires in 20 min) |
| | **Low confidence (coin flip)**: passes, logs why |
| 2:10 AM – 7:55 AM | Watches open trades. No new entries: late breakouts lost money in the backtest |
| 7:55 AM | Closes anything still open |
| ~8:05 AM | **Recap**: result, account, the shadow book (every breakout scored, bought or not), next open |

(April–October the times shift by 1–2 hours; Jarvis always messages in your local time.)

Telegram commands: `yes` / `no` (latest idea), `/status`, `/pause`, `/resume`, `/help`.

## Strategy: stocks in play (since Nov 2026)

A 59-day backtest of every opening-range breakout in ~1,000 US stocks ([research/RESULTS.md](research/RESULTS.md))
found the old rules lost about 0.16R a trade after realistic fills. Breakouts paid only in stocks that were already
**up 4 %+ on the day on 1.5× their normal opening volume**, breaking out by **10:30 AM New York**, with the stop at
the opening-range **low** at least 1 % away and a 2R target. Jarvis now trades only those (`"strategy": "in_play"`
and the `in_play` block in `jarvis/settings.json`; `"strategy": "classic"` brings back the old behaviour).

Those rules were chosen on the same 59 days they were tested on, so the backtest flatters them. The **shadow book**
on the dashboard's Lab tab scores every breakout Jarvis sees from now on: that's the real test.

## Safety rails

- Paper account (`"paper": true` in `trader/config.json`). Real money needs you to change that.
- Auto-buy works on paper only (`auto_trade_live: false` in `jarvis/settings.json`). On paper it buys
  medium and high confidence ideas (`auto_paper_min_confidence`); with real money it never buys below high,
  and only if you turn `auto_trade_live` on.
- Sizing grows with the account: each trade risks 3% of yesterday's closing value (`risk_per_trade_pct`),
  the daily loss limit is 10% (`daily_loss_pct`), orders up to 90%. Jarvis rewrites those $ numbers in
  `trader/config.json` each day. At $55 that's about $1.65 a trade and $5.50 a day.
- Goals: +2% a day, +8% a week (`daily_goal_pct` / `weekly_goal_pct`): +$1 / +$4 at $50. Once a goal is reached Jarvis stops
  opening trades (today / this week) to lock the profit in. Below the goal it keeps hunting, but never past the loss limits.
- QQQ (Nasdaq-100), SPY (S&P 500), TSLA, NVDA and AAPL are always watched, on top of the ~30 stocks from
  each morning's scan, and bought in part-shares (about $45) when a whole share costs more than an order may spend.
- PSQ and SH (1x inverse Nasdaq-100 / S&P 500 funds) are always watched too: they rise when the market
  falls, so Jarvis can profit on down days by buying, never short selling. No leveraged (2x/3x) funds. Alpaca holds its stop-loss; Jarvis sells at the
  target itself on a check-in.
- Every trade, auto or approved, goes through the risk check: 3% of the account max loss a trade, 10% a day,
  10 trades a day, reward:risk at least 1.5, a stop-loss on every order, no margin, no shorting, no options.
  These are **paper practice** limits (the day-trade counter is off). Real money stays locked until
  `live_limits_reviewed` is set to true in `jarvis/settings.json` after reviewing them.
- A "yes" re-checks the price and the limits before anything is sent.
- Everything is closed before the bell: nothing held overnight.

## Files

| Path | What |
|---|---|
| `jarvis/jarvis.py` | the engine: one check-in per run |
| `jarvis/settings.json` | auto-buy thresholds, watchlist size, your time zone |
| `trader/config.json` | your money limits |
| `tools/` | the day-trader-skill tools (MIT, Jake Schincariol), plus `movers.py` (stocks in play) |
| `research/` | the backtest and its results ([RESULTS.md](research/RESULTS.md)) |
| `docs/` | the dashboard (GitHub Pages): Home, Activity and Lab (backtest + shadow book) tabs |
| `.github/workflows/jarvis.yml` | the 5-minute schedule |
| `state/jarvis.json` | Jarvis's memory between check-ins |

## Setup

See [SETUP.md](SETUP.md).

Not financial advice. Odds are estimates from each stock's last 60 days, not promises. Most day traders lose money.
