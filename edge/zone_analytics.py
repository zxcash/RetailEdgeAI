import cv2
from ultralytics import YOLO
import time

print("==========================================")
print("       RETAILEDGE AI - ZONE ANALYTICS")
print("==========================================")

model = YOLO("yolo11n.pt")

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("ERROR: Camera could not be opened.")
    exit()

print("Camera connected.")
print("Zone analytics started.")
print("Move around the camera.")
print("Press Ctrl+C to stop.")
print()

# ------------------------------------------------
# STORE ZONES
# ------------------------------------------------

zones = {
    "GROCERY": (0, 0, 320, 240),
    "ELECTRONICS": (320, 0, 640, 240),
    "PHARMACY": (0, 240, 320, 480),
    "CHECKOUT": (320, 240, 640, 480)
}

# ------------------------------------------------
# DWELL TIME
# ------------------------------------------------

zone_entry_time = {}

zone_total_time = {
    "GROCERY": 0,
    "ELECTRONICS": 0,
    "PHARMACY": 0,
    "CHECKOUT": 0
}

last_time = time.time()

try:

    while True:

        ret, frame = cap.read()

        if not ret:
            print("\nERROR: Camera frame unavailable.")
            break

        results = model.track(
            frame,
            persist=True,
            classes=[0],
            conf=0.4,
            imgsz=320,
            verbose=False
        )

        current_time = time.time()

        if results[0].boxes is not None:

            boxes = results[0].boxes

            if boxes.id is not None:

                ids = boxes.id.int().tolist()
                coordinates = boxes.xyxy.tolist()

                for person_id, box in zip(ids, coordinates):

                    x1, y1, x2, y2 = box

                    center_x = int((x1 + x2) / 2)
                    center_y = int((y1 + y2) / 2)

                    current_zone = None

                    # Determine zone
                    for zone_name, coords in zones.items():

                        zx1, zy1, zx2, zy2 = coords

                        if (
                            zx1 <= center_x <= zx2
                            and
                            zy1 <= center_y <= zy2
                        ):
                            current_zone = zone_name
                            break

                    if current_zone:

                        key = (person_id, current_zone)

                        if key not in zone_entry_time:
                            zone_entry_time[key] = current_time

                        elapsed = current_time - zone_entry_time[key]

                        zone_total_time[current_zone] += (
                            elapsed
                        )

                        zone_entry_time[key] = current_time

        # Print analytics
        print(
            "\r"
            f"Grocery: {zone_total_time['GROCERY']:.1f}s | "
            f"Electronics: {zone_total_time['ELECTRONICS']:.1f}s | "
            f"Pharmacy: {zone_total_time['PHARMACY']:.1f}s | "
            f"Checkout: {zone_total_time['CHECKOUT']:.1f}s",
            end=""
        )

except KeyboardInterrupt:

    print("\n\nStopping zone analytics...")

finally:

    cap.release()

    print("\n")
    print("==========================================")
    print("           ZONE DWELL SUMMARY")
    print("==========================================")

    for zone, seconds in zone_total_time.items():

        print(
            f"{zone:<15}: {seconds:.1f} seconds"
        )

    print("==========================================")