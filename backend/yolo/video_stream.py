
import time
import base64
import cv2
from flask_socketio import SocketIO
from yolo.video_detection import VideoDetection
from queue import Queue
from threading import Event

def send_video_frames(socketio: SocketIO, video_detection: VideoDetection, data_queue: Queue, stop_event: Event):
    # cap = cv2.VideoCapture(0)  # 0 is the default camera
    cap = cv2.VideoCapture('/dev/video0')
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return
    
    frame_rate = 10
    prev = 0

    while video_detection.running and cap.isOpened() and not stop_event.is_set():
        time_elapsed = time.time() - prev
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame from video stream.")
            break
        if time_elapsed > 1.0 / frame_rate:
            prev = time.time()
            # Resize the frame to reduce size
            frame = cv2.resize(frame, (640, 480))

            # Perform detection and get person count along with bounding boxes
            frame, person_count, boxes = video_detection.detect_frame_with_boxes(frame)

            # Encode the frame in JPEG format with lower quality
            ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
            if not ret:
                print("Error: Could not encode frame.")
                continue

            frame_encoded = base64.b64encode(buffer).decode('utf-8')

            # Send the frame, person count, and bounding boxes via WebSocket
            socketio.emit('video_frame', {
                'frame': frame_encoded,
                'person_count': person_count,
                'boxes': boxes  # Bounding boxes information
            })

            # 将人数数据发送到队列中
            if not data_queue.empty():
                latest_data_point = data_queue.get()
                latest_data_point.person_count = person_count
                data_queue.put(latest_data_point)

    cap.release()
    cv2.destroyAllWindows()
