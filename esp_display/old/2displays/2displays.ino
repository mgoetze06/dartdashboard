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

void setup() {
  // put your setup code here, to run once:
  Multi_I2CInit(sda_list, scl_list, speed_list, NUM_BUSES);
  Multi_OLEDInit(bus_list, addr_list, type_list, flip_list, invert_list, NUM_DISPLAYS);
} // setup

void loop() {
  // put your main code here, to run repeatedly:
uint8_t i;
char szTemp[16];

  for (i=0; i<NUM_DISPLAYS; i++)
  {
    Multi_OLEDFill(i, 0);
    Multi_OLEDSetContrast(i, 20);
    Multi_OLEDWriteString(i, 10, 0, (char *)"Display", FONT_SMALL, 0);
    sprintf(szTemp, "Num: %d", i);
    Multi_OLEDWriteString(i, 10, 2, szTemp, FONT_LARGE, 0);
  }
  delay(5000);  
} // loop
