#include "dht.h"
#include <Time.h>

#define dhtPin A0

dht DHT;

int frequency = 2000;

int lastMinuteCounter = 0;
int lastMinuteTemperatureArray[30] = {1000};
int lastMinuteHumidityArray[30] = {1000};

bool addToHour = false;
int lastHourCounter = -1;
int lastHourAverageTemperatureArray[60] = {1000};
int lastHourAverageHumidityArray[60] = {1000};
int lastHourSDTemperatureArray[60] = {1000};
int lastHourSDHumidityArray[60] = {1000};

void checkCounters(){
  if(lastMinuteCounter < 29){
    lastMinuteCounter++;
    addToHour = false;
  }else{
    lastMinuteCounter = 0;
    lastHourCounter++;
    addToHour = true;
  }
  if(lastHourCounter >= 60) lastHourCounter = 0;
}

void addToMinuteArrays(){
  lastMinuteTemperatureArray[lastMinuteCounter] = (int)DHT.temperature;
  lastMinuteHumidityArray[lastMinuteCounter] = (int)DHT.humidity;
}

void addToHourArrays(){
  if(addToHour){
    addToAverageHours();
    addToSDHours();
  }
}

void addToAverageHours(){
  lastHourAverageTemperatureArray[lastHourCounter] = averageTemp();
  lastHourAverageHumidityArray[lastHourCounter] = averageHum();
}

void addToSDHours(){
  lastHourSDTemperatureArray[lastHourCounter] = SDTemp();
  lastHourSDHumidityArray[lastHourCounter] = SDHum();
}

float SDTemp(){
  float SDTmp = 0;
  float SDTemperature[30] = {0};
  for(int i = 0; i < 30; i++){
    SDTemperature[i] = pow(lastMinuteTemperatureArray[i] - lastHourAverageTemperatureArray[lastHourCounter], 2);
    SDTmp += SDTemperature[i];
  }
  return sqrt(SDTmp / 30);
}

float SDHum(){
  float SDHumi = 0;
  int SDHumidity[30] = {0};
  for(int i = 0; i < 30; i++){
    SDHumidity[i] = pow(lastMinuteHumidityArray[i] - lastHourAverageHumidityArray[lastHourCounter], 2);
    SDHumi += SDHumidity[i];
  }
  return sqrt(SDHumi / 30);
}

float averageTemp(){
  float averageTemperature = 0;
  for(int i = 0; i < 30; i++)
    averageTemperature += lastMinuteTemperatureArray[i];
  return (averageTemperature / 30);
}

float averageHum(){
  float averageHumidity = 0;
  for(int i = 0; i < 30; i++)
    averageHumidity += lastMinuteHumidityArray[i];
  return (averageHumidity / 30);
}

void printValues(){
  if (Serial.available() > 0) {
    int incomingByte = Serial.read();

    if(incomingByte == 49){
      printMinute();
    }else if(incomingByte == 50){
      printHour();
    }
  }
}

void printMinute(){
  for(int i = 0; i < 30; i++){
    Serial.print(lastMinuteTemperatureArray[i]);
    Serial.print(",");
    Serial.print(lastMinuteHumidityArray[i]);
    Serial.print(";");
  }
  Serial.println(lastMinuteCounter);
}

void printHour(){
  for(int i = 0; i < 60; i++){
    Serial.print(lastHourAverageTemperatureArray[i]);
    Serial.print(",");
    Serial.print(lastHourAverageHumidityArray[i]);
    Serial.print(";");
    Serial.print(lastHourSDTemperatureArray[i]);
    Serial.print(",");
    Serial.print(lastHourSDHumidityArray[i]);
    Serial.print(";");
  }
  Serial.println(lastHourCounter);
}

void resetData(){
  lastMinuteCounter = 0;
  lastHourCounter = -1;
  addToHour = false;
  for(int i = 0; i < 30; i++){
    lastMinuteTemperatureArray[i] = 1000;
    lastMinuteHumidityArray[i] = 1000;
  }
  for(int i = 0; i < 60; i++){
    lastHourAverageTemperatureArray[i] = 1000;
    lastHourAverageHumidityArray[i] = 1000;
    lastHourSDTemperatureArray[i] = 1000;
    lastHourSDHumidityArray[i] = 1000;
  }
}

void setup() {
  Serial.begin(9600);
  resetData();
}

void loop() {
  delay(frequency); 
  DHT.read11(dhtPin);

  addToMinuteArrays();
  addToHourArrays();

  printValues();

  checkCounters();
}
