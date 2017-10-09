#include <DHT.h>

/**
 * @var Connect temperature and humidity sensor on pin 2.
 */
#define DHTPIN    2

/**
 * @var Set the type of sensor used.
 */
#define DHTTYPE   DHT22

/**
 * @var Protocol version is 1.
 */
#define PROTOCOL_VERSION 1;

/**
 * @var Contains the connection to the sensor.
 */
DHT dht(DHTPIN, DHTTYPE);

/**
 * @var First packet will be packet 0.
 */
int packetCounter = 0;

/**
 * @var Set the update frequency.
 */
int delayUpdateInterval = 100;

/**
 * Setup the connections to the other devices.
 */
void setup() {
  Serial.begin(9600);
  dht.begin();  // Initialize temperature and humidity sensor.
}

/**
 * Continually update the measurements to the host device.
 */
void loop() {
  float temperature = dht.readTemperature();  // Measure temperature.
  float humidity = dht.readHumidity();        // Measure humidity.

  sendPacket("HUMIDITY_TEMPERATURE_SENSOR", "Temperature and Humidity", thsensor(temperature, humidity));

  // Put the result of sensor in String.
  delay(delayUpdateInterval);
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
 * Will generate the data to be send inside of the serial packet to the host
 * with the information from the temperature and humidity sensor.
 *
 * @param float temperature The measured temperature.
 * @param float humidity    The measured humidity.
 * @return Data formated such that the host device can process the measured
 *         values.
 */
String thsensor(float temperature, float humidity) {
  String result = "{\"Temperature\": \"";
  result += temperature;
  result += "C\", \"Humidity\": \"";
  result += humidity;
  result += "%\"}";

  return result;
}
