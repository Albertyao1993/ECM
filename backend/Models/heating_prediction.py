import joblib
import holidays
from datetime import datetime
import pandas as pd
import numpy as np
from pymongo import MongoClient
import os

class HeatingPrediction:
    def __init__(self, model_path=None, 
                 uri="mongodb://localhost:27017/", 
                 db_name="sensor_data", 
                 collection_name="readings"):
        """
        初始化预测类
        model_path: SVR模型文件路径
        uri: MongoDB连接URI
        db_name: 数据库名称
        collection_name: 集合名称
        """
        if model_path is None:
            # 获取当前文件所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(current_dir, 'SVR', 'svr_15min_heating.pkl')
            print(model_path)
        
        try:
            self.model = joblib.load(model_path)
        except Exception as e:
            raise Exception(f"无法加载模型文件 {model_path}: {str(e)}")
            
        self.de_holidays = holidays.DE()  # 德国节假日
        
        # 连接MongoDB
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def _get_latest_data(self):
        """获取MongoDB中最新的一条数据"""
        return self.collection.find_one(sort=[('timestamp', -1)])

    def _is_working_hour(self, hour):
        """判断是否是工作时间（9:00-17:00）"""
        return 9 <= hour < 17

    def _prepare_features(self, data):
        """准备模型所需的特征"""
        timestamp = data['timestamp']
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

        # 计算时间相关特征
        is_holiday = timestamp.date() in self.de_holidays
        day_of_week = timestamp.weekday() + 1
        hour_of_day = timestamp.hour
        is_working_hour = self._is_working_hour(hour_of_day)

        # 计算室内外温差
        indoor_temp = data['temperature']
        outdoor_temp = data['ow_temperature']
        temp_difference = indoor_temp - outdoor_temp

        # 创建特征字典
        features = {
            'is_holiday': 1 if is_holiday else 0,
            'day_of_week': day_of_week,
            'hour_of_day': hour_of_day,
            'is_working_hour': 1 if is_working_hour else 0,
            'number_of_people': data['person_count'],
            'Temperature': data['ow_temperature'],
            'Humidity': data['ow_humidity'],
            'Dewpoint': data['ow_dewpoint'],
            'Sun Duration': data['ow_sun_duration'],
            'Precipitation Height': data['ow_precipitation'],
            'Wind Speed': data['ow_wind_speed'],
            'Wind Direction': data['ow_wind_direction'],
            'indoor_temperature': indoor_temp,
            'temperature_difference': temp_difference
        }

        # 转换为DataFrame并确保列顺序正确
        feature_df = pd.DataFrame([features])
        expected_columns = [
            'is_holiday', 'day_of_week', 'hour_of_day', 'is_working_hour',
            'number_of_people', 'Temperature', 'Humidity', 'Dewpoint',
            'Sun Duration', 'Precipitation Height', 'Wind Speed', 'Wind Direction',
            'indoor_temperature', 'temperature_difference'
        ]
        return feature_df[expected_columns]

    def predict(self):
        """
        获取最新数据并进行预测
        返回：预测的能源消耗值
        """
        try:
            # 获取最新数据
            latest_data = self._get_latest_data()
            if not latest_data:
                raise ValueError("无法获取最新数据")

            # 准备特征
            features = self._prepare_features(latest_data)

            # 进行预测
            prediction = self.model.predict(features)

            return {
                'prediction': float(prediction[0]),
                'timestamp': latest_data['timestamp'],
                'features_used': features.to_dict(orient='records')[0]
            }

        except Exception as e:
            print(f"预测过程中发生错误: {str(e)}")
            return None

    def close(self):
        """关闭MongoDB连接"""
        self.client.close()