#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// WiFi credentials
const char* ssid = "Airel_9842878776";
const char* password = "air88581";

// MQTT broker details
const char* mqtt_server = "broker.emqx.io";  // Or your own broker
const int mqtt_port = 1883;
const char* mqtt_topic = "quantanics/sensor";      // Custom topic

#define TRIG_PIN D6
#define ECHO_PIN D5
#define BUZZER_PIN D7
#define MQ2_PIN A0

WiFiClient espClient;
PubSubClient client(espClient);

long duration;
float distance;
int smokeValue;

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP8266Client")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Measure distance
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  duration = pulseIn(ECHO_PIN, HIGH);
  distance = duration * 0.0343 / 2;

  // Read smoke level
  smokeValue = analogRead(MQ2_PIN);

  // Print values
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.print(" cm | Smoke: ");
  Serial.println(smokeValue);

  // Prepare JSON message
  String payload = "{";
  payload += "\"distance\":" + String(distance, 2) + ",";
  payload += "\"smoke\":" + String(smokeValue);
  payload += "}";

  // Publish to MQTT
  client.publish(mqtt_topic, payload.c_str());

  // Check conditions for buzzer
  if (distance > 20 || smokeValue > 500) {
    digitalWrite(BUZZER_PIN, HIGH);
  } else {
    digitalWrite(BUZZER_PIN, LOW);
  }

  delay(1000);
}
