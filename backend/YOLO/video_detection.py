# YOLO/video_detection.py
import cv2
from ultralytics import YOLO

class VideoDetection:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.running = False

    def detect_frame(self, frame):
        results = self.model(frame)
        person_count = 0
        for result in results:
            for box in result.boxes:
                if box.cls == 0:  # Class 0 is 'person' in COCO dataset
                    person_count += 1
                    if len(box.xyxy) == 4:
                        x1, y1, x2, y2 = box.xyxy
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        return frame, person_count

    def start_detection(self):
        self.running = True

    def stop_detection(self):
        self.running = False