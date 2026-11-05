#!/usr/bin/env python3
"""Jarvis: one "tick" of Jasper's trading assistant.

GitHub Actions runs this every ~5 minutes on US trading days. Each tick it:

  1. reads Telegram for your replies (Buy / Skip / yes / no / /status / /pause / /resume)
  2. syncs cash and positions from Alpaca
  3. does whatever the time of day calls for (New York time):
       08:00 .. open        morning brief: scan, news, watchlist, when to be awake
       09:45 .. 15:30       hunt: watch the watchlist for opening-range breakouts;
                            for each one: stop + target, 10,000-ish replays,
                            sizing to your limits, risk check; then either
                            auto-buys (paper + high confidence) or asks you
       flat-by .. close     closes anything still open
       after the close      sends the day's recap
  4. writes docs/state.json for the dashboard and state/jarvis.json for the next tick

Standard library only. Secrets come from environment variables:
  ALPACA_API_KEY, ALPACA_SECRET_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, SEC_USER_AGENT

  python jarvis/jarvis.py                    one tick, for real
  python jarvis/jarvis.py --dry-run          no orders, Telegram messages printed instead of sent
  python jarvis/jarvis.py --now "2026-11-04 10:30"   pretend it is this New York time
"""

import argparse
import datetime as dt
import html
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
P = lambda *a: os.path.join(ROOT, *a)  # noqa: E731

STATE_PATH = P("state", "jarvis.json")
DASH_PATH = P("docs", "state.json")
SETTINGS_PATH = P("jarvis", "settings.json")
CONFIG_PATH = P("trader", "config.json")
PORTFOLIO_PATH = P("trader", "portfolio.json")
BROKER_LOG = P("trader", "state", "broker.json")
WATCHLIST = P("trader", "watchlist.json")
WORK = P("trader", "work")
UTC = dt.timezone.utc

BOTS = {
    "jarvis":  ("Jarvis", "Your buddy. Messages you, takes your yes."),
    "scanner": ("Scout", "Scans ~6,000 US stocks for setups before the open."),
    "news":    ("Herald", "Reads headlines and SEC filings for the watchlist."),
    "entry":   ("Spotter", "Watches each chart for a breakout above the opening range."),
    "oracle":  ("Oracle", "Replays the rest of the day thousands of times: the odds."),
    "risk":    ("Guard", "Sizes the trade to your $ limits and blocks anything over them."),
    "broker":  ("Trader", "Sends approved orders to Alpaca and closes by the bell."),
}

SETUP_NAMES = {
    "breakout_20d": "20-day high breakout", "bull_flag": "bull flag", "reclaim_ma20": "back above its 20-day average",
    "oversold": "oversold", "oversold_bounce": "bouncing after a drop",
}


# --------------------------------------------------------------------------- time zones
# No tzdata needed: the US and Australian daylight-saving rules are fixed and simple.

def _nth_sunday(year, month, n):
    d = dt.date(year, month, 1)
    d += dt.timedelta(days=(6 - d.weekday()) % 7)
    return d + dt.timedelta(weeks=n - 1)


def ny_offset_hours(utc):
    y = utc.year
    start = dt.datetime.combine(_nth_sunday(y, 3, 2), dt.time(7, 0), UTC)   # 2:00 EST
    end = dt.datetime.combine(_nth_sunday(y, 11, 1), dt.time(6, 0), UTC)    # 2:00 EDT
    return -4 if start <= utc < end else -5


AU_ZONES = {  # name: (standard offset, observes daylight saving, short label)
    "Australia/Sydney": (10, True, "Sydney"), "Australia/Melbourne": (10, True, "Melbourne"),
    "Australia/Canberra": (10, True, "Canberra"), "Australia/Hobart": (10, True, "Hobart"),
    "Australia/Brisbane": (10, False, "Brisbane"), "Australia/Adelaide": (9.5, True, "Adelaide"),
    "Australia/Darwin": (9.5, False, "Darwin"), "Australia/Perth": (8, False, "Perth"),
}


def au_offset_hours(utc, zone):
    std, dst, _ = AU_ZONES.get(zone, AU_ZONES["Australia/Sydney"])
    if not dst:
        return std
    y = utc.year
    # starts first Sunday of October 02:00 standard time; ends first Sunday of April 03:00 daylight time
    start = dt.datetime.combine(_nth_sunday(y, 10, 1), dt.time(2, 0), UTC) - dt.timedelta(hours=std)
    end = dt.datetime.combine(_nth_sunday(y, 4, 1), dt.time(3, 0), UTC) - dt.timedelta(hours=std + 1)
    return std + 1 if (utc >= start or utc < end) else std


def to_ny(utc):
    return (utc + dt.timedelta(hours=ny_offset_hours(utc))).replace(tzinfo=None)


def ny_to_utc(naive_ny):
    guess = naive_ny.replace(tzinfo=UTC) + dt.timedelta(hours=5)
    return naive_ny.replace(tzinfo=UTC) - dt.timedelta(hours=ny_offset_hours(guess))


def to_local(utc, zone):
    return (utc + dt.timedelta(hours=au_offset_hours(utc, zone))).replace(tzinfo=None)


def clock_str(naive):
    return naive.strftime("%I:%M %p").lstrip("0")


def day_str(naive):
    return naive.strftime("%a %d %b").replace(" 0", " ")


# --------------------------------------------------------------------------- small helpers

def load_json(path, default=None):
    try:
        with open(path, encoding="utf-8-sig") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, default=str)
        fh.write("\n")
    os.replace(tmp, path)


def money(x, sign=False):
    if x is None:
        return "?"
    s = "-" if x < 0 else ("+" if sign and x > 0 else "")
    return "%s$%.2f" % (s, abs(x))


def pct(x):
    return "?" if x is None else "%d%%" % round(100 * x)


def esc(s):
    return html.escape(str(s), quote=False)


def hhmm(s):
    h, m = str(s).split(":")[:2]
    return dt.time(int(h), int(m))


def run_tool(name, *args, timeout=300):
    """Run one of the trading tools. Returns (exit code, stdout, stderr)."""
    cmd = [sys.executable, "-I", os.path.join(TOOLS, name)] + [str(a) for a in args]
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 124, "", "%s timed out" % name
    return r.returncode, r.stdout.decode("utf-8", "replace"), r.stderr.decode("utf-8", "replace")


def tool_json(name, *args, timeout=300):
    code, out, err = run_tool(name, *args, timeout=timeout)
    try:
        return code, json.loads(out), err
    except ValueError:
        return code, None, (err or out).strip()


# --------------------------------------------------------------------------- Alpaca

class Alpaca:
    def __init__(self, paper):
        self.paper = paper
        self.base = "https://paper-api.alpaca.markets" if paper else "https://api.alpaca.markets"
        self.key = os.environ.get("ALPACA_API_KEY", "")
        self.secret = os.environ.get("ALPACA_SECRET_KEY", "")
        self.ok = bool(self.key and self.secret)

    def call(self, method, path, body=None):
        if not self.ok:
            raise RuntimeError("Alpaca keys are not set (ALPACA_API_KEY / ALPACA_SECRET_KEY)")
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.base + path, data=data, method=method, headers={
            "APCA-API-KEY-ID": self.key, "APCA-API-SECRET-KEY": self.secret,
            "Content-Type": "application/json", "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read()
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:300]
            raise RuntimeError("Alpaca %s %s: HTTP %s %s" % (method, path, e.code, detail))
        return json.loads(raw) if raw.strip() else None

    def get(self, path):
        return self.call("GET", path)


# --------------------------------------------------------------------------- Telegram

