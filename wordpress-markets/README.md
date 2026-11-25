# WebThru Markets: free markets section for WordPress

Four pages for India and US markets, built from TradingView's free widgets. Nothing costs money.

| File | Page address | What it shows |
|---|---|---|
| `dist/1-markets-overview.html` | `/markets/` | Ticker tape, market overview (India, USA, commodities, crypto, forex), economic calendar, S&P 500 and Sensex heatmaps, top stories, US movers |
| `dist/2-markets-india.html` | `/markets/india/` | Sensex chart, leading Indian stocks by sector, Sensex heatmap, BSE movers, India screener, Indian companies listed in the US, India calendar |
| `dist/3-markets-usa.html` | `/markets/usa/` | Index charts, largest stocks and ETFs, S&P 500 heatmap, movers, US screener, news, US calendar |
| `dist/4-markets-symbol.html` | `/markets/symbol/` | One symbol: price header, candlestick chart, technical gauges (1 minute to monthly), company profile, financials, news |

Each file in `dist/` is a complete block of code (styles, layout and script). You paste one file into one page.

## Setup (about 20 minutes)

You need to be logged in to WordPress as an Administrator. Other roles can't save code that contains scripts.

1. **Create the parent page.** Pages > Add New, title **Markets**, address (slug) `markets`. Click **Edit with Elementor**.
   In Page Settings (gear icon) set Page Layout to **Elementor Full Width** and turn on **Hide Title**.
   Drag in an **HTML** widget, open `1-markets-overview.html` in a plain text editor, copy everything and paste it in.
   Save as draft, preview, then publish.
2. **Create the three child pages the same way**, each with Parent page set to Markets:
   - India, slug `india`: paste `2-markets-india.html`
   - USA, slug `usa`: paste `3-markets-usa.html`
   - Symbol, slug `symbol`: paste `4-markets-symbol.html`
3. **Add Markets to your main menu** (Appearance > Menus, or your Elementor header template).
4. **Test it.** Open `/markets/symbol/?tvwidgetsymbol=BSE:RELIANCE`, click a stock in the Market overview list,
   and search for `tcs` with "India (BSE)" selected.

Not using Elementor? Add a **Custom HTML** block in the block editor and paste the file into it instead.

## If something looks wrong

- **Widgets stay blank:** a speed or caching plugin is probably delaying the script (WP Rocket "Delay JavaScript execution",
  LiteSpeed Cache, Autoptimize). Exclude the four Markets pages, or the word `tradingview`, from JavaScript delay, defer and combine. Then clear the cache.
- **The code disappears after saving:** you're not logged in as an Administrator.
- **Content looks squeezed:** set the Elementor section's Content Width to Full Width.
- **Different page addresses:** change `'/markets/symbol/'` on the `var SYMBOL_PAGE` line in `src/shared.js` and the
  menu links in `src/nav.html`, then rebuild (see below).
- **Different accent colour:** change `--wt-accent:#2962ff` at the start of `src/shared.css`, then rebuild.

## What the free widgets can't do (tested November 2026)

- NSE prices, including Nifty 50, are blocked ("Permission denied"). Indian stocks use BSE instead.
  If someone opens an NSE symbol, the symbol page switches to the same company on BSE and says so.
- BSE prices are end-of-day: they update once after the market closes.
- There is no news for Indian stocks, so the symbol page hides the News section for them.
- The official S&P 500 index is blocked, so US indices use FOREX.com CFD prices that track the S&P 500, Nasdaq 100 and Dow.
  US stock prices are delayed.
- Clicking a heatmap block did not open the symbol page in testing. Clicking a stock in the overview lists and using the search box do.
- TradingView's logo and links stay on the widgets. That's the condition for using them free.

Every page footer says the content is for information only and is not investment advice. Keep that.

## Editing the pages

Don't edit the files in `dist/` by hand. Edit the files in `src/`, then rebuild:

```bash
cd wordpress-markets
python3 build.py
```

- `src/shared.css`, `src/shared.js`, `src/nav.html`, `src/footer.html`: shared by all four pages
  (the `mount()` helper in `shared.js` creates every widget)
- `src/pages/<page>.html` and `src/pages/<page>.js`: the layout and the symbols for each page

After rebuilding, paste the changed file from `dist/` into its WordPress page again.
