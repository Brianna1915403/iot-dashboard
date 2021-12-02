import random, time
import paho.mqtt.client as mqtt_client
from database import database

broker = "test.mosquitto.org"
port = 1883
db = database("_data.db")

class mqtt:
    def __init__(self, sub_topics, pub_topics) -> None:
        self.sub_topics = sub_topics
        self.pub_topics = pub_topics
    
    def on_connect(self, client, userdata, flags, rc):
        print(f"Connection code: {rc}\n")

    def on_message(self, client, userdata, msg):
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
            if (msg.topic == "SMARTHOME/rfid" and msg.payload.decode() != "RFID Reader: ONLINE"):
                db.open()
                rfid_key = db.select("rfid_key", where = f"key = '{msg.payload.decode()}'")
                if (not rfid_key):  
                    db.insert_into_access(msg.payload.decode(), "Unknown", "Denied")
                    result = client.publish(self.pub_topics['rfid'], "DENIED")
                    status = result[0]
                    if status == 0:
                        print(f"Send `DENIED` to topic `{self.pub_topics['rfid']}`")
                    else:
                        print(f"Failed to send message to topic {self.pub_topics['rfid']}")              
                else:
                    print(rfid_key)
                    user = db.select("user", where = f"id = '{rfid_key[0][2]}'") 
                    if (user != None):
                        db.insert_into_access(msg.payload.decode(), user[0][1], "Granted")
                    else:
                        db.insert_into_access(msg.payload.decode(), "Unknown", "Denied")
                        client.publish(self.pub_topics['rfid'], "DENIED")  
                db.close()
            elif (msg.topic == "SMARTHOME/light" and msg.payload.decode() != "Light: ONLINE"):
                print(msg.payload.decode()) 
                pass    
            elif(msg.topic == "SMARTHOME/DHT11" and msg.payload.decode() != "DHT11 Reader: ONLINE"):
                if(msg.payload.decode() == "ASK"):
                    # sensor.run()d
                    pass

    def subscribe(self, client: mqtt_client): 
        for sub_topic in self.sub_topics.values():
            client.subscribe(sub_topic)

    def run(self):
        client = mqtt_client.Client(client_id = 'main-client', clean_session = False)
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        client.connect(broker, port)

        self.subscribe(client)
        client.loop_forever()
