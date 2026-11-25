(function () {
  // ---- Settings you may want to change ----
  // Address of the symbol detail page. Every widget sends clicks here.
  var SITE = /^https?:$/.test(location.protocol) ? location.origin : 'https://webthruservices.com';
  var SYMBOL_PAGE = SITE + '/markets/symbol/';
  var THEME = 'light';   // 'light' or 'dark'
  var LOCALE = 'en';
  // -----------------------------------------

  var SYMBOL_RE = /^([A-Z0-9_]{1,20}:)?[A-Z0-9_.!&\-]{1,30}$/;

  function mount(id, file, cfg, height) {
    var host = document.getElementById(id);
    if (!host) return;
    host.innerHTML = '';
    // TradingView resets its own container to 100% height, so the fixed height goes on the outer box.
    if (height) host.style.height = height + 'px';
    var box = document.createElement('div');
    box.className = 'tradingview-widget-container';
    box.style.height = '100%';
    var inner = document.createElement('div');
    inner.className = 'tradingview-widget-container__widget';
    inner.style.height = '100%';
    box.appendChild(inner);
    var s = document.createElement('script');
    s.src = 'https://s3.tradingview.com/external-embedding/embed-widget-' + file + '.js';
    s.async = true;
    var base = { locale: LOCALE, colorTheme: THEME, isTransparent: true };
    for (var k in cfg) base[k] = cfg[k];
    s.text = JSON.stringify(base);
    box.appendChild(s);
    host.appendChild(box);
  }

  function symbolUrl(sym) {
    return SYMBOL_PAGE + '?tvwidgetsymbol=' + encodeURIComponent(sym);
  }

  function tape(list) {
    mount('wt-tape', 'ticker-tape', {
      symbols: list.map(function (x) { return { proName: x[0], title: x[1] }; }),
      showSymbolLogo: true,
      displayMode: 'adaptive',
      largeChartUrl: SYMBOL_PAGE
    });
  }

  function overview(id, tabs, height) {
    mount(id, 'market-overview', {
      dateRange: '12M',
      showChart: true,
      showSymbolLogo: true,
      showFloatingTooltip: false,
      width: '100%',
      height: '100%',
      largeChartUrl: SYMBOL_PAGE,
      tabs: tabs.map(function (t) {
        return {
          title: t[0],
          originalTitle: t[0],
          symbols: t[1].map(function (x) { return { s: x[0], d: x[1] }; })
        };
      })
    }, height || 480);
  }

  function heatmap(id, dataSource, height) {
    mount(id, 'stock-heatmap', {
      dataSource: dataSource,
      exchanges: [],
      grouping: 'sector',
      blockSize: 'market_cap_basic',
      blockColor: 'change',
      hasTopBar: false,
      isDataSetEnabled: false,
      isZoomEnabled: true,
      hasSymbolTooltip: true,
      isMonoSize: false,
      width: '100%',
      height: '100%',
      symbolUrl: SYMBOL_PAGE
    }, height || 520);
  }

  function movers(id, exchange, height) {
    mount(id, 'hotlists', {
      exchange: exchange,
      dateRange: '12M',
      showChart: true,
      showSymbolLogo: true,
      showFloatingTooltip: false,
      width: '100%',
      height: '100%',
      largeChartUrl: SYMBOL_PAGE
    }, height || 480);
  }

  function screener(id, market, height) {
    mount(id, 'screener', {
      market: market,
      defaultColumn: 'overview',
      defaultScreen: 'most_capitalized',
      showToolbar: true,
      width: '100%',
      height: '100%',
      largeChartUrl: SYMBOL_PAGE
    }, height || 520);
  }

  function calendar(id, countries, height) {
    mount(id, 'events', {
      importanceFilter: '0,1',
      countryFilter: countries,
      width: '100%',
      height: '100%'
    }, height || 480);
  }

  function news(id, cfg, height) {
    var c = { displayMode: 'regular', width: '100%', height: '100%' };
    for (var k in cfg) c[k] = cfg[k];
    mount(id, 'timeline', c, height || 480);
  }

  function chartOverview(id, list, height) {
    mount(id, 'symbol-overview', {
      symbols: list.map(function (x) { return [x[1], x[0] + '|12M']; }),
      chartOnly: false,
      width: '100%',
      height: '100%',
      showVolume: false,
      showMA: false,
      hideDateRanges: false,
      hideMarketStatus: false,
      hideSymbolLogo: false,
      scalePosition: 'right',
      scaleMode: 'Normal',
      noTimeScale: false,
      valuesTracking: '1',
      changeMode: 'price-and-percent',
      chartType: 'area',
      lineWidth: 2,
      dateRanges: ['1m|1D', '3m|1D', '12m|1D', '60m|1W', 'all|1M']
    }, height || 440);
  }

  // Search box in the menu bar
  var form = document.getElementById('wt-search');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var q = document.getElementById('wt-q');
      var v = q.value.trim().toUpperCase().replace(/\s+/g, '');
      if (!v) { q.focus(); return; }
      var market = document.getElementById('wt-market').value;
      if (v.indexOf(':') === -1 && market === 'IN') v = 'BSE:' + v;
      if (!SYMBOL_RE.test(v)) { q.value = ''; q.placeholder = 'Letters and numbers only'; q.focus(); return; }
      location.href = symbolUrl(v);
    });
  }

  /*PAGE*/
})();
