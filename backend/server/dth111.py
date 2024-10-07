# DHT111. py load the data from the sensor and send it to the client.

import threading
import time
from datetime import datetime, timezone, timedelta
import platform
import serial
from threading import Lock
# from Database.sensor_data import SensorData
from Database.sensor_data import SensorData
from Database.led_status import LEDStatus

class DTH111:
    def __init__(self, data_queue, lock, db):
        self.data_queue = data_queue
        self.lock = threading.RLock()
        self.db = db
        self.db_lock = threading.RLock()  # 新增一个专门用于数据库操作的锁
        self.latest_data = None
        self.ser = None
        self.led_status = "OFF"
        self.ac_status = "OFF"
        self.led_on_time = None
        self.led_usage_times = []
        self.last_led_change_time = None
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
            try:
                if not self.ser or not self.ser.is_open:
                    print("串口未连接，尝试重新初始化...")
                    if not self.init_serial():
                        print("串口初始化失败，等待 5 秒后重试...")
                        time.sleep(5)
                        continue

                line = self.ser.readline().decode().strip(",")
                print(f"原始数据: {line}")

                data = self.parse_sensor_data(line)
                if data:
                    print(f"解析后的数据: {data}")
                    self.data_queue.put(data)
                    self.latest_data = data
                    self.led_status = data.light_status  # 使用点号访问属性
                    self.ac_status = data.ac_status  # 使用点号访问属性

                time.sleep(2)
            except serial.SerialException as e:
                print(f"串口读取错误: {e}")
                self.ser = None  # 标记串口为未连接状态
                time.sleep(5)  # 等待一段时间后重试
            except Exception as e:
                print(f"读取传感器数据时出错: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(2)

    def parse_sensor_data(self, line):
        try:
            # 数据格式为 "温度,湿度,光照,声音,LED状态"
            temp, hum, light, sound, led_state = map(float, line.split(','))
            return SensorData(
                temperature=temp,
                humidity=hum,
                light=light,
                sound_state=int(sound),
                timestamp=datetime.now(),
                light_status="ON" if int(led_state) == 1 else "OFF",
                ac_status=self.ac_status
            )
        except ValueError as e:
            print(f"数据解析错误: {e}")
            return None

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
        current_time = datetime.now()
        if not self.lock.acquire(timeout=5):
            print("无法获取锁，跳过LED控制")
            return

        try:
            if light_value < 100 and self.led_status == "OFF":
                if self.send_command("LED_ON"):
                    new_status = "ON"
                    self.led_status = new_status
                    self.led_on_time = current_time
                    print(f"LED 开启，当前光照值: {light_value}")
            elif light_value >= 100 and self.led_status == "ON":
                if self.send_command("LED_OFF"):
                    new_status = "OFF"
                    self.led_status = new_status
                    if self.led_on_time:
                        usage_time = current_time - self.led_on_time
                        self.led_usage_times.append(usage_time)
                        self.led_on_time = None
                    print(f"LED 关闭，当前光照值: {light_value}")
            else:
                print(f"LED 状态保持不变，当前状态: {self.led_status}，光照值: {light_value}")
                return  # 如果状态没有改变，直接返回，不记录状态变化
        finally:
            self.lock.release()
        
        self.record_led_status_change(self.led_status, current_time)

    def record_led_status_change(self, new_status, timestamp):
        if self.last_led_change_time:
            duration = (timestamp - self.last_led_change_time).total_seconds()
            led_status = LEDStatus(
                timestamp=self.last_led_change_time,
                status=self.led_status,
                duration=duration
            )
            if not self.db_lock.acquire(timeout=5):
                print("无法获取数据库锁，跳过LED状态记录")
                return
            try:
                self.db.create_led_status(led_status.to_dict())
                print(f"记录LED状态变化: {led_status.to_dict()}")
            finally:
                self.db_lock.release()
        self.last_led_change_time = timestamp

    def get_led_usage_stats(self):
        if not self.db_lock.acquire(timeout=5):
            print("无法获取数据库锁，无法获取LED使用统计")
            return None
        try:
            stats = self.db.get_led_stats()
            print(f"获取LED使用统计: {stats}")
            return stats
        finally:
            self.db_lock.release()

    def close(self):
        with self.lock:
            if self.ser and self.ser.is_open:
                self.ser.close()
                print("串口已关闭")
    def __del__(self):
        self.close()