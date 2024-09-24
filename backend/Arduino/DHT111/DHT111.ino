#include <Wire.h>
#include <BH1750.h>
#include <DHT.h>

#define DHTPIN 2     // DHT 传感器连接到数字引脚 2
#define DHTTYPE DHT11   // DHT 11 传感器类型

DHT dht(DHTPIN, DHTTYPE);
BH1750 lightMeter;

void setup() {
  Serial.begin(9600);
  dht.begin();
  Wire.begin();
  lightMeter.begin();
}

void loop() {
  // 等待传感器稳定
  delay(2000);

  // 读取湿度和温度数据
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  // 检查读取是否成功
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  // 读取光照数据
  float lux = lightMeter.readLightLevel();
  if (lux == 0) {
    Serial.println("Failed to read from BH1750 sensor!");
    return;
  }

  // 将数据发送到串口
 
  Serial.print(temperature);
  Serial.print(",");
  Serial.print(humidity);
  Serial.print(",");
  Serial.println(lux);
}