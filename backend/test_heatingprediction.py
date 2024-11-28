import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Models.heating_prediction import HeatingPrediction
from datetime import datetime
import pandas as pd
import pytest
from pymongo import MongoClient

class TestHeatingPrediction:
    @classmethod
    def setup_class(cls):
        """设置测试环境"""
        # 获取模型文件的绝对路径
        # current_dir = os.path.dirname(os.path.abspath(__file__))
        # model_path = os.path.join(current_dir, 'SVR', 'svr_15min_heating.pkl')
        model_path = '../Models/SVR/svr_15min_heating.pkl'
        #
        # # 确保模型文件存在
        # if not os.path.exists(model_path):
        #     raise FileNotFoundError(f"模型文件不存在: {model_path}")
            
        cls.uri = "mongodb://localhost:27017/"
        cls.db_name = "sensor_data"
        cls.collection_name = "readings"
        
        # 连接MongoDB
        cls.client = MongoClient(cls.uri)
        cls.db = cls.client[cls.db_name]
        cls.collection = cls.db[cls.collection_name]
        
        # 准备测试数据
        cls.test_data = [
            {
                "timestamp": datetime(2024, 3, 20, 14, 30),  # 工作日下午
                "temperature": 22.5,  # 室内温度
                "ow_temperature": 18.3,  # 室外温度
                "ow_humidity": 65,
                "ow_dewpoint": 12.1,
                "ow_sun_duration": 45,  # 45分钟日照
                "ow_precipitation": 0.0,
                "ow_wind_speed": 3.5,
                "ow_wind_direction": 180,
                "person_count": 3
            },
            {
                "timestamp": datetime(2024, 3, 23, 10, 0),  # 周六上午
                "temperature": 21.0,
                "ow_temperature": 15.5,
                "ow_humidity": 70,
                "ow_dewpoint": 10.2,
                "ow_sun_duration": 60,  # 满日照
                "ow_precipitation": 0.2,
                "ow_wind_speed": 2.8,
                "ow_wind_direction": 90,
                "person_count": 1
            },
            {
                "timestamp": datetime(2024, 12, 25, 9, 30),  # 圣诞节
                "temperature": 23.5,
                "ow_temperature": 5.2,
                "ow_humidity": 80,
                "ow_dewpoint": 2.1,
                "ow_sun_duration": 15,  # 低日照
                "ow_precipitation": 1.5,
                "ow_wind_speed": 5.2,
                "ow_wind_direction": 270,
                "person_count": 4
            }
        ]
        
        # 插入测试数据
        cls.collection.insert_many(cls.test_data)

    # ... 其余测试方法保持不变 ...

    @classmethod
    def teardown_class(cls):
        """清理测试环境"""
        # 删除测试数据
        cls.collection.delete_many({
            "timestamp": {"$in": [data["timestamp"] for data in cls.test_data]}
        })
        cls.client.close()

    def test_feature_preparation(self):
        """测试特征准备功能"""
        predictor = HeatingPrediction()
        
        for test_data in self.test_data:
            features = predictor._prepare_features(test_data)
            
            # 验证特征列
            expected_columns = [
                'is_holiday', 'day_of_week', 'hour_of_day', 'is_working_hour',
                'number_of_people', 'Temperature', 'Humidity', 'Dewpoint',
                'Sun Duration', 'Precipitation Height', 'Wind Speed', 'Wind Direction',
                'indoor_temperature', 'temperature_difference'
            ]
            assert list(features.columns) == expected_columns
            
            # 验证温差计算
            temp_diff = test_data['temperature'] - test_data['ow_temperature']
            assert features['temperature_difference'].values[0] == temp_diff
            
            # 验证工作时间判断
            is_working_hour = 9 <= test_data['timestamp'].hour < 17
            assert features['is_working_hour'].values[0] == (1 if is_working_hour else 0)
            
            print(f"\n测试数据时间: {test_data['timestamp']}")
            print("特征值:")
            for col in features.columns:
                print(f"{col}: {features[col].values[0]}")
        
        predictor.close()

    def test_prediction(self):
        """测试预测功能"""
        predictor = HeatingPrediction()
        
        prediction_result = predictor.predict()
        assert prediction_result is not None
        assert 'prediction' in prediction_result
        assert 'features_used' in prediction_result
        
        print("\n预测结果:")
        print(f"预测值: {prediction_result['prediction']:.2f}")
        print("\n使用的特征:")
        for feature, value in prediction_result['features_used'].items():
            print(f"{feature}: {value}")
        
        predictor.close()

    def test_holiday_detection(self):
        """测试节假日检测"""
        predictor = HeatingPrediction()
        
        # 测试圣诞节数据
        christmas_data = next(data for data in self.test_data 
                            if data['timestamp'].month == 12 and data['timestamp'].day == 25)
        features = predictor._prepare_features(christmas_data)
        assert features['is_holiday'].values[0] == 1
        
        # 测试工作日数据
        workday_data = next(data for data in self.test_data 
                          if data['timestamp'].weekday() < 5)
        features = predictor._prepare_features(workday_data)
        assert features['is_holiday'].values[0] == 0
        
        predictor.close()

def run_tests():
    """运行所有测试"""
    print("开始测试 HeatingPrediction 类...")
    print("-" * 50)
    
    test = TestHeatingPrediction()
    test.setup_class()
    
    try:
        print("\n1. 测试特征准备")
        test.test_feature_preparation()
        print("✓ 特征准备测试通过")
        
        print("\n2. 测试预测功能")
        test.test_prediction()
        print("✓ 预测功能测试通过")
        
        print("\n3. 测试节假日检测")
        test.test_holiday_detection()
        print("✓ 节假日检测测试通过")
        
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        test.teardown_class()
        print("\n测试完成")

if __name__ == "__main__":
    run_tests()