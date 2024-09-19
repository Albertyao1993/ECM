import cv2
from ultralytics import YOLO

class VideoDetection:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.running = False

    def detect_frame_with_boxes(self, frame):
        results = self.model(frame)
        person_count = 0
        boxes = []  # 用于存储每个人的bounding box信息
        for result in results:
            for box in result.boxes:
                if int(box.cls[0]) == 0:  # Class 0 is 'person' in COCO dataset
                    person_count += 1
                    # 获取bounding box的坐标
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    # 绘制矩形框
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    # 将bounding box的坐标添加到列表中
                    width = x2 - x1
                    height = y2 - y1
                    boxes.append([x1, y1, width, height])
        return frame, person_count, boxes

    def start_detection(self):
        self.running = True

    def stop_detection(self):
        self.running = False
