#include "EspMQTTClient.h"
#include <SPI.h>
#include <MFRC522.h>

// --- MQTT SETUP START ---
EspMQTTClient client(
  "VELVET_1431",
  "IoTStuff",
  "test.mosquitto.org",  // MQTT Broker server ip
  "ESP8266-RFID" // Client name that uniquely identify your device       
);

String pub_topic = "SMARTHOME/rfid";
String sub_topic = "SMARTHOME/buzzer";
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

void checkRFID() {
  if ( ! rfid.PICC_IsNewCardPresent())
    return;
  if (rfid.PICC_ReadCardSerial()) {
    for (byte i = 0; i < 4; i++) {
      tag += rfid.uid.uidByte[i];
    }
    client.publish(pub_topic, tag);
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


void setup()
{
  Serial.begin(115200);

  // EspMQTTClient : 
  client.enableDebuggingMessages(); // Enable debugging messages sent to serial output
  client.enableHTTPWebUpdater(); // Enable the web updater. User and password default to values of MQTTUsername and MQTTPassword. These can be overrited with enableHTTPWebUpdater("user", "password").
  client.enableLastWillMessage("SMARTHOME/rfid/lastwill", "RFID Reader: OFFLINE");  // You can activate the retain flag by setting the third parameter to true
  client.enableMQTTPersistence();

  // RFID
  SPI.begin(); // Init SPI bus
  rfid.PCD_Init(); // Init MFRC522

  // Buzzer
  pinMode(buzzer, OUTPUT);
}

// This function is called once everything is connected (Wifi and MQTT)
// WARNING : YOU MUST IMPLEMENT IT IF YOU USE EspMQTTClient
void onConnectionEstablished()
{
  // Subscribe to "SMARTHOME/buzzer"
  client.subscribe(sub_topic, [](const String & payload) {
      beep();
  });
  // Publish a message to "SMARTHOME/rfid"
  client.publish(pub_topic, "RFID Reader: ONLINE"); // You can activate the retain flag by setting the third parameter to true
}

void loop()
{
  client.loop();
  if (client.isConnected()) {
    checkRFID();
  }
}
