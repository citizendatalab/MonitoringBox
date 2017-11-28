#include <Arduino.h>
#include "boxdriver/driver.h"
#include "SoftwareSerial.h"

SoftwareSerial K_30_Serial(12,13);  //Sets up a virtual serial port
                                    //Using pin 12 for Rx and pin 13 for Tx
byte readCO2[] = {0xFE, 0X44, 0X00, 0X08, 0X02, 0X9F, 0X25};  //Command packet to read Co2 (see app note)
byte response[] = {0,0,0,0,0,0,0};  //create an array to store the response

//multiplier for value. default is 1. set to 3 for K-30 3% and 10 for K-33 ICB
int valMultiplier = 1;
unsigned long valCO2;


void handlerGetCurrentCount(String *command, String *data) {
  BoxDriver::getInstance()->sendAttribute("CO2Val", valCO2);
}



void registerListener() {
  BoxDriver::getInstance()->addListener("getCurrentCount", handlerGetCurrentCount);
}

void setup() {
  K_30_Serial.begin(9600);
  BoxDriver::getInstance()->init("CO2_SENSOR", "EXPENSIVE_CO2_SENSOR", 9600, registerListener);
}

void loop() {
  sendRequest(readCO2);
  valCO2 = getValue(response);
  BoxDriver::getInstance()->tick();
}



void sendRequest(byte packet[])
{
  while(!K_30_Serial.available())  //keep sending request until we start to get a response
  {
    K_30_Serial.write(readCO2,7);
    delay(50);
  }
  
  int timeout=0;  //set a timeoute counter
  while(K_30_Serial.available() < 7 ) //Wait to get a 7 byte response
  {
    timeout++;  
    if(timeout > 10)    //if it takes to long there was probably an error
      {
        while(K_30_Serial.available())  //flush whatever we have
          K_30_Serial.read();
          
          break;                        //exit and try again
      }
      delay(50);
  }
  for (int i=0; i < 7; i++)
  {
    response[i] = K_30_Serial.read();
  }  
}

unsigned long getValue(byte packet[])
{
    int high = packet[3];                        //high byte for value is 4th byte in packet in the packet
    int low = packet[4];                         //low byte for value is 5th byte in the packet

  
    unsigned long val = high*256 + low;                //Combine high byte and low byte with this formula to get value
    return val* valMultiplier;
}

