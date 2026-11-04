# Jarvis HQ

Jasper's always-on paper-trading buddy. It runs on GitHub's servers (free), messages you on
Telegram, and shows a live dashboard of its bot crew. Your laptop can stay closed.

## What happens on a US trading day (Sydney time, Nov–Mar)

| Your time | Jarvis |
|---|---|
| ~12:00 AM | **Morning brief**: scans ~6,000 US stocks, reads the news, sends the watchlist and when to be awake |
| 1:30 AM | US market opens. Jarvis waits 15 min for the opening range |
| 1:45 AM – 7:30 AM | **Hunting**: every ~5 min it checks the watchlist for breakouts. For each one: stop, target, thousands of replays for the odds, sizing to your limits, risk check |
| | **High confidence + paper account**: buys by itself and tells you |
| | **Medium confidence**: asks you: Buy / Skip (expires in 20 min) |
| | **Low confidence (coin flip)**: passes, logs why |
| 7:55 AM | Closes anything still open |
| ~8:05 AM | **Recap**: result, account, next open |

(April–October the times shift by 1–2 hours; Jarvis always messages in your local time.)

Telegram commands: `yes` / `no` (latest idea), `/status`, `/pause`, `/resume`, `/help`.

## Safety rails

- Paper account (`"paper": true` in `trader/config.json`). Real money needs you to change that.
- Auto-buy works on paper only (`auto_trade_live: false` in `jarvis/settings.json`).
- Every trade, auto or approved, goes through the risk check: $1 max loss a trade, $3 a day,
  3 trades a day, reward:risk at least 1.5, a stop-loss on every order, no margin, no shorting, no options.
- A "yes" re-checks the price and the limits before anything is sent.
- Everything is closed before the bell: nothing held overnight.

## Files

| Path | What |
|---|---|
| `jarvis/jarvis.py` | the engine: one check-in per run |
| `jarvis/settings.json` | auto-buy thresholds, watchlist size, your time zone |
| `trader/config.json` | your money limits |
| `tools/` | the day-trader-skill tools (MIT, Jake Schincariol) |
| `docs/` | the dashboard (GitHub Pages) |
| `.github/workflows/jarvis.yml` | the 5-minute schedule |
| `state/jarvis.json` | Jarvis's memory between check-ins |

## Setup

See [SETUP.md](SETUP.md).

Not financial advice. Odds are estimates from each stock's last 60 days, not promises. Most day traders lose money.
