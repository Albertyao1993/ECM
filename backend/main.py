import signal
import sys
import os
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Event, Lock
from Database.db_operation import Database
from server.dth111 import DTH111
from yolo.video_detection import VideoDetection
from yolo.video_stream import VideoStream  # Import the VideoStream class
from Database.sensor_data import SensorData
from open_weather.weather import OpenWeather
import time
# import datetime
from datetime import datetime, timezone
from dateutil import parser

app = Flask(__name__)
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*")

data_queue = Queue()
stop_event = Event()  # 用于指示线程何时应该停止
lock = Lock()  # 用于确保线程安全

# Initialize the database
db = Database(uri="mongodb://localhost:27017/", db_name="sensor_data", collection_name="readings")
dth111 = DTH111(socketio=socketio, data_queue=data_queue, lock=lock)

api_key = 'fa3005c77c9d4631ef729307d175661f'
city = 'Darmstadt'
open_weather = OpenWeather(api_key, city)

model_path = os.path.normpath('yolo/weights/yolov8n.pt')
video_detection = VideoDetection(model_path=model_path)

# Create an instance of VideoStream
video_stream = VideoStream(socketio, video_detection, data_queue, stop_event, lock)

def websocket_thread():
    # 传感器数据线程
    print("Starting sensor data thread")
    while not stop_event.is_set():
        dth111.read_sensor_data()
        time.sleep(0.5)

def database_thread():
    # 数据库处理线程
    print("Starting database thread")
    while not stop_event.is_set():
        try:
            time.sleep(60)  # 每60秒插入一次数据
            if not data_queue.empty():
                latest_data_point = data_queue.get()

                weather_data = open_weather.get_weather_data()
                latest_data_point.ow_temperature = weather_data['ow_temperature']
                latest_data_point.ow_humidity = weather_data['ow_humidity']
                latest_data_point.ow_weather_desc = weather_data['ow_weather_desc']

                print(f"Inserting data into database: {latest_data_point.to_dict()}")

                db.create(latest_data_point.to_dict())
                print(f"Stored data: {latest_data_point.to_dict()}")
        except Exception as e:
            print(f"Error in database thread: {e}")

def video_frames_thread():
    # 视频流处理线程
    print("Starting video frames thread")
    while not stop_event.is_set():
        try:
            print("Sending video frames")
            video_stream.send_video_frames()  # 调用 VideoStream 实例的方法
        except Exception as e:
            print(f"Error in video frames thread: {e}")
            break

# 开启YOLO检测
video_detection.start_detection()

@app.route('/data', methods=['GET'])
def get_data():
    # 返回传感器数据
    return jsonify(dth111.get_data())

@app.route('/data/history', methods=['GET'])
def get_data_history():
    start_time_str = request.args.get('start_time')
    end_time_str = request.args.get('end_time')

    if not start_time_str or not end_time_str:
        # 如果未提供时间范围，默认返回过去30分钟的数据
        end_time = datetime.now(timezone.utc)
        start_time = end_time - datetime.timedelta(minutes=30)
    else:
        # 解析时间字符串，并转换为 UTC 时区
        start_time = parser.isoparse(start_time_str).astimezone(timezone.utc)
        end_time = parser.isoparse(end_time_str).astimezone(timezone.utc)

    print(f"Received request for data between {start_time} and {end_time}")

    data = db.read_by_time_range(start_time, end_time)
    return jsonify(data)

@app.route('/data/all', methods=['GET'])
def get_all_data():
    data = db.read_all()
    return jsonify(data)


@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')



# Use ThreadPoolExecutor to manage threads
executor = ThreadPoolExecutor(max_workers=4)
executor.submit(websocket_thread)
executor.submit(database_thread)
# executor.submit(video_frames_thread)

def signal_handler(sig, frame):
    print('Terminating...')
    stop_event.set()  # 设置停止标志
    video_detection.stop_detection()
    executor.shutdown(wait=True)
    sys.exit(0)

# 捕获终止信号
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    try:
        socketio.run(app, debug=True, host='127.0.0.1', port=5000, use_reloader=False, log_output=True)
    finally:
        video_detection.stop_detection()
        executor.shutdown(wait=True)
