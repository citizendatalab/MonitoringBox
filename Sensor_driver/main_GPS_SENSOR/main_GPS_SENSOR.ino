#include <Arduino.h>
#include "driver.h"
#include <SoftwareSerial.h>
#include "TinyGPS.h"

SoftwareSerial mySerial(6, 5); // RX, TX
TinyGPS gps;
void printFloat(double f, int digits = 2); 
void gpsdump(TinyGPS &gps);
long speed;
float flat, flon;
unsigned long date, times, chars;


void handlerGetCurrentCount(String *command, String *data) {
  BoxDriver::getInstance()->sendAttribute("Lat", flat);
  BoxDriver::getInstance()->sendAttribute("Lon", flon);
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
  gps.f_get_position(&flat, &flon);
  flat = flat;
  flon = flon;
  gps.get_datetime(&date, &times);
  date = date;
  times = times+1000000;
  speed = gps.f_speed_knots();
  BoxDriver::getInstance()->tick();
}

void printFloat(double number, int digits)
{
  // Handle negative numbers
  if (number < 0.0) {
     Serial.print('-');
     number = -number;
  }
 
  // Round correctly so that print(1.999, 2) prints as "2.00"
  double rounding = 0.5;
  for (uint8_t i=0; i<digits; ++i)
    rounding /= 10.0;
 
  number += rounding;
 
  // Extract the integer part of the number and print it
  unsigned long int_part = (unsigned long)number;
  double remainder = number - (double)int_part;
  Serial.print(int_part);
 
  // Print the decimal point, but only if there are digits beyond
  if (digits > 0)
    Serial.print("."); 
 
  // Extract digits from the remainder one at a time
  while (digits-- > 0) {
    remainder *= 10.0;
    int toPrint = int(remainder);
    Serial.print(toPrint);
    remainder -= toPrint;
  }
}
