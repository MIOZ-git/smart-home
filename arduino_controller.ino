#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>

// WiFi настройки
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Пины для устройств
const int LED_PIN = 2;           // Встроенный LED
const int RELAY_PIN = 4;         // Реле для управления устройствами
const int DHT_PIN = 5;           // Датчик температуры DHT22
const int MOTION_PIN = 6;        // Датчик движения PIR
const int LIGHT_SENSOR_PIN = 7;  // Датчик освещенности

WebServer server(80);

// Состояние устройств
bool ledState = false;
bool relayState = false;
float temperature = 0;
float humidity = 0;
bool motionDetected = false;
int lightLevel = 0;

void setup() {
  Serial.begin(115200);
  
  // Настройка пинов
  pinMode(LED_PIN, OUTPUT);
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(MOTION_PIN, INPUT);
  pinMode(LIGHT_SENSOR_PIN, INPUT);
  
  // Подключение к WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Подключение к WiFi...");
  }
  
  Serial.println("WiFi подключен!");
  Serial.print("IP адрес: ");
  Serial.println(WiFi.localIP());
  
  // Настройка веб-сервера
  setupWebServer();
  server.begin();
}

void loop() {
  server.handleClient();
  
  // Обновление датчиков
  updateSensors();
  
  delay(100);
}

void setupWebServer() {
  // Главная страница
  server.on("/", HTTP_GET, []() {
    String html = "<html><head><title>Умный дом - Arduino</title></head>";
    html += "<body><h1>Управление устройствами</h1>";
    html += "<p><a href='/led/on'>Включить LED</a> | <a href='/led/off'>Выключить LED</a></p>";
    html += "<p><a href='/relay/on'>Включить реле</a> | <a href='/relay/off'>Выключить реле</a></p>";
    html += "<p><a href='/status'>Статус устройств</a></p>";
    html += "</body></html>";
    server.send(200, "text/html", html);
  });
  
  // Управление LED
  server.on("/led/on", HTTP_GET, []() {
    digitalWrite(LED_PIN, HIGH);
    ledState = true;
    server.send(200, "text/plain", "LED включен");
  });
  
  server.on("/led/off", HTTP_GET, []() {
    digitalWrite(LED_PIN, LOW);
    ledState = false;
    server.send(200, "text/plain", "LED выключен");
  });
  
  // Управление реле
  server.on("/relay/on", HTTP_GET, []() {
    digitalWrite(RELAY_PIN, HIGH);
    relayState = true;
    server.send(200, "text/plain", "Реле включено");
  });
  
  server.on("/relay/off", HTTP_GET, []() {
    digitalWrite(RELAY_PIN, LOW);
    relayState = false;
    server.send(200, "text/plain", "Реле выключено");
  });
  
  // API для получения статуса
  server.on("/api/status", HTTP_GET, []() {
    StaticJsonDocument<200> doc;
    doc["led"] = ledState;
    doc["relay"] = relayState;
    doc["temperature"] = temperature;
    doc["humidity"] = humidity;
    doc["motion"] = motionDetected;
    doc["light_level"] = lightLevel;
    
    String response;
    serializeJson(doc, response);
    server.send(200, "application/json", response);
  });
  
  // API для управления устройствами
  server.on("/api/control", HTTP_POST, []() {
    String body = server.arg("plain");
    StaticJsonDocument<200> doc;
    deserializeJson(doc, body);
    
    if (doc.containsKey("led")) {
      bool state = doc["led"];
      digitalWrite(LED_PIN, state ? HIGH : LOW);
      ledState = state;
    }
    
    if (doc.containsKey("relay")) {
      bool state = doc["relay"];
      digitalWrite(RELAY_PIN, state ? HIGH : LOW);
      relayState = state;
    }
    
    server.send(200, "application/json", "{\"success\": true}");
  });
}

void updateSensors() {
  // Чтение датчика движения
  motionDetected = digitalRead(MOTION_PIN) == HIGH;
  
  // Чтение датчика освещенности
  lightLevel = analogRead(LIGHT_SENSOR_PIN);
  
  // Здесь можно добавить чтение DHT22 датчика
  // temperature = dht.readTemperature();
  // humidity = dht.readHumidity();
} 