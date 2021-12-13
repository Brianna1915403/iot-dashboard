import datetime
import sqlite3 as SQL

class database:

    def __init__(self, file):
        self.connection = None
        self.file = file

    def open(self):
        self.connection = SQL.connect(self.file, detect_types = SQL.PARSE_DECLTYPES | SQL.PARSE_COLNAMES)

    def close(self):
        self.connection.close()

    # Selecting a specific table from the database
    def select(self, table, order = "ASC", order_by = "id", what = "*", where = "1"):
        query = f"SELECT {what} FROM {table} WHERE {where} ORDER BY {order_by} {order} "
        cursor = self.connection.execute(query)
        rows = list()
        for row in cursor:
            rows.append(row)
        return rows

    # Update the user temp and light preference in the database 
    def update_user(self, user, temp, light):
        query = f"UPDATE user SET temperature = ?, light = ? WHERE id = ?"
        vals = (temp, light, user)
        self.connection.execute(query, vals)
        self.connection.commit()

    # Insert the temperature and humidity data taken from the dht11 into the database
    def insert_into_dht11(self, temperature, humidity):
        query = f"INSERT INTO dht11 (temperature, humidity, date) VALUES(?, ?, ?)"
        vals = (temperature, humidity, datetime.datetime.now())
        self.connection.execute(query, vals)
        self.connection.commit()

    # Insert the LED data depending if its on or not into the database
    def insert_into_led(self, isOn):
        query = f"INSERT INTO led (is_on, date) VALUES(?, ?)"
        vals = (isOn, datetime.datetime.now())
        self.connection.execute(query, vals)
        self.connection.commit()

    # Insert the motor data depending if its on or not into the database 
    def insert_into_motor(self, isOn):
        query = f"INSERT INTO motor (is_on, date) VALUES(?, ?)"
        vals = (isOn, datetime.datetime.now())
        self.connection.execute(query, vals)
        self.connection.commit()

    # Insert the access data into the database 
    def insert_into_access(self, key, user, access_status):
        query = f"INSERT INTO access (key, user, access_status, date) VALUES(?, ?, ?, ?)"
        vals = (key, user, access_status, datetime.datetime.now())
        self.connection.execute(query, vals)
        self.connection.commit()