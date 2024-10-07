# DHT111.py load the data from the sensor and send it to the client.

import threading
import time
from datetime import datetime, timezone, timedelta
import platform
import serial
from threading import Lock
from Database.sensor_data import SensorData
from Database.led_status import LEDStatus

class DTH111:
    def __init__(self, data_queue, lock, db):
        self.data_queue = data_queue
        self.lock = threading.RLock()
        self.db = db
        self.db_lock = threading.RLock()  # Add a lock specifically for database operations
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
            raise Exception(f"Unsupported operating system: {os_type}")

    def init_serial(self):
        with self.lock:
            if self.ser and self.ser.is_open:
                print("Serial port is already open, no need to reinitialize")
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
                print(f"Successfully connected to port: {port}, baud rate: {baud_rate}")
                return True
            except serial.SerialException as e:
                print(f"Failed to connect to {port}: {e}")
                if "Access is denied" in str(e):
                    print("This might be a permission issue. Make sure you have the right to access the serial port.")
                elif "Port is already open" in str(e):
                    print("The port is already in use by another program. Please close other programs that might be using this port.")
                elif "No such file or directory" in str(e):
                    print("The specified port was not found. Make sure the device is properly connected.")
                return False

    def read_sensor_data(self):
        while True:
            try:
                if not self.ser or not self.ser.is_open:
                    print("Serial port not connected, attempting to reinitialize...")
                    if not self.init_serial():
                        print("Serial initialization failed, retrying in 5 seconds...")
                        time.sleep(5)
                        continue

                line = self.ser.readline().decode().strip(",")
                print(f"Raw data: {line}")

                data = self.parse_sensor_data(line)
                if data:
                    print(f"Parsed data: {data}")
                    self.data_queue.put(data)
                    self.latest_data = data
                    self.led_status = data.light_status
                    self.ac_status = data.ac_status

                time.sleep(2)
            except serial.SerialException as e:
                print(f"Serial read error: {e}")
                self.ser = None  # Mark serial as disconnected
                time.sleep(5)  # Wait before retrying
            except Exception as e:
                print(f"Error reading sensor data: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(2)

    def parse_sensor_data(self, line):
        try:
            # Data format: "temperature,humidity,light,sound,LED_state"
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
            print(f"Data parsing error: {e}")
            return None

    def get_latest_data(self):
        if self.latest_data is None:
            # If no latest data, return default values
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
                        print(f"[{threading.current_thread().name}] Acquired lock, preparing to send command")
                        self.ser.write(f"{command}\n".encode())
                    print(f"[{threading.current_thread().name}] Command sent: {command}")
                    return True
                except serial.SerialException as e:
                    print(f"Error sending command (attempt {attempt + 1}/{max_attempts}): {e}")
                    self.ser = None  # Mark serial as disconnected
            else:
                print(f"Serial not connected, attempting to reinitialize (attempt {attempt + 1}/{max_attempts})...")
                if self.init_serial():
                    continue  # If initialization successful, try sending command again
            
            time.sleep(1)  # Wait before retrying
        
        print(f"Unable to send command '{command}', maximum attempts reached")
        return False

    def control_led(self, light_value):
        current_time = datetime.now()
        if not self.lock.acquire(timeout=5):
            print("Unable to acquire lock, skipping LED control")
            return

        try:
            new_status = self.led_status  # Default to current status
            if light_value < 100 and self.led_status == "OFF":
                if self.send_command("LED_ON"):
                    new_status = "ON"
                    print(f"LED turned ON, current light value: {light_value}")
            elif light_value >= 100 and self.led_status == "ON":
                if self.send_command("LED_OFF"):
                    new_status = "OFF"
                    print(f"LED turned OFF, current light value: {light_value}")
            
            # Call record_led_status_change regardless of status change
            self.record_led_status_change(new_status, current_time)
            print(f"LED status update: {self.led_status} -> {new_status}")
        finally:
            self.lock.release()

    def record_led_status_change(self, new_status, timestamp):
        print(f"Recording LED status change: {self.led_status} -> {new_status}")
        if self.last_led_change_time:
            duration = (timestamp - self.last_led_change_time).total_seconds()
            led_status = LEDStatus(
                timestamp=self.last_led_change_time,
                status=self.led_status,
                duration=duration
            )
            if not self.db_lock.acquire(timeout=5):
                print("Unable to acquire database lock, skipping LED status recording")
                return
            try:
                result = self.db.create_led_status(led_status.to_dict())
                print(f"LED status record result: {result}")
                self.db.update_energy_consumption(led_status)
                print(f"Recorded LED status change and energy consumption: {led_status.to_dict()}")
            except Exception as e:
                print(f"Error recording LED status: {e}")
            finally:
                self.db_lock.release()
        else:
            print("This is the first LED status change, not recording duration")
        self.last_led_change_time = timestamp
        self.led_status = new_status

    def get_led_usage_stats(self):
        if not self.db_lock.acquire(timeout=5):
            print("Unable to acquire database lock, cannot get LED usage statistics")
            return None
        try:
            stats = self.db.get_led_stats()
            print(f"Retrieved LED usage statistics: {stats}")
            return stats
        finally:
            self.db_lock.release()

    def close(self):
        with self.lock:
            if self.ser and self.ser.is_open:
                self.ser.close()
                print("Serial port closed")
    def __del__(self):
        self.close()