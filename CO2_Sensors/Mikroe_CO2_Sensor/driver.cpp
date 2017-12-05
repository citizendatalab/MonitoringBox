#include "driver.h"
#include <Arduino.h>

BoxDriver* BoxDriver::instance = false;

BoxDriver* BoxDriver::getInstance() {
    if (instance == false) {
        instance = new BoxDriver();
        instance->hasInited = false;
        instance->sendDataPacketCount = 0;
        instance->receivedPacketCount = 0;
        instance->sendDataPacketCount = 0;
    }

    return instance;
}

BoxDriver::BoxDriver() {
}

void BoxDriver::init(String name, String type, long speed, void (*registerer)()) {
  if (this->hasInited == false) {
    this->serialSpeed = speed;
    Serial.begin(speed);
    this->sensorName = name;
    this->sensorType = type;
    this->registerer = registerer;
    this->hasInited = true;
    this->sendCommands = false;
  }
}

void BoxDriver::registerListeners() {
  this->registerer();
  this->addListener("ping", BoxDriver::statCommandListener);
  this->addListener("help", BoxDriver::helpCommandListener);
}

void BoxDriver::tick() {
  if (Serial.available() > 0) {
    this->receivedPacketCount++;

    // Read a line.
    String dataIn = Serial.readStringUntil('\n');

    // Remove the new line char (terminator).
    dataIn = dataIn.substring(0, dataIn.length() - 1);
    unsigned int i = 0;
    while (i <= dataIn.length() && dataIn.charAt(i) != ':') {
      i++;
    }

    this->sendPacketHeader();
    this->packetStatus = 0;
    this->callListener(&dataIn.substring(0, i), &dataIn.substring(i + 1, dataIn.length()));
    if (this->packetStatus & 0x01 == 1) {
      this->sendDataPacketCount++;
    }
    this->sendPacketFooter();
  }
}

void BoxDriver::sendStats() {
  this->sendAttribute("stat.receivedPacketCount", this->receivedPacketCount);
  this->sendAttribute("stat.sendPacketCount", this->sendPacketCount);
  this->sendAttribute("stat.sendDataPacketCount", this->sendDataPacketCount);
}
void BoxDriver::setCommandSuccess() {
  this->packetStatus |= 0x02;
}

void BoxDriver::sendAttributeRaw(String *name, String *value) {
  if (this->packetStatus & 0x01 == 1) {
    this->sendDataPacketCount++;
    Serial.print(",");
  }
  this->packetStatus |= 1;
  Serial.print("\"");
  Serial.print(*name);
  Serial.print("\":");
  Serial.print(*value);
}

void BoxDriver::sendAttribute(String name, String *value) {
  this->sendAttributeRaw(&name, &("\"" + (*value) + "\""));
}

void BoxDriver::sendAttribute(String name, char *value) {
  this->sendAttributeRaw(&name, &("\"" + String(value) + "\""));
}

void BoxDriver::sendAttribute(String name, float value) {
  this->sendAttributeRaw(&name, &String(value));
}

void BoxDriver::sendAttribute(String name, double value) {
  this->sendAttributeRaw(&name, &String(value));
}

void BoxDriver::sendAttribute(String name, long value) {
  this->sendAttributeRaw(&name, &String(value));
}

void BoxDriver::sendAttribute(String name, int value) {
  this->sendAttributeRaw(&name, &String(value));
}

void BoxDriver::sendAttribute(String name, char value) {
  this->sendAttributeRaw(&name, &String(value));
}

void BoxDriver::sendAttribute(String name, bool value) {
  this->sendAttributeRaw(&name, &String((value) == 1 ? "1" : "0"));
}

void BoxDriver::sendAttribute(String name, unsigned long value) {
  this->sendAttributeRaw(&name, &String(value));
}

void BoxDriver::sendAttribute(String name, unsigned int value) {
  this->sendAttributeRaw(&name, &String(value));
}

void BoxDriver::sendAttribute(String name, unsigned char value) {
  this->sendAttributeRaw(&name, &String(value));
}

void BoxDriver::sendPacketHeader() {
  unsigned long timestamp = millis();

  // Generate the packet contents and immediatly send it, we do this because of
  // memory constraints.
  Serial.print("{\"packetNumer\":");
  Serial.print(this->sendDataPacketCount);
  Serial.print(", \"version\":");
  Serial.print(BoxDriver::PROTOCOL_VERSION);
  Serial.print(", \"timestamp\":");
  Serial.print(timestamp);
  Serial.print(", \"sensor\": \"");
  Serial.print(this->sensorType);
  Serial.print("\", \"name\": \"");
  Serial.print(this->sensorName);
  Serial.print("\", \"data\":{");
}

void BoxDriver::sendPacketFooter() {
  Serial.print("},\"status\":\"");
  if (this->packetStatus & 0x01 == 0x01 || this->packetStatus & 0x02 == 0x02) {
    Serial.print("COMMAND_EXECUTED");
  } else {
    Serial.print("UNKOWN_COMMAND");
  }
  Serial.println("\"}");
  this->sendDataPacketCount++;
}

void BoxDriver::addListener(String command, void (*listener)(String*, String*)) {
  if (this->sendCommands) {
    this->sendAttribute("command[" + String(this->comandCounter) + "]", &command);
    this->comandCounter++;
    return;
  }
  if ((*this->searchingCommand) == command) {
    (*listener)(&command, this->data);
  }
}

void BoxDriver::callListener(String *command, String *data) {
  this->searchingCommand = command;
  this->data = data;
  this->registerListeners();
}

static void BoxDriver::statCommandListener(String *command, String *data) {
    BoxDriver::getInstance()->sendAttribute("pong", true);
    BoxDriver::getInstance()->sendStats();
}

static void BoxDriver::helpCommandListener(String *command, String *data) {
  BoxDriver::getInstance()->sendAttribute("listener_count", 0);
  BoxDriver::getInstance()->sendAttribute("listener_registered_count", 1);
  BoxDriver::getInstance()->comandCounter = 0;
  BoxDriver::getInstance()->sendCommands = true;
  BoxDriver::getInstance()->registerListeners();
  BoxDriver::getInstance()->sendCommands = false;
}
