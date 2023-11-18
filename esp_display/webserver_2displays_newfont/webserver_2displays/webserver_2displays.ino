#include <Arduino.h>
#include "secrets.h"
#include <ESP8266WiFi.h>
//#include <WiFiMulti.h>
#include <ESP8266WebServer.h> 
#include <ArduinoJson.h>
#include <Multi_BitBang.h>
#include <Multi_OLED.h>


#define NUM_DISPLAYS 2
#define NUM_BUSES 2
// I2C bus info
uint8_t scl_list[NUM_BUSES] = {5,5}; //{9,9,9,9};
uint8_t sda_list[NUM_BUSES] = {4, 2}; //{5,6,7,8};
int32_t speed_list[NUM_BUSES] = {400000L, 400000L};
// OLED display info
uint8_t bus_list[NUM_DISPLAYS] = {0,1}; // can be multiple displays per bus
uint8_t addr_list[NUM_DISPLAYS] = {0x3c, 0x3c};
uint8_t type_list[NUM_DISPLAYS] = {OLED_128x64, OLED_128x64};
uint8_t flip_list[NUM_DISPLAYS] = {0,0};
uint8_t invert_list[NUM_DISPLAYS] = {0,0};



//WiFiClient espClient;

// CONST VARIABLES
const char *ssid = WIFI_SSID;
const char *pass = WIFI_PASSWORD;

char prev_punkte0[16];
char prev_punkte1[16];
char spieler[1];


ESP8266WebServer server(80);    // Create a webserver object that listens for HTTP request on port 80

void handleRoot();              // function prototypes for HTTP handlers
void handleNotFound();

void setup(){
    Serial.begin(9600);
    sprintf(prev_punkte0, "%s", "0");
    sprintf(prev_punkte1, "%s", "0");
    sprintf(spieler, "%s", "0");

    Serial.setDebugOutput(true);
    Serial.println("init displays");
    Multi_I2CInit(sda_list, scl_list, speed_list, NUM_BUSES);
    Multi_OLEDInit(bus_list, addr_list, type_list, flip_list, invert_list, NUM_DISPLAYS);
    Serial.println("init displays done");

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
    int i = 0;
    char szTemp[16];
    IPAddress ip = WiFi.localIP();
    for (i=0; i<NUM_DISPLAYS; i++)
    {
        Multi_OLEDFill(i, 0);
        Multi_OLEDSetContrast(i, 20);
        sprintf(szTemp, "Display: %d", i);
        Multi_OLEDWriteString(i, 10, 0, szTemp, FONT_SMALL, 0);
        sprintf(szTemp, "IP: %d.%d.%d.%d", ip[0], ip[1], ip[2], ip[3]);
        Multi_OLEDWriteString(i, 10, 2, szTemp, FONT_SMALL, 0);
    }
}

void handleUpdate(){
    String postBody = server.arg("plain");
    Serial.println(postBody);
    char szTemp[16];
    char szTemp1[1];
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
            if (postObj.containsKey("punkte0") && postObj.containsKey("punkte1")) {
 
                Serial.println(F("done."));


                const char* recievedData2 = postObj["spieler"];
                Serial.println("Spieler:");
                Serial.write(recievedData2,strlen(recievedData2));
                sprintf(spieler, "%s", recievedData2);
                if(atoi(spieler) == 0){
                  const char* recievedData0 = postObj["punkte0"];
                  Serial.print("punkte0: ");
                  Serial.write(recievedData0,strlen(recievedData0));
                  Multi_OLEDFill(0,0x00);
                  sprintf(szTemp, "%s", recievedData0);
                  Multi_OLEDWriteString(0, 0, 0, szTemp, FONT_FILL, 0);
                }else{
                  const char* recievedData1 = postObj["punkte1"];
                  Serial.print("punkte1: ");
                  Serial.write(recievedData1,strlen(recievedData1));
                  Multi_OLEDFill(1,0x00);
                  sprintf(szTemp, "%s", recievedData1);
                  Multi_OLEDWriteString(1, 0, 0, szTemp, FONT_FILL, 0);
                }
                // Here store data or doing operation


                



                

                // for(int i=0;i < 10;i++){
                //   int y = i;
                //   Multi_OLEDDrawLine(atoi(spieler), 0, y, 127, y);
                //   y = 40 +i;
                //   Multi_OLEDDrawLine(atoi(spieler), 0, y, 127, y);
                //   if(i == 9){
                //     for(int j=0;j < 4;j++){
                //       int x = 2 + j;
                //       Multi_OLEDDrawLine(atoi(spieler), x, 0, x, y);
                //       x = 127 - j;
                //       Multi_OLEDDrawLine(atoi(spieler), x, 0, x, y);

                //     }

                //   }
                // }

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