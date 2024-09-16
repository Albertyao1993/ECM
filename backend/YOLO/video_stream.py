# YOLO/video_stream.py
import cv2
from flask_socketio import SocketIO
from yolo.video_detection import VideoDetection

def send_video_frames(socketio: SocketIO, video_detection: VideoDetection):
    cap = cv2.VideoCapture(0)  # 0 is the default camera
    while video_detection.running and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Perform detection
        frame, person_count = video_detection.detect_frame(frame)

        # Encode the frame in JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Send the frame and person count via WebSocket
        socketio.emit('video_frame', {'frame': frame, 'person_count': person_count})

    cap.release()
    cv2.destroyAllWindows()
