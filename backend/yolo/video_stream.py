# YOLO/video_stream.py
import time
import base64
import cv2
from flask_socketio import SocketIO
from yolo.video_detection import VideoDetection

def send_video_frames(socketio: SocketIO, video_detection: VideoDetection):
    # cap = cv2.VideoCapture(0)  # 0 is the default camera
    cap = cv2.VideoCapture('/dev/video0')
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

        time.sleep(1)

    cap.release()
    cv2.destroyAllWindows()
