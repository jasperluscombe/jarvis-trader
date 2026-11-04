#!/usr/bin/env python3
"""Find your Telegram chat ID and send Jarvis's first hello.

1. Make a bot with @BotFather in Telegram and copy its token.
2. Save the token as an environment variable (never paste it in a chat):
     [Environment]::SetEnvironmentVariable('TELEGRAM_BOT_TOKEN','<token>','User')
3. Open your new bot in Telegram and send it any message (e.g. "hi").
4. Run:  python jarvis/telegram_setup.py

It prints your chat ID (put it in the TELEGRAM_CHAT_ID secret on GitHub) and sends a test message.
The token itself is never printed.
"""
import json
import os
import sys
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
if not token and os.name == "nt":
    try:  # a new PowerShell window isn't needed: read the saved User variable directly
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
            token = winreg.QueryValueEx(k, "TELEGRAM_BOT_TOKEN")[0].strip()
    except OSError:
        pass
if not token:
    sys.exit("TELEGRAM_BOT_TOKEN isn't set yet. See the steps at the top of this file.")


def api(method, payload=None):
    req = urllib.request.Request("https://api.telegram.org/bot%s/%s" % (token, method),
                                 data=json.dumps(payload or {}).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


me = api("getMe")["result"]
print("Bot found: @%s" % me["username"])
ups = api("getUpdates", {"timeout": 0})["result"]
chats = {}
for u in ups:
    m = u.get("message") or {}
    c = m.get("chat") or {}
    if c.get("type") == "private":
        chats[c["id"]] = c.get("first_name", "")
if not chats:
    sys.exit("No messages yet. Open @%s in Telegram, send it 'hi', then run this again." % me["username"])
if len(chats) > 1:
    print("More than one person has messaged this bot:", chats)
chat_id, name = list(chats.items())[-1]
api("sendMessage", {"chat_id": chat_id, "parse_mode": "HTML",
                    "text": "🤖 <b>Jarvis online.</b> Hi %s! Once GitHub is set up I'll message you here "
                            "before the US open, with trade ideas, and with a recap after the bell." % name})
print("Your chat ID: %s  (%s)" % (chat_id, name))
print("Sent a test message. Put this number in the TELEGRAM_CHAT_ID secret on GitHub.")
