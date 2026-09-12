import cv2
from ultralytics import YOLO
import time

print("==========================================")
print("       RETAILEDGE AI - SHOPPER TRACKING")
print("==========================================")

print("Loading YOLO model...")
model = YOLO("yolo11n.pt")
print("YOLO loaded.")

print("Opening camera...")
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("ERROR: Camera could not be opened.")
    exit()

print("Camera connected.")
print()
print("Tracking started.")
print("Move in front of the camera.")
print("Press Ctrl+C to stop.")
print()

total_frames = 0
max_people = 0

try:

    while True:

        ret, frame = cap.read()

        if not ret:
            print("\nERROR: Could not read camera frame.")
            break

        # YOLO tracking
        results = model.track(
            frame,
            persist=True,
            classes=[0],
            conf=0.4,
            imgsz=320,
            verbose=False
        )

        total_frames += 1

        current_people = 0
        tracking_ids = []

        if results[0].boxes is not None:

            boxes = results[0].boxes

            current_people = len(boxes)

            if boxes.id is not None:
                tracking_ids = boxes.id.int().tolist()

        if current_people > max_people:
            max_people = current_people

        # Print live analytics
        print(
            f"\rCurrent shoppers: {current_people} | "
            f"Tracking IDs: {tracking_ids} | "
            f"Peak shoppers: {max_people}",
            end=""
        )

        time.sleep(0.03)

except KeyboardInterrupt:

    print("\n\nStopping tracking...")

finally:

    cap.release()

    print("Camera released.")

    print()
    print("==========================================")
    print("             SESSION SUMMARY")
    print("==========================================")
    print(f"Frames processed : {total_frames}")
    print(f"Peak shoppers    : {max_people}")
    print("==========================================")