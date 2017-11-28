#include <Arduino.h>
#include "boxdriver/driver.h"
int gsrSensor = A0;
int gsrVal;
int gsrMax = 0;
int gsrMin = 1024;
int gsrAvg = 0;
int i = 1;
int gsrSum = 0;


void handlerGetCurrentCount(String *command, String *data) {
  BoxDriver::getInstance()->sendAttribute("GSRval", gsrVal);
  BoxDriver::getInstance()->sendAttribute("GSRmin", gsrMin);
  BoxDriver::getInstance()->sendAttribute("GSRmax", gsrMax);
  BoxDriver::getInstance()->sendAttribute("GSRavg", gsrAvg);

}



void registerListener() {
  BoxDriver::getInstance()->addListener("getCurrentCount", handlerGetCurrentCount);
  
}

void setup() {  
  BoxDriver::getInstance()->init("GSR_SENSOR", "GSR_SENSOR", 9600, registerListener);
}

void loop() {
  gsrVal = analogRead(gsrSensor);
  if(gsrVal > 5){
    if(gsrVal < 1024){
      if(gsrVal > gsrMax){
        gsrMax = gsrVal;
        }
      else if(gsrVal < gsrMin){
        gsrMin = gsrVal;
        }
      while(i != 0){
        gsrSum = gsrSum + gsrVal;
        gsrAvg = gsrSum / i;
        i++;
        }
      }
    }
  BoxDriver::getInstance()->tick();  
}
