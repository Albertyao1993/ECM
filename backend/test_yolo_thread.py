import cv2
import time
from queue import Queue
from threading import Event, Lock, Thread
from yolo.video_detection import VideoDetection
from yolo.video_stream import VideoStream

def simulate_data_queue():
    while not stop_event.is_set():
        if not data_queue.empty():
            data = data_queue.get()
            print(f"检测到的人数: {data.person_count}")
        time.sleep(1)

if __name__ == "__main__":
    data_queue = Queue()
    stop_event = Event()
    lock = Lock()

    video_detection = VideoDetection(model_path='yolo/weights/yolov8n.pt')
    video_stream = VideoStream(video_detection, data_queue, stop_event, lock)

    # 创建一个模拟数据队列的线程
    data_thread = Thread(target=simulate_data_queue)
    data_thread.start()

    try:
        print("开始 YOLO 检测测试")
        print("程序将每分钟捕获一次图像并检测人数")
        print("按 Ctrl+C 停止测试")

        video_stream.capture_and_detect()
    except KeyboardInterrupt:
        print("测试停止")
    finally:
        stop_event.set()
        data_thread.join()
        print("测试结束")