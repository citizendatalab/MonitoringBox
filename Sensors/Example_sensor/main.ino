#include <Arduino.h>

/**
 * @var Protocol version is 1.
 */
#define PROTOCOL_VERSION 1;

/**
 * @var First packet will be packet 0.
 */
int packetCounter = 0;

/**
 * @var Set the update frequency.
 */
int delayUpdateInterval = 100;

/**
 * @var Counter used as test data.
 */
unsigned int counter = 0;

/**
 * Setup the connections to the host device.
 */
void setup() {
    // put your setup code here, to run once:
    Serial.begin(9600);
}

/**
 * Will send a JSON packet by serial to the host device.
 *
 * @param char *sensor  The sensor type.
 * @param char *name    The name of the sensor.
 * @param String result The data the sensor measured.
 */
void sendPacket(char *sensor, char *name, String result) {
  unsigned long timestamp = millis();

  // Generate the packet contents.
  String protoPacket = "{\"packetNumer\":";
  protoPacket += packetCounter;
  protoPacket += ", \"version\":";
  protoPacket += PROTOCOL_VERSION;
  protoPacket += ", \"update_interval\":";
  protoPacket += delayUpdateInterval;
  protoPacket += ", \"timestamp\":";
  protoPacket += timestamp;
  protoPacket += ", \"sensor\": \"";
  protoPacket += sensor;
  protoPacket += "\", \"name\": \"";
  protoPacket += name;
  protoPacket += "\", \"data\":";
  protoPacket += result;
  protoPacket += "}";

  // Send the packet.
  char packet[protoPacket.length() + 1];
  protoPacket.toCharArray(packet, protoPacket.length() + 1);
  Serial.println(packet);

  // Update the packet counter.
  packetCounter++;
}

/**
 * Will generate the data to be send inside of the serial packet to the host.
 *
 * @param unsigned int count  The current number of rounds of data that has
 *                            been send.
 * @return Data formated such that the host device can process the measured
 *         values.
 */
String exampleSensor(unsigned int count) {
  String result = "{\"counter\":";
  result += counter;
  result += "}";

  return result;
}

/**
 * Continually update the measurements to the host device.
 */
void loop() {
  sendPacket("EXAMPLE_SENSOR", "counter", exampleSensor(counter));

  counter++;

  // Put the result of sensor in String.
  delay(delayUpdateInterval);
}
