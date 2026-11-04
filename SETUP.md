# Setting up Jarvis (about 15 minutes)

You do the account and key steps yourself. Keys go into GitHub's encrypted Secrets, never into a chat or a file.

## 1. Telegram bot (your phone)

1. In Telegram, search **@BotFather** → send `/newbot` → pick a name (e.g. *Jarvis*) and a username ending in `bot`.
2. BotFather replies with a **token**. Save it on your laptop in PowerShell:
   ```
   [Environment]::SetEnvironmentVariable('TELEGRAM_BOT_TOKEN','paste-token-here','User')
   ```
3. Open your new bot in Telegram and send it `hi`.
4. Tell Claude "Telegram's ready". Claude runs `python jarvis/telegram_setup.py`, which finds your chat ID and sends a test message.

## 2. GitHub repository

1. On github.com → **New repository** → name `jarvis-trader` → **Public** (needed for free 5-minute runs and the free dashboard) → don't add any files → Create.
   Public means anyone with the link can see the code, the paper trades and the dashboard. Your keys stay secret.
2. Tell Claude the repository link. Claude pushes the code (a GitHub sign-in window will pop up the first time).

## 3. Secrets (Settings → Secrets and variables → Actions → New repository secret)

| Name | Value |
|---|---|
| `ALPACA_API_KEY` | your Alpaca **paper** key |
| `ALPACA_SECRET_KEY` | your Alpaca **paper** secret |
| `TELEGRAM_BOT_TOKEN` | the token from BotFather |
| `TELEGRAM_CHAT_ID` | the number `telegram_setup.py` printed |
| `SEC_USER_AGENT` | `Jasper jasperjackman@icloud.com` (the SEC asks for a name and email) |

## 4. Switch it on

1. **Actions** tab → enable workflows if asked → **Jarvis** → **Run workflow** (a first test run).
2. **Settings → Pages** → Source: *Deploy from a branch* → Branch `main`, folder `/docs` → Save.
   Your dashboard appears at `https://<your-username>.github.io/jarvis-trader/` within a few minutes.
3. Jarvis messages you on Telegram on its first run. From then on it checks in every ~5 minutes on US trading days.

## Good to know

- GitHub runs scheduled jobs on a best-effort basis: a check-in can be a few minutes late, and a tap on
  **Buy** is acted on at the next check-in (up to ~5–10 min). Fine for paper trading.
- To change your city: edit `"timezone"` in `jarvis/settings.json` (`Australia/Sydney`, `Australia/Melbourne`,
  `Australia/Brisbane`, `Australia/Adelaide`, `Australia/Perth`, ...).
- To stop everything: send `/pause` in Telegram, or disable the workflow in the Actions tab.
