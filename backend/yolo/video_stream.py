import time
import base64
import cv2
import os
from flask_socketio import SocketIO
from yolo.video_detection import VideoDetection
from queue import Queue
from threading import Event, Lock

class VideoStream:
    def __init__(self, socketio: SocketIO, video_detection: VideoDetection, data_queue: Queue, stop_event: Event, lock: Lock):
        self.socketio = socketio
        self.video_detection = video_detection
        self.data_queue = data_queue
        self.stop_event = stop_event
        self.lock = lock
        self.frame_rate = 10
        self.prev = 0

        # Detect OS and set camera source
        if os.name == 'nt':  # Windows
            self.camera_source = 0
        else:  # Linux
            self.camera_source = '/dev/video0'

    def send_video_frames(self):
        cap = cv2.VideoCapture(self.camera_source)
        if not cap.isOpened():
            print("Error: Could not open video stream.")
            return

        while self.video_detection.running and cap.isOpened() and not self.stop_event.is_set():
            time_elapsed = time.time() - self.prev
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame from video stream.")
                break
            if time_elapsed > 1.0 / self.frame_rate:
                self.prev = time.time()
                # Resize the frame to reduce size
                frame = cv2.resize(frame, (320, 240))

                # Perform detection and get person count along with bounding boxes
                frame, person_count, boxes = self.video_detection.detect_frame_with_boxes(frame)

                # Encode the frame in JPEG format with lower quality
                ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 10])
                if not ret:
                    print("Error: Could not encode frame.")
                    continue

                frame_encoded = base64.b64encode(buffer).decode('utf-8')

                # Send the frame, person count, and bounding boxes via WebSocket
                self.socketio.emit('video_frame', {
                    'frame': frame_encoded,
                    'person_count': person_count,
                    'boxes': boxes  # Bounding boxes information
                })

                # 将人数数据发送到队列中
                with self.lock:
                    if not self.data_queue.empty():
                        latest_data_point = self.data_queue.get()
                        latest_data_point.person_count = person_count
                        self.data_queue.put(latest_data_point)

        cap.release()
        cv2.destroyAllWindows()
