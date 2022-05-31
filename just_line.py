import pandas as pd
import plotly.express as px
import yfinance as yf

# Your filepath to the csv
filepath = 'copy your filepath here'

# Tickers you wish to compare
compared_tickers = ['SPY', 'QQQ', 'VTI']


trans = pd.read_csv(filepath)
trans = pd.DataFrame(
    trans, columns=['Date', 'Ticker', 'Price', 'Amount']).dropna()

for i in range(len(trans)):
    trans['Date'][i] = trans['Date'][i].replace('/', '-')

# Basic holdings info
ticker_cb = trans.groupby('Ticker')['Price'].mean()
ticker_amt = trans.groupby('Ticker')['Amount'].sum()
ticker_symbol = [i for i in ticker_amt.index]

# Append cost columns
trans['Cost'] = trans['Price'] * trans['Amount']

start_date = trans.iloc[1]['Date']
end_date = trans.iloc[-1]['Date']


# Get historical price
def get_stock_price(ticker):
    data = yf.download(ticker, start=start_date, end=end_date)['Open']
    return data


# Init history price for holdings
price_history = pd.DataFrame()
for i in ticker_symbol:
    price_history[i] = get_stock_price(i)

holding_list = trans.drop_duplicates('Ticker')['Ticker']
date_list = trans.drop_duplicates('Date')['Date']
testdf = pd.DataFrame(index=date_list)

# Create a new df that have share amount of all positions at given date
secdf = pd.DataFrame()
for i in holding_list:
    subdf = trans[trans['Ticker'] == i]
    del subdf['Ticker']
    del subdf['Price']
    del subdf['Cost']
    subdf.columns = ['Date', i]
    secdf = pd.merge(testdf, subdf, on='Date', how='left')
    testdf = secdf

# Position at any given date
holdings = testdf.groupby('Date', sort=False).sum().cumsum()

# Formate the price_history given same index as holdings
price_history = pd.DataFrame(price_history, index=holdings.index)
price_history.fillna(method='ffill', inplace=True)

# Get portofolio value at any given date
port_value = price_history.mul(holdings).sum(axis=1)

# Get the benchamark portfolio value history


def get_bench_his(ticker):
    # Get benchmark performace
    benchmark_his = get_stock_price(ticker)
    benchmark_his = pd.DataFrame(benchmark_his, index=holdings.index)
    benchmark_his.fillna(method='ffill', inplace=True)

    # Get buy dollar amount at any given date
    benchmark_his['Buy Cost'] = pd.DataFrame(
        trans.groupby('Date', sort=False).sum()['Cost'])

    # Get amount of VOO able to buy given the dolloar used that day
    benchmark_his['Buy Amount'] = benchmark_his['Buy Cost'] / \
        benchmark_his['Open']

    # Get value of VOO portfolio at any given date
    benchmark_port = benchmark_his.groupby('Date', sort=False).sum().cumsum()
    benchmark_port_value = benchmark_his['Open'].mul(
        benchmark_port['Buy Amount'])

    return benchmark_port_value


# Create empty columns in the plot df
plot_df = pd.DataFrame()
plot_df['Date'] = port_value.index
plot_df['PortValue'] = [1] * len(port_value)
for i in range(len(port_value)):
    plot_df['PortValue'][i] = port_value[i]

# Initialize the line with your portfolio
line_fig = px.line(plot_df, x='Date', y='PortValue',
                   labels={'Date': 'Date Since Inception',
                           'PortValue': 'Portfolio Value'},
                   hover_data={'PortValue': ':.2f'},
                   )
line_fig.add_scatter(x=plot_df['Date'], y=plot_df['PortValue'], name='Mine')

# Customize the chart
line_fig.update_xaxes(rangeslider_visible=True)
line_fig.update_layout(legend=dict(yanchor='top', y=0.99,
                                   xanchor='left', x=0.05),
                       font_color="white", font_family="Book Antiqua",
                       hovermode='x unified', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgb(0,0,0)')
# Add ticker to the plot df


def add_ticker(tickerlist):
    for ticker in tickerlist:
        plot_df[ticker] = [1] * len(plot_df)
        ticker_series = get_bench_his(ticker)
        for i in range(len(plot_df)):
            plot_df[ticker][i] = ticker_series[i]
        line_fig.add_scatter(x=plot_df['Date'], y=plot_df[ticker], name=ticker)


add_ticker(compared_tickers)
line_fig.show()
