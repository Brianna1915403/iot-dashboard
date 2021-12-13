import random, time, sensor, photoresistor
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
                        dht11_res = client.publish(self.pub_topics['dht11'], user[0][3])
                        light_res = client.publish(self.pub_topics['light'], user[0][4])
                        if dht11_res[0] == 0:
                            print(f"Send `{user[0][3]}` to topic `{self.pub_topics['dht11']}`")
                        else:
                            print(f"Failed to send message to topic {self.pub_topics['dht11']}")  
                        if light_res[0] == 0:
                            print(f"Send `{user[0][4]}` to topic `{self.pub_topics['light']}`")
                        else:
                            print(f"Failed to send message to topic {self.pub_topics['light']}") 
                    else:
                        db.insert_into_access(msg.payload.decode(), "Unknown", "Denied")
                        client.publish(self.pub_topics['rfid'], "DENIED")  
                db.close()
            if (msg.topic == "SMARTHOME/light" and msg.payload.decode() != "Light: ONLINE"):
                photoresistor.openlight() 
            if(msg.topic == "SMARTHOME/DHT11" and msg.payload.decode() != "DHT11 Reader: ONLINE"):
                db.open()
                answer = str(msg.payload.decode()).split(",")
                #if the temperature passes the threshold, it will send message with ASK
                if(answer[0] == "ASK"):
                    db.insert_into_dht11(answer[1], answer[2])
                    sensor.sendEmail()
                else:
                    #Otherwise, insert data in database
                    db.insert_into_dht11(answer[0], answer[1])
                db.close()


    def subscribe(self, client: mqtt_client): 
        for sub_topic in self.sub_topics.values():
            client.subscribe(sub_topic)

    def run(self):
        client = mqtt_client.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        client.connect(broker, port)

        self.subscribe(client)
        client.loop_forever()
