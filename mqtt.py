import random, time
from paho.mqtt import client as mqtt_client
from database import database

broker = "test.mosquitto.org"
port = 1883
db = database("_data.db")

class mqtt:
    def __init__(self, sub_topic, pub_topic) -> None:
        self.sub_topic = sub_topic
        self.pub_topic = pub_topic
        self.client_id = f'client-mqtt-{random.randint(0, 10000)}'
    
    def connect_mqtt(self) -> mqtt_client:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(self.client_id)
        client.on_connect = on_connect
        client.connect(broker, port)
        return client

    def subscribe(self, client: mqtt_client):
        def on_message(client, userdata, msg):
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
            if (msg.topic == "SMARTHOME/rfid" and msg.payload.decode() != "RFID Reader: ONLINE"):
                db.open()
                rfid_key = db.select("rfid_key", where = f"key = '{msg.payload.decode()}'")
                if (not rfid_key):  
                    db.insert_into_access(msg.payload.decode(), "Unknown", "Denied")
                    result = client.publish(self.pub_topic, "DENIED")
                    status = result[0]
                    if status == 0:
                        print(f"Send `DENIED` to topic `{self.pub_topic}`")
                    else:
                        print(f"Failed to send message to topic {self.pub_topic}")              
                else:
                    print(rfid_key)
                    user = db.select("user", where = f"id = '{rfid_key[0][2]}'") 
                    if (user != None):
                        db.insert_into_access(msg.payload.decode(), user[0][1], "Granted")
                    else:
                        db.insert_into_access(msg.payload.decode(), "Unknown", "Denied")
                        client.publish(self.pub_topic, "DENIED")  
                db.close()
            elif (msg.topic == "SMARTHOME/light" and msg.payload.decode() != "Light: ONLINE"):
                print(msg.payload.decode()) 
                pass
            

        client.subscribe(self.sub_topic)
        client.on_message = on_message

    def publish(self, client):
        msg_count = 0
        while True:
            time.sleep(1)
            msg = f"messages: {msg_count}"
            result = client.publish(self.pub_topic, msg)
            # result: [0, 1]
            status = result[0]
            if status == 0:
                print(f"Send `{msg}` to topic `{self.pub_topic}`")
            else:
                print(f"Failed to send message to topic {self.pub_topic}")
            msg_count += 1

    def run(self):
        client_sub = self.connect_mqtt()
        self.subscribe(client_sub)
        client_sub.loop_forever()