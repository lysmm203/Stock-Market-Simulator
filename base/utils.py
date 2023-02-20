import yfinance as yf
import matplotlib.pyplot as plt
plt.switch_backend('Agg')
from io import BytesIO
import base64, uuid
import pandas as pd
from .models import StockTicker
import os
import datetime, time
import requests

index_ticker_hash = {
    's&p': '^GSPC',
    'djia': '^DJI',
    'nasdaq': '^NDX'
}

index_name_hash = {
    's&p': 'S&P 500',
    'djia': 'Dow Jones Industrial Average',
    'nasdaq': 'Nasdaq-100'
}


def add_tickers_to_db():
    csv_path = os.path.join(os.path.dirname(__file__), 'stocks.csv')
    tickers_df = pd.read_csv(csv_path)

    for index, row in tickers_df.iterrows():
        _, _ = StockTicker.objects.get_or_create(
            ticker=row['ticker'],
            first_trade_date=row['first_trade_date'],
            company_name=row['company_name']
        )

# Function to read data from the database and filter out the stocks that fit in the timeframe defined by
# start_year to the current year. end_year isn't needed for filtering as all the stocks in the database
# are valid at the current time that the user runs the program in
def filter_stock_by_start_date(start_date):
    filtered_stocks = []
    stock_tickers = StockTicker.objects.all()

    for stock in stock_tickers:
        first_trade_date = stock.first_trade_date
        if first_trade_date < start_date:
            filtered_stocks.append((stock.ticker, stock.company_name))
    return filtered_stocks


def query_historical_stock_data(stock_ticker, start_date, end_date):
    url = 'https://query1.finance.yahoo.com/v7/finance/chart/{stock_ticker}?period1={start_date}&period2={end_date}&interval=1d&events=history&includeAdjustedClose=true'
    user_agent_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    query_url = url.format(stock_ticker=stock_ticker, start_date=start_date, end_date=end_date)

    response = requests.get(url=query_url, headers=user_agent_headers)
    data = response.json()
    return data

# chosen_stock will be a string of the format Ticker:Company name. The purpose of the ticker_extractor function
# is to extract just the ticker out of the chosen_stock string
def ticker_extractor(chosen_stock):
    res = ""
    for char in chosen_stock:
        if char == ":":
            break
        res += char

    return res


def calculate_stock_growth(stock_data, amount_invested):

    stock_price_history = stock_data['chart']['result'][0]['indicators']['quote'][0]['close']

    stock_growth_percentage = [(x / stock_price_history[0]) * 100 for x in stock_price_history]

    # The growth of the investment in dollars (based on amount invested)
    stock_investment_growth = [(percentage * amount_invested) for percentage in stock_growth_percentage]

    return (stock_growth_percentage, stock_investment_growth)


# The start and end represent the start year and end year set by the user. The stock portfolio refers
# to the dictionary of stocks that are created when
def plot_stock_data(start_date, end_date, stock_portfolio, index, portfolio_only=False, percentage=False):
    index_ticker = index_ticker_hash[index]
    index_name = index_name_hash[index]
    amount_invested_index = 0

    start_date_datetime = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    start_date_epoch = int(time.mktime(start_date_datetime.timetuple()))

    end_date_datetime = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    end_date_epoch = int(time.mktime(end_date_datetime.timetuple()))


    # Create an empty Series to save the dollar values of the user's portfolio. The ticker used is the first ticker of
    # the stock portfolio to copy the TimeStamp index.
    portfolio_and_index_tracker = pd.DataFrame()

    for ticker in stock_portfolio:
        stock_data = query_historical_stock_data(ticker, start_date_epoch, end_date_epoch)
        amount_invested_stock = stock_portfolio[ticker]
        amount_invested_index += stock_portfolio[ticker]

        if portfolio_and_index_tracker.empty:
            timestamp_epoch = stock_data['chart']['result'][0]['timestamp']
            timestamp_datetime = [datetime.datetime.utcfromtimestamp(time).date() for time in timestamp_epoch]

            portfolio_and_index_tracker = pd.DataFrame(0, index=timestamp_datetime, columns=['Portfolio Value', 'Index Value', 'Portfolio Growth', 'Index Growth'])


        stock_growth = calculate_stock_growth(stock_data, amount_invested_stock)

        for i in range(len(stock_growth[0])):
            portfolio_and_index_tracker['Portfolio Value'][i] += stock_growth[1][i]

        # Add the individual stock growth percentage into the dataframe
        portfolio_and_index_tracker[ticker] = stock_growth[1]

    for i in range(len(stock_growth[0])):
        portfolio_and_index_tracker['Portfolio Growth'][i] = (portfolio_and_index_tracker['Portfolio Value'][i]/portfolio_and_index_tracker['Portfolio Value'][0]) * 100

    # Historical price of the index
    index_data = query_historical_stock_data(index_ticker, start_date_epoch, end_date_epoch)

    index_growth = calculate_stock_growth(index_data, amount_invested_index)



    portfolio_and_index_tracker['Index Value'] = index_growth[1]
    portfolio_and_index_tracker['Index Growth'] = index_growth[0]

    portfolio_tracker = portfolio_and_index_tracker.iloc[:, 4:].copy()

    plt.figure(figsize=(10, 4))
    plt.ticklabel_format(style='plain')

    # Portfolio vs Index in dollars
    if not portfolio_only and not percentage:
        plt.plot(portfolio_and_index_tracker['Portfolio Value'], label="Portfolio")
        plt.plot(portfolio_and_index_tracker['Index Value'], label=index_name)
        plt.legend()

    # Portfolio vs Index in percentage
    elif not portfolio_only and percentage:
        plt.plot(portfolio_and_index_tracker['Portfolio Growth'], label="Portfolio")
        plt.plot(portfolio_and_index_tracker['Index Growth'], label=index_name)
        plt.legend()

    # Constituents of Portfolio in dollars
    elif portfolio_only and not percentage:
        for column in portfolio_tracker:
            plt.plot(portfolio_tracker[column], label=column)
        plt.legend()
    # Constituents of Portfolio in percentage
    else:
        for column in portfolio_tracker:
            percentage = portfolio_tracker[column].divide(portfolio_tracker[column][0]) * 100
            plt.plot(percentage, label=column)
        plt.legend()



    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    return graph