# sensor_simulator.py
import random
import time
from datetime import datetime
from flask_socketio import SocketIO

class SensorSimulator:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.data = []

    def generate_sensor_data(self):
        while True:
            new_data_point = {
                'timestamp': datetime.now().isoformat(),
                'temperature': round(random.uniform(20.0, 30.0), 2),  # 模拟温度数据 20.0 到 30.0 度
                'humidity': round(random.uniform(30.0, 70.0), 2)     # 模拟湿度数据 30% 到 70%
            }
            self.data.append(new_data_point)
            
            # 只保留最新的20个数据点
            if len(self.data) > 20:
                self.data.pop(0)
            
            # 向所有连接的客户端发送数据
            self.socketio.emit('sensor_data', new_data_point)
            print(f"Sent data: {new_data_point}")
            
            time.sleep(2)  # 每2秒生成一次数据

    def get_data(self):
        return self.data
