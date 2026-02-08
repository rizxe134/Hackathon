import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os
import time
import urllib.request

capture = cv2.VideoCapture(0)

MODEL_URL = "C:\Code\Project\hand_landmarker.task"
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "hand_landmarker.task")


# def ensure_model() -> None:
#     os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
#     if not os.path.exists(MODEL_PATH):
#         print(f"Downloading model to: {MODEL_PATH}")
#         urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)


# ensure_model()

options = vision.HandLandmarkerOptions(
    base_options=python.BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=vision.RunningMode.VIDEO,
    num_hands=2,
)
landmarker = vision.HandLandmarker.create_from_options(options)

try:
    HAND_CONNECTIONS = mp.solutions.hands.HAND_CONNECTIONS
except Exception:
    # Fallback in case 'mp.solutions' is unavailable in this environment
    HAND_CONNECTIONS = [
        (0, 1), (1, 2), (2, 3), (3, 4),        # thumb
        (0, 5), (5, 6), (6, 7), (7, 8),        # index
        (5, 9), (9, 10), (10, 11), (11, 12),   # middle
        (9, 13), (13, 14), (14, 15), (15, 16), # ring
        (13, 17), (0, 17), (17, 18), (18, 19), (19, 20),  # pinky + palm
    ]


while True:
    success, frame = capture.read()
    if not success:
        continue

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
    timestamp_ms = int(time.time() * 1000)

    result = landmarker.detect_for_video(mp_image, timestamp_ms)

    h, w = frame.shape[:2]
    for hand_landmarks in result.hand_landmarks:
        # Draw landmark connections (skeleton)
        for start_idx, end_idx in HAND_CONNECTIONS:
            s = hand_landmarks[start_idx]
            e = hand_landmarks[end_idx]
            x1 = max(0, min(w - 1, int(s.x * w)))
            y1 = max(0, min(h - 1, int(s.y * h)))
            x2 = max(0, min(w - 1, int(e.x * w)))
            y2 = max(0, min(h - 1, int(e.y * h)))
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Draw landmarks (your rectangles) on top
        for lm in hand_landmarks:
            cx, cy = int(lm.x * w), int(lm.y * h)
            half = 3  # rectangle "radius" in pixels
            x1 = max(0, cx - half)
            y1 = max(0, cy - half)
            x2 = min(w - 1, cx + half)
            y2 = min(h - 1, cy + half)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), -1)
    
    cv2.imshow("frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

landmarker.close()
capture.release()
cv2.destroyAllWindows()

