import time
import cv2
import os
from yolo.video_detection import VideoDetection
from queue import Queue
from threading import Event, Lock
from Database.sensor_data import SensorData

class VideoStream:
    def __init__(self, video_detection: VideoDetection, data_queue: Queue, stop_event: Event, lock: Lock, dth111):
        self.video_detection = video_detection
        self.data_queue = data_queue
        self.stop_event = stop_event
        self.lock = lock
        self.dth111 = dth111

        # Check the operating system and set the camera source
        if os.name == 'nt':  # Windows
            self.camera_source = 0
        else:  # Linux
            self.camera_source = '/dev/video0'

    def capture_and_detect(self):
        cap = cv2.VideoCapture(self.camera_source)
        if not cap.isOpened():
            print("Error: Unable to open video stream.")
            return

        while not self.stop_event.is_set():
            # Capture an image every minute
            time.sleep(60)

            ret, frame = cap.read()
            if not ret:
                print("Error: Unable to read frame from video stream.")
                continue

            # Perform detection and get person count
            person_count = self.video_detection.detect_persons(frame)
            print(f"Number of persons detected: {person_count}")  # Add this log line

            # Send person count data to the queue
            with self.lock:
                if self.dth111.latest_data:
                    self.dth111.latest_data.person_count = person_count

        cap.release()
