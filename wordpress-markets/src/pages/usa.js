  document.getElementById('wt-market').value = 'US';
  tape([
    ['FOREXCOM:SPXUSD', 'S&P 500'], ['FOREXCOM:NSXUSD', 'Nasdaq 100'], ['FOREXCOM:DJI', 'Dow Jones'],
    ['NASDAQ:AAPL', 'Apple'], ['NASDAQ:NVDA', 'Nvidia'], ['NASDAQ:MSFT', 'Microsoft'],
    ['NASDAQ:AMZN', 'Amazon'], ['NASDAQ:GOOGL', 'Alphabet'], ['NASDAQ:TSLA', 'Tesla']
  ]);
  chartOverview('wt-hero', [['FOREXCOM:SPXUSD', 'S&P 500'], ['FOREXCOM:NSXUSD', 'Nasdaq 100'], ['FOREXCOM:DJI', 'Dow Jones 30']], 460);
  overview('wt-overview', [
    ['Largest', [['NASDAQ:NVDA', 'Nvidia'], ['NASDAQ:AAPL', 'Apple'], ['NASDAQ:MSFT', 'Microsoft'],
      ['NASDAQ:GOOGL', 'Alphabet'], ['NASDAQ:AMZN', 'Amazon'], ['NASDAQ:META', 'Meta']]],
    ['Finance', [['NYSE:JPM', 'JPMorgan Chase'], ['NYSE:V', 'Visa'], ['NYSE:MA', 'Mastercard'],
      ['NYSE:BAC', 'Bank of America'], ['NYSE:GS', 'Goldman Sachs']]],
    ['ETFs', [['AMEX:SPY', 'SPDR S&P 500 ETF'], ['NASDAQ:QQQ', 'Invesco QQQ'], ['AMEX:DIA', 'SPDR Dow Jones ETF'],
      ['AMEX:IWM', 'iShares Russell 2000']]]
  ], 460);
  heatmap('wt-heat', 'SPX500', 560);
  movers('wt-movers', 'US', 520);
  screener('wt-screener', 'america', 520);
  news('wt-news', { feedMode: 'market', market: 'stock' }, 480);
  calendar('wt-cal', 'us', 480);
