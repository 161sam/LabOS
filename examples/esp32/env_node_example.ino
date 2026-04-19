#include <WiFi.h>
#include <PubSubClient.h>

const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* MQTT_HOST = "192.168.1.50";
const int MQTT_PORT = 1883;
const char* NODE_ID = "esp32-a1";
const int REACTOR_ID = 1;

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
unsigned long lastPublishAt = 0;

String controlTopic() {
  return "labos/reactor/" + String(REACTOR_ID) + "/control/#";
}

String statusTopic() {
  return "labos/node/" + String(NODE_ID) + "/status";
}

String heartbeatTopic() {
  return "labos/node/" + String(NODE_ID) + "/heartbeat";
}

String telemetryTopic(const char* sensorType) {
  return "labos/reactor/" + String(REACTOR_ID) + "/telemetry/" + String(sensorType);
}

String ackTopic() {
  return "labos/reactor/" + String(REACTOR_ID) + "/ack";
}

String extractField(const String& payload, const String& key) {
  int keyIndex = payload.indexOf("\"" + key + "\"");
  if (keyIndex < 0) {
    return String();
  }
  int colonIndex = payload.indexOf(':', keyIndex);
  if (colonIndex < 0) {
    return String();
  }
  int start = colonIndex + 1;
  while (start < (int)payload.length() && (payload[start] == ' ' || payload[start] == '\"')) {
    start++;
  }
  int end = start;
  while (end < (int)payload.length() && payload[end] != '\"' && payload[end] != ',' && payload[end] != '}') {
    end++;
  }
  return payload.substring(start, end);
}

void publishAck(const String& commandId, const String& commandUid, bool ok, const String& errorMessage) {
  String payload = "{\"status\":\"";
  payload += ok ? "ok" : "error";
  payload += "\"";
  if (commandId.length() > 0) {
    payload += ",\"command_id\":" + commandId;
  }
  if (commandUid.length() > 0) {
    payload += ",\"command_uid\":\"" + commandUid + "\"";
  }
  if (!ok && errorMessage.length() > 0) {
    payload += ",\"error\":\"" + errorMessage + "\"";
  }
  payload += "}";
  mqttClient.publish(ackTopic().c_str(), payload.c_str());
}

void publishStatus(const char* statusValue) {
  String payload =
    "{\"name\":\"ESP32 Env Node A1\",\"reactor_id\":" + String(REACTOR_ID) +
    ",\"node_type\":\"env_control\",\"status\":\"" + String(statusValue) +
    "\",\"firmware_version\":\"example-v1\"}";
  mqttClient.publish(statusTopic().c_str(), payload.c_str());
}

void publishHeartbeat() {
  String payload =
    "{\"reactor_id\":" + String(REACTOR_ID) +
    ",\"node_type\":\"env_control\",\"firmware_version\":\"example-v1\"}";
  mqttClient.publish(heartbeatTopic().c_str(), payload.c_str());
}

void publishTelemetry() {
  float waterTemp = 28.5 + (millis() % 1000) / 1000.0;
  String payload =
    "{\"value\":" + String(waterTemp, 2) +
    ",\"unit\":\"degC\",\"source\":\"device\",\"node_id\":\"" + String(NODE_ID) + "\"}";
  mqttClient.publish(telemetryTopic("temp").c_str(), payload.c_str());
}

void handleControlMessage(char* topic, byte* payload, unsigned int length) {
  String message;
  for (unsigned int index = 0; index < length; index++) {
    message += (char)payload[index];
  }

  Serial.print("Control message on ");
  Serial.print(topic);
  Serial.print(": ");
  Serial.println(message);

  String commandId = extractField(message, "command_id");
  String commandUid = extractField(message, "command_uid");

  if (String(topic).endsWith("/light")) {
    if (message.indexOf("\"command\":\"on\"") >= 0) {
      Serial.println("Would switch light ON");
    } else if (message.indexOf("\"command\":\"off\"") >= 0) {
      Serial.println("Would switch light OFF");
    }
  }

  if (String(topic).endsWith("/pump")) {
    if (message.indexOf("\"command\":\"on\"") >= 0) {
      Serial.println("Would switch pump ON");
    } else if (message.indexOf("\"command\":\"off\"") >= 0) {
      Serial.println("Would switch pump OFF");
    }
  }

  publishAck(commandId, commandUid, true, String());
}

void ensureWifi() {
  while (WiFi.status() != WL_CONNECTED) {
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    delay(2000);
  }
}

void ensureMqtt() {
  while (!mqttClient.connected()) {
    if (mqttClient.connect(NODE_ID)) {
      mqttClient.subscribe(controlTopic().c_str());
      publishStatus("online");
      publishHeartbeat();
    } else {
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  mqttClient.setServer(MQTT_HOST, MQTT_PORT);
  mqttClient.setCallback(handleControlMessage);
  ensureWifi();
}

void loop() {
  ensureWifi();
  ensureMqtt();
  mqttClient.loop();

  if (millis() - lastPublishAt > 10000) {
    publishHeartbeat();
    publishTelemetry();
    lastPublishAt = millis();
  }
}
