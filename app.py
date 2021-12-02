# Run w/ python app.py
# Visit http://127.0.0.1:8050

# Internal Imports
from os import terminal_size
from database import database
from mqtt import mqtt as MQTT

# External Imports
import pandas as pd
import plotly.express as px
import dash_daq as daq
import dash
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output
import multiprocessing
from collections import OrderedDict

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
        value = -17,
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
        value = 30,
        label = 'Humidity',
        max = 100,
        min = 0
    )

def get_light():
    db.open()
    rows = db.select("led", "DESC")
    db.close()
    return daq.PowerButton(
        id = 'light-btn',
        on = True,
        label = 'Light',
        labelPosition = 'bottom'
    )

def get_fan():
    db.open()
    rows = db.select("motor", "DESC")
    db.close()
    return daq.PowerButton(
        id = 'motor-btn',
        on = False,
        label = 'Motor',
        labelPosition = 'bottom'
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
    nearby_devices = bluetooth.discover_devices(lookup_names=True, lookup_class=True)
    print("Found {} devices".format(len(nearby_devices)))

    threshold = input_value 
    addresses = []
    names = []
    rssis = []

    for addr, name, rssi in nearby_devices:
        if (rssi > threshold): 
            addresses.append(addr)
            names.append(name)
            rssis.append(rssi)      

    data = OrderedDict(
        [
            ("Address", addresses),
            ("Device Name", names),
            ("RSSI", rssis),
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

def number_bluetooth_devices():  
    nearby_devices = bluetooth.discover_devices(lookup_names=True, lookup_class=True)
    return "Found {} devices".format(len(nearby_devices))

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
                            html.P("Lorem ipsum dolor sit, amet consectetur adipisicing elit. Aut voluptatum, voluptate reprehenderit amet dolorum, hic dolore praesentium temporibus sequi quisquam soluta magnam dolorem iure ipsum laboriosam iusto optio doloremque asperiores eum officia ratione molestiae aspernatur beatae fugit. Fugiat adipisci nesciunt non corporis dicta, eligendi nulla, iste incidunt enim earum necessitatibus."),
                            html.Div(className = "graph-tables", children = [
                                html.Div(id = "access-logs", children = [
                                    html.H3("Access Logs"),
                                    get_access_logs()
                                ])
                            ]),
                        ]),
                        html.Aside(className = "right-sidebar", children = [
                            html.Div(className = "btns", children = [
                                html.Div(className = "btn", id = "light-btn-card", children = get_light()),
                                html.Div(className = "btn", id = "fan-btn-card", children = get_fan()),
                            ])
                        ]),
                    ])                                      
                ]
            ),
            dcc.Tab(
                label = "Account",
                className = "account",            
                children = [
                    html.Div(className = "", id = "account-prefs", children = html.P("This is Account Prefs.")),
                    # html.Div(className = "photoresistor-lights", id = "photoresistor", children = get_photolights()),
                    html.Div(["Light Threshold: ", dcc.Input(id="light-threshold", value="500", type="number")]),
                    html.Div(["Temperature Threshold: ", dcc.Input(id="temperature-threshold", value="20", type="number")])
                ]
            ),
            dcc.Tab(
                label = "Bluetooth",
                className = "bluetooth",            
                children = [
                    html.Div(className = "", id = "bluetooth", children = html.P("Bluetooth")),
                    html.Div(["Threshold: ", dcc.Input(id="input-threshold", value="100000", type="number")]),
                    html.Div(className = "center-graphs", children = [
                            html.Div(className = "graph-tables", children = [
                                html.Div(id = "bluetoothlogs", children = [
                                    html.H3(number_bluetooth_devices()),
                                    get_bluetooth_devices(500)
                                ])
                            ]),
                        ]),
                ]
            ),
        ]),
        dcc.Interval(
            id='1-second-interval',
            interval=1000, 
            n_intervals=0
        )
    ]
)

# --- Updates Start ---

# @app.callback(Output('humidity', 'children'), [Input('1-sec-interval', 'n_intervals')])
# def update_humidity():
#     return get_humidity()

# @app.callback(Output('temperature', 'children'), [Input('1-sec-interval', 'n_intervals')])
# def update_temperature():
#     return get_temperature()

# @app.callback(Output('light', 'children'), [Input('light-btn', 'on')])
# def update_light(on):
#     # print(f"Button has been clicked {on} times")
#     return get_light()

# @app.callback(Output('motor', 'children'), [Input('motor-btn', 'n_clicks')])
# def update_motor(n_clicks):
#     print(f"Button has been clicked {n_clicks} times")
#     return get_motor()

# --- Updates End ---

def run_server_debug():
    app.run_server(debug = True)

def run_mqtt():
    MQTT("SMARTHOME/rfid", "SMARTHOME/buzzer").run()

def run_light_mqtt():
    MQTT("SMARTHOME/light", "SMARTHOME/threshold").run()
def run_sensor():
    # arduinoSensor.run()
    pass

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