class Telegram:
    def __init__(self, dry_run):
        self.token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        # Keep only the ID itself (digits and a leading minus for groups): a stray space, dot or quote pasted
        # into the secret makes every reply look like it came from a stranger.
        raw = str(os.environ.get("TELEGRAM_CHAT_ID", "")).strip()
        digits = "".join(ch for ch in raw if ch.isdigit())
        self.chat = ("-" if raw.startswith("-") else "") + digits if digits else ""
        self.dry = dry_run
        self.ok = bool(self.token and self.chat)
        self.health = {}

    def api(self, method, payload):
        url = "https://api.telegram.org/bot%s/%s" % (self.token, method)
        req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=40) as r:
            return json.loads(r.read())

    def send(self, text, buttons=None):
        if self.dry or not self.ok:
            print("\n[telegram%s]\n%s%s\n" % ("" if self.ok else " - not configured", text,
                  ("\n" + " | ".join(b[0] for b in buttons)) if buttons else ""))
            return None
        payload = {"chat_id": self.chat, "text": text, "parse_mode": "HTML",
                   "disable_web_page_preview": True}
        if buttons:
            payload["reply_markup"] = {"inline_keyboard": [[{"text": t, "callback_data": d} for t, d in buttons]]}
        try:
            mid = self.api("sendMessage", payload).get("result", {}).get("message_id")
            self.health["sent_ok"] = self.health.get("sent_ok", 0) + 1
            return mid
        except Exception as e:  # never let a message failure stop trading logic
            why = str(e)
            if isinstance(e, urllib.error.HTTPError):
                try:
                    why = "HTTP %s %s" % (e.code, json.loads(e.read()).get("description", ""))
                except Exception:
                    why = "HTTP %s" % e.code
            if self.token:
                why = why.replace(self.token, "<token>")
            self.health["send_failed"] = self.health.get("send_failed", 0) + 1
            self.health["last_error"] = why[:200]
            print("telegram send failed:", why, file=sys.stderr)
            return None

    def edit_buttons_off(self, message_id, note):
        if self.dry or not self.ok or not message_id:
            return
        try:
            self.api("editMessageReplyMarkup", {"chat_id": self.chat, "message_id": message_id,
                                                "reply_markup": {"inline_keyboard": []}})
            if note:
                self.send(note)
        except Exception:
            pass

    def updates(self, offset):
        if not self.ok:
            return []
        try:
            res = self.api("getUpdates", {"offset": offset, "timeout": 0,
                                          "allowed_updates": ["message", "callback_query"]})
            return res.get("result", [])
        except Exception as e:
            self.health["updates_error"] = str(e).replace(self.token, "<token>")[:200]
            print("telegram getUpdates failed:", e, file=sys.stderr)
            return []

    def answer(self, callback_id, text):
        if self.dry or not self.ok:
            return
        try:
            self.api("answerCallbackQuery", {"callback_query_id": callback_id, "text": text[:190]})
        except Exception:
            pass


# --------------------------------------------------------------------------- Jarvis

