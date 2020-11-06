import pandas as pd
from datetime import timezone
from datetime import datetime
import yfinance as yf

# from yahoofinancials import YahooFinancials

# dt = datetime.now().date()
# dt = str(dt)
# dx = dt.split('-')

date = datetime(2020,11,20)

ticker = "FB"

# currentPrice = yf.download(ticker, start=date, progress=True)
# currentPrice.head()

# dt = datetime(int(dx[0]), int(dx[1]), int(dx[2]))
# timestamp = int(dt.replace(tzinfo=timezone.utc).timestamp())

timestamp = int(date.replace(tzinfo=timezone.utc).timestamp())

timestamp = str(timestamp)

temp = pd.read_html("https://finance.yahoo.com/quote/"+ticker+"/options?date="+timestamp+"&p="+ticker+"&straddle=true")

temp = temp[0]

print(timestamp)