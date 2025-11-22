#include <DHT.h>

#define PIN_MQ2 34
#define PIN_DHT 4
#define PIN_LED 2
#define PIN_BUZZER 18


#define DHTTYPE DHT11
DHT dht(PIN_DHT, DHTTYPE);


int GAS_LIMIT = 1800;    
int TEMP_LIMIT = 40;   

bool ai_alert_active = false; 

void setup() {
  Serial.begin(115200); 
  
  dht.begin();
  pinMode(PIN_MQ2, INPUT);
  pinMode(PIN_LED, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);

  
  digitalWrite(PIN_LED, HIGH);
  for (int i = 0; i < 100; i++) { 
      digitalWrite(PIN_BUZZER, HIGH); 
      delayMicroseconds(1000); 
      digitalWrite(PIN_BUZZER, LOW); 
      delayMicroseconds(1000); 
  }
  digitalWrite(PIN_LED, LOW);
  
  Serial.println("SYSTEM_READY");
}

void loop() {
  
  int gasValue = analogRead(PIN_MQ2);
  float temp = dht.readTemperature();

  
  bool hardware_danger = false;
  if (gasValue > GAS_LIMIT || temp > TEMP_LIMIT) {
    hardware_danger = true;
  }

  
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == '1') ai_alert_active = true; 
    if (command == '0') ai_alert_active = false; 
  }

  
  Serial.print(gasValue);
  Serial.print(",");
  Serial.println(temp);


  if (hardware_danger || ai_alert_active) {
    digitalWrite(PIN_LED, HIGH);
    
    
    
    for (int i = 0; i < 100; i++) {
       digitalWrite(PIN_BUZZER, HIGH);
       delayMicroseconds(1000); 
       digitalWrite(PIN_BUZZER, LOW);
       delayMicroseconds(1000); 
    }
    
    
    digitalWrite(PIN_LED, LOW);
    delay(100); 
    
  } else {
    
    digitalWrite(PIN_LED, LOW);
    digitalWrite(PIN_BUZZER, LOW);
    delay(200); 
  }
  
  
}