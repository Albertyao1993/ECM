import cv2
from ultralytics import YOLO

class VideoDetection:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def detect_persons(self, frame):
        results = self.model(frame)
        person_count = 0
        for result in results:
            for box in result.boxes:
                if int(box.cls[0]) == 0:  # Class 0 is 'person' in COCO dataset
                    person_count += 1
        return person_count
