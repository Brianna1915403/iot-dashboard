# Run w/ python app.py
# Visit http://127.0.0.1:8050

# Internal Imports
from os import terminal_size

from dash.development.base_component import Component
from database import database
from mqtt import mqtt as MQTT
import photoresistor

# External Imports
import pandas as pd
import plotly.express as px
import dash_daq as daq
import dash
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output, State
import multiprocessing
from collections import OrderedDict
import os
import re

bl_input_value = -100
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

db = database("_data.db")

def get_temperature():
    db.open()
    rows = db.select("dht11", "DESC")
    db.close()
    return daq.Gauge(
        showCurrentValue = True,
        units = 'C',
        value = rows[0][1],
        label = 'Temperature',
        max = 40,
        min = -20
    )

def get_humidity():
    db.open()
    rows = db.select("dht11", "DESC")
    db.close()
    return daq.Gauge(
        showCurrentValue = True,
        units = '%',
        value = rows[0][2],
        label = 'Humidity',
        max = 100,
        min = 0
    )

def get_light(isOn = False):
    return daq.PowerButton(
        id = 'light-btn',
        on = isOn,
        label = 'Light',
        labelPosition = 'bottom'
    )

def get_mode():
    return daq.PowerButton(
        id = 'motor-btn',
        on = True,
        label = 'Mode',
        labelPosition = 'bottom'
    )

def get_users():
    db.open()
    rows = db.select("user")
    db.close()
    users = []
    for row in rows:
        users.append({'label': row[1], 'value': row[0]})
    return dcc.Dropdown(
        id='user-dropdown',
        options=users,
        value=None
    )

def get_access_logs():
    dates = []
    rfids = []
    users = []
    access_status = []

    db.open()
    rows = db.select('access')
    db.close()

    for row in rows:
        rfids.append(row[1])
        users.append(row[2])
        access_status.append(row[3])
        dates.append(row[4])

    data = OrderedDict(
        [
            ("Date", dates),
            ("RFID", rfids),
            ("User", users),
            ("Access", access_status)
        ]
    )

    df = pd.DataFrame(OrderedDict([(name, col_data) for (name, col_data) in data.items()]))
    return dash_table.DataTable(
        data = df.to_dict('records'),
        columns = [{'id': c, 'name': c} for c in df.columns],
        page_size = 10,
        style_cell_conditional = [
            {'if': {'column_id': 'Date'}, 'width': '200px'},
        ]
    )

def get_bluetooth_devices(input_value):
    f = open('output.txt', 'r')
    lines = f.readlines()

    bl_devices = {}
    for line in lines:
        if "transmitterId:" in line:
            transmitter = re.findall(r"'(.*?)'", line)
            trans = transmitter[0]
        if "rssi:" in line:
            rssiNum = [int(s) for s in re.findall(r'-?\d+', line)]
            bl_devices[trans] = rssiNum[0]

    addresses = []
    rssis = []
    key_list = list(bl_devices.keys())
    for key in key_list:
        if (input_value < bl_devices[key]):
            addresses.append(key)
            rssis.append(bl_devices[key])  

    data = OrderedDict(
        [
            ("Address", addresses),
            ("RSSI", rssis),
        ]
    )

    df = pd.DataFrame(OrderedDict([(name, col_data) for (name, col_data) in data.items()]))
    return html.Div(className = "bl", children = [html.Label(children = f"Bluetooth Devices: {len(addresses)}"),
        dash_table.DataTable(
        data = df.to_dict('records'),
        columns = [{'id': c, 'name': c} for c in df.columns],
        page_size = 10,
        style_cell_conditional = [
            {'if': {'column_id': 'Date'}, 'width': '200px'},
        ]
    )])

# def number_bluetooth_devices():  
#     nearby_devices = bluetooth.discover_devices(lookup_names=True, lookup_class=True)
#     return "Found {} devices".format(len(nearby_devices))

# def get_photolights():
#     db.open()
#     rows = db.select("user", "DESC")
#     light_rows = db.select("photoresistor")
#     db.close()
#     threshold_light = rows[0][4]
#     print(threshold_light)
#     curlight = light_rows[0][1]
#     print(curlight)
#     if curlight < threshold_light:
#         photoresistor.openlight()
#         print ("lit")
#     else:
#         photoresistor.closelight()
#         print ("not lit")

