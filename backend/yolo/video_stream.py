# YOLO/video_stream.py
import time
import base64
import cv2
from flask_socketio import SocketIO
from yolo.video_detection import VideoDetection
from queue import Queue

def send_video_frames(socketio: SocketIO, video_detection: VideoDetection, data_queue: Queue):
    cap = cv2.VideoCapture(0)  # 0 is the default camera

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    while video_detection.running and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Perform detection
        frame, person_count = video_detection.detect_frame(frame)

        # Encode the frame in JPEG format
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
        ret, buffer = cv2.imencode('.jpg', frame, encode_param)
        # frame = buffer.tobytes()
        frame = base64.b64encode(buffer).decode('utf-8')

        # Send the frame and person count via WebSocket
        socketio.emit('video_frame', {'frame': frame, 'person_count': person_count})
        if not data_queue.empty():
                    latest_data_point = data_queue.get()
                    latest_data_point.person_count = person_count
                    data_queue.put(latest_data_point)


        time.sleep(0.1)


    cap.release()
    cv2.destroyAllWindows()
