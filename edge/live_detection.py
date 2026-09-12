import cv2
from ultralytics import YOLO
import time

print("====================================")
print("      RETAILEDGE AI ENGINE")
print("====================================")

print("Loading YOLO model...")

model = YOLO("yolo11n.pt")

print("YOLO model loaded.")

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("ERROR: Camera could not be opened.")
    exit()

print("Camera connected.")
print("AI detection started.")
print("Press Ctrl+C to stop.")

try:

    while True:

        success, frame = cap.read()

        if not success:
            print("Failed to read camera frame.")
            break

        # Run YOLO
        results = model(
            frame,
            classes=[0],
            conf=0.4,
            imgsz=320,
            verbose=False
        )

        # Number of detected people
        people_count = len(results[0].boxes)

        print(
            f"\rPeople detected: {people_count}",
            end=""
        )

        time.sleep(0.01)

except KeyboardInterrupt:

    print("\n\nStopping RetailEdge AI...")

finally:

    cap.release()

    print("Camera released.")
    print("RetailEdge AI stopped.")