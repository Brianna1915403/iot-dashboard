# Run w/ python app.py
# Visit http://127.0.0.1:8050

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_daq as daq
import pandas as pd
import plotly.express as px
from database import database

app = dash.Dash(__name__)

db = database("_data.db")

def get_temperature():
    db.open()
    rows = db.select("dht11", "DESC")
    db.close()
    return daq.Thermometer(
        showCurrentValue = True,
        units = '°C',
        value = (rows[0][1] if rows else 'N/A'),
        label = 'Temperature',
        max = 40,
        min = -20
    )

def get_humidity():
    db.open()
    rows = db.select("dht11", "DESC")
    db.close()
    return daq.Thermometer(
        showCurrentValue = True,
        units = '%',
        value = (rows[0][2] if rows else 'N/A'),
        label = 'Humidity',
        max = 100,
        min = 0
    )

def get_light():
    db.open()
    rows = db.select("light", "DESC")
    db.close()
    return daq.PowerButton(
        id = 'light-btn',
        on = (rows[0][1] if rows else False),
        label = 'Light',
        labelPosition = 'bottom'
    )

def get_motor():
    db.open()
    rows = db.select("motor", "DESC")
    db.close()
    return daq.PowerButton(
        id = 'motor-btn',
        on = (rows[0][1] if rows else False),
        label = 'Motor',
        labelPosition = 'bottom'
    )

app.layout = html.Div(
    className = 'container',
    children = [
        html.H1(children='IoT Dashboard'),
        html.Div(
            className = 'dht11',
            children = [
                html.Div(
                    className = 'card',
                    id = 'temperature',
                    children = get_temperature()
                ),
                html.Div(
                    className = 'card',
                    id = 'humidity',
                    children = get_humidity()
                )
            ]
        ),
        html.Div(
            className = 'toggles',
            children = [
                html.Div(
                    className = 'card',
                    id = 'led',
                    children = get_light()
                ),
                html.Div(
                    className = 'card',
                    id = 'motor',
                    children = get_motor()
                )
            ]
        ),
        dcc.Interval(
            id = '1-sec-interval',
            interval = 1000,
            n_intervals = 0
        )
    ]
)

# --- Updates Start ---

@app.callback(Output('humidity', 'children'), [Input('1-sec-interval', 'n_intervals')])
def update_humidity():
    return get_humidity()

@app.callback(Output('temperature', 'children'), [Input('1-sec-interval', 'n_intervals')])
def update_temperature():
    return get_temperature()

@app.callback(Output('light', 'children'), [Input('light-btn', 'n_clicks')])
def update_light(n_clicks):
    print(f"Button has been clicked {n_clicks} times")
    return get_light()

@app.callback(Output('motor', 'children'), [Input('motor-btn', 'n_clicks')])
def update_light(n_clicks):
    print(f"Button has been clicked {n_clicks} times")
    return get_motor()

# --- Updates End ---

if __name__ == '__main__':
    app.run_server(debug = True);