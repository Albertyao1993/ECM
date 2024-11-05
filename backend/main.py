import signal
import sys
from flask import Flask, jsonify, request
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
import queue
from Agents.led_agent import LEDAgent
import asyncio
import uuid
import logging
import traceback
from Models.heating_prediction import HeatingPrediction

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}},supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*")

data_queue = Queue()
stop_event = Event()
lock = Lock()

executor = ThreadPoolExecutor(max_workers=3)

# Initialize the database
db = Database(uri="mongodb://localhost:27017/", db_name="sensor_data", collection_name="readings")
dth111 = DTH111(data_queue=data_queue, lock=lock, db=db)
open_weather = OpenWeather('fa3005c77c9d4631ef729307d175661f', 'Darmstadt')
video_detection = VideoDetection(model_path='yolo/weights/yolov8n.pt')
video_stream = VideoStream(socketio, video_detection, data_queue, stop_event, lock)

led_agent = LEDAgent()

# Initialize HeatingPrediction
heating_predictor = HeatingPrediction()

def load_sensor_data():
    # Sensor data thread
    print("Starting sensor data thread")
    while not stop_event.is_set():
        dth111.read_sensor_data()

def database_thread():
    print("Starting database thread")
    while not stop_event.is_set():
        try:
            time.sleep(60)
            data_points = []
            try:
                while True:
                    data_point = data_queue.get_nowait()
                    if isinstance(data_point, dict):
                        # Remove fields not defined in SensorData
                        data_point = {k: v for k, v in data_point.items() if k in SensorData.__annotations__}
                        data_points.append(SensorData(**data_point))
                    elif isinstance(data_point, SensorData):
                        data_points.append(data_point)
                    else:
                        print(f"Unexpected data type in queue: {type(data_point)}")
            except queue.Empty:
                pass

            if data_points:
                print(f"Processing {len(data_points)} data points")
                avg_temperature = sum(dp.temperature for dp in data_points) / len(data_points)
                avg_humidity = sum(dp.humidity for dp in data_points) / len(data_points)
                avg_light = sum(dp.light for dp in data_points) / len(data_points)
                timestamp = datetime.now()

                if not lock.acquire(timeout=5):
                    print("Unable to acquire lock, skipping this data processing")
                    continue

                try:
                    dth111.control_led(avg_light)
                finally:
                    lock.release()

                avg_data_point = SensorData(
                    timestamp=timestamp,
                    temperature=avg_temperature,
                    humidity=avg_humidity,
                    light=avg_light,
                    light_status=dth111.led_status,
                    ac_status=dth111.ac_status,
                    sound_state=data_points[-1].sound_state,
                    person_count=data_points[-1].person_count
                )

                weather_data = open_weather.get_weather_data()
                avg_data_point.ow_temperature = weather_data['ow_temperature']
                avg_data_point.ow_humidity = weather_data['ow_humidity']
                avg_data_point.ow_weather_desc = weather_data['ow_weather_desc']
                avg_data_point.ow_dewpoint = weather_data['ow_dewpoint']
                avg_data_point.ow_wind_speed = weather_data['ow_wind_speed']
                avg_data_point.ow_wind_direction = weather_data['ow_wind_direction']
                avg_data_point.ow_precipitation = weather_data['ow_precipitation']
                avg_data_point.ow_sun_duration = weather_data['ow_sun_duration']

                print(f"Inserting data into database: {avg_data_point.to_dict()}")
                db.create(avg_data_point.to_dict())
                print("Data inserted successfully")
            else:
                print("No data points to process")
        except Exception as e:
            print(f"Error in database thread: {e}")
            import traceback
            traceback.print_exc()

def video_frames_thread():
    # Video stream processing thread
    print("Starting video frames thread")
    while not stop_event.is_set():
        try:
            video_stream.send_video_frames()
        except Exception as e:
            print(f"Error in video frames thread: {e}")
            break

# Start YOLO detection
video_detection.start_detection()

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
        data = dth111.latest_data
        print(f"Realtime data: {data}")
        if data:
            return jsonify({
                'temperature': data.temperature,
                'humidity': data.humidity,
                'light': data.light,
                'timestamp': data.timestamp.isoformat(),
                'light_status': data.light_status,
                'ac_status': data.ac_status,
                'sound_state': data.sound_state,
                'person_count': data.person_count,
                'ow_temperature': data.ow_temperature,
                'ow_humidity': data.ow_humidity,
                'ow_weather_desc': data.ow_weather_desc,
                'ow_dewpoint': data.ow_dewpoint,
                'ow_wind_speed': data.ow_wind_speed,
                'ow_wind_direction': data.ow_wind_direction,
                'ow_precipitation': data.ow_precipitation,
                'ow_sun_duration': data.ow_sun_duration
            })
        else:
            return jsonify({'error': 'No data available'}), 404
    except Exception as e:
        print(f"Error in get_realtime_data: {e}")
        return jsonify({'error': str(e)}), 500

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

