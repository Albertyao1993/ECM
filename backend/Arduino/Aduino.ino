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

  // 将数据发送到串口
  Serial.print(temperature);
  Serial.print(",");
  Serial.print(humidity);
  Serial.print(",");
  Serial.print(lux);
  Serial.print(",");
  Serial.print(soundState);
  Serial.print(",");
  Serial.println(digitalRead(LED_PIN));  // 添加 LED 状态

  // 检查是否有来自 Python 的命令
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    if (command == "LED_ON") {
      digitalWrite(LED_PIN, HIGH);
    } else if (command == "LED_OFF") {
      digitalWrite(LED_PIN, LOW);
    }
  }
}