# YOLO/video_stream.py
import time
import base64
import cv2
from flask_socketio import SocketIO
from yolo.video_detection import VideoDetection
from queue import Queue
from threading import Event

def send_video_frames(socketio: SocketIO, video_detection: VideoDetection, data_queue: Queue, stop_event: Event):
    cap = cv2.VideoCapture(0)  # 0 is the default camera
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    while video_detection.running and cap.isOpened() and not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame from video stream.")
            break

        # Resize the frame to reduce size
        frame = cv2.resize(frame, (640, 480))

        # Perform detection
        frame, person_count = video_detection.detect_frame(frame)

        # Encode the frame in JPEG format with lower quality
        ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
        if not ret:
            print("Error: Could not encode frame.")
            continue

        frame = base64.b64encode(buffer).decode('utf-8')

        # Send the frame and person count via WebSocket
        socketio.emit('video_frame', {'frame': frame, 'person_count': person_count})

        # 将人数数据发送到队列中
        if not data_queue.empty():
            latest_data_point = data_queue.get()
            latest_data_point.person_count = person_count
            data_queue.put(latest_data_point)

    cap.release()
    cv2.destroyAllWindows()
