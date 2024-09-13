import sys
import os
from flask import Flask,jsonify
from flask_socketio import SocketIO
# 将项目根目录添加到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from server.dth111 import DTH111




app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # 启用 CORS 允许前端访问


@app.route('/data', methods=['GET'])
def get_data():
    # 返回当前存储的所有数据
    return jsonify(dth111.get_data())


dth111 = DTH111(socketio=SocketIO())



if __name__ == '__main__':
    socketio.run(app, debug=True,host='127.0.0.1', port=5000,use_reloader=False,log_output=True)