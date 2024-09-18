import os
import signal
import sys
import time
from threading import Event
from queue import Queue
from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor

# 导入数据库、传感器和YOLO模型相关的模块
from Database.db_operation import Database
from server.dth111 import DTH111
from yolo.video_detection import VideoDetection
from yolo.video_stream import send_video_frames
from Database.sensor_data import SensorData

# 初始化Flask应用
app = Flask(__name__)
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*")  # 启用CORS以允许前端访问

data_queue = Queue()
stop_event = Event()

# 初始化数据库和传感器
db = Database(uri="mongodb://localhost:27017/", db_name="sensor_data", collection_name="readings")
dth111 = DTH111(socketio=socketio, data_queue=data_queue)

# 初始化YOLOv8模型
model_path = os.path.normpath('yolo/weights/yolov8n.pt')
video_detection = VideoDetection(model_path=model_path)

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
            send_video_frames(socketio, video_detection, data_queue, stop_event)  # 处理视频帧和人数检测
        except Exception as e:
            print(f"Error in video frames thread: {e}")
            break

# 开启YOLO检测
video_detection.start_detection()

@app.route('/data', methods=['GET'])
def get_data():
    # 返回传感器数据
    return jsonify(dth111.get_data())

# WebSocket事件处理
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# 线程池管理
executor = ThreadPoolExecutor(max_workers=4)
executor.submit(websocket_thread)  # 启动传感器数据线程
executor.submit(database_thread)  # 启动数据库线程
executor.submit(video_frames_thread)  # 启动视频帧处理线程

# 信号处理，优雅停止所有线程
def signal_handler(sig, frame):
    print('Terminating...')
    stop_event.set()
    video_detection.stop_detection()
    executor.shutdown(wait=True)
    sys.exit(0)

# 捕获终止信号
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    try:
        # 启动Flask-SocketIO应用
        socketio.run(app, debug=True, host='127.0.0.1', port=5000, use_reloader=False, log_output=True)
    finally:
        # 优雅停止线程和YOLO检测
        video_detection.stop_detection()
        executor.shutdown(wait=True)
