import serial
import time
import platform

def detect_os():
    os_type = platform.system()
    
    if os_type == "Windows":
        return "Windows"
    elif os_type == "Linux":
        return "Linux"
    else:
        raise Exception(f"不支持的系统: {os_type}")

# 检测系统平台并选择串口
os_type = detect_os()

if os_type == "Windows":
    port = 'COM3'  # Windows 串口号
elif os_type == "Linux":
    port = '/dev/ttyACM0'  # Linux 串口设备

# 设置波特率
baud_rate = 9600

# 初始化串口连接
try:
    ser = serial.Serial(port, baud_rate, timeout=1)
    # 等待串口稳定
    time.sleep(2)
    
    print(f"连接到串口: {port}，波特率: {baud_rate}")
    
    while True:
        # 从串口读取一行数据
        line = ser.readline().decode('utf-8').strip()
        
        if line:
            print(line)  # 打印从 Arduino 读取到的数据
except serial.SerialException as e:
    print(f"串口连接错误: {e}")
except KeyboardInterrupt:
    print("程序终止")
finally:
    if 'ser' in locals() and ser.is_open:
        # 关闭串口
        ser.close()
        print("串口已关闭")
