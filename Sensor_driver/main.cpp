#include <Arduino.h>
#include "boxdriver/driver.h"

unsigned long counter;
unsigned int interval;

void handlerGetCurrentCount(String *command, String *data) {
  BoxDriver::getInstance()->sendAttribute("count", counter);
}

void handlerSetInterval(String *command, String *data) {
  interval = (*data).toInt();
  BoxDriver::getInstance()->setCommandSuccess();
}

void registerListener() {
  BoxDriver::getInstance()->addListener("getCurrentCount", handlerGetCurrentCount);
  BoxDriver::getInstance()->addListener("setInterval", handlerSetInterval);
}

void setup() {
  interval = 1;
  counter = 0;
  BoxDriver::getInstance()->init("SimpleTest", "EXAMPLE_SENSOR", 9600, registerListener);
}

void loop() {
  BoxDriver::getInstance()->tick();
  if (millis() % interval == 0) {
    counter++;
  }
}
