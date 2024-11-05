# backend/open_weather/weather.py
import requests
import math
from datetime import datetime
import time

class OpenWeather:
    def __init__(self, api_key, city):
        self.api_key = api_key
        self.city = city

    def get_weather_data(self):
        url = f"http://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={self.api_key}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            
            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            dewpoint = self._calculate_dewpoint(temp, humidity)
            
            # 计算当前小时的日照时长
            sun_duration = self._calculate_sun_duration(
                data["sys"]["sunrise"],
                data["sys"]["sunset"]
            )
            
            return {
                "ow_temperature": temp,
                "ow_humidity": humidity,
                "ow_weather_desc": data["weather"][0]["description"],
                "ow_dewpoint": round(dewpoint, 2),
                "ow_wind_speed": data["wind"]["speed"],  # 米/秒
                "ow_wind_direction": data["wind"].get("deg", 0),  # 角度
                "ow_precipitation": data.get("rain", {}).get("1h", 0),  # 最近1小时降水量(mm)
                "ow_sun_duration": sun_duration  # 当前小时的日照分钟数（0-60）
            }
        else:
            response.raise_for_status()

    def _calculate_dewpoint(self, temperature, humidity):
        """
        使用Magnus公式计算露点
        temperature: 温度（摄氏度）
        humidity: 相对湿度（百分比）
        """
        a = 17.27
        b = 237.7
        
        alpha = ((a * temperature) / (b + temperature)) + math.log(humidity/100.0)
        return (b * alpha) / (a - alpha)

    def _calculate_sun_duration(self, sunrise, sunset):
        """
        计算当前小时的实际日照时长（分钟）
        sunrise: 日出时间戳
        sunset: 日落时间戳
        返回：当前小时内的实际日照分钟数（0-60）
        """
        current_time = time.time()
        current_datetime = datetime.fromtimestamp(current_time)
        
        # 获取当前小时的起始和结束时间戳
        hour_start = datetime(
            current_datetime.year,
            current_datetime.month,
            current_datetime.day,
            current_datetime.hour
        ).timestamp()
        hour_end = hour_start + 3600  # 一小时后的时间戳

        # 如果当前小时完全在日落之后或日出之前，返回0
        if hour_start >= sunset or hour_end <= sunrise:
            return 0.0

        # 如果当前小时完全在日出和日落之间，返回60
        if hour_start >= sunrise and hour_end <= sunset:
            return 60.0

        # 计算部分重叠的情况
        effective_start = max(hour_start, sunrise)
        effective_end = min(hour_end, sunset)
        
        # 计算有效日照分钟数
        sun_minutes = (effective_end - effective_start) / 60
        
        return round(min(60.0, max(0.0, sun_minutes)), 2)