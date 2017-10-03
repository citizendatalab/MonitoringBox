void setup() {

  Serial.begin(9600);
  // put your setup code here, to run once:

}


int counter = 0;
#define ver 1;
int updateinterval;
unsigned long timestamp;
int a = 100;


void loop() {
  
  abc("GPS", gpsr(456,789));
  abc("CO2", CO2(100));
  abc("HeartRate", Heartrate(140));
  abc("Galvanic Skin Response", gsr(1));
  abc("Temperature and Humidity", thsensor(14,60));

  counter++;
  delay(a);
}




void abc(char * sensor, String result){
  // Generate the packet
  timestamp = (millis()/1000);
  updateinterval = a;
  String out = "{'packetNumer':";
  out += counter;
  out += ", 'version':";
  out += ver;
  out += ", 'updateInterval':";
  out += updateinterval;
  out += ", 'timestamp':";
  out += timestamp;
  out += "s, 'sensor': ";
  out += sensor;
  out += ", 'Data':";
  out += result;
  out += "}";



  // Send the packet
  char temp[out.length() + 1];
  out.toCharArray(temp, out.length() + 1);
  Serial.println(temp);
}

 String  gpsr(float lon, float lat)
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
  }

String gsr(int vol)
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
  }
  


