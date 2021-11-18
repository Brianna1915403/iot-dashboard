#include "EspMQTTClient.h"


// --- MQTT SETUP START ---
EspMQTTClient client(
  "SWIphone",
  "tgex2qw869crv",
  "test.mosquitto.org",  // MQTT Broker server ip
  "ESP8266"         // Client name that uniquely identify your device
);
String pub_topic = "SMARTHOME/light";
String sub_topic = "SMARTHOME/light-threshold";

bool isON = false;
bool threshold = 500;

// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(115200);
  pinMode(A0, INPUT);

  // EspMQTTClient : 
  client.enableDebuggingMessages(); // Enable debugging messages sent to serial output
  client.enableHTTPWebUpdater(); // Enable the web updater. User and password default to values of MQTTUsername and MQTTPassword. These can be overrited with enableHTTPWebUpdater("user", "password").
  client.enableLastWillMessage("SMARTHOME/light/lastwill", "Light: OFFLINE");  // You can activate the retain flag by setting the third parameter to true
  client.enableMQTTPersistence();
}

// This function is called once everything is connected (Wifi and MQTT)
// WARNING : YOU MUST IMPLEMENT IT IF YOU USE EspMQTTClient
void onConnectionEstablished()
{
  client.subscribe(sub_topic, [](const String & payload) {
      threshold = payload.toInt();
  });
  // Publish a message to "SMARTHOME/rfid"
  client.publish(pub_topic, "Lights: ONLINE"); // You can activate the retain flag by setting the third parameter to true
}

void checkLight(){
  int sensorValue = analogRead(A0);
  bool current_state = sensorValue < threshold; // If it lower then it will turn on
  if (current_state != isON) {
    isON = !isON;
    client.publish(pub_topic, isON ? "ON" : "OFF");
  }
  // print out the value you read:
  Serial.println(sensorValue);
}

// the loop routine runs over and over again forever:
void loop() {
  client.loop();
  checkLight();
}
