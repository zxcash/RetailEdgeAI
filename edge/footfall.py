import cv2
from ultralytics import YOLO
import time

print("==========================================")
print("       RETAILEDGE AI - FOOTFALL")
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
print("Footfall analytics started.")
print("Move across the camera area.")
print("Press Ctrl+C to stop.")
print()

# ------------------------------------------------
# FOOTFALL VARIABLES
# ------------------------------------------------

entry_count = 0
exit_count = 0

# Remember the previous vertical position of each person
previous_positions = {}

# Keep track of people already counted
counted_entries = set()
counted_exits = set()

# Virtual entrance line
# Change this value if necessary
LINE_Y = 300

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

        if results[0].boxes is not None:

            boxes = results[0].boxes

            if boxes.id is not None:

                ids = boxes.id.int().tolist()

                coordinates = boxes.xyxy.tolist()

                for person_id, box in zip(ids, coordinates):

                    x1, y1, x2, y2 = box

                    # Calculate center point
                    center_x = int((x1 + x2) / 2)
                    center_y = int((y1 + y2) / 2)

                    # Previous position
                    previous_y = previous_positions.get(person_id)

                    if previous_y is not None:

                        # Moving DOWN across line
                        if (
                            previous_y < LINE_Y
                            and center_y >= LINE_Y
                            and person_id not in counted_entries
                        ):

                            entry_count += 1
                            counted_entries.add(person_id)

                            print(
                                f"\nENTRY detected! "
                                f"Person ID: {person_id}"
                            )

                        # Moving UP across line
                        elif (
                            previous_y > LINE_Y
                            and center_y <= LINE_Y
                            and person_id not in counted_exits
                        ):

                            exit_count += 1
                            counted_exits.add(person_id)

                            print(
                                f"\nEXIT detected! "
                                f"Person ID: {person_id}"
                            )

                    previous_positions[person_id] = center_y

        current_people = 0

        if results[0].boxes is not None:
            current_people = len(results[0].boxes)

        print(
            f"\rCurrent: {current_people} | "
            f"Entries: {entry_count} | "
            f"Exits: {exit_count}",
            end=""
        )

        time.sleep(0.03)

except KeyboardInterrupt:

    print("\n\nStopping footfall analytics...")

finally:

    cap.release()

    print("\nCamera released.")

    print()
    print("==========================================")
    print("             FOOTFALL SUMMARY")
    print("==========================================")
    print(f"Total Entries : {entry_count}")
    print(f"Total Exits   : {exit_count}")
    print(f"Current Count : {entry_count - exit_count}")
    print("==========================================")