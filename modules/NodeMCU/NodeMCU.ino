#include "EspMQTTClient.h"
#include <SPI.h>
#include <MFRC522.h>

// --- MQTT SETUP START ---
EspMQTTClient client(
  "SWIphone",
  "tgex2qw869crv",
  "172.20.10.9",  // MQTT Broker server ip
  "ESP8266"         // Client name that uniquely identify your device
);

String pub_light_topic = "SMARTHOME/light";
String sub_light_topic = "SMARTHOME/light-threshold";
String pub_rfid_topic = "SMARTHOME/rfid";
String sub_rifd_topic = "SMARTHOME/buzzer";
// --- MQTT SETUP END ---

// --- RFID SETUP START ---
constexpr uint8_t RST_PIN = D3;
constexpr uint8_t SS_PIN = D4; 

MFRC522 rfid(SS_PIN, RST_PIN);
MFRC522::MIFARE_Key key;

String tag;
// --- RFID SETUP END ---

// --- BUZZER START ---
const unsigned char buzzer = 5;
// --- BUZZER END ---

// --- LIGHT START ---
bool isON = false;
int threshold = 500;
// --- LIGHT END ---

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(A0, INPUT);

  // EspMQTTClient : 
  client.enableDebuggingMessages(); // Enable debugging messages sent to serial output
  client.enableHTTPWebUpdater(); // Enable the web updater. User and password default to values of MQTTUsername and MQTTPassword. These can be overrited with enableHTTPWebUpdater("user", "password").
  client.enableLastWillMessage("SMARTHOME/nodemcu/lastwill", "Light: OFFLINE");  // You can activate the retain flag by setting the third parameter to true
  client.enableMQTTPersistence();

  // RFID :
  SPI.begin(); // Init SPI bus
  rfid.PCD_Init(); // Init MFRC522

  // Buzzer :
  pinMode(buzzer, OUTPUT);  
}

void onConnectionEstablished()
{
  client.subscribe(sub_light_topic, [](const String & payload) {
      threshold = payload.toInt();
  });  
  client.publish(pub_light_topic, "Lights: ONLINE");
//
//  client.subscribe(sub_rifd_topic, [](const String & payload) {
//      beep();
//  });  
//  client.publish(pub_rfid_topic, "RFID Reader: ONLINE");
}

void checkRFID() {
  if ( ! rfid.PICC_IsNewCardPresent())
    return;
  if (rfid.PICC_ReadCardSerial()) {
    for (byte i = 0; i < 4; i++) {
      tag += rfid.uid.uidByte[i];
    }
    client.publish(pub_rfid_topic, tag);
    tag = "";
    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();    
  }
}

void beep() {
  for (int i = 0; i < 3; ++i) {
    digitalWrite(buzzer, HIGH);
    delay(1000);
    digitalWrite(buzzer, LOW);
  }
}

void checkLight(){
  int sensorValue = analogRead(A0);
  bool current_state = sensorValue < threshold; // If it lower then it will turn on
  if (current_state == isON) {    
    return;
  } else {
    isON = current_state;
//    client.publish(pub_light_topic, isON ? "ON" : "OFF");
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  client.loop();
//  checkRFID();
  checkLight();
}
