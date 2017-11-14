#include <Wire.h>
#include "MAX30105.h"

#include "heartRate.h"

MAX30105 particleSensor;

const byte RATE_SIZE = 4; //Increase this for more averaging. 4 is good.
byte rates[RATE_SIZE]; //Array of heart rates
byte rateSpot = 0;
long lastBeat = 0; //Time at which the last beat occurred

float beatsPerMinute;


int counter = 0;  //Counter start with 0
#define ver 1;  //version is 1
int updateinterval;
unsigned long timestamp;
int a = 1000;  //a is used as delay time and updateinterval
long sensor_previousTime = 0;
long sensor_interval = a;


void setup() {
   Serial.begin(115200);
  Serial.println("Initializing...");

  // Initialize sensor
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) //Use default I2C port, 400kHz speed
  {
    Serial.println("MAX30105 was not found. Please check wiring/power. ");
    while (1);
  }
  Serial.println("Place your index finger on the sensor with steady pressure.");

  particleSensor.setup(); //Configure sensor with default settings
  particleSensor.setPulseAmplitudeRed(0x0A); //Turn Red LED to low to indicate sensor is running
  particleSensor.setPulseAmplitudeGreen(0); //Turn off Green LED
}

void loop() {


      long irValue = particleSensor.getIR();

  

  if (checkForBeat(irValue) == true)
  {
      //We sensed a beat!
    long delta = millis() - lastBeat;
    lastBeat = millis();

    beatsPerMinute = 60 / (delta / 1000.0);

    if (beatsPerMinute < 255 && beatsPerMinute > 20)
    {
      rates[rateSpot++] = (byte)beatsPerMinute; //Store this reading in the array
      rateSpot %= RATE_SIZE; //Wrap variable   
    }
  }
if(millis() - sensor_previousTime > sensor_interval){
    sensor_previousTime = millis(); 
//
//
//  /*abc("GPS", gpsr(456,789));
//  abc("CO2", CO2(100));*/
  abc("'HeartRate'", HeartrateGen(irValue,beatsPerMinute));
//  /*abc("Galvanic Skin Response", gsr(1));
//  abc("'Temperature and Humidity'", thsensor(temperature,humidity));*/
//  //Put the result of sensor in String
  counter++;  
  }
}



void abc(char * sensor, String result){

  timestamp = (millis()/1000); 
  updateinterval = a; //updateinterval is same with delay time
  String out = "{'packetNumer':";
  out += counter;
  out += ", 'version':";
  out += ver;
  out += ", 'updateInterval':";
  out += updateinterval;
  out += ", 'timestamp':'";
  out += timestamp;
  out += "s', 'sensor': ";
  out += sensor;
  out += ", 'Data':";
  out += result;
  out += "}";



  // Send the packet
  char temp[out.length() + 1];
  out.toCharArray(temp, out.length() + 1);
  Serial.println(temp);
}

 /*String  gpsr(float lon, float lat)
{
 String gpsr = " {'long':";
 gpsr += lon;
 gpsr += ", 'latt':";
 gpsr += lat;
 gpsr += "}";
   
return gpsr;
  }

 String thsensor(float tem, float hum)
{
 String th = " {'Temperature':'";
 th += tem;
 th += "C', 'Humidity':'";
 th += hum;
 th += "%'}";
 
 return th;    
  } //make result String

/*String gsr(int vol)
{
 String gsr = " {'Galvanic Skin Response':";
 gsr += vol;
 gsr += "V}";
 return gsr;
  }

String CO2(int ppm)
{
 String CO2 = " {'CO2':";
 CO2 += ppm;
 CO2 += "ppm}";
 return CO2;  
  }*/

String HeartrateGen(long irValue,float beatsPerMinute)
{
 String Heartrate = " {'IR':";
 Heartrate += irValue;
 Heartrate += ",'HeartRate':'";
 Heartrate += beatsPerMinute;
 Heartrate += "bpm'}";
return Heartrate;
  }
  


