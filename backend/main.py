# app.py
from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from threading import Thread
from queue import Queue
from Database.db_operation import Database
from server.dth111 import DTH111
import time

app = Flask(__name__)
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*")  # 启用 CORS 允许前端访问

data_queue = Queue()

# 初始化数据库
db = Database(uri="mongodb://localhost:27017/", db_name="sensor_data", collection_name="readings")
dth111 = DTH111(socketio=socketio, data_queue=data_queue)

def websocket_thread():
    # 创建传感器模拟器实例
    dth111.read_sensor_data()

def database_thread():
    while True:
        try:
            # 每隔1分钟插入当前时刻的数据
            time.sleep(60)
            if not data_queue.empty():
                latest_data_point = data_queue.get()
                db.create(latest_data_point.to_dict())
                print(f"Stored data: {latest_data_point.to_dict()}")
        except Exception as e:
            print(f"Error in database thread: {e}")

# 启动 WebSocket 线程
ws_thread = Thread(target=websocket_thread)
ws_thread.daemon = True
ws_thread.start()

# 启动数据库线程
db_thread = Thread(target=database_thread)
db_thread.daemon = True
db_thread.start()

@app.route('/data', methods=['GET'])
def get_data():
    # 返回当前存储的所有数据
    # return jsonify(sensor_simulator.get_data())
    return jsonify(dth111.get_data())

if __name__ == '__main__':
    socketio.run(app, debug=True, host='127.0.0.1', port=5000, use_reloader=False, log_output=True)
