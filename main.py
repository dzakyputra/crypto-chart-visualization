from flask import Flask, jsonify, request, send_file
from binance.client import Client
import plotly.graph_objects as go
import datetime
import os

BINANCE_PUBLIC_KEY = "YYUDVC9T6o9c0hF4UXZFC3go2NtLyUikJS77Fr7W1Rw1fIz5Y28i1xXfIhAMKMf6"

app = Flask(__name__)
binance_client = Client(BINANCE_PUBLIC_KEY)

@app.route("/api/v1/get_chart", methods=["GET"])
def info():
    
    # Parsing the request body
    content = request.json

    pair = content.get("pair")
    if pair is None:
        pair = "BTCUSDT"

    interval = content.get("interval")
    if interval is None:
        interval = "15m"

    lookback = content.get("lookback")
    if lookback is None:
        lookback = "1 day ago UTC"

    ## Get candlestick data from Binance
    try:
        klines = binance_client.get_historical_klines(pair, interval, lookback)
    except:
        return "error", 500

    time = []
    open = []
    high = []
    low = []
    close = []

    for data in klines:
        dt_object = datetime.datetime.fromtimestamp(data[6]/1000.0)
        time.append(dt_object)
        open.append(data[1])
        high.append(data[2])
        low.append(data[3])
        close.append(data[4])

    # Visualizing the data using plotly
    fig = go.Figure()
    
    trace_candlestick = go.Candlestick(x=time, open=open, high=high, low=low, close=close)
    
    fig.add_trace(trace_candlestick)
    fig.update_layout(title_text=pair, title_x=0.5, xaxis_rangeslider_visible=False, showlegend=False)
        
    # Save the visualization and send it to the client
    image_path = str(int(datetime.datetime.utcnow().timestamp())) + '-' + pair + '.png'
    fig.write_image(image_path)

    return send_file(image_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
