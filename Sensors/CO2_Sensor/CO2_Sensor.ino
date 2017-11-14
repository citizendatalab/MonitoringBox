#include "boxdriver/driver.h"

const double Rl      = 1.0;               // Rl (Ohm) - Load resistance
const double Vadc_5  = 0.0048828125;         // ADC step 5V/1024 4,88mV (10bit ADC)
const double Vadc_33 = 0.0032226562;         // ADC step 3,3V/1024 3,22mV (10bit ADC)
double Vrl;                                  // Output voltage
double Rs;                                   // Rs (Ohm) - Sensor resistance
double ppm;                                  // ppm
double ratio;                                // Rs/Rl ratio

unsigned int adc_rd;
char txt[16];

//Calculation of PPM
void calculatePPM() {
  double lgPPM;
  Vrl = (double)adc_rd * Vadc_5;                 // For 5V Vcc use Vadc_5  and  for 3V Vcc use Vadc_33
  Rs = Rl * (5 - Vrl) / Vrl;                     // Calculate sensor resistance
  ratio = Rs / Rl;                               // Calculate ratio
  lgPPM = (log10(ratio) * -0.8) + 0.9;           // Calculate ppm
  ppm = pow(10, lgPPM);                          // Calculate ppm
}

//Read sensor
void readSensor() {
  adc_rd = analogRead(A1);                       // Read RA2
  //  delay(10);                                 // Pause 10ms
}

void registerListeners() {
  BoxDriver::getInstance()->addListener("getValue", handlerGetValue);
}

void handlerGetValue(String *command, String *data) {
  BoxDriver::getInstance()->sendAttribute("Value", ppm);
}

void setup() {
  delay(100);                                    // Pause of 100ms for ADC module stabilization

  BoxDriver::getInstance()->init("Simple CO2 Sensor", "CO2_SENSOR", 9600, registerListeners);
  //Initial read ADC and display PPM value on LCD
  readSensor();                                  // Read sensor
  calculatePPM();                                // Calculating PPM value
}

void loop() {
  if (millis() % 500 == 0) {
    readSensor();                                // Read sensor
    calculatePPM();                              // Calculating PPM value
  }
  
  BoxDriver::getInstance()->tick();
}
