from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_cors import CORS
import serial
import time
import platform
import threading

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")

def detect_os():
    os_type = platform.system()
    
    if os_type == "Windows":
        return "Windows"
    elif os_type == "Linux":
        return "Linux"
    else:
        raise Exception(f"不支持的系统: {os_type}")
    
def init_serial():
    os_type = detect_os()
    if os_type == "Windows":
        port = 'COM3'
    elif os_type == "Linux":
        port = '/dev/ttyACM0'
    baud_rate = 9600

    try:
        serial_port = serial.Serial(port, baud_rate, timeout=1) 
        time.sleep(2)
        print(f"port connected: {port},baud_rate: {baud_rate}")
        return serial_port
    except serial.SerialException as e:
        print(f"Serial connection error: {e}")
        return None
def read_from_serial(ser):
    try:
        while True:
            line = ser.readline().decode('utf-8').strip()
            if line:
                print(f"Emitting temperature update: {line}")
                socketio.emit('temperature_update',{'temperature': line} )
                print('Temperature update emitted')
    except KeyboardInterrupt:
      print('Program terminated')
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print('Serial port closed')
        print('The try except is finished')


@socketio.on('connect')
def handle_connect():
    
    print('Client connected')

# @socketio.on('disconnect')
# def handle_disconnect():
#     print('Client disconnected')


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    ser = init_serial()
    if ser:
        ser_threading = threading.Thread(target=read_from_serial, args=(ser,))
        ser_threading.daemon = True
        ser_threading.start()
    socketio.run(app, host='localhost', port=5000, debug=True,use_reloader=False,log_output=True)