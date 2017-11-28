#include <Arduino.h>
#include "boxdriver/driver.h"
#include <SoftwareSerial.h>
#include <TinyGPS.h>

SoftwareSerial mySerial(6, 5); // RX, TX
TinyGPS gps; 
void gpsdump(TinyGPS &gps);
long lat, lon, speed;
unsigned long date, times, chars;


void handlerGetCurrentCount(String *command, String *data) {
  BoxDriver::getInstance()->sendAttribute("Lat", lat);
  BoxDriver::getInstance()->sendAttribute("Lon", lon);
  BoxDriver::getInstance()->sendAttribute("Date(ddmmyy)", date);
  BoxDriver::getInstance()->sendAttribute("Time(hhmmsscc)", times);
  BoxDriver::getInstance()->sendAttribute("Speed", speed);

}



void registerListener() {
  BoxDriver::getInstance()->addListener("getCurrentCount", handlerGetCurrentCount);
}

void setup() {
  mySerial.begin(9600); 
  BoxDriver::getInstance()->init("GPS_SENSOR", "GPS_SENSOR", 9600, registerListener);
}

void loop() {
  bool newdata = false;
  unsigned long start = millis();
 
  // Every 5 seconds we print an update
  while (millis() - start < 5000) {
    if (mySerial.available()) {
      char c = mySerial.read();
      // Serial.print(c);  // uncomment to see raw GPS data
      if (gps.encode(c)) {
        newdata = true;
        // break;  // uncomment to print new data immediately!
      }
    }
  }
  gps.get_position(&lat, &lon);
  lat = lat;
  lon = lon;
  gps.get_datetime(&date, &times);
  date = date;
  times = times;
  speed = gps.f_speed_knots();
  BoxDriver::getInstance()->tick();
}
