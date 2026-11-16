#!/usr/bin/env python3
"""Movers for Jarvis: which liquid stocks are "in play" right now. Standard library only.

    python3 movers.py scan                     # liquid stocks up >= 3 % on the day, biggest first
    python3 movers.py scan --min-gain 4 --min-price 5 --max-price 40 --top 30 --json
    python3 movers.py rvol TSLA --json         # today's opening-range volume vs its own last 14 sessions

Why: 60 days of replays (research/backtest.py) say an opening-range breakout only pays in a stock that is
already up strongly on the day on unusually heavy opening volume ("in play"); the same breakout in a quiet
stock loses money after costs. The scanner's daily setups can't see that, so this looks at today.

scan   reads trader/liquid.json (written by the morning scan: every stock over the price and volume floor)
       and asks Yahoo's spark endpoint for today's price and yesterday's close, 20 symbols a request.
rvol   one v8 chart (15 days of 5-minute bars): the volume of the first --or-minutes (15) today divided by
       the average of the same minutes over the previous sessions (at least 5 are needed).

Data: Yahoo's free chart JSON (unofficial, can lag). Exit code 0 when something was found.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scan  # noqa: E402  (Yahoo plumbing and the trading calendar)


def gain_rows(data, min_gain, min_price, max_price):
    """Pure. {SYM: series} -> movers, biggest gain first."""
    out = []
    for sym, s in data.items():
        m = s.get("meta") or {}
        price, prev = m.get("regularMarketPrice"), m.get("previousClose") or m.get("chartPreviousClose")
        if not price or not prev or prev <= 0:
            continue
        gain = 100.0 * (price / prev - 1)
        if gain >= min_gain and min_price <= price <= max_price and prev >= min_price:
            out.append({"symbol": sym, "price": round(float(price), 2), "prev_close": round(float(prev), 2),
                        "gain_pct": round(gain, 2), "volume": m.get("regularMarketVolume")})
    out.sort(key=lambda r: -r["gain_pct"])
    return out


def cmd_scan(a):
    try:
        doc = json.load(open(a.liquid))
    except (OSError, ValueError) as e:
        print("movers.py: can't read %s (%s): run the morning scan first" % (a.liquid, e), file=sys.stderr)
        return 1
    # yesterday's close can sit a little outside today's price range, so keep a margin before asking Yahoo
    syms = [r["symbol"] for r in doc.get("symbols", [])
            if a.min_price * 0.7 <= (r.get("price") or 0) <= a.max_price * 1.1]
    data, failed = scan.fetch_spark(syms, "1d", "5m", a.pause)
    rows = gain_rows(data, a.min_gain, a.min_price, a.max_price)[: a.top]
    out = {"created_by": "jarvis-movers", "as_of": doc.get("as_of"), "checked": len(syms), "failed": len(failed),
           "filters": {"min_gain_pct": a.min_gain, "min_price": a.min_price, "max_price": a.max_price},
           "movers": rows}
    if a.json:
        print(json.dumps(out, indent=1))
    else:
        print("%d of %d liquid stocks are up %g %% or more:" % (len(rows), len(syms), a.min_gain))
        for r in rows:
            print("  %-6s %8.2f  %+6.2f %%" % (r["symbol"], r["price"], r["gain_pct"]))
    return 0 if rows else 1


def opening_volumes(series, or_minutes=15):
    """Pure. A 5-minute series -> {date: volume of the session's first or_minutes}. A session counts only when
    every bar of its opening range is there."""
    n = or_minutes // 5
    days = {}
    for ts, v, c in zip(series["t"], series.get("v") or [], series["c"]):
        if c is None or ts % 300:
            continue
        e = scan.ts_to_eastern(ts)
        k = (e.hour * 60 + e.minute - 570) // 5
        if 0 <= k < n:
            days.setdefault(e.date(), {})[k] = v or 0
    return {d: sum(b.values()) for d, b in days.items() if len(b) == n}


def rvol(series, or_minutes=15, lookback=14, min_sessions=5):
    """Pure. -> (today's opening volume / the average of the previous sessions, sessions used) or (None, n)."""
    vols = opening_volumes(series, or_minutes)
    if not vols:
        return None, 0
    days = sorted(vols)
    prev = [vols[d] for d in days[:-1]][-lookback:]
    if len(prev) < min_sessions or sum(prev) <= 0:
        return None, len(prev)
    return vols[days[-1]] / (sum(prev) / len(prev)), len(prev)


def cmd_rvol(a):
    try:
        if a.offline:
            series = scan.parse_chart(scan._read_maybe_gz(a.offline), a.symbol)
        else:
            series = scan.parse_chart(scan.yahoo_get(scan.chart_path(a.symbol, "15d", "5m")), a.symbol)
    except (scan.ScanError, OSError, ValueError) as e:
        print("movers.py: %s" % e, file=sys.stderr)
        return 1
    x, n = rvol(series, a.or_minutes)
    out = {"symbol": a.symbol, "rvol": round(x, 2) if x is not None else None, "sessions": n, "or_minutes": a.or_minutes}
    if a.json:
        print(json.dumps(out))
    elif x is None:
        print("%s: not enough history for a relative volume (%d sessions)." % (a.symbol, n))
    else:
        print("%s: opening volume %.1fx its %d-session average." % (a.symbol, x, n))
    return 0 if x is not None else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="Stocks in play for Jarvis.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("scan")
    p.add_argument("--liquid", default="trader/liquid.json")
    p.add_argument("--min-gain", type=float, default=3.0, help="percent up on yesterday's close")
    p.add_argument("--min-price", type=float, default=5.0)
    p.add_argument("--max-price", type=float, default=1e9)
    p.add_argument("--top", type=int, default=30)
    p.add_argument("--pause", type=float, default=0.15)
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("rvol")
    p.add_argument("symbol")
    p.add_argument("--or-minutes", type=int, default=15)
    p.add_argument("--offline", metavar="FILE", help="a saved v8 chart JSON instead of the network")
    p.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    return cmd_scan(a) if a.cmd == "scan" else cmd_rvol(a)


if __name__ == "__main__":
    sys.exit(main())