class Jarvis:
    def __init__(self, args):
        self.args = args
        # a dry run keeps its own state so it never pollutes the real one
        self.state_path = STATE_PATH.replace(".json", ".dryrun.json") if args.dry_run else STATE_PATH
        self.dash_path = DASH_PATH.replace(".json", ".dryrun.json") if args.dry_run else DASH_PATH
        self.settings = load_json(SETTINGS_PATH, {})
        self.cfg = load_json(args.test_config or CONFIG_PATH, {})
        self.st = load_json(self.state_path, {}) or {}
        self.tz = self.settings.get("timezone", "Australia/Sydney")
        if args.now:
            self.now_utc = ny_to_utc(dt.datetime.strptime(args.now, "%Y-%m-%d %H:%M"))
        else:
            self.now_utc = dt.datetime.now(UTC)
        self.ny = to_ny(self.now_utc)
        self.today = self.ny.date().isoformat()
        self.paper = bool(self.cfg.get("paper", True))
        self.alpaca = Alpaca(self.paper)
        self.tg = Telegram(args.dry_run)
        self.account = None
        self.positions = []
        self.cal = None  # today's market session (open, close) in New York time, or None
        self.errors = []
        for k, v in {"tg_offset": 0, "paused": False, "proposals": [], "events": [], "trades": [],
                     "done": {}, "candidates": [], "candidates_day": None, "seen": {}, "bots": {}}.items():
            self.st.setdefault(k, v)
        if self.st.get("seen_day") != self.today:
            self.st["seen"], self.st["seen_day"] = {}, self.today
        if args.test_candidates:
            self.st["candidates"] = [{"symbol": s, "setups": ["test"]} for s in args.test_candidates.split(",")]
            self.st["candidates_day"] = self.today

    def extra(self, tool):
        """Extra flags for a tool: the pinned clock, plus test-only overrides."""
        a = self.args
        out = ["--now", a.now] if a.now else []
        if a.test_config and tool in ("entry.py", "exit.py", "size.py", "check.py"):
            out += ["--config", a.test_config]
        if a.test_portfolio and tool in ("size.py", "check.py"):
            out += ["--portfolio", a.test_portfolio]
        if a.test_entry_data and tool == "entry.py":
            out += ["--offline", a.test_entry_data]
        if a.test_tm_data and tool == "timemachine.py":
            out += ["--offline", a.test_tm_data]
        if a.dry_run and tool == "check.py":
            out += ["--state", BROKER_LOG.replace(".json", ".dryrun.json")]
        return out

    # ---- bookkeeping
    def local(self, utc=None):
        return to_local(utc or self.now_utc, self.tz)

    def tz_label(self):
        return AU_ZONES.get(self.tz, AU_ZONES["Australia/Sydney"])[2]

    def ny_time_local(self, t):
        """A New York clock time today, as your local time string."""
        return clock_str(self.local(ny_to_utc(dt.datetime.combine(self.ny.date(), t))))

    def event(self, bot, text):
        self.st["events"].append({"t": self.now_utc.isoformat(timespec="seconds"), "bot": bot, "text": text})
        self.st["events"] = self.st["events"][-80:]
        self.bot(bot, "working", text)
        print("[%s] %s" % (bot, text))

    def bot(self, bot, status, text):
        self.st["bots"][bot] = {"status": status, "text": text, "t": self.now_utc.isoformat(timespec="seconds")}

    def once(self, key):
        """True the first time it is called for this key today."""
        if self.st["done"].get(key) == self.today:
            return False
        self.st["done"][key] = self.today
        return True

    def mode(self):
        return "PAPER" if self.paper else "REAL MONEY"

    # ---- broker log shared with the risk check
    def broker_path(self):
        return BROKER_LOG.replace(".json", ".dryrun.json") if self.args.dry_run else BROKER_LOG

    def broker_log(self):
        return load_json(self.broker_path(), {"orders": []}) or {"orders": []}

    def log_order(self, rec):
        log = self.broker_log()
        log.setdefault("orders", []).append(rec)
        save_json(self.broker_path(), log)

    def entries_today(self):
        return [r for r in self.broker_log().get("orders", [])
                if r.get("date") == self.today and r.get("kind") == "entry" and r.get("status") == "placed"]

    def risk_used_today(self):
        return round(sum(float(r.get("max_loss") or 0) for r in self.entries_today()), 2)

    # ---- sync
    def sync(self):
        if not self.alpaca.ok:
            self.errors.append("Alpaca keys missing")
            return
        try:
            self.account = self.alpaca.get("/v2/account")
            self.positions = self.alpaca.get("/v2/positions") or []
            cal = self.alpaca.get("/v2/calendar?start=%s&end=%s" % (self.today, self.today)) or []
            if cal and cal[0].get("date") == self.today:
                self.cal = (hhmm(cal[0]["open"]), hhmm(cal[0]["close"]))
            nxt = self.alpaca.get("/v2/calendar?start=%s&end=%s" % (
                self.today, (self.ny.date() + dt.timedelta(days=10)).isoformat())) or []
            self.st["next_sessions"] = [
                {"date": c["date"], "open": c["open"], "close": c["close"]} for c in nxt[:6]]
        except Exception as e:
            self.errors.append(str(e))
            print("sync failed:", e, file=sys.stderr)
            return
        save_json(PORTFOLIO_PATH, {
            "cash": float(self.account.get("cash") or 0),
            "positions": [{"symbol": p["symbol"], "qty": float(p["qty"])} for p in self.positions],
            "synced_from": "alpaca", "at": self.now_utc.isoformat(timespec="seconds")})
        self.scale_limits()

    def size_base(self):
        """The account value sizing is measured from: yesterday's closing value, so it holds still all day."""
        return self.last_close()

    def last_close(self):
        """Yesterday's closing value. A brand-new account reports 0 there, so use today's value instead
        (otherwise the whole balance looks like today's profit)."""
        a = self.account or {}
        last = float(a.get("last_equity") or 0)
        return last if last > 0 else float(a.get("equity") or 0)

    def scale_limits(self):
        """Grow (or shrink) the $ limits with the account: risk a fixed % of its value, not a fixed $1."""
        S = self.settings
        pct = S.get("risk_per_trade_pct")
        base = self.size_base()
        if not pct or base <= 0 or self.args.test_config:
            return
        new = {
            "budget": round(base, 2),
            "max_loss_per_trade_usd": round(base * float(pct) / 100, 2),
            "max_daily_loss_usd": round(base * float(S.get("daily_loss_pct", 10)) / 100, 2),
            "max_order_usd": round(base * float(self.cfg.get("max_position_pct") or 90) / 100, 2),
        }
        changed = {k: v for k, v in new.items() if self.cfg.get(k) != v}
        if not changed:
            return
        self.cfg.update(new)
        if not self.args.dry_run:
            save_json(CONFIG_PATH, self.cfg)
        self.event("risk", "Limits resized to your %s account: %s a trade, %s a day, orders up to %s." % (
            money(base), money(new["max_loss_per_trade_usd"]), money(new["max_daily_loss_usd"]), money(new["max_order_usd"])))

    # ---- Telegram replies
    def handle_messages(self):
        ups = self.tg.updates(self.st["tg_offset"])
        for u in ups:
            self.st["tg_offset"] = u["update_id"] + 1
            if "callback_query" in u:
                cq = u["callback_query"]
                if str(cq.get("message", {}).get("chat", {}).get("id")) != self.tg.chat:
                    continue
                action, _, pid = str(cq.get("data", "")).partition(":")
                reply = self.decide(pid, action == "buy", source="button")
                self.tg.answer(cq["id"], reply)
            elif "message" in u:
                m = u["message"]
                cid = str(m.get("chat", {}).get("id"))
                if cid != self.tg.chat:
                    # Masked, the repo is public: enough to tell the IDs apart, not to use them.
                    mask = lambda s: "%s…%s (%d digits)" % (s[:2], s[-2:], len(s))
                    self.tg.health["ignored_other_chat"] = "message from %s, secret is %s" % (mask(cid), mask(self.tg.chat))
                    continue
                self.tg.health["handled"] = self.tg.health.get("handled", 0) + 1
                self.command(str(m.get("text", "")).strip())

    def command(self, text):
        t = text.lower().strip(" !.")
        pend = [p for p in self.st["proposals"] if p["status"] == "pending"]
        if t in ("/start", "/help", "help"):
            self.tg.send(self.help_text())
        elif t in ("/status", "status"):
            self.tg.send(self.status_text())
        elif t in ("/pause", "pause", "stop"):
            self.st["paused"] = True
            self.event("jarvis", "Paused by you: no new trades until you send /resume.")
            self.tg.send("⏸ Paused. I won't open any new trades (paper or real) until you send /resume. "
                         "Anything already open still has its stop and target, and I'll still close it by the bell.")
        elif t in ("/resume", "resume", "start"):
            self.st["paused"] = False
            self.event("jarvis", "Resumed by you.")
            self.tg.send("▶️ Back on. I'll keep watching the charts.")
        elif t in ("yes", "y", "yep", "yeah", "buy", "buy it", "do it", "go"):
            if not pend:
                self.tg.send("Nothing is waiting for a yes right now.")
            else:
                self.tg.send(self.decide(pend[-1]["id"], True, source="text"))
        elif t in ("no", "n", "nah", "skip", "pass"):
            if pend:
                self.tg.send(self.decide(pend[-1]["id"], False, source="text"))
        else:
            self.tg.send("I understand: <b>yes</b> / <b>no</b> (for the latest idea), /status, /pause, /resume, /help.")

    def help_text(self):
        return ("🤖 <b>Jarvis here.</b>\n"
                "I watch the US market for you (it's open %s–%s your time on trading days).\n\n"
                "• I message you a <b>morning brief</b> before the open\n"
                "• When a chart breaks out I send a <b>trade idea</b> with the profit if it works, the loss if it doesn't, and the odds. Tap <b>Buy</b> or <b>Skip</b>\n"
                "• On the paper account I buy ideas that pass your rules by myself and tell you (real money always asks first)\n"
                "• I close everything before the bell and send a <b>recap</b>\n\n"
                "Commands: /status /pause /resume, or just reply yes / no.\n"
                "Note: I check in every ~5 minutes while the market's around, every ~30 minutes otherwise, "
                "so a reply can take a little while."
                % (self.ny_time_local(dt.time(9, 30)), self.ny_time_local(dt.time(16, 0))))

    def status_text(self):
        a = self.account or {}
        eq, last = float(a.get("equity") or 0), self.last_close()
        lines = ["📊 <b>Status</b> (%s)" % self.mode(),
                 "Account: %s (today %s)" % (money(eq), money(eq - last, sign=True)),
                 "Trades today: %d of %s · risk used %s of %s" % (
                     len(self.entries_today()), self.cfg.get("max_trades_per_day"),
                     money(self.risk_used_today()), money(float(self.cfg.get("max_daily_loss_usd") or 0))),
                 "Auto-buy: %s" % self.auto_label(),
                 "Paused: %s" % ("yes" if self.st["paused"] else "no")]
        for p in self.positions:
            lines.append("• %s %s sh, %s (%s)" % (p["symbol"], p["qty"], money(float(p["market_value"])),
                                                 money(float(p["unrealized_pl"]), sign=True)))
        return "\n".join(lines)

    # ---- approvals
    def find(self, pid):
        for p in self.st["proposals"]:
            if p["id"] == pid:
                return p
        return None

    def decide(self, pid, yes, source):
        p = self.find(pid)
        if not p:
            return "I can't find that idea any more."
        if p["status"] != "pending":
            return "%s is already %s." % (p["symbol"], p["status"])
        if self.now_utc > dt.datetime.fromisoformat(p["expires"]):
            p["status"] = "expired"
            self.tg.edit_buttons_off(p.get("msg_id"), None)
            return "⌛ %s expired: the price has probably moved. I'll send a fresh idea if it sets up again." % p["symbol"]
        if not yes:
            p["status"] = "skipped"
            self.event("jarvis", "You skipped %s." % p["symbol"])
            self.tg.edit_buttons_off(p.get("msg_id"), None)
            return "👍 Skipped %s." % p["symbol"]
        if self.st["paused"]:
            return "I'm paused. Send /resume first."
        if self.live_locked():
            return "🔒 Real money is locked until your limits are reviewed."
        p["approved_by"] = source
        self.event("jarvis", "You said yes to %s. Re-checking the price and your limits." % p["symbol"])
        ok, msg = self.recheck_and_place(p, source="your yes")
        self.tg.edit_buttons_off(p.get("msg_id"), None)
        return msg

    def recheck_and_place(self, p, source):
        """Fresh quote -> resize -> risk check -> place. A yes never skips the rules."""
        sym = p["symbol"]
        if not self.args.now:
            run_tool("alerts.py", "quote", sym, "--write", "trader/prices.json", timeout=60)
        sizing, order, why = self.size_and_check(sym)
        if why:
            p["status"] = "blocked"
            self.event("risk", "%s no longer fits your limits: %s" % (sym, why))
            return False, "🛑 Not placed: %s no longer fits your limits (%s)." % (sym, why)
        p["order"], p["sizing"] = order, sizing
        return self.place(p, source)

    def is_fractional(self, sym):
        return sym in set(self.settings.get("fractional") or [])

    def size_fractional(self, plan):
        """Size a part-share buy (e.g. QQQ at ~$500 with a $50 account) to the same $ limits size.py uses."""
        c = self.cfg
        entry, stop, target = float(plan["entry"]), float(plan["stop"]), float(plan["target"])
        rps = round(entry - stop, 4)
        if rps <= 0:
            return None, None, "the stop isn't below the entry"
        budget = float(c.get("budget") or 0)
        cash = float((self.account or {}).get("cash") or (load_json(self.portfolio_path(), {}) or {}).get("cash") or budget)
        cap = min(float(c.get("max_order_usd") or budget), budget * float(c.get("max_position_pct") or 100) / 100,
                  cash - budget * float(c.get("cash_buffer_pct") or 0) / 100)
        by_loss = float(c.get("max_loss_per_trade_usd") or 0) / rps * entry
        notional = int(min(cap, by_loss) * 100) / 100.0
        if notional < float(c.get("min_order_usd") or 1):
            return None, None, "only %s fits your limits, under the %s minimum order" % (money(notional), money(float(c.get("min_order_usd") or 1)))
        qty = notional / entry
        rr = (target - entry) / rps
        if rr + 1e-9 < float(c.get("min_reward_risk") or 0):
            return None, None, "reward:risk %.2f is under your %.2f minimum" % (rr, float(c.get("min_reward_risk")))
        bound = "max loss" if by_loss <= cap else "cash / order cap"
        max_loss = round(qty * rps, 2)
        sizing = {"symbol": plan["symbol"], "entry": entry, "stop": stop, "target": target, "risk_per_share": rps,
                  "reward_risk": round(rr, 2), "qty": round(qty, 6), "cost": notional, "max_loss": max_loss,
                  "bound_by": bound, "fractional": True, "refusal": None}
        order = {"symbol": plan["symbol"], "side": "buy", "notional": "%.2f" % notional, "type": "market",
                 "time_in_force": "day",
                 "why": "part-share %s breakout: %s, bound by your %s" % (plan["symbol"], money(notional), bound),
                 "plan": {"entry": entry, "stop": stop, "target": target, "risk_per_share": rps, "max_loss": max_loss,
                          "setup": plan.get("setup"), "entry_time": plan.get("entry_time"), "flat_by": plan.get("flat_by")}}
        return sizing, order, None

    def portfolio_path(self):
        return self.args.test_portfolio or PORTFOLIO_PATH

    def size_and_check(self, sym):
        """Size the planned trade and run the risk check. Returns (sizing, order, None) or (None, None, why)."""
        plan_path = os.path.join("trader", "work", "%s-plan.json" % sym)
        orders_path = os.path.join("trader", "work", "%s-orders.json" % sym)
        plan = load_json(P(plan_path)) or {}
        # Part-shares only when a whole share costs more than one order may spend; otherwise whole shares,
        # which carry their stop and target at Alpaca as a bracket.
        too_dear = float(plan.get("entry") or 0) > float(self.cfg.get("max_order_usd") or 0)
        if self.is_fractional(sym) and too_dear:
            sizing, order, why = self.size_fractional(plan)
            if why:
                return None, None, why
            save_json(P(orders_path), [order])
        else:
            code, sz, err = tool_json("size.py", "--plan", plan_path, "--write", orders_path, "--json", *self.extra("size.py"))
            sizing = (sz or {}).get("sizing") or {}
            if not sz or sizing.get("refusal") or not sz.get("orders"):
                return None, None, sizing.get("refusal") or (err or "sizing failed")[-160:]
            order = sz["orders"][0]
            sizing["qty"] = int(float(order["qty"]))
        code, chk, err = tool_json("check.py", "--orders", orders_path, "--no-write", "--json", *self.extra("check.py"))
        res = ((chk or {}).get("results") or [{}])[0]
        if not chk or res.get("verdict") != "PASS":
            return None, None, "; ".join(res.get("reasons") or []) or (err or "risk check failed")[-160:]
        return sizing, order, None

    def qty_text(self, p):
        s = p["sizing"]
        if s.get("fractional"):
            return "%s of %s (≈%.4f shares)" % (money(s["cost"]), p["symbol"], s["qty"])
        return "%d %s" % (s["qty"], p["symbol"])

    def place(self, p, source):
        o = {k: v for k, v in p["order"].items() if k not in ("why", "plan")}
        # The sizing tool writes the MCP tool's flat fields; Alpaca's REST API wants them nested.
        tp, sl = o.pop("take_profit_limit_price", None), o.pop("stop_loss_stop_price", None)
        if tp is not None:
            o["take_profit"] = {"limit_price": str(tp)}
        if sl is not None:
            o["stop_loss"] = {"stop_price": str(sl)}
        o["client_order_id"] = "jarvis-%s" % p["id"]
        s = p["sizing"]
        if self.args.dry_run:
            res = {"id": "dry-run", "status": "dry-run"}
        else:
            try:
                res = self.alpaca.call("POST", "/v2/orders", o)
            except Exception as e:
                p["status"] = "failed"
                self.event("broker", "Order for %s failed: %s" % (p["symbol"], e))
                return False, "⚠️ Alpaca refused the %s order: %s" % (p["symbol"], e)
        p["status"] = "placed"
        p["broker_id"] = res.get("id")
        self.log_order({"date": self.today, "at": self.now_utc.isoformat(timespec="seconds"),
                        "symbol": p["symbol"], "side": "buy", "kind": "entry", "qty": o.get("qty") or s.get("qty"),
                        "notional": o.get("notional"), "max_loss": s.get("max_loss"), "status": "placed",
                        "broker_id": res.get("id"), "source": source, "paper": self.paper})
        self.st["trades"].append({"date": self.today, "t": self.now_utc.isoformat(timespec="seconds"),
                                  "symbol": p["symbol"], "qty": s.get("qty"), "entry": s.get("entry"),
                                  "stop": s.get("stop"), "target": s.get("target"), "max_loss": s.get("max_loss"),
                                  "target_profit": p.get("target_profit"), "source": source,
                                  "confidence": p.get("confidence"), "paper": self.paper, "result": None})
        self.st["trades"] = self.st["trades"][-150:]
        if s.get("fractional"):
            # Alpaca won't attach a stop/target to part-shares: put a real stop order at the broker as soon as
            # the buy fills, and Jarvis sells at the target itself on a check-in.
            m = {"symbol": p["symbol"], "date": self.today, "order_id": res.get("id"), "stop": s["stop"],
                 "target": s["target"], "qty": None, "stop_order_id": None, "done": False}
            self.st.setdefault("managed", []).append(m)
            if not self.args.dry_run:
                for _ in range(8):
                    if self.place_managed_stop(m):
                        break
                    time.sleep(2)
            where = ("Stop %s is at Alpaca%s; I sell at the target %s myself (I check every ~5 min, so it can "
                     "fill a little either side)." % (money(s["stop"]), "" if m["stop_order_id"] or self.args.dry_run
                                                     else " as soon as the buy fills", money(s["target"])))
        else:
            where = "Stop %s, target %s are waiting at Alpaca." % (money(s.get("stop")), money(s.get("target")))
        msg = ("✅ <b>Bought %s</b> (%s, %s)\nAbout %s. %s\n"
               "If the target hits: <b>%s</b> · if the stop hits: <b>%s</b>"
               % (self.qty_text(p), self.mode(), source, money(s.get("cost")), where,
                  money(p.get("target_profit"), sign=True), money(-(s.get("max_loss") or 0))))
        self.event("broker", "Bought %s (%s)." % (self.qty_text(p), source))
        return True, msg

    def place_managed_stop(self, m):
        """Once a part-share buy has filled, park a stop-loss for exactly the filled shares at Alpaca."""
        if m.get("stop_order_id"):
            return True
        try:
            o = self.alpaca.get("/v2/orders/%s" % m["order_id"])
        except Exception as e:
            self.errors.append(str(e))
            return False
        if o.get("status") in ("canceled", "expired", "rejected"):
            m["done"] = True
            self.event("broker", "%s buy was %s." % (m["symbol"], o.get("status")))
            return True
        filled = float(o.get("filled_qty") or 0)
        if o.get("status") != "filled" or filled <= 0:
            return False
        m["qty"], m["fill"] = filled, float(o.get("filled_avg_price") or 0)
        try:
            so = self.alpaca.call("POST", "/v2/orders", {
                "symbol": m["symbol"], "qty": ("%.9f" % filled).rstrip("0").rstrip("."), "side": "sell",
                "type": "stop", "stop_price": "%.2f" % m["stop"], "time_in_force": "day",
                "client_order_id": "jarvis-stop-%s" % uuid.uuid4().hex[:8]})
            m["stop_order_id"] = so.get("id")
            self.event("broker", "Stop-loss for %s parked at Alpaca at %s." % (m["symbol"], money(m["stop"])))
        except Exception as e:
            self.event("broker", "Couldn't park the %s stop at Alpaca: %s. I'll watch it myself." % (m["symbol"], e))
            m["stop_order_id"] = "self-watch"
        return True

    def manage_open(self):
        """Each check-in during the session: look after part-share trades (stop parked? target reached?)."""
        held = {p["symbol"]: p for p in self.positions}
        for m in self.st.get("managed", []):
            if m.get("done") or m.get("date") != self.today:
                continue
            if not m.get("stop_order_id"):
                self.place_managed_stop(m)
            pos = held.get(m["symbol"])
            if not pos:
                if m.get("qty"):
                    m["done"] = True  # stopped out (or closed elsewhere)
                    self.event("broker", "%s is closed (stop or manual)." % m["symbol"])
                continue
            price = float(pos.get("current_price") or 0)
            hit_target = price >= m["target"]
            hit_self_stop = m.get("stop_order_id") == "self-watch" and price <= m["stop"]
            if not (hit_target or hit_self_stop) or self.args.dry_run:
                continue
            try:
                if m.get("stop_order_id") not in (None, "self-watch"):
                    self.alpaca.call("DELETE", "/v2/orders/%s" % m["stop_order_id"])
                    time.sleep(1)
                self.alpaca.call("DELETE", "/v2/positions/%s" % urllib.parse.quote(m["symbol"]))
                m["done"] = True
                pl = float(pos.get("unrealized_pl") or 0)
                self.log_order({"date": self.today, "at": self.now_utc.isoformat(timespec="seconds"),
                                "symbol": m["symbol"], "side": "sell", "kind": "exit", "qty": pos["qty"],
                                "status": "placed", "source": "target" if hit_target else "stop (self-watched)"})
                self.event("broker", "%s %s at %s (%s)." % ("🎯 Target hit: sold" if hit_target else "Stop hit: sold",
                                                          m["symbol"], money(price), money(pl, sign=True)))
                self.tg.send("%s <b>%s</b> at about %s: <b>%s</b>" % (
                    "🎯 Target hit! Sold" if hit_target else "🛑 Stop hit. Sold", m["symbol"], money(price), money(pl, sign=True)))
            except Exception as e:
                self.event("broker", "Couldn't sell %s: %s" % (m["symbol"], e))

    # ---- morning brief
    def scan(self):
        self.bot("scanner", "working", "Scanning every US stock...")
        uni = P("trader", "universe.txt")
        if not os.path.exists(uni) or time.time() - os.path.getmtime(uni) > 20 * 3600:
            code, out, err = run_tool("scan.py", "universe", timeout=180)
            if code != 0 and not os.path.exists(uni):
                self.event("scanner", "Couldn't download the stock list: %s" % (err.strip()[-200:] or code))
                return []
        code, out, err = run_tool("scan.py", "daily", "--min-price", self.settings.get("min_price", 5),
                                  "--min-volume", self.settings.get("min_volume", 1000000), "--quiet",
                                  "--out", "trader/watchlist.json", timeout=900)
        if code != 0 and not os.path.exists(WATCHLIST):
            self.event("scanner", "Scan failed: %s" % (err.strip()[-200:] or code))
            return []
        wl = load_json(WATCHLIST, {}) or {}
        hits = wl.get("hits", [])
        want = set(self.settings.get("setups") or [])
        lo, hi = self.settings.get("min_price", 5), self.settings.get("max_price", 40)
        c = [h for h in hits if lo <= (h.get("price") or 0) <= hi and (not want or want & set(h.get("setups", [])))]
        c.sort(key=lambda h: -(h.get("price") or 0) * (h.get("volume") or 0))
        c = c[: int(self.settings.get("candidates", 20))]
        self.st["candidates"] = c
        self.st["candidates_day"] = self.today
        self.event("scanner", "Scanned the US market: %d charts matched a setup, %d fit your $%s-$%s price range. "
                   "Watching the top %d." % (len(hits), len([h for h in hits if lo <= (h.get("price") or 0) <= hi]),
                                             lo, hi, len(c)))
        return c

    def news_for(self, symbols):
        if not symbols:
            return {}
        self.bot("news", "working", "Reading the news...")
        code, data, err = tool_json("news.py", "--tickers", *symbols, "--hours", 18, "--all", "--json", timeout=300)
        out = {}
        if not isinstance(data, dict):
            self.event("news", "News check failed: %s" % (err[-160:] if err else code))
            return out
        for m in data.get("moves", []) or []:
            out.setdefault(m.get("ticker") or m.get("symbol"), {})["move"] = m
        for it in data.get("items", []) or []:
            for t in (it.get("touches") or [it.get("ticker")]):
                d = out.setdefault(t, {})
                d.setdefault("headlines", []).append(it)
        self.event("news", "Read %d headlines and filings for %d stocks." % (len(data.get("items", []) or []), len(symbols)))
        return out

    def brief(self):
        c = self.scan()
        top = [h["symbol"] for h in c[:8]]
        news = self.news_for(top)
        self.st["news"] = {k: {"headlines": [{"title": h.get("title"), "url": h.get("url") or h.get("link"),
                                              "tags": h.get("tags")} for h in v.get("headlines", [])[:3]]}
                           for k, v in news.items() if k}
        open_t, close_t = self.cal
        lines = ["☀️ <b>Morning brief</b> · %s" % day_str(self.local()),
                 "US market opens <b>%s</b> and closes <b>%s</b> your time (%s)."
                 % (self.ny_time_local(open_t), self.ny_time_local(close_t), self.tz_label()),
                 "Breakouts usually trigger in the first 2 hours: if you want to approve trades yourself, "
                 "be awake about <b>%s–%s</b>." % (self.ny_time_local(dt.time(9, 45)), self.ny_time_local(dt.time(11, 30))),
                 "",
                 "Mode: <b>%s</b> · auto-buy: <b>%s</b>" % (self.mode(), self.auto_label()),
                 "You can sleep: I'll trade the ideas that pass your rules and tell you what I did."
                 if self.auto_ok("medium") else
                 "I'll ask before each trade, so ideas expire if you're asleep.",
                 "Your limits: %s max loss a trade, %s a day, %s trades." % (
                     money(float(self.cfg.get("max_loss_per_trade_usd") or 0)),
                     money(float(self.cfg.get("max_daily_loss_usd") or 0)), self.cfg.get("max_trades_per_day")),
                 "🎯 Goals: <b>%s today</b>, <b>%s this week</b> (week so far %s).%s" % (
                     money(self.goals()["daily_goal"], sign=True),
                     money(self.goals()["weekly_goal"], sign=True),
                     money(self.goals()["week_pl"], sign=True),
                     " I stop for the day once today's goal is in." if self.settings.get("stop_when_goal_hit", True) else ""),
                 "📈 Always watching: <b>%s</b> (PSQ and SH rise when the market falls)" % ", ".join(self.settings.get("always_watch") or [])
                 if self.settings.get("always_watch") else "",
                 "", "👀 <b>Watching today</b> (%d stocks):" % len(c)]
        for h in c[:8]:
            n = news.get(h["symbol"], {})
            head = (n.get("headlines") or [{}])[0].get("title")
            lines.append("• <b>%s</b> %s · %s%s" % (h["symbol"], money(h.get("price")),
                                                   ", ".join(SETUP_NAMES.get(s, s.replace("_", " ")) for s in h.get("setups", [])),
                                                   ("\n   📰 " + esc(head[:110])) if head else ""))
        if self.st["paused"]:
            lines.append("\n⏸ I'm paused: send /resume to let me trade today.")
        lines.append("\nA watchlist is charts that match a pattern, not a promise. Not financial advice.")
        self.tg.send("\n".join(lines))
        self.event("jarvis", "Sent the morning brief.")

    def auto_allowed(self):
        return bool(self.settings.get("auto_trade_paper")) if self.paper else bool(self.settings.get("auto_trade_live"))

    def auto_floor(self):
        """The lowest confidence Jarvis buys without asking. Real money: high only, whatever the settings say."""
        if not self.paper:
            return "high"
        f = str(self.settings.get("auto_paper_min_confidence", "high")).lower()
        return f if f in ("high", "medium") else "high"

    def auto_ok(self, conf):
        rank = {"low": 0, "medium": 1, "high": 2}
        return self.auto_allowed() and rank.get(conf, 0) >= rank[self.auto_floor()]

    def auto_label(self):
        if not self.auto_allowed():
            return "OFF (I'll ask you)"
        return "ON for %s" % ("high and medium confidence" if self.auto_floor() == "medium" else "high confidence")

    # ---- hunting
    def goals(self):
        """Today's and this week's profit against the goals. Sends a message the first time each is reached."""
        a = self.account or {}
        eq, last = float(a.get("equity") or 0), self.last_close()
        wk = "%d-W%02d" % self.ny.date().isocalendar()[:2]
        w = self.st.get("week") or {}
        if w.get("id") != wk and last:
            w = {"id": wk, "start": last}
            self.st["week"] = w
        day_pl = round(eq - last, 2) if a else 0.0
        week_pl = round(eq - float(w.get("start") or eq), 2) if a else 0.0
        S = self.settings
        dg = (round(last * float(S["daily_goal_pct"]) / 100, 2) if S.get("daily_goal_pct") and last
              else float(S.get("daily_goal_usd") or 0))
        wstart = float(w.get("start") or last or 0)
        wg = (round(wstart * float(S["weekly_goal_pct"]) / 100, 2) if S.get("weekly_goal_pct") and wstart
              else float(S.get("weekly_goal_usd") or 0))
        g = {"day_pl": day_pl, "week_pl": week_pl, "daily_goal": dg, "weekly_goal": wg,
             "day_hit": bool(dg) and day_pl >= dg, "week_hit": bool(wg) and week_pl >= wg}
        stop = self.settings.get("stop_when_goal_hit", True)
        if g["day_hit"] and self.once("daily_goal"):
            self.event("jarvis", "🎯 Daily goal reached: %s today." % money(day_pl, sign=True))
            self.tg.send("🎯 <b>Daily goal reached!</b> %s today (goal %s).%s" % (
                money(day_pl, sign=True), money(dg), " Locking it in: no new trades today." if stop else ""))
        if g["week_hit"] and self.st.get("week_goal_sent") != wk:
            self.st["week_goal_sent"] = wk
            self.event("jarvis", "🏆 Weekly goal reached: %s this week." % money(week_pl, sign=True))
            self.tg.send("🏆 <b>Weekly goal reached!</b> %s this week (goal %s).%s" % (
                money(week_pl, sign=True), money(wg), " Taking the rest of the week off to protect it." if stop else ""))
        return g

    def record_equity(self):
        a = self.account
        if not a:
            return
        eq = float(a.get("equity") or 0)
        h = self.st.setdefault("equity_history", [])
        if h:
            last_t = dt.datetime.fromisoformat(h[-1]["t"])
            if abs(h[-1]["eq"] - eq) < 0.005 and (self.now_utc - last_t) < dt.timedelta(hours=6):
                return
        h.append({"t": self.now_utc.isoformat(timespec="seconds"), "eq": round(eq, 2)})
        del h[:-800]

    def live_locked(self):
        """The current limits were set for paper practice. Real money stays locked until they're reviewed."""
        if self.paper or self.settings.get("live_limits_reviewed"):
            return False
        if self.once("live_lock_note"):
            self.tg.send("🔒 <b>Real-money mode is locked.</b> Your limits (up to 10 trades a day, a 10% daily loss limit, "
                         "no day-trade counter) were set for paper practice. Review them and set "
                         "<code>live_limits_reviewed</code> to true in jarvis/settings.json before I trade real money.")
            self.event("risk", "Real money is locked until the limits are reviewed.")
        self.bot("risk", "idle", "Real money locked: limits not reviewed yet.")
        return True

    def hunt(self):
        if self.st["paused"]:
            self.bot("entry", "idle", "Paused by you.")
            return
        if self.live_locked():
            return
        if self.st.get("candidates_day") != self.today or not self.st["candidates"]:
            self.scan()
        g = self.goals()
        if self.settings.get("stop_when_goal_hit", True) and (g["day_hit"] or g["week_hit"]):
            self.bot("entry", "idle", "%s goal reached: locking in the profit, no new trades %s." % (
                "Weekly" if g["week_hit"] else "Daily", "until next week" if g["week_hit"] else "today"))
            return
        max_trades = int(self.cfg.get("max_trades_per_day") or 3)
        if len(self.entries_today()) >= max_trades:
            self.bot("entry", "idle", "Done for today: %d of %d trades used." % (max_trades, max_trades))
            return
        daily = float(self.cfg.get("max_daily_loss_usd") or 0)
        per = float(self.cfg.get("max_loss_per_trade_usd") or 0)
        if daily and self.risk_used_today() + min(per, 0.01) > daily:
            self.bot("entry", "idle", "Daily loss limit used up. Resting until tomorrow.")
            return
        held = {p["symbol"] for p in self.positions}
        pending = {p["symbol"] for p in self.st["proposals"] if p["status"] == "pending"}
        os.makedirs(WORK, exist_ok=True)
        checked = triggered = 0
        always = [{"symbol": s, "setups": ["always watched"]} for s in (self.settings.get("always_watch") or [])]
        names = {h["symbol"] for h in always}
        watch = self.st.setdefault("watch", {})
        if watch.get("_day") != self.today:
            watch.clear()
            watch["_day"] = self.today
        for h in always + [c for c in self.st["candidates"] if c["symbol"] not in names]:
            sym = h["symbol"]
            if sym in self.st["seen"] or sym in held or sym in pending:
                continue
            checked += 1
            entry_path = os.path.join("trader", "work", "%s-entry.json" % sym)
            code, e, err = tool_json("entry.py", "check", sym, "--write", entry_path, "--json",
                                     *self.extra("entry.py"), timeout=60)
            if not e:
                continue
            status = e.get("status")
            watch[sym] = {"status": status, "level": e.get("level"), "last": (e.get("last") or {}).get("close"),
                          "vs": (e.get("last") or {}).get("vs_level_pct"), "reason": e.get("reason"),
                          "t": self.now_utc.isoformat(timespec="seconds")}
            if status == "expired":
                self.st["seen"][sym] = "expired"
            elif status == "triggered":
                age = e.get("minutes_since") or 0
                self.st["seen"][sym] = "triggered"
                if age > int(self.settings.get("max_trigger_age_minutes", 15)):
                    self.event("entry", "%s broke out %d min ago: too late to chase." % (sym, age))
                    continue
                triggered += 1
                self.event("entry", "%s broke out at %s (%s)." % (sym, money((e.get("trigger") or {}).get("price")),
                                                                    (e.get("trigger") or {}).get("time")))
                self.evaluate(sym, entry_path)
                if len(self.entries_today()) >= max_trades:
                    break
        self.bot("entry", "working", "Checked %d charts at %s New York: %d breakouts." % (
            checked, clock_str(self.ny), triggered))

    def evaluate(self, sym, entry_path):
        S = self.settings
        plan_path = os.path.join("trader", "work", "%s-plan.json" % sym)
        orders_path = os.path.join("trader", "work", "%s-orders.json" % sym)
        code, plan, err = tool_json("exit.py", "plan", "--from", entry_path, "--stop", S.get("stop", "or-mid"),
                                    "--target", S.get("target", "2R"), "--write", plan_path, "--json",
                                    *self.extra("exit.py"))
        if not plan or code != 0:
            self.event("risk", "No sensible stop/target for %s: %s" % (sym, (err or "")[-160:]))
            return
        self.bot("oracle", "working", "Replaying %s %s times..." % (sym, S.get("replays", 5000)))
        code, tm, err = tool_json("timemachine.py", "run", "--plan", plan_path, "--replays", S.get("replays", 5000),
                                  "--json", *self.extra("timemachine.py"), timeout=600)
        if not tm or "mc" not in tm:
            self.event("oracle", "Couldn't replay %s: %s" % (sym, (err or "")[-160:]))
            return
        mc, hist = tm["mc"], tm.get("history") or {}
        mc.pop("bands", None)
        self.event("oracle", "%s: target first %s, stop first %s, neither %s (%d replays). History: %s fired, %s won, %s lost."
                   % (sym, pct(mc.get("p_target")), pct(mc.get("p_stop")), pct(mc.get("p_neither")),
                      mc.get("replays", 0), hist.get("triggered"), hist.get("target"), hist.get("stop")))
        sizing, order, why = self.size_and_check(sym)
        if why:
            self.event("risk", "Skipped %s: %s" % (sym, why))
            return
        qty = sizing["qty"]
        target_profit = round(qty * (sizing["target"] - sizing["entry"]), 2)
        avg_r = mc.get("avg_R") or 0.0
        exp = round(avg_r * (sizing.get("max_loss") or 0), 2)
        conf = self.confidence(mc, hist)
        p = {"id": uuid.uuid4().hex[:8], "symbol": sym, "created": self.now_utc.isoformat(timespec="seconds"),
             "expires": (self.now_utc + dt.timedelta(minutes=int(S.get("approval_minutes", 20)))).isoformat(timespec="seconds"),
             "status": "new", "plan": {k: plan.get(k) for k in ("entry", "stop", "target", "entry_time", "stop_label", "target_label", "flat_by")},
             "sizing": sizing, "order": order, "odds": mc, "history": {k: hist.get(k) for k in ("sessions", "triggered", "target", "stop", "close", "avg_R")},
             "target_profit": target_profit, "expected": exp, "confidence": conf}
        self.st["proposals"].append(p)
        self.st["proposals"] = self.st["proposals"][-60:]
        if conf == "low":
            p["status"] = "passed"
            self.event("jarvis", "Passed on %s: the odds are no better than a coin flip (avg %+.2fR)." % (sym, avg_r))
            return
        if self.auto_ok(conf):
            ok, msg = self.place(p, "auto: %s confidence" % conf)
            self.tg.send(self.idea_text(p, auto=True) + "\n\n" + msg)
            return
        p["status"] = "pending"
        p["msg_id"] = self.tg.send(self.idea_text(p), buttons=[("✅ Buy", "buy:%s" % p["id"]), ("❌ Skip", "skip:%s" % p["id"])])
        self.event("jarvis", "Asked you about %s (confidence %s)." % (sym, conf))

    def confidence(self, mc, hist):
        S = self.settings
        avg_r = mc.get("avg_R") or 0
        n = hist.get("triggered") or 0
        h_avg = hist.get("avg_R")
        if (avg_r >= S.get("auto_min_avg_r", 0.15) and (mc.get("p_target") or 0) >= S.get("auto_min_p_target", 0.35)
                and n >= S.get("auto_min_history_trades", 8) and h_avg is not None and h_avg > S.get("auto_min_history_avg_r", 0)):
            return "high"
        if avg_r > S.get("ask_min_avg_r", 0.0) and (h_avg is None or h_avg >= S.get("ask_min_history_avg_r", -0.1)):
            return "medium"
        return "low"

    def idea_text(self, p, auto=False):
        s, mc, h = p["sizing"], p["odds"], p["history"]
        exp_local = clock_str(self.local(dt.datetime.fromisoformat(p["expires"])))
        badge = {"high": "🟢 HIGH", "medium": "🟡 MEDIUM", "low": "🔴 LOW"}[p["confidence"]]
        lines = ["%s <b>%s: %s</b> (%s)" % ("🤖" if auto else "💡", "Auto-trade" if auto else "Trade idea", p["symbol"], self.mode()),
                 "Buy <b>%s</b> at about %s a share = %s" % (self.qty_text(p), money(s["entry"]), money(s.get("cost"))),
                 "🎯 Target %s → <b>%s</b> if it gets there" % (money(s["target"]), money(p["target_profit"], sign=True)),
                 "🛑 Stop %s → <b>%s</b> if it drops there (a fast drop can fill worse)" % (money(s["stop"]), money(-(s.get("max_loss") or 0))),
                 "⏱ Either way I close it by %s your time." % self.ny_time_local(hhmm(self.cfg.get("flat_by", "15:55"))),
                 "",
                 "📊 %s replays of today: target first <b>%s</b>, stop first <b>%s</b>, neither by the close %s"
                 % ("{:,}".format(mc.get("replays", 0)), pct(mc.get("p_target")), pct(mc.get("p_stop")), pct(mc.get("p_neither"))),
                 "📜 Last %s days: this setup fired %s×: %s hit target, %s hit stop"
                 % (h.get("sessions"), h.get("triggered"), h.get("target"), h.get("stop")),
                 "💡 Average result across the replays: <b>%s</b> a trade · confidence %s"
                 % (money(p["expected"], sign=True), badge)]
        if not auto:
            lines.append("\nTap Buy or reply <b>yes</b> by %s your time, or it expires." % exp_local)
        lines.append("<i>Odds come from this stock's last 60 days. They're an estimate, not a promise.</i>")
        return "\n".join(lines)

    # ---- end of day
    def flatten(self):
        if not self.positions:
            return
        if self.args.dry_run:
            self.event("broker", "Would close %s now (dry run)." % ", ".join(p["symbol"] for p in self.positions))
            return
        try:
            self.alpaca.call("DELETE", "/v2/orders")
        except Exception as e:
            self.event("broker", "Couldn't cancel open orders: %s" % e)
        for m in self.st.get("managed", []):
            if m.get("date") == self.today:
                m["done"] = True
        for pos in self.positions:
            sym = pos["symbol"]
            try:
                self.alpaca.call("DELETE", "/v2/positions/%s" % urllib.parse.quote(sym))
                self.log_order({"date": self.today, "at": self.now_utc.isoformat(timespec="seconds"), "symbol": sym,
                                "side": "sell", "kind": "exit", "qty": pos["qty"], "status": "placed", "source": "flat by close"})
                self.event("broker", "Closed %s %s before the bell (%s)." % (
                    pos["qty"], sym, money(float(pos.get("unrealized_pl") or 0), sign=True)))
                self.tg.send("🔔 Closing <b>%s %s</b> before the bell: about %s on it." % (
                    pos["qty"], sym, money(float(pos.get("unrealized_pl") or 0), sign=True)))
            except Exception as e:
                self.event("broker", "Couldn't close %s: %s" % (sym, e))
                self.tg.send("⚠️ I couldn't close %s: %s. Please check Alpaca." % (sym, esc(e)))

    def recap(self):
        a = self.account or {}
        eq, last = float(a.get("equity") or 0), self.last_close()
        trades = [t for t in self.st["trades"] if t["date"] == self.today]
        fills = {}
        if self.alpaca.ok and not self.args.dry_run:
            try:
                after = ny_to_utc(dt.datetime.combine(self.ny.date(), dt.time(0, 0))).isoformat().replace("+00:00", "Z")
                for o in self.alpaca.get("/v2/orders?status=closed&nested=true&limit=200&after=%s" % after) or []:
                    for x in [o] + (o.get("legs") or []):
                        if x.get("filled_qty") and float(x["filled_qty"]) > 0:
                            q, px = float(x["filled_qty"]), float(x["filled_avg_price"])
                            f = fills.setdefault(x["symbol"], 0.0)
                            fills[x["symbol"]] = f + (q * px if x["side"] == "sell" else -q * px)
            except Exception as e:
                self.errors.append(str(e))
        for t in trades:
            if t["symbol"] in fills and t.get("result") is None:
                t["result"] = round(fills[t["symbol"]], 2)
        lines = ["🌙 <b>Day recap</b> · %s (%s)" % (day_str(self.local()), self.mode()),
                 "Account: <b>%s</b> · today <b>%s</b>" % (money(eq), money(eq - last, sign=True)), ""]
        if trades:
            for t in trades:
                lines.append("• %s %s sh (%s): %s" % (t["symbol"], ("%g" % round(t["qty"] or 0, 4)), t["source"],
                                                    money(t["result"], sign=True) if t["result"] is not None else "result pending"))
        else:
            lines.append("No trades today: nothing cleared your rules. That's normal, and it's a good day too.")
        done = [t for t in self.st["trades"] if t.get("result") is not None]
        if done:
            wins = sum(1 for t in done if t["result"] > 0)
            lines.append("\nSo far: %d trades, %d winners, total %s." % (len(done), wins, money(sum(t["result"] for t in done), sign=True)))
        g = self.goals()
        lines.append("\n🎯 Daily goal %s: %s %s · 🏆 week %s of %s %s" % (
            money(g["daily_goal"]), money(g["day_pl"], sign=True), "✅" if g["day_hit"] else "❌",
            money(g["week_pl"], sign=True), money(g["weekly_goal"]), "✅" if g["week_hit"] else ""))
        nxt = [s for s in self.st.get("next_sessions", []) if s["date"] > self.today]
        if nxt:
            n = nxt[0]
            o_utc = ny_to_utc(dt.datetime.strptime(n["date"] + " " + n["open"], "%Y-%m-%d %H:%M"))
            lines.append("\nNext open: <b>%s %s</b> your time." % (day_str(self.local(o_utc)), clock_str(self.local(o_utc))))
        self.tg.send("\n".join(lines))
        self.event("jarvis", "Sent the day's recap.")

    # ---- the tick
    def expire(self):
        for p in self.st["proposals"]:
            if p["status"] == "pending" and self.now_utc > dt.datetime.fromisoformat(p["expires"]):
                p["status"] = "expired"
                self.tg.edit_buttons_off(p.get("msg_id"), None)
                self.event("jarvis", "%s expired with no answer." % p["symbol"])

    def tick(self):
        self.bot("jarvis", "working", "Checking in.")
        self.sync()
        self.handle_messages()
        if self.st.get("welcomed") is None and self.tg.ok:
            self.st["welcomed"] = self.today
            self.tg.send(self.help_text())
        t = self.ny.time()
        self.goals()
        self.record_equity()
        if self.cal:
            open_t, close_t = self.cal
            if open_t <= t < close_t:
                self.manage_open()
            flat = min(hhmm(self.cfg.get("flat_by", "15:55")),
                       (dt.datetime.combine(self.ny.date(), close_t) - dt.timedelta(minutes=5)).time())
            start = max(hhmm(self.cfg.get("no_entries_before", "09:45")), open_t)
            stop = min(hhmm(self.cfg.get("no_entries_after", "15:30")),
                       (dt.datetime.combine(self.ny.date(), close_t) - dt.timedelta(minutes=30)).time())
            brief_t = hhmm(self.settings.get("brief_at", "08:00"))
            if t < min(brief_t, open_t):
                self.bot("entry", "idle", "Trading day ahead: morning brief at %s, market opens %s (your time)."
                         % (self.ny_time_local(brief_t), self.ny_time_local(open_t)))
            elif brief_t <= t < open_t:
                if self.once("brief"):
                    self.brief()
                self.bot("entry", "idle", "Waiting for the opening bell (%s your time)." % self.ny_time_local(open_t))
            elif open_t <= t < start:
                self.bot("entry", "working", "Building the opening range: first entries from %s your time."
                         % self.ny_time_local(start))
            elif start <= t < stop:
                self.hunt()
            elif stop <= t < flat:
                self.bot("entry", "idle", "No new entries this late. Watching open trades.")
            elif flat <= t < (dt.datetime.combine(self.ny.date(), close_t) + dt.timedelta(minutes=5)).time():
                self.flatten()
                self.bot("broker", "working", "Closing anything still open before the bell.")
            elif t >= close_t:
                if self.once("recap"):
                    self.recap()
                self.bot("entry", "idle", "Market closed. Back tomorrow.")
            close_plus = (dt.datetime.combine(self.ny.date(), close_t) + dt.timedelta(minutes=15)).time()
            if open_t <= t <= close_plus or self.st.get("charts", {}).get("date") != self.today and t > open_t:
                self.update_charts()
        else:
            self.bot("entry", "idle", "No US market today. Resting.")
        self.expire()
        self.bot("jarvis", "idle", "All good. Next check-in in about 5 minutes.")
        if self.tg.health:
            h = dict(self.tg.health, at=self.now_utc.isoformat(timespec="seconds"))
            self.st["telegram_health"] = h
            log = self.st.setdefault("telegram_log", [])
            log.append(h)
            del log[:-20]
        self.write_dashboard()
        save_json(self.state_path, self.st)

    # ---- live chart data
    def fetch_bars(self, sym):
        """Today's 5-minute bars from Yahoo's free chart endpoint: [[epoch, open, high, low, close], ...]."""
        url = "https://query2.finance.yahoo.com/v8/finance/chart/%s?range=1d&interval=5m" % urllib.parse.quote(sym)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                res = json.loads(r.read())["chart"]["result"][0]
        except Exception as e:
            print("bars failed for", sym, e, file=sys.stderr)
            return []
        q = res["indicators"]["quote"][0]
        out = []
        for i, t in enumerate(res.get("timestamp") or []):
            o, h, l, c = (q[k][i] for k in ("open", "high", "low", "close"))
            if None in (o, h, l, c):
                continue
            out.append([int(t), round(o, 2), round(h, 2), round(l, 2), round(c, 2)])
        return out

    def fills_today(self):
        """Every filled buy and sell today at Alpaca (bracket legs included): the dots on the chart."""
        if not self.alpaca.ok:
            return []
        try:
            after = ny_to_utc(dt.datetime.combine(self.ny.date(), dt.time(0, 0))).isoformat().replace("+00:00", "Z")
            orders = self.alpaca.get("/v2/orders?status=all&nested=true&limit=200&after=%s" % after) or []
        except Exception as e:
            self.errors.append(str(e))
            return []
        out = []
        for o in orders:
            for x in [o] + (o.get("legs") or []):
                if x.get("filled_at") and float(x.get("filled_qty") or 0) > 0:
                    out.append({"symbol": x["symbol"], "side": x["side"], "price": float(x["filled_avg_price"]),
                                "qty": float(x["filled_qty"]), "t": x["filled_at"], "type": x.get("type")})
        return out

    def update_charts(self):
        syms = list(self.settings.get("always_watch") or [])
        for t in self.st["trades"]:
            if t["date"] == self.today and t["symbol"] not in syms:
                syms.insert(0, t["symbol"])
        for p in self.positions:
            if p["symbol"] not in syms:
                syms.insert(0, p["symbol"])
        syms = syms[:8]
        fills = self.fills_today()
        charts = {}
        for s in syms:
            bars = self.fetch_bars(s)
            if not bars:
                continue
            first = [b for b in bars[:3]]  # 9:30, 9:35, 9:40: the 15-minute opening range
            charts[s] = {
                "bars": bars,
                "or_high": max(b[2] for b in first), "or_low": min(b[3] for b in first),
                "plans": [{k: t.get(k) for k in ("entry", "stop", "target", "t", "source")}
                          for t in self.st["trades"] if t["date"] == self.today and t["symbol"] == s],
                "fills": [f for f in fills if f["symbol"] == s],
            }
        if charts:
            first_bar = next(iter(charts.values()))["bars"][0][0]
            session = to_ny(dt.datetime.fromtimestamp(first_bar, UTC)).date().isoformat()
            self.st["charts"] = {"date": session, "updated": self.now_utc.isoformat(timespec="seconds"),
                                 "symbols": charts}

    def next_checkin(self):
        """The next check-in: every 5 min 12:00-21:55 UTC Monday-Friday, otherwise on the hour and half hour."""
        t = self.now_utc.replace(second=0, microsecond=0)
        t += dt.timedelta(minutes=5 - t.minute % 5)
        for _ in range(8 * 24 * 12):
            if (t.weekday() < 5 and 12 <= t.hour <= 21) or t.minute in (0, 30):
                return t
            t += dt.timedelta(minutes=5)
        return t

    def stats(self):
        done = [t for t in self.st["trades"] if t.get("result") is not None]
        wins = [t["result"] for t in done if t["result"] > 0]
        losses = [t["result"] for t in done if t["result"] <= 0]
        return {"trades": len(done), "wins": len(wins), "losses": len(losses),
                "win_rate": round(len(wins) / len(done), 3) if done else None,
                "avg_win": round(sum(wins) / len(wins), 2) if wins else None,
                "avg_loss": round(sum(losses) / len(losses), 2) if losses else None,
                "best": max((t["result"] for t in done), default=None),
                "worst": min((t["result"] for t in done), default=None),
                "auto": sum(1 for t in self.st["trades"] if str(t.get("source", "")).startswith("auto")),
                "ideas": len(self.st["proposals"]),
                "passed": sum(1 for p in self.st["proposals"] if p.get("status") == "passed")}

    def _bot_view(self, b):
        """A bot looks busy on the dashboard only if it did something this check-in."""
        b = dict(b)
        if b.get("status") == "working" and b.get("t") != self.now_utc.isoformat(timespec="seconds"):
            b["status"] = "idle"
        return b

    def write_dashboard(self):
        a = self.account or {}
        eq, last = float(a.get("equity") or 0), self.last_close()
        sessions = []
        for s in self.st.get("next_sessions", [])[:5]:
            o = ny_to_utc(dt.datetime.strptime(s["date"] + " " + s["open"], "%Y-%m-%d %H:%M"))
            c = ny_to_utc(dt.datetime.strptime(s["date"] + " " + s["close"], "%Y-%m-%d %H:%M"))
            sessions.append({"date": s["date"], "open_utc": o.isoformat(), "close_utc": c.isoformat(),
                             "open_local": "%s %s" % (day_str(self.local(o)), clock_str(self.local(o))),
                             "close_local": clock_str(self.local(c))})
        done = [t for t in self.st["trades"] if t.get("result") is not None]
        dash = {
            "updated_utc": self.now_utc.isoformat(timespec="seconds"),
            "updated_local": "%s %s" % (day_str(self.local()), clock_str(self.local())),
            "timezone": self.tz_label(), "tz": self.tz, "mode": self.mode(), "paused": self.st["paused"],
            "auto_trade": self.auto_allowed(),
            "account": {"equity": eq, "cash": float(a.get("cash") or 0), "day_pl": round(eq - last, 2), "start": 50.0},
            "limits": {k: self.cfg.get(k) for k in ("max_loss_per_trade_usd", "max_daily_loss_usd", "max_trades_per_day",
                                                     "min_reward_risk", "no_entries_before", "no_entries_after", "flat_by")},
            "today": {"trades": len(self.entries_today()), "risk_used": self.risk_used_today()},
            "goals": self.goals(),
            "equity_history": self.st.get("equity_history", [])[-400:],
            "stats": self.stats(),
            "charts": self.st.get("charts") or {},
            "focus": [dict({"symbol": s}, **(self.st.get("watch", {}).get(s) or {}))
                      for s in (self.settings.get("always_watch") or [])],
            "market_open": bool(self.cal) and self.cal[0] <= self.ny.time() < self.cal[1],
            "next_checkin_utc": self.next_checkin().isoformat(timespec="seconds"),
            "settings": {"auto": self.auto_label(), "target": self.settings.get("target"),
                         "candidates": self.settings.get("candidates"), "always_watch": self.settings.get("always_watch")},
            "positions": [{"symbol": p["symbol"], "qty": float(p["qty"]), "value": float(p["market_value"]),
                           "pl": float(p["unrealized_pl"]), "entry": float(p["avg_entry_price"])} for p in self.positions],
            "bots": [dict({"id": k, "name": v[0], "role": v[1]},
                          **self._bot_view(self.st["bots"].get(k, {"status": "idle", "text": "Standing by."})))
                     for k, v in BOTS.items()],
            "watchlist": [{"symbol": h["symbol"], "price": h.get("price"), "setups": h.get("setups"),
                           "news": ((self.st.get("news") or {}).get(h["symbol"]) or {}).get("headlines", [])[:1]}
                          for h in self.st["candidates"]],
            "proposals": [{k: p.get(k) for k in ("symbol", "status", "created", "confidence", "target_profit", "expected")} |
                          {"max_loss": (p.get("sizing") or {}).get("max_loss"), "p_target": (p.get("odds") or {}).get("p_target"),
                           "p_stop": (p.get("odds") or {}).get("p_stop")} for p in self.st["proposals"][-15:]][::-1],
            "trades": self.st["trades"][-40:][::-1],
            "record": {"trades": len(done), "wins": sum(1 for t in done if t["result"] > 0),
                       "total": round(sum(t["result"] for t in done), 2)},
            "sessions": sessions,
            "events": self.st["events"][-40:][::-1],
            "errors": self.errors[-5:],
        }
        save_json(self.dash_path, dash)


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="One tick of Jarvis.")
    ap.add_argument("--dry-run", action="store_true", help="no orders; Telegram messages printed, not sent")
    ap.add_argument("--now", help='pretend it is this New York time, "YYYY-MM-DD HH:MM"')
    # testing only: replay saved market data through the real pipeline
    ap.add_argument("--test-config", help=argparse.SUPPRESS)
    ap.add_argument("--test-portfolio", help=argparse.SUPPRESS)
    ap.add_argument("--test-entry-data", help=argparse.SUPPRESS)
    ap.add_argument("--test-tm-data", help=argparse.SUPPRESS)
    ap.add_argument("--test-candidates", help=argparse.SUPPRESS)
    args = ap.parse_args()
    Jarvis(args).tick()


if __name__ == "__main__":
    main()
