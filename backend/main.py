# app.py
from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from threading import Thread
from server.sensor_simulator import SensorSimulator

app = Flask(__name__)
CORS(app,origins="*")
socketio = SocketIO(app, cors_allowed_origins="*")  # 启用 CORS 允许前端访问

# 创建传感器模拟器实例
sensor_simulator = SensorSimulator(socketio)

# 启动后台线程生成数据
thread = Thread(target=sensor_simulator.generate_sensor_data)
thread.daemon = True
thread.start()

@app.route('/data', methods=['GET'])
def get_data():
    # 返回当前存储的所有数据
    return jsonify(sensor_simulator.get_data())

if __name__ == '__main__':
    socketio.run(app, debug=True,host='127.0.0.1', port=5000,use_reloader=False,log_output=True)
