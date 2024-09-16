# DHT111. py load the data from the sensor and send it to the client.

import time
from datetime import datetime
from flask_socketio import SocketIO
import platform
import serial

from Database.sensor_data import SensorData
from queue import Queue

class DTH111:
    def __init__(self, socketio: SocketIO, data_queue: Queue):
        self.socketio = socketio
        self.data = []
        self.data_queue = data_queue

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
                    print(f"Received data: {line}")
                    temperature, humidity = line.split(',')
                    # temperature = line
                    # new_data_point = {
                    #     'timestamp': datetime.now().isoformat(),
                    #     'temperature': float(temperature),
                    #     'humidity': float(humidity)
                    #     # 'humidity': 50.0
                    # }
                    new_data_point = SensorData(
                        timestamp=datetime.now().isoformat(),
                        temperature=float(temperature),
                        humidity=float(humidity)
                    )
                    self.data.append(new_data_point)
                    
                    # 只保留最新的20个数据点
                    if len(self.data) > 20:
                        self.data.pop(0)
                    
                    # 向所有连接的客户端发送数据
                    self.socketio.emit('sensor_data', new_data_point.to_dict())
                    print(f"Sent data: {new_data_point.to_dict()}")

                    self.data_queue.put(new_data_point)
        except KeyboardInterrupt:
            print("Program terminated")
        finally:
            if 'ser' in locals() and ser.is_open:
                ser.close()
                print("Serial port closed")
            

    def get_data(self):
        return self.data