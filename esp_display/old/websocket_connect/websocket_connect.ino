#include <ESP8266WiFi.h>
//#include <WiFi.h> // ESP32 WiFi Library
//#include <WebServer.h> // WebServer Library for ESP32
#include <WebSocketsClient.h> // WebSocket Client Library for WebSocket
#include <ArduinoJson.h> // Arduino JSON Library
//#include <Adafruit_SSD1306.h> // OLED Display Library 

//#define SCREEN_WIDTH 128 // OLED display width, in pixels
//#define SCREEN_HEIGHT 64 // OLED display height, in pixels
// Wifi Credentials
const char* ssid = "99Problems WiFi aint one"; // Wifi SSID
const char* password = "stehtaufmrouter"; //Wi-FI Password
WebSocketsClient webSocket; // websocket client class instance
StaticJsonDocument<100> doc; // Allocate a static JSON document
//Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1); //SSD1306 instance 
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  if (type == WStype_TEXT)
  {
    // deserialize incoming Json String
    DeserializationError error = deserializeJson(doc, payload); 
    if (error) { // Print erro msg if incomig String is not JSON formated
      Serial.print(F("deserializeJson() failed: "));
      Serial.println(error.c_str());
      return;
    }
    const String pin_stat = doc["PIN_Status"]; // String variable tha holds LED status
    const float t = doc["Temp"]; // Float variable that holds temperature
    const float h = doc["Hum"]; // Float variable that holds Humidity
    Serial.print(String(pin_stat)); // Print the received data for debugging
    Serial.print(String(t));
    Serial.println(String(h));
    // webSocket.sendTXT("OK"); // Send acknowledgement
    /* LED: OFF
       TMP: Temperature
       Hum: Humidity
    */
    // display.clearDisplay(); // Clear the display
    // display.setCursor(0, 0); // Set the cursor position to (0,0)
    // display.println("LED:"); // Print LED: on the display
    // display.setCursor(45, 0); // Set the cursor
    // display.print(pin_stat); // print LED Status to the display
    // display.setCursor(0, 20); // Set the cursor position (0, 20)
    // display.println("TMP:"); // Print TMP: on the display
    // display.setCursor(45, 20); // Set the cursor position (45, 20)
    // display.print(t); // Print temperature value
    // display.setCursor(0, 40); // Set the cursor position (0, 40)
    // display.println("HUM:");// Print HUM: on the display
    // display.setCursor(45, 40); // Set the cursor position (45, 40)
    // display.print(h); // Print Humidity vsalue
    // display.display(); // Show all the information on the display
  }
}
void setup() {
  // put your setup code here, to run once:
  // Connect to local WiFi
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.begin(115200);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println();
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP()); // Print local IP address
  //if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3D for 128x64
  //  Serial.println(F("SSD1306 allocation failed")); // OLED display not found
  //  for (;;);
  //}
  delay(2000); // wait for 2s
  //display.clearDisplay(); // clear the display
  //display.setTextSize(2); // set Test size to 2
  //display.setTextColor(WHITE); //set display colour to "WHITE"
  //address, port, and URL path
  webSocket.begin("192.168.0.9", 5000, "/socket.io/?EIO=4&transport=polling");
  // WebSocket event handler
  webSocket.onEvent(webSocketEvent);
  // if connection failed retry every 5s
  webSocket.setReconnectInterval(5000);
}

void loop() { 
  webSocket.loop(); // Keep the socket alive
  }

