import matplotlib.pyplot as plt

plt.switch_backend('Agg')
from io import BytesIO
import base64
import pandas as pd
from .models import StockTicker
import os
import datetime, time
import requests

index_ticker_hash = {
    'S&P 500': '^GSPC',
    'DJIA': '^DJI',
    'NASDAQ-100': '^NDX'
}

index_name_hash = {
    'S&P 500': 'Standard & Poor\'s 500',
    'DJIA': 'Dow Jones Industrial Average',
    'NASDAQ-100': 'Nasdaq-100'
}


def add_tickers_to_db():
    """
    Deletes all previous entries and add the rows of the stocks.csv file into the database.

    :return: None
    """
    csv_path = os.path.join(os.path.dirname(__file__), 'stocks.csv')
    tickers_df = pd.read_csv(csv_path)

    StockTicker.objects.all().delete()
    for index, row in tickers_df.iterrows():
        _, _ = StockTicker.objects.get_or_create(
            ticker=row['ticker'],
            first_trade_date=row['first_trade_date'],
            company_name=row['company_name']
        )


def filter_stock_by_start_date(start_date):
    """
    Filters out the stocks that have a first trade date that is greater than the start date set by the user

    :param start_date: A string that represents the start date set by the user in the Stock Market Parameters page. The
    format of the string is YYYY-MM-DD
    :return filtered_stocks: A list of strings representing all the filtered stocks
    """
    filtered_stocks = []
    stock_tickers = StockTicker.objects.all()

    for stock in stock_tickers:
        first_trade_date = stock.first_trade_date
        if first_trade_date < start_date:
            filtered_stocks.append((stock.ticker, stock.company_name))
    return filtered_stocks


def query_historical_stock_data(stock_ticker, start_date, end_date):
    """
    Makes a request to the Yahoo Finance API for the historical stock data of the given stock. The time period for the
    historical stock data is defined by the start_date and end_date. The response to the server is then returned as
    a dictionary.

    :param stock_ticker: A string that represents the specific ticker that is used
    :param start_date: A string that represents the start date set by the user in the Stock Market Parameters page. The
    format of the string is YYYY-MM-DD
    :param end_date: A string that represents the end date set by the user in the Stock Market Parameters page. The
    format of the string is YYYY-MM-DD
    :return data: A dictionary containing the server's response
    """
    url = 'https://query1.finance.yahoo.com/v7/finance/chart/{stock_ticker}?period1={start_date}&period2={end_date}\
    &interval=1d&events=history&includeAdjustedClose=true'
    user_agent_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko)\
         Chrome/39.0.2171.95 Safari/537.36'}

    query_url = url.format(stock_ticker=stock_ticker, start_date=start_date, end_date=end_date)

    response = requests.get(url=query_url, headers=user_agent_headers)
    data = response.json()
    return data

def ticker_extractor(chosen_stock):
    """
    Extracts the ticker from the chosen_stock string.

    :param chosen_stock: A string with the formet of Ticker:Company Name
    :return res: The substring that represents the ticker
    """
    res = ""
    for char in chosen_stock:
        if char == ":":
            break
        res += char

    return res


def calculate_investment_fluctuations(stock_data, amount_invested):
    """
    Calculates the change in the initial investment amount for a specific stock in terms of raw dollars and percentages

    :param stock_data: The array of historical stock data
    :param amount_invested: An integer representing the amount invested in the given stock. This is defined by the
    user input in the Stock Selection page
    :return stock_growth: A tuple of two integer lists containing the growth of the stock in terms of percentages in the
    first index, and raw dollars in the second index
    """

    stock_growth_percentage = [(x / stock_data[0]) * 100 for x in stock_data]

    # The growth of the investment in dollars (based on amount invested)
    stock_investment_growth = [(percentage * float(amount_invested)) / 100 for percentage in stock_growth_percentage]

    stock_growth = (stock_growth_percentage, stock_investment_growth)

    return stock_growth


