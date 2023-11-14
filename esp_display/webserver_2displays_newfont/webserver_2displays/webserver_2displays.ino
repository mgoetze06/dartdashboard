#include <Arduino.h>
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


char prev_punkte0[16];
char prev_punkte1[16];
char spieler[1];

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

    for (uint8_t t = 4; t > 0; t--){
        Serial.printf("[SETUP] BOOT WAIT %d...\n", t);
        Serial.flush();
        delay(1000);
    }   

    int i = 0;
    char szTemp[16];
    for (i=0; i<NUM_DISPLAYS; i++)
    {
        Multi_OLEDFill(i, 0);
        Multi_OLEDSetContrast(i, 20);
        Serial.println("write to display");
        sprintf(szTemp, "A");
        Multi_OLEDWriteString(i, 0, 0, szTemp, FONT_FILL, 0);
        Serial.println("write to display done");
        // sprintf(szTemp, "IP: %d.%d.%d.%d", ip[0], ip[1], ip[2], ip[3]);
        // Multi_OLEDWriteString(i, 10, 2, szTemp, FONT_SMALL, 0);
    }
}

void loop(){

}