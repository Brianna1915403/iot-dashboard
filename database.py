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

    def select(self, table, order = "ASC", order_by = "id", what = "*", where = "1"):
        query = f"SELECT {what} FROM {table} WHERE {where} ORDER BY {order_by} {order} "
        cursor = self.connection.execute(query)
        rows = list()
        for row in cursor:
            rows.append(row)
        return rows

    def insert_into_dht11(self, temperature, humidity):
        query = f"INSERT INTO dht11 (temperature, humidity, date) VALUES(?, ?, ?)"
        vals = (temperature, humidity, datetime.datetime.now())
        self.connection.execute(query, vals)
        self.connection.commit()

    def insert_into_led(self, isOn):
        query = f"INSERT INTO led (is_on, date) VALUES(?, ?)"
        vals = (isOn, datetime.datetime.now())
        self.connection.execute(query, vals)
        self.connection.commit()

    def insert_into_motor(self, isOn):
        query = f"INSERT INTO motor (is_on, date) VALUES(?, ?)"
        vals = (isOn, datetime.datetime.now())
        self.connection.execute(query, vals)
        self.connection.commit()

    def insert_into_access(self, key, user, access_status):
        query = f"INSERT INTO access (key, user, access_status, date) VALUES(?, ?, ?, ?)"
        vals = (key, user, access_status, datetime.datetime.now())
        self.connection.execute(query, vals)
        self.connection.commit()