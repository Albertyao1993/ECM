# backend/open_weather/weather.py
import requests

class OpenWeather:
    def __init__(self, api_key, city):
        self.api_key = api_key
        self.city = city

    def get_weather_data(self):
        url = f"http://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={self.api_key}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(data)  # 打印天气数据
            return {
                "ow_temperature": data["main"]["temp"],
                "ow_humidity": data["main"]["humidity"],
                "ow_weather_desc": data["weather"][0]["description"],
            }
        else:
            response.raise_for_status()