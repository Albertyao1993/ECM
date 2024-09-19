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
import time
import datetime

app = Flask(__name__)
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*")

data_queue = Queue()
stop_event = Event()  # 用于指示线程何时应该停止
lock = Lock()  # 用于确保线程安全

# Initialize the database
db = Database(uri="mongodb://localhost:27017/", db_name="sensor_data", collection_name="readings")
dth111 = DTH111(socketio=socketio, data_queue=data_queue, lock=lock)

model_path = os.path.normpath('YOLO/weights/yolov8n.pt')
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
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    if start_time and end_time:
        start_time = datetime.datetime.fromisoformat(start_time)
        end_time = datetime.datetime.fromisoformat(end_time)
        data = db.read_by_time_range(start_time, end_time)
    else:
        data = db.read_all()
    return jsonify(data)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# WebRTC signaling
@socketio.on('offer')
def handle_offer(data):
    socketio.emit('offer', data, broadcast=True)

@socketio.on('answer')
def handle_answer(data):
    socketio.emit('answer', data, broadcast=True)

@socketio.on('ice-candidate')
def handle_ice_candidate(data):
    socketio.emit('ice-candidate', data, broadcast=True)

# Use ThreadPoolExecutor to manage threads
executor = ThreadPoolExecutor(max_workers=4)
executor.submit(websocket_thread)
executor.submit(database_thread)
executor.submit(video_frames_thread)

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
