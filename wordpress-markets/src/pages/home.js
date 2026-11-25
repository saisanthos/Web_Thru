  tape([
    ['BSE:SENSEX', 'Sensex'], ['FOREXCOM:SPXUSD', 'S&P 500'], ['FOREXCOM:NSXUSD', 'Nasdaq 100'],
    ['FOREXCOM:DJI', 'Dow Jones'], ['FX_IDC:USDINR', 'USD/INR'], ['OANDA:XAUUSD', 'Gold'],
    ['OANDA:WTICOUSD', 'Crude oil'], ['BINANCE:BTCUSDT', 'Bitcoin'], ['BINANCE:ETHUSDT', 'Ethereum']
  ]);
  overview('wt-overview', [
    ['India', [['BSE:SENSEX', 'Sensex'], ['BSE:RELIANCE', 'Reliance Industries'], ['BSE:HDFCBANK', 'HDFC Bank'],
      ['BSE:TCS', 'TCS'], ['BSE:INFY', 'Infosys'], ['BSE:ICICIBANK', 'ICICI Bank']]],
    ['USA', [['FOREXCOM:SPXUSD', 'S&P 500'], ['FOREXCOM:NSXUSD', 'Nasdaq 100'], ['FOREXCOM:DJI', 'Dow Jones 30'],
      ['NASDAQ:AAPL', 'Apple'], ['NASDAQ:NVDA', 'Nvidia'], ['NASDAQ:MSFT', 'Microsoft']]],
    ['Commodities', [['OANDA:XAUUSD', 'Gold'], ['OANDA:XAGUSD', 'Silver'], ['OANDA:WTICOUSD', 'WTI crude oil'],
      ['OANDA:BCOUSD', 'Brent crude oil']]],
    ['Crypto', [['BINANCE:BTCUSDT', 'Bitcoin'], ['BINANCE:ETHUSDT', 'Ethereum'], ['BINANCE:SOLUSDT', 'Solana'],
      ['BINANCE:XRPUSDT', 'XRP']]],
    ['Forex', [['FX_IDC:USDINR', 'USD/INR'], ['FX_IDC:EURINR', 'EUR/INR'], ['FX:EURUSD', 'EUR/USD'],
      ['FX:GBPUSD', 'GBP/USD'], ['FX:USDJPY', 'USD/JPY']]]
  ], 520);
  calendar('wt-cal', 'in,us', 520);
  heatmap('wt-heat-us', 'SPX500', 480);
  heatmap('wt-heat-in', 'SENSEX', 480);
  news('wt-news', { feedMode: 'all_symbols' }, 520);
  movers('wt-movers-us', 'US', 520);
