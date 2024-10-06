import signal
import sys
from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Event, Lock
from Database.db_operation import Database
from server.dth111 import DTH111
from yolo.video_detection import VideoDetection
from yolo.video_stream import VideoStream
from Database.sensor_data import SensorData
from open_weather.weather import OpenWeather
import time
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}},supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*")


data_queue = Queue()
stop_event = Event()
lock = Lock()

executor = ThreadPoolExecutor(max_workers=3)

# Initialize the database
db = Database(uri="mongodb://localhost:27017/", db_name="sensor_data", collection_name="readings")
dth111 = DTH111(data_queue=data_queue, lock=lock)
open_weather = OpenWeather('fa3005c77c9d4631ef729307d175661f', 'Darmstadt')
video_detection = VideoDetection(model_path='yolo/weights/yolov8n.pt')
video_stream = VideoStream(socketio, video_detection, data_queue, stop_event, lock)

def load_sensor_data():
    # 传感器数据线程
    print("Starting sensor data thread")
    while not stop_event.is_set():
        dth111.read_sensor_data()

def database_thread():
    print("Starting database thread")
    while not stop_event.is_set():
        try:
            time.sleep(60)
            if not data_queue.empty():
                data_points = []
                while not data_queue.empty():
                    data_points.append(data_queue.get())

                if data_points:
                    avg_temperature = sum(dp.temperature for dp in data_points) / len(data_points)
                    avg_humidity = sum(dp.humidity for dp in data_points) / len(data_points)
                    avg_light = sum(dp.light for dp in data_points) / len(data_points)
                    timestamp = datetime.now()

                    with lock:
                        dth111.control_led(avg_light)

                    avg_data_point = SensorData(
                        timestamp=timestamp,
                        temperature=avg_temperature,
                        humidity=avg_humidity,
                        light=avg_light,
                        light_status=dth111.led_status,
                        ac_status=dth111.ac_status
                    )

                    weather_data = open_weather.get_weather_data()
                    avg_data_point.ow_temperature = weather_data['ow_temperature']
                    avg_data_point.ow_humidity = weather_data['ow_humidity']
                    avg_data_point.ow_weather_desc = weather_data['ow_weather_desc']

                    print(f"Inserting data into database: {avg_data_point.to_dict()}")
                    db.create(avg_data_point.to_dict())
                    print("Data inserted successfully")
        except Exception as e:
            print(f"Error in database thread: {e}")

def video_frames_thread():
    # 视频流处理线程
    print("Starting video frames thread")
    while not stop_event.is_set():
        try:
            video_stream.send_video_frames()
        except Exception as e:
            print(f"Error in video frames thread: {e}")
            break

# 开启YOLO检测
video_detection.start_detection()

# @app.route('/data', methods=['GET'])
# def get_data():
#     # 返回传感器数据
#     return jsonify(dth111.get_data())

@app.route('/data/ac_state', methods=['GET'])
def get_current_data():
    try:
        latest_data_point = db.read_latest()
        if latest_data_point:
            return jsonify({
                'ac_state': latest_data_point.get('ac_state', False),
                'window_state': latest_data_point.get('window_state', False)
            })
        else:
            return jsonify({'error': 'No data available'}), 404
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/data/realtime', methods=['GET'])
def get_realtime_data():
    try:
        data = dth111.get_latest_data()
        print(f"Realtime data: {data}")
        if data['temperature'] is None:
            return jsonify({'error': 'No sensor data available'}), 404
        return jsonify(data)
    except Exception as e:
        print(f"Error in get_realtime_data: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/data/history', methods=['GET'])
def get_data_history():
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=30)
    
    print(f"Querying data from {start_time} to {end_time}")
    data = db.read_by_time_range(start_time, end_time)
    return jsonify(data)

@app.route('/data/led_status', methods=['GET'])
def get_led_status():
    return jsonify({'led_status': dth111.led_status})

def signal_handler(sig, frame):
    print('Terminating...')
    stop_event.set()
    video_detection.stop_detection()
    if "executor" in globals():
        executor.shutdown(wait=True)
    dth111.close()
    sys.exit(0)



signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def initialize_serial():
    max_attempts = 5
    for attempt in range(max_attempts):
        if dth111.init_serial():
            print("串口初始化成功")
            return True
        print(f"串口初始化失败，尝试 {attempt + 1}/{max_attempts}")
        time.sleep(2)
    return False


if __name__ == '__main__':
    try:
        if not initialize_serial():
            print("无法初始化串口，程序退出")
            sys.exit(1)

        video_detection.start_detection()
        executor.submit(load_sensor_data)
        executor.submit(database_thread)
        executor.submit(video_frames_thread)

        socketio.run(app, debug=True, host='0.0.0.0', port=5000,use_reloader=False)
    except Exception as e:
        print(f"程序运行时发生错误: {e}")
    finally:
        stop_event.set()
        dth111.close()
        if "executor" in globals():
            executor.shutdown(wait=True)


