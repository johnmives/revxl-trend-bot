# RevXL Trend Bot (lite)

A slow, daily trend-following crypto strategy for [Freqtrade](https://www.freqtrade.io) on Kraken: BTC, ETH and SOL. MIT licensed. Ships in paper-trading mode.

![Worst drawdown since 2019](assets/botkit-cover.png)

## The honest summary

- Backtested since 2019 in the Freqtrade engine: about +401% versus about +566% for simply holding BTC. **It did not beat buy-and-hold.**
- What it does: it cut the worst drawdown from about 77% (BTC) to about 40%, and it made about +23% in the 2021-22 bear market while BTC lost about 62%.
- Win rate is about 31%. A few large winners pay for many small losses.
- Backtests are not promises. This is not financial advice.

## Rules

- Buy when the daily close is above the 50-day EMA, the 20-day EMA is above the 50-day EMA, and the close is above its 20-day average.
- Sell when the daily close drops below the 20-day EMA.
- Stop: exit when a daily CLOSE ends 15% below entry. Intraday wicks do not trigger it. A -35% exchange stop is only a catastrophe floor.
- Kill switch: after a 25% loss in about 60 days, no new trades for 14 days.
- At most 3 positions.

## Run it (paper first)

```bash
cp .env.example .env          # leave FREQTRADE__DRY_RUN=true
docker compose up -d
docker compose logs -f
python3 tests/test_daily_close_stop.py   # stop-logic regression fixtures
```

Use Kraken API keys with withdrawals OFF, and only after at least 30 days of paper trading.

## Want the research behind it?

This repo is the strategy only. The **[full Trend Bot Kit](https://revxljohn.gumroad.com/l/trend-bot-kit)** adds the walk-forward lab (10 strategies, data fetcher, results CSV), the Kraken vs Coinbase feed cross-check, the reserve ensemble strategy and a Mac 24/7 setup.

Write-ups: [jcalloway.hashnode.dev](https://jcalloway.hashnode.dev) and [jcalloway.dev](https://jcalloway.dev).


## Taxes on bot trades (US)

Every sell the bot makes is a taxable event. 2026 is the first year Kraken's Form 1099-DA can include cost basis, and only for coins bought in the same account from Jan 1, 2026, so check it before filing.

Step 1: in Kraken, open Documents and export Trades from your first trade to today.

Step 2: get a quick FIFO estimate and a list of sells missing basis with the free, in-browser [Kraken tax estimator](https://jcalloway.dev/tools/kraken-crypto-tax-estimator).

Step 3: for the actual filing (Form 8949), import the export into tax software such as [CoinLedger](https://jcalloway.dev/go/coinledger) (code CRYPTOTAX10 for 10% off) or [Koinly](https://jcalloway.dev/go/koinly).

Partner links: the author may earn a commission. Not tax advice.
