  document.getElementById('wt-market').value = 'IN';
  tape([
    ['BSE:SENSEX', 'Sensex'], ['BSE:RELIANCE', 'Reliance'], ['BSE:HDFCBANK', 'HDFC Bank'],
    ['BSE:ICICIBANK', 'ICICI Bank'], ['BSE:INFY', 'Infosys'], ['BSE:TCS', 'TCS'],
    ['BSE:SBIN', 'SBI'], ['FX_IDC:USDINR', 'USD/INR'], ['OANDA:XAUUSD', 'Gold']
  ]);
  chartOverview('wt-hero', [['BSE:SENSEX', 'Sensex'], ['FX_IDC:USDINR', 'USD/INR']], 460);
  overview('wt-overview', [
    ['Top companies', [['BSE:RELIANCE', 'Reliance Industries'], ['BSE:HDFCBANK', 'HDFC Bank'],
      ['BSE:BHARTIARTL', 'Bharti Airtel'], ['BSE:TCS', 'TCS'], ['BSE:ICICIBANK', 'ICICI Bank'], ['BSE:SBIN', 'State Bank of India']]],
    ['Banks', [['BSE:HDFCBANK', 'HDFC Bank'], ['BSE:ICICIBANK', 'ICICI Bank'], ['BSE:SBIN', 'State Bank of India'],
      ['BSE:KOTAKBANK', 'Kotak Mahindra Bank'], ['BSE:AXISBANK', 'Axis Bank']]],
    ['IT', [['BSE:TCS', 'TCS'], ['BSE:INFY', 'Infosys'], ['BSE:HCLTECH', 'HCLTech'],
      ['BSE:WIPRO', 'Wipro'], ['BSE:TECHM', 'Tech Mahindra']]],
    ['Rupee and gold', [['FX_IDC:USDINR', 'USD/INR'], ['FX_IDC:EURINR', 'EUR/INR'], ['FX_IDC:GBPINR', 'GBP/INR'],
      ['OANDA:XAUUSD', 'Gold (USD)']]]
  ], 460);
  heatmap('wt-heat', 'SENSEX', 520);
  movers('wt-movers', 'BSE', 520);
  screener('wt-screener', 'india', 520);
  overview('wt-adr', [
    ['US listings', [['NYSE:INFY', 'Infosys'], ['NYSE:HDB', 'HDFC Bank'], ['NYSE:IBN', 'ICICI Bank'],
      ['NYSE:WIT', 'Wipro'], ['NYSE:RDY', "Dr. Reddy's"], ['NASDAQ:MMYT', 'MakeMyTrip']]]
  ], 460);
  calendar('wt-cal', 'in', 460);
