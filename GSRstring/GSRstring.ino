
/***********************
 Arduino Biofeedback
 Genuary 2014
 Giovanni Gentile
 http://www.0lab.it
 Creative Common License
************************/



//GRS
int counter = 0;  //Counter start with 0
#define ver 1;  //version is 1
int updateinterval;
unsigned long timestamp;
int a = 100;  //a is used as delay time and updateinterval

int grsSensor = A0;
int gsrVal;
int gsrMax = 0;
int gsrMin = 1024;
int gsrAvg = 0;
int i = 1;
int gsrSum = 0;

void setup()
{
  //init seriale
  Serial.begin(9600);
 
}
 
void loop()
{
  
  
  //1 sec delay
  delay(a);
  
  //Value GSR
  gsrVal = analogRead (grsSensor);

  if(gsrVal > 5){
    if(gsrVal < 1024){
      if(gsrVal > gsrMax){
        gsrMax = gsrVal;
        }
      else if(gsrVal < gsrMin){
        gsrMin = gsrVal;
        }
      while(i != 0){
        gsrSum = gsrSum + gsrVal;
        gsrAvg = gsrSum / i;
        i++;
        }
      }
    }

  timestamp = (millis()/1000);
  updateinterval = a;
  String out =  "{'packetNumer':";
  out += counter;
  out += ", 'version':";
  out += ver;
  out += ", 'updateInterval':";
  out += updateinterval;
  out += ", 'timestamp':'";
  out += timestamp;
  out += "s', 'sensor': 'GSR', 'Data':";
  char temp[out.length() + 1];
  out.toCharArray(temp, out.length() + 1);
  Serial.print(temp);

  
  //upload to serial
  Serial.print("{'GSR':");
  Serial.print(gsrVal);
  Serial.print(", 'GSRMIN':");
  Serial.print(gsrMin);
  Serial.print(", 'GSRMAX':");
  Serial.print(gsrMax);
  Serial.print(", 'GSRAVG':");
  Serial.print(gsrAvg);
  Serial.println("}");
  
  
 
  }


