#include <Wire.h>
#include <BH1750.h>
#include <DHT.h>

#define DHTPIN 2      // DHT 传感器连接到数字引脚 2
#define DHTTYPE DHT11 // DHT 11 传感器类型
#define SOUND_PIN 7   // 声音传感器连接到数字引脚 7
#define LED_PIN 13    // LED 连接到数字引脚 13

DHT dht(DHTPIN, DHTTYPE);
BH1750 lightMeter;

void setup() {
  Serial.begin(9600);
  dht.begin();
  Wire.begin();
  lightMeter.begin();
  pinMode(SOUND_PIN, INPUT); // 设置声音传感器引脚为输入模式
  pinMode(LED_PIN, OUTPUT);  // 设置LED引脚为输出模式
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

  // 读取声音传感器数据
  int soundState = digitalRead(SOUND_PIN);

  // 控制LED灯，如果光线低于50，点亮LED，否则关闭
  if (lux < 50) {
    digitalWrite(LED_PIN, HIGH);  // 点亮LED
  } else {
    digitalWrite(LED_PIN, LOW);   // 关闭LED
  }

  // 将数据发送到串口
  Serial.print(temperature);
  Serial.print(",");
  Serial.print(humidity);
  Serial.print(",");
  Serial.print(lux);
  Serial.print(",");
  if (soundState == HIGH) {
    Serial.println("1");
  } else {
    Serial.println("0");
  }
}