app.layout = html.Div(
    className = "dashboard-container",
    children = [
        html.H1(children = 'SMART Home - Dashboard', id = "title"),
        dcc.Tabs([
            dcc.Tab(
                label = "Dashboard",
                className = "dashboard-tab",            
                children = [
                    html.Div(className = "dashboard", children = [
                        html.Aside(className = "left-sidebar card", children = [
                            html.Div(className = "temp-gauge", id = "temperature-gauge", children = get_temperature()),
                            html.Div(className = "hum-gauge", id = "humidity-gauge", children = get_humidity()),
                        ]),
                        html.Div(className = "center-graphs", children = [
                            html.P(id = 'formatting-text', children = "Lorem ipsum dolor sit, amet consectetur adipisicing elit. Aut voluptatum, voluptate reprehenderit amet dolorum, hic dolore praesentium temporibus sequi quisquam soluta magnam dolorem iure ipsum laboriosam iusto optio doloremque asperiores eum officia ratione molestiae aspernatur beatae fugit. Fugiat adipisci nesciunt non corporis dicta, eligendi nulla, iste incidunt enim earum necessitatibus."),
                            dcc.Tabs(className = "graph-tables", children = [
                                dcc.Tab(id = "access-logs", label = "Access Logs", children = [
                                    html.Br(),
                                    get_access_logs()
                                ]),
                                dcc.Tab(id = "bluetooth-table", label = "Bluetooth", children = [
                                    html.Br(),
                                    html.Div(["Threshold: ", dcc.Input(id="bl-threshold", value="-100", type="number", debounce=True)]),
                                    html.Div(id = 'ble', children = [
                                        get_bluetooth_devices(bl_input_value)
                                    ])                                    
                                ])
                            ]),
                        ]),
                        html.Aside(className = "right-sidebar", children = [
                            html.Div(className = "btns", children = [
                                html.Div(className = "btn", id = "light-btn-card", children = get_light()),
                                html.Br(),
                                html.Div(className = "btn", id = "mode-btn-card", children = get_mode()),
                            ])
                        ]),
                    ])                                      
                ]
            ),
            dcc.Tab(
                label = "Account",
                className = "account",            
                children = [
                    html.Div(id = '', className = "account-container", children = [
                        html.Br(),
                        html.Label('Users: '),
                        get_users(),                        
                        html.Br(),
                        html.Div(className = 'card', children = [
                            html.Div(children = [
                                html.Label('Temperature Threshold:'),
                                dcc.Input(id='temperature-threshold', className = 'threashold', min = '-20', max = '40', placeholder="-20 - 40"),
                            ]),
                            html.Div(children = [
                                html.Label('Light Threshold:'),
                                dcc.Input(id="light-threshold", className = 'threashold', type='number', min = 0, max = 10000, step = 1, placeholder="0 - 10000")
                            ]),
                        ]),
                        html.Br(),
                        html.Button(id='update-btn', children='Update'),
                        html.Div(id='empty-div', children=[])
                    ])                    
                ]
            )
        ]),
        dcc.Interval(
            id='10-second-interval',
            interval=10000, 
            n_intervals=0
        )
    ]
)

# --- Updates Start ---

@app.callback(Output('humidity-gauge', 'children'), [Input('10-second-interval', 'n_intervals')])
def update_humidity(val):
    return get_humidity()

@app.callback(Output('temperature-gauge', 'children'), [Input('10-second-interval', 'n_intervals')])
def update_temperature(val):
    return get_temperature()

@app.callback(Output('light-btn-card', 'children'), [Input('light-btn', 'on')])
def update_light(on):
    photoresistor.solo_light(on)
    return get_light(on)

@app.callback(Output('empty-div', 'children'), [Input('update-btn', 'n_clicks')], [State('user-dropdown', 'value'), State('temperature-threshold', 'value'), State('light-threshold', 'value')])
def update_user(clicks, user, temp, light):
    if (clicks):
        db.open()
        db.update_user(user, temp, light)
        db.close()
        
@app.callback(Output('ble', 'children'), [Input('bl-threshold', 'value')])
def update_ble(value):
    return get_bluetooth_devices(int(value))

@app.callback(Output('temperature-threshold', 'value'), [Input('user-dropdown', 'value')])
def update_temp(value):
    if (not value):
        return ""
    else:
        db.open()
        rows = db.select("user")
        db.close()
        return rows[value - 1][3]

@app.callback(Output('light-threshold', 'value'), [Input('user-dropdown', 'value')])
def update_temp(value):
    if (not value):
        return ""
    else:
        db.open()
        rows = db.select("user")
        db.close()
        return rows[value - 1][4]
# --- Updates End ---

def run_server_debug():
    app.run_server(debug = True)

def run_mqtt():
    sub_topics = {'dht11' : "SMARTHOME/DHT11", 'rfid' : "SMARTHOME/rfid", 'light' : "SMARTHOME/light"}
    pub_topics = {'dht11' : "SMARTHOME/DHT11_Threshold", 'rfid' : "SMARTHOME/buzzer", 'light' : "SMARTHOME/light-threshold"}
    MQTT(sub_topics, pub_topics).run()

if __name__ == '__main__':  
    jobs = []
    app_thread = multiprocessing.Process(target = run_server_debug)
    mqtt_thread = multiprocessing.Process(target = run_mqtt)
    jobs.append(app_thread)
    jobs.append(mqtt_thread)

    for j in jobs:
        j.start()

    for j in jobs:
        j.join()
