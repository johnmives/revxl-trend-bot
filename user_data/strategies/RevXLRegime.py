"""
RevXLRegime — slow daily trend-following for Kraken spot (BTC/ETH/SOL vs USD).

Rules (evaluated on daily candles, executed on the hourly loop):
  ENTER long when daily close > daily EMA(slow) AND daily EMA(fast) > EMA(slow)
                  AND daily close is at a 20-day breakout-ish strength (close > 20d mean).
  EXIT when daily close < daily EMA(fast) (trend weakening),
  or when a completed DAILY CLOSE is 15% or more below the entry price (daily-close stop).
  The exchange-price stoploss is only a -35% catastrophe floor, so a brief intraday wick
  (e.g. Kraken BTC hit $100k on Oct 10, 2025 vs $107k on Coinbase) can't sell at the bottom.
  Changed Sep 28, 2026 from a 15% intraday stop after a 2023-2026 replay: +106% vs +64-70%,
  max drawdown 39% vs 49-51%. Previous version: RevXLRegime.py.bak-2026-09-28
Sits in cash in bear markets. Few trades -> low fees. Profits compound (stake 'unlimited').
"""
from freqtrade.strategy import IStrategy, IntParameter, informative
from pandas import DataFrame
import talib.abstract as ta


class RevXLRegime(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = "1h"
    can_short = False
    startup_candle_count = 30

    stoploss = -0.35                     # catastrophe floor only; the real stop is daily_close_stop below
    daily_close_stop_pct = 0.15          # exit if a completed daily close is 15%+ below entry
    trailing_stop = False
    minimal_roi = {"0": 100}             # no take-profit cap: ride the trend
    use_exit_signal = True
    process_only_new_candles = True

    fast = IntParameter(10, 40, default=20, space="buy")
    slow = IntParameter(40, 120, default=50, space="buy")

    @property
    def protections(self):
        return [
            {"method": "CooldownPeriod", "stop_duration_candles": 24},
            # KILL SWITCH: >25% drawdown over ~60 days -> stop opening trades for 14 days
            {"method": "MaxDrawdown", "lookback_period_candles": 1440, "trade_limit": 2,
             "stop_duration_candles": 336, "max_allowed_drawdown": 0.25},
        ]

    @informative("1d")
    def populate_indicators_1d(self, df: DataFrame, metadata: dict) -> DataFrame:
        for n in (10, 20, 30, 40, 50, 60, 80, 100):
            df[f"ema{n}"] = ta.EMA(df, timeperiod=n)
        df["sma20"] = df["close"].rolling(20).mean()
        return df

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        return df

    def populate_entry_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        f, s = df[f"ema{self.fast.value}_1d"], df[f"ema{self.slow.value}_1d"]
        df.loc[
            (df["close_1d"] > s) & (f > s) & (df["close_1d"] > df["sma20_1d"]) & (df["volume"] > 0),
            "enter_long",
        ] = 1
        return df

    def populate_exit_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        f = df[f"ema{self.fast.value}_1d"]
        df.loc[df["close_1d"] < f, "exit_long"] = 1
        return df

    def custom_exit(self, pair, trade, current_time, current_rate, current_profit, **kwargs):
        """Daily-close stop: uses the last COMPLETED daily candle (close_1d), not intraday prices."""
        df, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if df is None or df.empty or "close_1d" not in df.columns:
            return None
        close_1d = df["close_1d"].iloc[-1]
        if close_1d == close_1d and close_1d <= trade.open_rate * (1 - self.daily_close_stop_pct):
            return "daily_close_stop"
        return None
