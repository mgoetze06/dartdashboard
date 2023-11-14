#include <Arduino.h>
#include "secrets.h"
#include <ESP8266WiFi.h>
//#include <WiFiMulti.h>

#include <SocketIoClient.h>

#define USE_SERIAL Serial

//WiFiClient espClient;
SocketIoClient webSocket;

// CONST VARIABLES
const char *ssid = WIFI_SSID;
const char *pass = WIFI_PASSWORD;
//const char *HOST = "192.168.0.9";
char host[] = "192.168.0.9"; // Socket.IO Server Address
int port = 5000; // Socket.IO Port Address
char path[] = "/socket.io/?transport=websocket"; // Socket.IO Base Path

void event(const char *payload, size_t length){
    USE_SERIAL.printf("got message: %s\n", payload);
}

void setup(){
    USE_SERIAL.begin(9600);

    USE_SERIAL.setDebugOutput(true);

    USE_SERIAL.println();
    USE_SERIAL.println();
    USE_SERIAL.println();

    for (uint8_t t = 4; t > 0; t--){
        USE_SERIAL.printf("[SETUP] BOOT WAIT %d...\n", t);
        USE_SERIAL.flush();
        delay(1000);
    }   


    // Connect to WIFI
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, pass);
    //WiFiMulti.addAP(ssid, pass);

    while (WiFi.status() != WL_CONNECTED){
        delay(100);
    }

    // Receive events from server
    webSocket.on("event", event);

    webSocket.begin(host,port,path);
}

int count = 0;

void loop(){
    webSocket.loop();
    //count++;
    //if (count == 18000){
    //    count = 0;
//
        // Send data to Server
  //      webSocket.emit("status", "Hello from esp32!");
    //}
}