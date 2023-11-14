#include <Arduino.h>
#include "secrets.h"
#include <ESP8266WiFi.h>
//#include <WiFiMulti.h>
#include <ESP8266WebServer.h> 
#include <ArduinoJson.h>


//WiFiClient espClient;

// CONST VARIABLES
const char *ssid = WIFI_SSID;
const char *pass = WIFI_PASSWORD;

ESP8266WebServer server(80);    // Create a webserver object that listens for HTTP request on port 80

void handleRoot();              // function prototypes for HTTP handlers
void handleNotFound();

void setup(){
    Serial.begin(9600);

    Serial.setDebugOutput(true);

    Serial.println();
    Serial.println();
    Serial.println();

    for (uint8_t t = 4; t > 0; t--){
        Serial.printf("[SETUP] BOOT WAIT %d...\n", t);
        Serial.flush();
        delay(1000);
    }   


    // Connect to WIFI
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, pass);
    //WiFiMulti.addAP(ssid, pass);

    while (WiFi.status() != WL_CONNECTED){
        delay(100);
    }

    server.on("/", handleRoot);               // Call the 'handleRoot' function when a client requests URI "/"
    server.on("/update", HTTP_POST, handleUpdate);
    server.onNotFound(handleNotFound);        // When a client requests an unknown URI (i.e. something other than "/"), call function "handleNotFound"

    server.begin();                           // Actually start the server
    Serial.println("HTTP server started");
}

void handleUpdate(){
    String postBody = server.arg("plain");
    Serial.println(postBody);
 
    DynamicJsonDocument doc(512);
    DeserializationError error = deserializeJson(doc, postBody);
    if (error) {
        // if the file didn't open, print an error:
        Serial.print(F("Error parsing JSON "));
        Serial.println(error.c_str());
 
        String msg = error.c_str();
 
        server.send(400, F("text/html"),
                "Error in parsin json body! <br>" + msg);
 
    } else {
        JsonObject postObj = doc.as<JsonObject>();
 
        Serial.print(F("HTTP Method: "));
        Serial.println(server.method());
 
        if (server.method() == HTTP_POST) {
            if (postObj.containsKey("sender") && postObj.containsKey("receiver")) {
 
                Serial.println(F("done."));
 
                // Here store data or doing operation
                Serial.print("sender: ");
                const char* sender = postObj["sender"];
                Serial.println(sender);
                Serial.print("receiver: ");
                const char* receiver = postObj["receiver"];
                Serial.println(receiver);
                Serial.print("message: ");
                const char* message = postObj["message"];
                Serial.println(message);
                serializeJson(doc, Serial);
                // Serial.print("sender: ");
                // Serial.println(postObj["sender"]);
                // Serial.print("reciever: ");
                // //Serial.println(doc["sender"]);
                // Serial.print("message: ");
                //Serial.println(doc["message"]);
                // Create the response
                // To get the status of the result you can get the http status so
                // this part can be unusefully
                DynamicJsonDocument doc(512);
                doc["status"] = "OK";
 
                Serial.print(F("Stream..."));
                String buf;
                serializeJson(doc, buf);
 
                server.send(201, F("application/json"), buf);
                Serial.print(F("done."));
 
            }else {
                DynamicJsonDocument doc(512);
                doc["status"] = "KO";
                doc["message"] = F("No data found, or incorrect!");
 
                Serial.print(F("Stream..."));
                String buf;
                serializeJson(doc, buf);
 
                server.send(400, F("application/json"), buf);
                Serial.print(F("done."));
            }
        }
    }
    Serial.println("updated...");
}

void handleRoot() {
  server.send(200, "text/plain", "Hello world!");   // Send HTTP status 200 (Ok) and send some text to the browser/client
}

void handleNotFound(){
  server.send(404, "text/plain", "404: Not found"); // Send HTTP status 404 (Not Found) when there's no handler for the URI in the request
}

void loop(){
  server.handleClient();      
}