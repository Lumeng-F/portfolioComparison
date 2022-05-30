import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf

filepath = '../project_ana/static/user_csv/userupload.csv'

def userdf(filepath):
    trans = pd.read_csv(filepath)
    trans = pd.DataFrame(trans, columns=['Date', 'Ticker', 'Price', 'Amount']).dropna()

    for i in range(len(trans)):
        trans['Date'][i] = trans['Date'][i].replace('/', '-')

    # Basic holdings info
    ticker_cb = trans.groupby('Ticker')['Price'].mean()
    ticker_amt = trans.groupby('Ticker')['Amount'].sum()
    ticker_symbol = [i for i in ticker_amt.index]

    # Append cost columns
    trans['Cost'] = trans['Price'] * trans['Amount']
    print(1)
    return trans

def get_stock_price(df, ticker):
    data = yf.download(ticker, start=df.iloc[1]['Date'], 
                        end=df.iloc[-1]['Date'])['Open']
    print(2)

    return data

def get_price_history(df):
    amt = df.groupby('Ticker')['Amount'].sum()
    symbol = [i for i in amt.index]
    price_history = pd.DataFrame()
    for i in symbol:
        price_history[i] = get_stock_price(df, i)
    
    price_history = pd.DataFrame(price_history, index=get_holdings(df).index)
    price_history.fillna(method='ffill', inplace=True)
    print(3)

    return price_history

def get_holdings(df):
    holding_list = df.drop_duplicates('Ticker')['Ticker']
    date_list = df.drop_duplicates('Date')['Date']
    tempdf = pd.DataFrame(index=date_list)
    tempdf2 = pd.DataFrame()
    for i in holding_list:
        tempdf3 = df[df['Ticker'] == i]
        del tempdf3['Ticker']
        del tempdf3['Price']
        del tempdf3['Cost']
        tempdf3.columns = ['Date', i]
        tempdf2 = pd.merge(tempdf, tempdf3, on='Date', how='left')
        tempdf = tempdf2
    holdings = tempdf.groupby('Date', sort=False).sum().cumsum()
    print(4)
   
    return holdings

def get_port_value(df):
    port_value = get_price_history(df).mul(get_holdings(df)).sum(axis=1)
    return port_value

def get_bench_his(df, ticker):
    # Get benchmark performace
    benchmark_his = get_stock_price(ticker)
    benchmark_his = pd.DataFrame(benchmark_his, index=get_holdings(df).index)
    benchmark_his.fillna(method='ffill', inplace=True)

    # Get buy dollar amount at any given date
    benchmark_his['Buy Cost'] = pd.DataFrame(df.groupby('Date', sort=False).sum()['Cost'])

    # Get amount of VOO able to buy given the dolloar used that day
    benchmark_his['Buy Amount'] = benchmark_his['Buy Cost'] / benchmark_his['Open']

    # Get value of VOO portfolio at any given date
    benchmark_port = benchmark_his.groupby('Date', sort=False).sum().cumsum()
    benchmark_port_value = benchmark_his['Open'].mul(benchmark_port['Buy Amount'])

    return benchmark_port_value
    
def get_line_df(df):
    plot_df = pd.DataFrame()
    port_value = get_port_value(df)
    plot_df['Date'] = port_value.index
    plot_df['PortValue'] = [1] * len(port_value)
    for i in range(len(port_value)):
        plot_df['PortValue'][i] = port_value[i]
    
    return plot_df

def get_pie_df(df):
    price_history = get_price_history(df)
    holdings = get_holdings(df)
    end_date = df.iloc[-1]['Date']
    pie_df = price_history.mul(holdings).T
    pie_df = pie_df[end_date]
    return pie_df

def new_line_fig(df):
    plot_df = get_line_df(df)
    line_fig = px.line(plot_df, x='Date', y='PortValue',
                    labels={'Date': 'Date Since Inception', 'PortValue': 'Portfolio Value'},
                    hover_data={'PortValue': ':.2f'})
    line_fig.add_scatter(x=plot_df['Date'], y=plot_df['PortValue'], name='Mine')
    # Customize the chart
    line_fig.update_xaxes(rangeslider_visible=True)
    line_fig.update_layout(legend=dict(yanchor='top', y=0.99,
                                       xanchor='left', x=0.05),
                           font_color="white", font_family="Courier New",
                           hovermode='x unified', plot_bgcolor='rgba(0,0,0,0)'
                           , paper_bgcolor='rgb(0,0,0)')
    return line_fig

def new_pie_fig(df):
    price_history = get_price_history(df)
    holdings = get_holdings(df)
    end_date = df.iloc[-1]['Date']
    pie_df = price_history.mul(holdings).T
    pie_df = pie_df[end_date]

    pie_fig = go.Figure(data=[go.Pie(labels=pie_df.index, values=pie_df.values, \
                                    insidetextorientation='radial', hole=.3,
                                    texttemplate="%{label}: %{value:$,.03s} <br>(%{percent})")])

    pie_fig.update_traces(hoverinfo='none', textposition='inside', textfont_size=12)
    pie_fig.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', font_family="Courier New")

    return pie_fig

def get_final_values(df):
    total_cost = df.groupby('Date', sort=False).sum()['Cost'].sum()
    final_value = get_port_value(df)[-1]
    net_pl = total_cost - final_value

    total_cost = f'{total_cost:.2f}'
    final_value = f'{final_value:.2f}'
    net_pl = f'{net_pl:.2f}'

    final_values = (total_cost, final_value, net_pl)
    return final_values

def get_pos_list(pie_df):
    position_df = pd.DataFrame(pie_df)
    position_df.columns = ['amount']
    position_df['name'] = pie_df.index
    position_df['percent'] = (pie_df / pie_df.sum()) * 100
    position_df = position_df.sort_values(by='percent', ascending=False)

    pos_list = []
    for i in range(len(position_df)):
        new_amount = position_df['amount'][i]
        new_percent = position_df['percent'][i]
        new_tuple = {'ticker':  position_df['name'][i],
                    'amount':  f'$ {new_amount:.2f}',
                    'percent': f'{new_percent:.2f} %'}
        pos_list.append(new_tuple)
    return pos_list
