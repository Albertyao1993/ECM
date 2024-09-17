# app.py
import os
import time
import datetime
from threading import Thread
from queue import Queue
from flask import Flask, jsonify, request, Response
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor

from Database.db_operation import Database
from server.dth111 import DTH111
from yolo.video_detection import VideoDetection
from yolo.video_stream import send_video_frames
from Database.sensor_data import SensorData

app = Flask(__name__)
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable CORS for frontend access

data_queue = Queue()

# Initialize the database
db = Database(uri="mongodb://localhost:27017/", db_name="sensor_data", collection_name="readings")
dth111 = DTH111(socketio=socketio, data_queue=data_queue)

model_path = os.path.normpath('YOLO/weights/yolov8n.pt')
video_detection = VideoDetection(model_path=model_path)  # Initialize the YOLOv8 model with platform-independent path

def websocket_thread():
    # Start reading sensor data
    dth111.read_sensor_data()

def database_thread():
    while True:
        try:
            # Insert the current data into the database every minute
            time.sleep(60)
            if not data_queue.empty():
                latest_data_point = data_queue.get()
                db.create(latest_data_point.to_dict())
                print(f"Stored data: {latest_data_point.to_dict()}")
        except Exception as e:
            print(f"Error in database thread: {e}")

# Start the YOLOv8 detection thread
video_detection.start_detection()

@app.route('/data', methods=['GET'])
def get_data():
    # Return the current stored data
    return jsonify(dth111.get_data())

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
executor = ThreadPoolExecutor(max_workers=3)
executor.submit(websocket_thread)
executor.submit(database_thread)
executor.submit(send_video_frames, socketio, video_detection, data_queue)

if __name__ == '__main__':
    try:
        socketio.run(app, debug=True, host='127.0.0.1', port=5000, use_reloader=False, log_output=True)
    finally:
        video_detection.stop_detection()
        executor.shutdown(wait=True)
