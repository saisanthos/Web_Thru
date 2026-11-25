  var DEFAULT_SYMBOL = 'FOREXCOM:SPXUSD';
  var NON_EQUITY = ['FOREXCOM', 'OANDA', 'FX', 'FX_IDC', 'BINANCE', 'COINBASE', 'CAPITALCOM',
    'BITSTAMP', 'KRAKEN', 'TVC', 'INDEX', 'CRYPTO'];

  var params = new URLSearchParams(location.search);
  var raw = (params.get('tvwidgetsymbol') || params.get('symbol') || '').trim().toUpperCase();
  var sym = SYMBOL_RE.test(raw) ? raw : DEFAULT_SYMBOL;
  var notes = [];

  if (sym.indexOf('NSE:') === 0) {
    sym = 'BSE:' + sym.slice(4);
    notes.push('NSE prices are not available in these free widgets, so this page shows the same company on BSE.');
  }
  var exch = sym.indexOf(':') > -1 ? sym.split(':')[0] : '';
  var ticker = sym.split(':').pop();
  var isIndia = exch === 'BSE';
  var isEquity = NON_EQUITY.indexOf(exch) === -1 && !(isIndia && /^(SENSEX|BSE)/.test(ticker));

  if (isIndia) {
    notes.push('Indian prices come from BSE and update at the end of each trading day, so use the daily (1 day) view for the chart and technical ratings.');
    document.getElementById('wt-market').value = 'IN';
  } else {
    document.getElementById('wt-market').value = 'US';
  }

  var NAMES = {
    'FOREXCOM:SPXUSD': 'S&P 500', 'FOREXCOM:NSXUSD': 'Nasdaq 100', 'FOREXCOM:DJI': 'Dow Jones',
    'BSE:SENSEX': 'Sensex', 'FX_IDC:USDINR': 'USD/INR', 'OANDA:XAUUSD': 'Gold', 'BINANCE:BTCUSDT': 'Bitcoin'
  };
  var name = NAMES[sym] || ticker;
  document.title = name + ' price, chart and technical analysis';
  document.getElementById('wt-title').textContent = name + ' price, chart and technical analysis';
  document.getElementById('wt-crumb').textContent = 'Markets / ' + (exch ? exch + ' / ' : '') + ticker;

  var banners = document.getElementById('wt-banners');
  notes.forEach(function (n) {
    var p = document.createElement('p');
    p.className = 'wt-banner';
    p.textContent = n;
    banners.appendChild(p);
  });

  function hideSection(id) {
    document.getElementById(id).classList.add('wt-hide');
    var tab = document.querySelector('.wt-tabs a[data-sec="' + id + '"]');
    if (tab) tab.classList.add('wt-hide');
  }

  tape([
    ['BSE:SENSEX', 'Sensex'], ['FOREXCOM:SPXUSD', 'S&P 500'], ['FOREXCOM:NSXUSD', 'Nasdaq 100'],
    ['FOREXCOM:DJI', 'Dow Jones'], ['FX_IDC:USDINR', 'USD/INR'], ['OANDA:XAUUSD', 'Gold'], ['BINANCE:BTCUSDT', 'Bitcoin']
  ]);
  mount('wt-info', 'symbol-info', { symbol: sym, width: '100%' });
  mount('wt-chart-w', 'advanced-chart', {
    symbol: sym,
    autosize: true,
    interval: 'D',
    timezone: 'exchange',
    theme: THEME,
    style: '1',
    allow_symbol_change: false,
    calendar: false,
    withdateranges: true,
    hide_side_toolbar: false,
    details: false,
    support_host: 'https://www.tradingview.com'
  }, 560);
  mount('wt-tech-w', 'technical-analysis', {
    symbol: sym,
    interval: '1D',
    showIntervalTabs: true,
    displayMode: 'multiple',
    width: '100%',
    height: '100%'
  }, 480);

  if (isEquity) {
    mount('wt-profile', 'symbol-profile', { symbol: sym, width: '100%', height: '100%' }, 420);
    mount('wt-fin', 'financials', { symbol: sym, displayMode: 'regular', width: '100%', height: '100%' }, 420);
  } else {
    hideSection('wt-company');
  }

  if (!isIndia) {
    news('wt-news-w', { feedMode: 'symbol', symbol: sym }, 460);
  } else {
    hideSection('wt-news');
  }

  var chips = [
    ['India', [['BSE:SENSEX', 'Sensex'], ['BSE:RELIANCE', 'Reliance'], ['BSE:TCS', 'TCS'], ['BSE:HDFCBANK', 'HDFC Bank'], ['BSE:INFY', 'Infosys']]],
    ['USA', [['FOREXCOM:SPXUSD', 'S&P 500'], ['NASDAQ:AAPL', 'Apple'], ['NASDAQ:NVDA', 'Nvidia'], ['NASDAQ:MSFT', 'Microsoft'], ['NASDAQ:TSLA', 'Tesla']]],
    ['Other', [['BINANCE:BTCUSDT', 'Bitcoin'], ['OANDA:XAUUSD', 'Gold'], ['FX_IDC:USDINR', 'USD/INR']]]
  ];
  var box = document.getElementById('wt-chips');
  chips.forEach(function (group) {
    var label = document.createElement('span');
    label.textContent = group[0] + ':';
    box.appendChild(label);
    group[1].forEach(function (c) {
      var a = document.createElement('a');
      a.href = symbolUrl(c[0]);
      a.textContent = c[1];
      box.appendChild(a);
    });
  });
