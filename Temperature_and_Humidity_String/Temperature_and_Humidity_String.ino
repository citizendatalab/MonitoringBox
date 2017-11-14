#include <DHT.h>        
#define DHTPIN    2       // Connect sensor with pin2
#define DHTTYPE   DHT22   
DHT dht(DHTPIN, DHTTYPE); 

int counter = 0;  //Counter start with 0
#define ver 1;  //version is 1
int updateinterval;
unsigned long timestamp;
int a = 100;  //a is used as delay time and updateinterval



void setup() {
  Serial.begin(9600);
  dht.begin();  //initialize Sensor
}

void loop() {

  float temperature = dht.readTemperature();  //Mesure temperature  
  float humidity = dht.readHumidity();  //Mesure humidity 
  /*abc("GPS", gpsr(456,789));
  abc("CO2", CO2(100));
  abc("HeartRate", Heartrate(140));
  abc("Galvanic Skin Response", gsr(1));*/
  abc("'Temperature and Humidity'", thsensor(temperature,humidity));
  //Put the result of sensor in String
  counter++;  
  delay(a);
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
  out += ", 'timestamp':";
  out += timestamp;
  out += "'s', 'sensor': ";
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
  }*/

 String thsensor(float tem, float hum)
{
 String th = " {'Temperature':";
 th += tem;
 th += "'\'C', 'Humidity':";
 th += hum;
 th += "'%'}";
 
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
  }

String Heartrate(int bpm)
{
 String Heartrate = " {'Heartrate':";
 Heartrate += bpm;
 Heartrate += "bpm}";
return Heartrate;
  }*/
  


