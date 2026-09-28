"""Regression fixtures for the daily-close stop (suggested by a Hashnode reader, Sep 28 2026).

Mirrors RevXLRegime.custom_exit's decision rule on hourly bars carrying the last COMPLETED
daily close (as Freqtrade's @informative('1d') merge provides). Feed and timezone are pinned:
Kraken daily candles, UTC day boundaries.
Case A: intraday low pierces entry*0.85 but the day closes above it -> stay in.
Case B: the day closes below entry*0.85 -> exit intent on the FIRST hourly bar after that close
        (filled at that bar's market, never at the already-known close).
Run: python3 research/test_daily_close_stop.py
"""
STOP = 0.15
FEED, TZ = "kraken", "UTC"

def exit_intent(hourly, entry):
    """hourly: list of dicts {ts, low, close_1d(last completed daily close or None)}. Returns ts of first exit intent."""
    for bar in hourly:
        c = bar["close_1d"]
        if c is not None and c <= entry * (1 - STOP):
            return bar["ts"]
    return None

def day(prev_close, n_hours, start, low):
    return [{"ts": f"{start}T{h:02d}:00Z", "low": low if h == 12 else prev_close, "close_1d": prev_close} for h in range(n_hours)]

entry = 100.0
# Case A: Oct-10-style wick to 80 (below 85) intraday, daily close 95. Next day sees close_1d=95.
a = day(100, 24, "2025-10-10", low=80) + day(95, 24, "2025-10-11", low=94)
assert exit_intent(a, entry) is None, "Case A must stay open (wick only)"
# Case B: daily close 84 on Oct 10 -> first bar of Oct 11 carries close_1d=84 -> exit intent there.
b = day(100, 24, "2025-10-10", low=80) + day(84, 24, "2025-10-11", low=83)
assert exit_intent(b, entry) == "2025-10-11T00:00Z", exit_intent(b, entry)
print(f"OK: wick-only stays open; close-below exits on next bar ({FEED}, {TZ}).")
