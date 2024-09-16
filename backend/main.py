# app.py
import time
from threading import Thread
from queue import Queue
from flask import Flask, jsonify, request, Response
from flask_socketio import SocketIO
from flask_cors import CORS

from Database.db_operation import Database
from server.dth111 import DTH111
from YOLO.video_detection import VideoDetection

app = Flask(__name__)
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable CORS for frontend access

data_queue = Queue()

# Initialize the database
db = Database(uri="mongodb://localhost:27017/", db_name="sensor_data", collection_name="readings")
dth111 = DTH111(socketio=socketio, data_queue=data_queue)
video_detection = VideoDetection()

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

# Start the WebSocket thread
ws_thread = Thread(target=websocket_thread)
ws_thread.daemon = True
ws_thread.start()

# Start the database thread
db_thread = Thread(target=database_thread)
db_thread.daemon = True
db_thread.start()

# Start the YOLOv8 detection thread
video_detection.start_detection()

@app.route('/data', methods=['GET'])
def get_data():
    # Return the current stored data
    return jsonify(dth111.get_data())



if __name__ == '__main__':
    try:
        socketio.run(app, debug=True, host='127.0.0.1', port=5000, use_reloader=False, log_output=True)
    finally:
        video_detection.stop_detection()
