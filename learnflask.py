import json
import os
import plotly
import sys
from flask import Flask, render_template, request
from analyze_csv import *
from generate_line_chart import get_line_df, new_line_fig_2, new_pie_fig

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './static/user_csv/'
fpath = '../project_ana/static/user_csv/userupload.csv'
line_fig = new_line_fig_2(get_line_df(fpath))
pie_fig = new_pie_fig(fpath)

@app.route("/")
def homepage():
    lineJSON = json.dumps(line_fig, cls=plotly.utils.PlotlyJSONEncoder)

    pieJSON = json.dumps(pie_fig, cls=plotly.utils.PlotlyJSONEncoder)

    contribution = total_cost
    value = final_value
    net = net_pl

    return render_template('home.html', lineJSON=lineJSON, pieJSON=pieJSON,
                           cost=contribution, value=value, net=net)

@app.route("/position")
def position():
    pieJSON = json.dumps(pie_fig, cls=plotly.utils.PlotlyJSONEncoder)
    poslist = pos_list
    return render_template('position.html', title='position', pieJSON=pieJSON,
                           posdic=poslist)



line_fig = new_line_fig_2(get_line_df(fpath))

@app.route("/compare", methods=['POST', 'GET'])
def compare():
    global line_fig
    user_input = request.form
    user_tickers = []

    for i in user_input.items():
        user_tickers.append(i[1].upper())

    try:
        if bool(user_tickers[0]) == False:
            line_fig = new_line_fig_2(get_line_df(fpath))
        else:
            for ticker in user_tickers:
                plot_df[ticker] = [1] * len(port_value)
                ticker_series = get_bench_his(ticker)
                for i in range(len(port_value)):
                    plot_df[ticker][i] = ticker_series[i]
                line_fig.add_scatter(x=plot_df['Date'], y=plot_df[ticker], name=ticker)
    except:
        pass



    lineJSON = json.dumps(line_fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('compare.html', title='compare', lineJSON=lineJSON)


@app.route("/import", methods=['GET', 'POST'])
def importfile():
    global lineJSON
    global pieJSON
    
    if request.method == "POST":
        if request.files:
            usercsv = request.files['file']
            usercsv.save(os.path.join(app.config['UPLOAD_FOLDER'], 'userupload.csv'))

           
    
    lineJSON = json.dumps(line_fig, cls=plotly.utils.PlotlyJSONEncoder)
    pieJSON = json.dumps(pie_fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('import.html', title='import')

if __name__ == '__main__':
    app.run(debug=True)
