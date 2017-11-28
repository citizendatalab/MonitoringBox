#include <Arduino.h>
#include "boxdriver/driver.h"
#include <DHT.h>
#define DHTPIN 2
#define DHTTYPE   DHT22   
DHT dht(DHTPIN, DHTTYPE); 
float temperature;
float humidity;

void handlerGetCurrentCount(String *command, String *data) {
  BoxDriver::getInstance()->sendAttribute("Temperature", temperature);
  BoxDriver::getInstance()->sendAttribute("Humidity", humidity);

}



void registerListener() {
  BoxDriver::getInstance()->addListener("getCurrentCount", handlerGetCurrentCount);
}

void setup() {
  dht.begin();
  BoxDriver::getInstance()->init("TEM_AND_HUM_SENSOR", "TEM_AND_HUM_SENSOR", 9600, registerListener);
}

void loop() {
  temperature = dht.readTemperature();
  humidity = dht.readHumidity();
  BoxDriver::getInstance()->tick();  
}
