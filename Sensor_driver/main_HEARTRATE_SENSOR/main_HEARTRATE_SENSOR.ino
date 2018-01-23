#include <Arduino.h>
#include "driver.h"
#include "MAX30105.h"
#include "heartRate.h"
#include <Wire.h>

MAX30105 particleSensor;

const byte RATE_SIZE = 4; //Increase this for more averaging. 4 is good.
byte rates[RATE_SIZE]; //Array of heart rates
byte rateSpot = 0;
long lastBeat = 0; //Time at which the last beat occurred
long sensor_previousTime = 0;
long sensor_interval = 100;
float beatsPerMinute;
long irValue;

void handlerGetCurrentCount(String *command, String *data) {
  BoxDriver::getInstance()->sendAttribute("irValue", irValue);
  BoxDriver::getInstance()->sendAttribute("beatsPerMinute", beatsPerMinute);
 
}

void registerListener() {
  BoxDriver::getInstance()->addListener("getCurrentCount", handlerGetCurrentCount);
}

void setup() {
  BoxDriver::getInstance()->init("HEARTRATE_SENSOR", "HEARTRATE_SENSOR", 9600, registerListener);
  particleSensor.begin(Wire, I2C_SPEED_FAST);
  particleSensor.setup(); //Configure sensor with default settings
  particleSensor.setPulseAmplitudeRed(0x0A); //Turn Red LED to low to indicate sensor is running
  particleSensor.setPulseAmplitudeGreen(0); //Turn off Green LED
}

void loop() {
  
  irValue = particleSensor.getIR();
  if(checkForBeat(irValue) == true){
    long delta = millis() - lastBeat;
    lastBeat = millis();

    beatsPerMinute = 60 / (delta / 1000.0);
    if(beatsPerMinute < 255 && beatsPerMinute > 20){
      rates[rateSpot++] = (byte)beatsPerMinute;
      rateSpot %= RATE_SIZE;
    }
  }
  if(millis() - sensor_previousTime > sensor_interval){
    sensor_previousTime = millis();
  }
BoxDriver::getInstance()->tick();
}
