#include <DHT.h>

#define DHTPIN 2
#define DHTTYPE DHT22
#define PIRPIN 3

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
  pinMode(PIRPIN, INPUT);
  delay(2000); // allow sensor to stabilize before reading
}

void loop() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  int motion = digitalRead(PIRPIN);

  // Check for sensor read errors
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Failed to read from DHT22 sensor!");
    delay(5000);
    return;
  }

  // Print as comma-separated values: temperature,humidity,motion
  Serial.print(temperature);
  Serial.print(",");
  Serial.print(humidity);
  Serial.print(",");
  Serial.println(motion);

  delay(30000); // 5 minutes per sample
}
