from bs4 import BeautifulSoup as bs4
import requests
import re
import csv
import datetime as dt

def extract_ticker_and_name(soup):
    """
    Extracts the ticker and name of the company from a BeautifulSoup object. When extracting the tickers and name,
    it also excludes all stock tickers with . or -

    :param soup: A BeautifulSoup object
    :return all_tickers: A set of strings containing all of the tickers that are extracted from the BeautifulSoup
    object, excluding those with . or -
    """
    all_tickers = set()

    for row in soup:
        company_ticker = row.contents[0].text
        company_name = row.contents[1].text

        if re.search('\.|-', company_ticker) or len(company_ticker) > 4:
            continue
        else:
            all_tickers.add((company_name, company_ticker))

    return all_tickers

def get_all_tickers():
    """
    Scrapes the eoddata.com website to get all the tickers from the NYSE and NASDAQ exchange

    :return all_tickers: A set of strings containing all of the tickers from the NYSE and NASDAQ exchanges,
    excluding those with . or -
    """
    urls = ['https://eoddata.com/stocklist/NYSE/{alphabet}.htm', 'https://eoddata.com/stocklist/NASDAQ/{alphabet}.htm']
    all_tickers = set()

    for url in urls:
        for i in range(26):
            alphabet = chr(ord('A') + i)
            page = requests.get(url.format(alphabet=alphabet))
            soup = bs4(page.content, 'html.parser')

            odd_rows = soup.find_all("tr", {"class": "ro"})
            even_rows = soup.find_all("tr", {"class": "re"})

            odd_row_stocks = extract_ticker_and_name(odd_rows)
            even_row_tickers = extract_ticker_and_name(even_rows)

            all_tickers.update(odd_row_stocks)
            all_tickers.update(even_row_tickers)
    return all_tickers


def create_stock_data():
    """
    Creates a csv file with three columns: company_name, ticker, and first_trade_date. The first_trade_date is
    extracted by querying the stock data through the Yahoo Finance API

    :return: None, but creates a stocks.csv file that is saved under the base directory
    """

    # Set the user agent headers to be able to send queries to Yahoo Finance
    user_agent_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/39.0.2171.95 Safari/537.36'}

    # The Yahoo Finance url for making queries
    query_url = 'https://query2.finance.yahoo.com/v8/finance/chart/{ticker}'

    all_tickers = get_all_tickers()

    csv_data = {
        'company_name': [],
        'ticker': [],
        'first_trade_date': []
    }

    for company, ticker in all_tickers:
        # Format the request url and use it to get the stock data
        request_url = query_url.format(ticker=ticker)
        print(f"Requested ticker: {ticker}")
        data = requests.get(
            url=request_url,
            headers=user_agent_headers
        )
        data = data.json()

        # Get the first trade year of the specific stock in epoch form
        try:
            first_date_epoch = data['chart']['result'][0]['meta']['firstTradeDate']
        except:
            print(f"Ticker for {company} failed")
            continue

        # If the first trade year exists, append it to the first_trade_date key. Otherwise, append 0
        if first_date_epoch:
            csv_data['first_trade_date'].append(first_date_epoch)
        else:
            csv_data['first_trade_date'].append(0)

        # Add the stock ticker and company name to the dictionary
        csv_data['ticker'].append(ticker)
        csv_data['company_name'].append(company)

    # Write all the data into a csv file
    with open('base/stocks.csv', 'w') as f:
        writer = csv.writer(f)

        writer.writerow(csv_data.keys())

        for row in zip(*csv_data.values()):
            writer.writerow(row)

create_stock_data()
