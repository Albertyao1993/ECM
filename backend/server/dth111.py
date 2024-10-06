# DHT111. py load the data from the sensor and send it to the client.

import threading
import time
from datetime import datetime, timezone, timedelta
import platform
import serial
from threading import Lock
# from Database.sensor_data import SensorData
from Database.sensor_data import SensorData

class DTH111:
    def __init__(self, data_queue, lock):
        self.data_queue = data_queue
        self.lock = lock
        self.latest_data = None
        self.ser = None
        self.led_status = "OFF"
        self.ac_status = "OFF"
        self.led_on_time = None
        self.led_usage_times = []
        self.init_serial()

    def detect_os(self):
        os_type = platform.system()
        if os_type == "Windows":
            return "Windows"
        elif os_type == "Linux":
            return "Linux"
        else:
            raise Exception(f"不支持的操作系统: {os_type}")

    def init_serial(self):
        with self.lock:
            if self.ser and self.ser.is_open:
                print("串口已经打开，无需重新初始化")
                return True

            if self.ser:
                self.ser.close()
                self.ser = None

            os_type = self.detect_os()
            if os_type == "Windows":
                port = 'COM3'
            elif os_type == "Linux":
                port = '/dev/ttyACM0'
            baud_rate = 9600

            try:
                self.ser = serial.Serial(port, baud_rate, timeout=1)
                print(f"成功连接到端口: {port}, 波特率: {baud_rate}")
                return True
            except serial.SerialException as e:
                print(f"尝试连接到 {port} 失败: {e}")
                if "Access is denied" in str(e):
                    print("这可能是权限问题。请确保您有权限访问该串口。")
                elif "Port is already open" in str(e):
                    print("该串口已被其他程序占用。请关闭其他可能使用该串口的程序。")
                elif "No such file or directory" in str(e):
                    print("找不到指定的串口。请确保设备已正确连接。")
                return False

    def read_sensor_data(self):
        while True:
            if not self.ser or not self.ser.is_open:
                print("串口未连接，尝试重新初始化...")
                if not self.init_serial():
                    print("串口初始化失败，等待 5 秒后重试...")
                    time.sleep(5)
                    continue

            try:
                with self.lock:
                    line = self.ser.readline().decode('utf-8').strip(",")
                if line:
                    parts = line.split(',')
                    if len(parts) != 5:
                        print(f"无效的数据格式: {line}")
                        continue

                    temperature, humidity, light, sound_state, led_state = parts

                    timestamp = datetime.now(timezone.utc).astimezone()

                    new_data_point = SensorData(
                        timestamp=timestamp,
                        temperature=float(temperature),
                        humidity=float(humidity),
                        light=float(light),
                        sound_state=int(sound_state),
                        light_status=self.led_status
                    )

                    with self.lock:
                        self.data_queue.put(new_data_point)
                        self.latest_data = new_data_point.to_dict()
                    
                    print(f"新数据点: {new_data_point.to_dict()}")

                    # 控制 LED
                    self.control_led(float(light))
            except serial.SerialException as e:
                print(f"串口通信错误: {e}")
                self.ser = None
            except Exception as e:
                print(f"读取传感器数据时出错: {e}")

            time.sleep(2)

    def get_latest_data(self):
        if self.latest_data is None:
            # 如果没有最新数据，返回一个默认值
            return {
                "timestamp": datetime.now(timezone.utc).astimezone().isoformat(),
                "temperature": None,
                "humidity": None,
                "light": None,
                "sound_state": None,
                "light_status": self.led_status,
                "ac_status": self.ac_status
            }
        return self.latest_data

    def send_command(self, command):
        max_attempts = 3
        for attempt in range(max_attempts):
            if self.ser and self.ser.is_open:
                try:
                    with self.lock:
                        print(f"[{threading.current_thread().name}] 获得锁，准备发送命令")
                        self.ser.write(f"{command}\n".encode())
                    print(f"[{threading.current_thread().name}] 命令已发送: {command}")
                    return True
                except serial.SerialException as e:
                    print(f"发送命令时出错 (尝试 {attempt + 1}/{max_attempts}): {e}")
                    self.ser = None  # 标记串口为未连接状态
            else:
                print(f"串口未连接，尝试重新初始化 (尝试 {attempt + 1}/{max_attempts})...")
                if self.init_serial():
                    continue  # 如果成功初始化，尝试再次发送命令
            
            time.sleep(1)  # 在重试之前等待一秒
        
        print(f"无法发送命令 '{command}'，达到最大尝试次数")
        return False

    def control_led(self, light_value):
        if light_value < 100 and self.led_status == "OFF":
            self.send_command("LED_ON")
            self.led_status = "ON"
            self.led_on_time = datetime.now()
        elif light_value >= 100 and self.led_status == "ON":
            self.send_command("LED_OFF")
            self.led_status = "OFF"
            if self.led_on_time:
                usage_time = datetime.now() - self.led_on_time
                self.led_usage_times.append(usage_time)
                self.led_on_time = None

    def get_led_usage_stats(self):
        total_usage = sum(self.led_usage_times, timedelta())
        avg_usage = total_usage / len(self.led_usage_times) if self.led_usage_times else timedelta()
        return {
            "total_usage": str(total_usage),
            "average_usage": str(avg_usage),
            "usage_count": len(self.led_usage_times)
        }

    def close(self):
        with self.lock:
            if self.ser and self.ser.is_open:
                self.ser.close()
                print("串口已关闭")
    def __del__(self):
        self.close()