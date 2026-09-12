import cv2
from ultralytics import YOLO
import time

print("==========================================")
print("      RETAILEDGE AI - INVENTORY AI")
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
print("Inventory monitoring started.")
print("Show objects/products to the camera.")
print("Press Ctrl+C to stop.")
print()

# ------------------------------------------------
# DEMO SHELF
# ------------------------------------------------

# Three virtual shelf sections
shelves = {
    "SHELF_A": {
        "x1": 0,
        "y1": 0,
        "x2": 213,
        "y2": 480,
        "minimum_stock": 2
    },

    "SHELF_B": {
        "x1": 213,
        "y1": 0,
        "x2": 426,
        "y2": 480,
        "minimum_stock": 2
    },

    "SHELF_C": {
        "x1": 426,
        "y1": 0,
        "x2": 640,
        "y2": 480,
        "minimum_stock": 2
    }
}

try:

    while True:

        ret, frame = cap.read()

        if not ret:
            print("\nERROR: Could not read camera.")
            break

        results = model(
            frame,
            conf=0.35,
            imgsz=320,
            verbose=False
        )

        # Count objects inside each shelf
        shelf_counts = {
            "SHELF_A": 0,
            "SHELF_B": 0,
            "SHELF_C": 0
        }

        if results[0].boxes is not None:

            for box in results[0].boxes.xyxy.tolist():

                x1, y1, x2, y2 = box

                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)

                for shelf_name, shelf in shelves.items():

                    if (
                        shelf["x1"] <= center_x <= shelf["x2"]
                        and
                        shelf["y1"] <= center_y <= shelf["y2"]
                    ):

                        shelf_counts[shelf_name] += 1

        # ------------------------------------------------
        # INVENTORY STATUS
        # ------------------------------------------------

        status = {}

        for shelf_name, count in shelf_counts.items():

            minimum = shelves[shelf_name]["minimum_stock"]

            if count == 0:

                status[shelf_name] = "OUT OF STOCK"

            elif count < minimum:

                status[shelf_name] = "LOW STOCK"

            else:

                status[shelf_name] = "OK"

        print(
            "\r"
            f"A:{shelf_counts['SHELF_A']} "
            f"({status['SHELF_A']}) | "
            f"B:{shelf_counts['SHELF_B']} "
            f"({status['SHELF_B']}) | "
            f"C:{shelf_counts['SHELF_C']} "
            f"({status['SHELF_C']})",
            end=""
        )

        time.sleep(0.1)

except KeyboardInterrupt:

    print("\n\nStopping inventory monitoring...")

finally:

    cap.release()

    print("\nCamera released.")

    print()
    print("==========================================")
    print("          INVENTORY SUMMARY")
    print("==========================================")

    for shelf_name in shelves:

        print(
            f"{shelf_name:<10}: "
            f"{shelf_counts[shelf_name]} items "
            f"- {status[shelf_name]}"
        )

    print("==========================================")