def calculate_overall_stock_change(stock_data):
    """
    Calculates the overall growth of a stock, represented in percentages

    :param stock_data: The array representing the historical price changes of the investment of a stock
    :return: A tuple of strings, first representing the change in percentage, and the second representing the change in
    raw dollars
    """

    percentage_change = ((stock_data[-1] - stock_data[0]) / stock_data[0]) * 100
    dollar_change = stock_data[-1] - stock_data[0]

    percentage_res = f"{percentage_change:.2f}%"

    # There's no need to append '-' if percentage_change is less than 0 since the value itself will be negative
    if percentage_change > 0:
        percentage_res = "+" + percentage_res

    # If dollar_change is less than 0 and the string isn't reformatted, it will print out values such as $-201. Thus,
    # it is reformatted as follows
    if dollar_change > 0:
        dollar_res = f"+${dollar_change:.2f}"
    else:
        dollar_res = f"-${abs(dollar_change):.2f}"

    return (percentage_res, dollar_res)


def create_plotting_df(start_date, end_date, stock_portfolio, index):
    """
    Creates a pandas dataframe to be used for plotting the results. The columns are comprised of the value of the
    user's portfolio (in $), the value of the selected index (in $), the growth of the portfolio (in %), and the
    growth of the index (in %). Additionally, the growth of each stock (in %) in the portfolio is added as a column.

    :param start_date: A string that represents the start date set by the user in the Stock Market Parameters page. The
    format of the string is YYYY-MM-DD
    :param end_date: A string that represents the end date set by the user in the Stock Market Parameters page. The
    format of the string is YYYY-MM-DD
    :param stock_portfolio: A dictionary with key value pairs of Ticker:Investment amount that represents the user's
    portfolio
    :param index: A string representing the index that is chosen by the user
    :return portfolio_and_index_tracker: A pandas dataframe containing the total value of the user's portfolio and
    index, the growth of the portfolio and index, and the growth of each stock that make up the index

    """
    index_ticker = index_ticker_hash[index]
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

        # If the dataframe is empty, add the timestamp indices and create the default 4 columns
        if portfolio_and_index_tracker.empty:
            timestamp_epoch = stock_data['chart']['result'][0]['timestamp']
            timestamp_datetime = [datetime.datetime.utcfromtimestamp(time).date() for time in timestamp_epoch]

            portfolio_and_index_tracker = pd.DataFrame(0, index=timestamp_datetime,
                                                       columns=['Portfolio Value', 'Index Value', 'Portfolio Growth',
                                                                'Index Growth'])

        historical_stock_data = stock_data['chart']['result'][0]['indicators']['quote'][0]['close']
        stock_growth = calculate_investment_fluctuations(historical_stock_data, amount_invested_stock)

        for i in range(len(stock_growth[0])):
            portfolio_and_index_tracker['Portfolio Value'][i] += stock_growth[1][i]

        # Add the individual stock fluctuations (in $) into the dataframe
        portfolio_and_index_tracker[ticker] = stock_growth[1]

    for i in range(len(stock_growth[0])):
        portfolio_and_index_tracker['Portfolio Growth'][i] = (portfolio_and_index_tracker['Portfolio Value'][i] /
                                                              portfolio_and_index_tracker['Portfolio Value'][0]) * 100

    # Historical price of the index
    index_data = query_historical_stock_data(index_ticker, start_date_epoch, end_date_epoch)
    historical_index_data = index_data['chart']['result'][0]['indicators']['quote'][0]['close']

    index_growth = calculate_investment_fluctuations(historical_index_data, amount_invested_index)

    portfolio_and_index_tracker['Index Value'] = index_growth[1]
    portfolio_and_index_tracker['Index Growth'] = index_growth[0]

    return portfolio_and_index_tracker


def plot_stock_data(portfolio_and_index_tracker, index, portfolio_only=False, percentage=False):
    """
    Creates a plot for the data and returns a string of decoded bytes that represent the plotted graph as
    a PNG image

    :param portfolio_and_index_tracker: A pandas dataframe returned by the create_plotting_df function
    :param index: A string representing the index that is chosen by the user
    :param portfolio_only: A boolean value to determine whether only the portfolio should be graphed or not. If False,
    the graph will include both the portfolio and the index
    :param percentage: A boolean value to determine whether the percentage should be graphed or not. If False,
    the graph is plotted with regards to the dollar
    :return graph: A string of decoded bytes that represent the graph as a PNG image
    """
    index_name = index_name_hash[index]

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

    # plt.savefig('graph.png')

    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    return graph
