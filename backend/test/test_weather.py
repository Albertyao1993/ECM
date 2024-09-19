# backend/test/test_weather.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from open_weather.weather import OpenWeather

class TestOpenWeather(unittest.TestCase):
    def test_get_weather_data(self):
        api_key = "fa3005c77c9d4631ef729307d175661f"  # 请替换为你的实际 API 密钥
        city = "Darmstadt"
        weather = OpenWeather(api_key, city)
        data = weather.get_weather_data()

        # 检查返回的数据是否包含预期的键
        self.assertIn('main', data)
        self.assertIn('temp', data['main'])
        self.assertIn('humidity', data['main'])
        self.assertIn('weather', data)
        self.assertIn('description', data['weather'][0])

if __name__ == '__main__':
    unittest.main()