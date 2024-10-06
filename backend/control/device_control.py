import serial
from datetime import datetime, timedelta
import platform

class DeviceControl:
    def __init__(self):
        self.ser = self.init_serial()
        self.led_status = "OFF"
        self.ac_status = "OFF"
        self.led_on_time = None
        self.led_usage_times = []

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
            print(f"Connected to port: {port}, baud_rate: {baud_rate}")
            return serial_port
        except serial.SerialException as e:
            print(f"Serial connection error: {e}")
            return None

    def send_command(self, command):
        if self.ser:
            self.ser.write(f"{command}\n".encode())
        else:
            print("Serial connection not established. Cannot send command.")

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
        if self.ser:
            self.ser.close()