#include "SoftwareSerial.h"

SoftwareSerial K_30_Serial(12,13);  //Sets up a virtual serial port
                                    //Using pin 12 for Rx and pin 13 for Tx
byte readCO2[] = {0xFE, 0X44, 0X00, 0X08, 0X02, 0X9F, 0X25};  //Command packet to read Co2 (see app note)
byte response[] = {0,0,0,0,0,0,0};  //create an array to store the response

//multiplier for value. default is 1. set to 3 for K-30 3% and 10 for K-33 ICB
int valMultiplier = 1;

int counter = 0;  //Counter start with 0
#define ver 1;  //version is 1
int updateinterval;
unsigned long timestamp;
int a = 100;  //a is used as delay time and updateinterval



void setup() {
  Serial.begin(9600);
  K_30_Serial.begin(9600);    //Opens the virtual serial port with a baud of 9600
}

void loop() {
  sendRequest(readCO2);
  unsigned long valCO2 = getValue(response);
 
  /*abc("GPS", gpsr(456,789));*/
  abc("CO2", CO2(valCO2));
  /*abc("HeartRate", Heartrate(140));
  abc("Galvanic Skin Response", gsr(1));
  abc("Temperature and Humidity", thsensor(temperature,humidity));*/
  //Put the result of sensor in String
  counter++;  
  delay(a);
}


void sendRequest(byte packet[])
{
  while(!K_30_Serial.available())  //keep sending request until we start to get a response
  {
    K_30_Serial.write(readCO2,7);
    delay(50);
  }
  
  int timeout=0;  //set a timeoute counter
  while(K_30_Serial.available() < 7 ) //Wait to get a 7 byte response
  {
    timeout++;  
    if(timeout > 10)    //if it takes to long there was probably an error
      {
        while(K_30_Serial.available())  //flush whatever we have
          K_30_Serial.read();
          
          break;                        //exit and try again
      }
      delay(50);
  }
  
  for (int i=0; i < 7; i++)
  {
    response[i] = K_30_Serial.read();
  }  
}

unsigned long getValue(byte packet[])
{
    int high = packet[3];                        //high byte for value is 4th byte in packet in the packet
    int low = packet[4];                         //low byte for value is 5th byte in the packet

  
    unsigned long val = high*256 + low;                //Combine high byte and low byte with this formula to get value
    return val* valMultiplier;
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
  out += "\\'s', 'sensor': ";
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
 String th = " {'Temperature':";
 th += tem;
 th += "'C, 'Humidity':";
 th += hum;
 th += "%}";
 
 return th;    
  } //make result String

/*String gsr(int vol)
{
 String gsr = " {'Galvanic Skin Response':";
 gsr += vol;
 gsr += "V}";
 return gsr;
  }*/

String CO2(unsigned long ppm)
{
 String CO2 = " {'CO2':'";
 CO2 += ppm;
 CO2 += "ppm'}";
 return CO2;  
  }

/*String Heartrate(int bpm)
{
 String Heartrate = " {'Heartrate':";
 Heartrate += bpm;
 Heartrate += "bpm}";
return Heartrate;
  }*/
  


