#include "dht.h"
#define dhtPin A0

dht DHT;
int freq = 2000;

void setup(){
  Serial.begin(9600);
}

void loop(){
    delay(freq); 
    DHT.read11(dhtPin);
    Serial.print((int)DHT.temperature);
    Serial.print(","); 
    Serial.println((int)DHT.humidity);
}
