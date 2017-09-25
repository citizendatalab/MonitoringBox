

#include <DHT.h>        

#define DHTPIN    2       // Connect Arduino's pin 2 and Temperature&Humidity Sensor
#define DHTTYPE   DHT22   // Choose DHT-22 case in DHT.h

DHT dht(DHTPIN, DHTTYPE); // Set PIN and TYPE

void setup() {
  Serial.begin(9600);   
  dht.begin();         
}

void loop() {

  float temperature = dht.readTemperature();  // Measure Temperature
  float humidity = dht.readHumidity();        // Measure Humidity

  // Print temperature at Serial Monitor
  Serial.print("Temperature: ");
  Serial.print(temperature);

  // Print humidity at Serial Monitor
  Serial.print(", Humidity: ");
  Serial.println(humidity);

  //Delay for satisfied measuring and printing
  delay(1000);
}
