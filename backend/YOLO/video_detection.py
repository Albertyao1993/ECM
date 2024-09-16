import cv2
from ultralytics import YOLO
from threading import Thread

class VideoDetection:
    def __init__(self, model_path='yolov8n.pt'):
        self.model = YOLO(model_path)
        self.running = False

    def detect_webcam(self):
        cap = cv2.VideoCapture(0)  # 0 is the default camera

        while self.running and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Perform detection
            results = self.model(frame)

            # Count the number of persons detected
            person_count = 0
            for result in results:
                for box in result.boxes:
                    if box.cls == 0:  # Class 0 is 'person' in COCO dataset
                        person_count += 1
                        if len(box.xyxy) == 4:
                            x1, y1, x2, y2 = box.xyxy
                            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

            # Display the number of detected persons on the frame
            cv2.putText(frame, f"Detected {person_count} persons", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            print(f"Detected {person_count} persons")

            # Display the frame
            cv2.imshow('YOLOv8 Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def start_detection(self):
        self.running = True
        self.thread = Thread(target=self.detect_webcam)
        self.thread.start()

    def stop_detection(self):
        self.running = False
        self.thread.join()