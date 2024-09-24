# DHT111. py load the data from the sensor and send it to the client.

import time
from datetime import datetime, timezone
from flask_socketio import SocketIO
import platform
import serial
from threading import Lock

from Database.sensor_data import SensorData
from queue import Queue

class DTH111:
    def __init__(self, socketio: SocketIO, data_queue: Queue, lock: Lock):
        self.socketio = socketio
        # self.data = []
        self.data_queue = data_queue
        self.lock = lock

    def detect_os(self):
        os_type = platform.system()
        if os_type == "Windows":
            return "Windows"
        elif os_type == "Linux":
            return "Linux"
        else:
            raise Exception(f"Unsupported OS: {os_type}")
        
    def init_serial(self):
        os_type = self.detect_os()
        if os_type == "Windows":
            port = 'COM3'
        elif os_type == "Linux":
            port = '/dev/ttyACM0'
        baud_rate = 9600

        try:
            serial_port = serial.Serial(port, baud_rate, timeout=1) 
            time.sleep(2)
            print(f"Connected to port: {port}, baud_rate: {baud_rate}")
            return serial_port
        except serial.SerialException as e:
            print(f"Serial connection error: {e}")
            return None

    def read_sensor_data(self):
        ser = self.init_serial()
        try:
            while True:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    # print(f"Received data: {line}")
                    temperature, humidity,light = line.split(',')

                    # 格式化时间戳
                    timestamp = datetime.now(timezone.utc).astimezone() 

                    new_data_point = SensorData(
                        timestamp=timestamp,
                        temperature=float(temperature),
                        humidity=float(humidity),
                        light=float(light)
                    )
                    # self.data.append(new_data_point)
                    
                    # 只保留最新的20个数据点
                    # if len(self.data) > 20:
                    #     self.data.pop(0)
                    
                    # 将数据发送到队列中
                    with self.lock:
                        self.data_queue.put(new_data_point)
                    
                    # # 通过 WebSocket 发送数据
                    # self.socketio.emit('sensor_data', [dp.to_dict() for dp in self.data])
                
                # 每2秒读取一次数据
                time.sleep(60)
        except Exception as e:
            print(f"Error reading sensor data: {e}")
        finally:
            if ser:
                ser.close()

    def get_data(self):
        return self.data