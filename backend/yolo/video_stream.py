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

        # 检测操作系统并设置摄像头源
        if os.name == 'nt':  # Windows
            self.camera_source = 0
        else:  # Linux
            self.camera_source = '/dev/video0'

    def capture_and_detect(self):
        cap = cv2.VideoCapture(self.camera_source)
        if not cap.isOpened():
            print("错误：无法打开视频流。")
            return

        while not self.stop_event.is_set():
            # 每分钟捕获一次图像
            time.sleep(60)

            ret, frame = cap.read()
            if not ret:
                print("错误：无法从视频流读取帧。")
                continue

            # 执行检测并获取人数
            person_count = self.video_detection.detect_persons(frame)
            print(f"检测到的人数: {person_count}")  # 添加这行日志

            # 将人数数据发送到队列中
            with self.lock:
                # if not self.data_queue.empty():
                #     latest_data_point = self.data_queue.get()
                #     latest_data_point.person_count = person_count
                #     self.data_queue.put(latest_data_point)
                # else:
                #     print("警告：数据队列为空，创建新的数据点")
                #     from Database.sensor_data import SensorData
                #     new_data_point = SensorData(person_count=person_count)
                #     self.data_queue.put(new_data_point)
                if self.dth111.latest_data:
                    self.dth111.latest_data.person_count = person_count
                

        cap.release()