@app.route('/data/led_stats', methods=['GET'])
def get_led_stats():
    try:
        led_stats = dth111.get_led_usage_stats()
        return jsonify(led_stats)
    except Exception as e:
        logging.error(f"Error in get_led_stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/data/led_history', methods=['GET'])
def get_led_history():
    history = db.get_led_status_history()
    print(f"LED history: {[status.to_dict() for status in history]}")  # Add this log
    return jsonify([status.to_dict() for status in history])

@app.route('/data/led_analysis', methods=['GET'])
def get_led_analysis():
    task_id = request.args.get('task_id')
    if task_id:
        # 检查任务是否完成
        if task_id in analysis_results:
            result = analysis_results.pop(task_id)
            return jsonify(result)
        else:
            return jsonify({'status': 'processing'}), 202
    else:
        # 开始新的分析任务
        task_id = str(uuid.uuid4())
        executor.submit(perform_led_analysis, task_id)
        return jsonify({'task_id': task_id}), 202

analysis_results = {}

def perform_led_analysis(task_id):
    try:
        latest_data = dth111.get_latest_data()
        if not latest_data:
            raise ValueError("无法获取最新数据")
        light_value = latest_data.light
        led_stats = dth111.get_led_usage_stats()
        if not led_stats:
            raise ValueError("无法获取LED使用统计")
        duration = led_stats['total_on_time'] / 3600  # 转换为小时

        logging.info(f"Performing LED analysis: light_value={light_value}, duration={duration}")
        analysis = led_agent.analyze_and_suggest(light_value, duration)
        logging.info(f"LED analysis result: {analysis}")
        
        # 确保所有必要的键都存在
        required_keys = ['led_action', 'energy_info', 'analysis', 'suggestion']
        for key in required_keys:
            if key not in analysis:
                analysis[key] = "信息不可用"

        analysis_results[task_id] = analysis
    except Exception as e:
        logging.error(f"Error in perform_led_analysis: {str(e)}")
        logging.error(traceback.format_exc())
        analysis_results[task_id] = {
            'led_action': led_agent.control_led(light_value) if 'light_value' in locals() else "无法确定",
            'energy_info': led_agent.calculate_energy(duration) if 'duration' in locals() else "无法计算",
            'analysis': "由于技术问题，无法生成完整分析。",
            'suggestion': "请稍后再试。"
        }

@app.route('/data/energy_stats', methods=['GET'])
def get_energy_stats():
    stats = db.get_energy_stats()
    return jsonify(stats)

@app.route('/data/weather', methods=['GET'])
def get_weather_data():
    try:
        weather_data = open_weather.get_weather_data()
        return jsonify(weather_data)
    except Exception as e:
        logging.error(f"Error getting weather data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/data/heating-prediction', methods=['GET'])
def get_heating_prediction():
    try:
        # 获取当前预测
        prediction_result = heating_predictor.predict()
        if not prediction_result:
            return jsonify({'error': 'Unable to generate prediction'}), 500

        # 计算估算成本 (假设每千瓦时0.3欧元)
        COST_PER_KWH = 0.3
        estimated_usage = prediction_result['prediction']
        estimated_cost = estimated_usage * COST_PER_KWH

        # 根据预测值生成节能建议
        tips = []
        if estimated_usage > 20:  # 高能耗
            tips = [
                "Consider lowering room temperature by 1-2 degrees, each degree reduction saves about 6% energy",
                "Check if doors and windows are properly sealed to avoid heat loss",
                "Turn off heating in unused rooms"
            ]
        elif estimated_usage > 10:  # 中等能耗
            tips = [
                "Use timer to turn on heating only when needed",
                "Ensure radiators are not blocked by furniture",
                "Consider using smart thermostats to optimize heating"
            ]
        else:  # 低能耗
            tips = [
                "Current energy consumption is good",
                "Maintain current usage habits",
                "Consider scheduling regular maintenance"
            ]

        # 构建响应数据
        response_data = {
            'prediction': {
                'estimated_usage': round(estimated_usage, 2),
                'estimated_cost': round(estimated_cost, 2),
                'timestamp': prediction_result['timestamp'],
            },
            'tips': tips,
            'features': prediction_result['features_used']
        }

        return jsonify(response_data)

    except Exception as e:
        print(f"Error getting heating prediction: {str(e)}")
        return jsonify({'error': str(e)}), 500

def signal_handler(sig, frame):
    print('Terminating...')
    stop_event.set()
    video_detection.stop_detection()
    if "executor" in globals():
        executor.shutdown(wait=True)
    dth111.close()
    heating_predictor.close()  # 关闭预测器连接
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def initialize_serial():
    max_attempts = 5
    for attempt in range(max_attempts):
        if dth111.init_serial():
            print("Serial initialization successful")
            return True
        print(f"Serial initialization failed, attempt {attempt + 1}/{max_attempts}")
        time.sleep(2)
    return False

if __name__ == '__main__':
    try:
        if not initialize_serial():
            print("Unable to initialize serial, program exiting")
            sys.exit(1)

        video_detection.start_detection()
        executor.submit(load_sensor_data)
        executor.submit(database_thread)
        # executor.submit(video_frames_thread)

        socketio.run(app, debug=True, host='0.0.0.0', port=5000,use_reloader=False)
    except Exception as e:
        print(f"Error occurred during program execution: {e}")
    finally:
        stop_event.set()
        dth111.close()
        if "executor" in globals():
            executor.shutdown(wait=True)
        video_detection.stop_detection()
        logging.info("Program execution completed")