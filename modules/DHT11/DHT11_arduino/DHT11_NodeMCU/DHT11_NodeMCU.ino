#include "DHT.h"
#include "EspMQTTClient.h"

#define DHTPIN 2
#define DHTTYPE DHT11 
// --- MQTT SETUP START ---
EspMQTTClient client(
  "VELVET_1431",// "SWIphone", //  "Merry Xmas",
  "IoTStuff", // "tgex2qw869crv",//  "09475325323",
  "test.mosquitto.org", // MQTT Broker server ip
  "ESP8266-DHT11" // Client name that uniquely identify your device       
);

String pub_topic = "SMARTHOME/DHT11";
String sub_topic = "SMARTHOME/DHT11-Threshold";

DHT dht(DHTPIN, DHTTYPE);
float threshold = 30;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  // EspMQTTClient : 
  client.enableDebuggingMessages(); // Enable debugging messages sent to serial output
  client.enableHTTPWebUpdater(); // Enable the web updater. User and password default to values of MQTTUsername and MQTTPassword. These can be overrited with enableHTTPWebUpdater("user", "password").
  client.enableLastWillMessage("SMARTHOME/DHT11", "DHT11 Reader: OFFLINE");  // You can activate the retain flag by setting the third parameter to true
  client.enableMQTTPersistence();
  dht.begin();
}

void onConnectionEstablished()
{
  // Subscribe to "SMARTHOME/dht11-threshold"
  client.subscribe(sub_topic, [](const String & payload) {
    if(!payload.isEmpty()){
      threshold = payload.toFloat();
    }
  });
  // Publish a message to "SMARTHOME/dht11"
  client.publish(pub_topic, "DHT11 Reader: ONLINE"); // You can activate the retain flag by setting the third parameter to true
}

void checkDHT11() {
  // Reading temperature or humidity takes about 250 milliseconds!
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  float h = dht.readHumidity();
  // Read temperature as Celsius (the default)
  float t = dht.readTemperature();

  if(t >= threshold){
    client.publish(pub_topic, "ASK," + String(t) + "," + String(h));
  }
  else{
    client.publish(pub_topic, String(t) + "," + String(h));
  }
}

void loop(){
  // Wait a few seconds between measurements.
  client.loop();
  if (client.isConnected()) {
    delay(5000);
    checkDHT11();
  }
}
  
