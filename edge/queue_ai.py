import cv2
from ultralytics import YOLO
import time

print("==========================================")
print("       RETAILEDGE AI - QUEUE AI")
print("==========================================")

print("Loading YOLO model...")

model = YOLO("yolo11n.pt")

print("YOLO loaded.")
print("Opening checkout camera...")

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("ERROR: Camera could not be opened.")
    exit()

print("Camera connected.")
print("Queue intelligence started.")
print("Stand in front of the camera to simulate shoppers.")
print("Press Ctrl+C to stop.")
print()

# ------------------------------------------------
# QUEUE SETTINGS
# ------------------------------------------------

QUEUE_MIN = 0
QUEUE_MAX = 3

# Approximate service time per customer
SERVICE_TIME = 2.5

peak_queue = 0
total_samples = 0
queue_sum = 0

try:

    while True:

        ret, frame = cap.read()

        if not ret:
            print("\nERROR: Could not read camera frame.")
            break

        results = model.track(
            frame,
            persist=True,
            classes=[0],
            conf=0.4,
            imgsz=320,
            verbose=False
        )

        queue_length = 0

        if results[0].boxes is not None:

            boxes = results[0].boxes

            if boxes.id is not None:

                # Every detected person is treated
                # as a shopper in the checkout queue
                queue_length = len(boxes.id)

        # Update statistics

        if queue_length > peak_queue:
            peak_queue = queue_length

        queue_sum += queue_length
        total_samples += 1

        average_queue = (
            queue_sum / total_samples
        )

        # ------------------------------------------------
        # WAIT TIME ESTIMATION
        # ------------------------------------------------

        estimated_wait = (
            queue_length * SERVICE_TIME
        )

        # ------------------------------------------------
        # CONGESTION
        # ------------------------------------------------

        if queue_length == 0:

            congestion = "NO QUEUE"

        elif queue_length <= 2:

            congestion = "NORMAL"

        elif queue_length <= 4:

            congestion = "BUSY"

        else:

            congestion = "CRITICAL"

        # ------------------------------------------------
        # COUNTER RECOMMENDATION
        # ------------------------------------------------

        if queue_length >= 5:

            recommendation = "OPEN ADDITIONAL COUNTER"

        elif queue_length >= 3:

            recommendation = "MONITOR QUEUE"

        else:

            recommendation = "NO ACTION"

        print(
            "\r"
            f"Queue: {queue_length} | "
            f"Wait: {estimated_wait:.1f}s | "
            f"Status: {congestion} | "
            f"{recommendation}",
            end=""
        )

        time.sleep(0.1)

except KeyboardInterrupt:

    print("\n\nStopping queue intelligence...")

finally:

    cap.release()

    average_queue = (
        queue_sum / total_samples
        if total_samples > 0
        else 0
    )

    print("\nCamera released.")

    print()
    print("==========================================")
    print("             QUEUE SUMMARY")
    print("==========================================")
    print(f"Peak Queue      : {peak_queue}")
    print(f"Average Queue   : {average_queue:.1f}")
    print(
        f"Current Wait    : "
        f"{peak_queue * SERVICE_TIME:.1f} seconds"
    )

    if peak_queue >= 5:
        print("Recommendation   : OPEN ADDITIONAL COUNTER")
    elif peak_queue >= 3:
        print("Recommendation   : MONITOR QUEUE")
    else:
        print("Recommendation   : NORMAL OPERATION")

    print("==========================================")