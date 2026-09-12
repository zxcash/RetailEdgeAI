import cv2
import numpy as np
from ultralytics import YOLO
import time

print("==========================================")
print("       RETAILEDGE AI - HEATMAP")
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
print("Collecting shopper movement data...")
print("Move around in front of the camera.")
print("Press Ctrl+C to stop.")
print()

# Heatmap grid
GRID_WIDTH = 64
GRID_HEIGHT = 48

heatmap = np.zeros(
    (GRID_HEIGHT, GRID_WIDTH),
    dtype=np.float32
)

frames = 0

try:

    while True:

        ret, frame = cap.read()

        if not ret:
            print("\nERROR: Could not read camera frame.")
            break

        height, width = frame.shape[:2]

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

                coordinates = boxes.xyxy.tolist()

                for box in coordinates:

                    x1, y1, x2, y2 = box

                    # Person center
                    center_x = int((x1 + x2) / 2)
                    center_y = int((y1 + y2) / 2)

                    # Convert camera coordinate to grid
                    grid_x = int(
                        center_x / width * GRID_WIDTH
                    )

                    grid_y = int(
                        center_y / height * GRID_HEIGHT
                    )

                    grid_x = max(
                        0,
                        min(GRID_WIDTH - 1, grid_x)
                    )

                    grid_y = max(
                        0,
                        min(GRID_HEIGHT - 1, grid_y)
                    )

                    heatmap[grid_y, grid_x] += 1

        frames += 1

        if frames % 10 == 0:

            print(
                f"\rFrames analyzed: {frames}",
                end=""
            )

        time.sleep(0.03)

except KeyboardInterrupt:

    print("\n\nStopping heatmap collection...")

finally:

    cap.release()

    print("\nCamera released.")

# ------------------------------------------------
# GENERATE HEATMAP IMAGE
# ------------------------------------------------

print("Generating heatmap...")

# Smooth the heatmap
heatmap_smooth = cv2.GaussianBlur(
    heatmap,
    (0, 0),
    sigmaX=3,
    sigmaY=3
)

# Normalize
if heatmap_smooth.max() > 0:

    normalized = cv2.normalize(
        heatmap_smooth,
        None,
        0,
        255,
        cv2.NORM_MINMAX
    )

else:

    normalized = heatmap_smooth

normalized = normalized.astype(np.uint8)

# Apply heatmap colors
colored_heatmap = cv2.applyColorMap(
    normalized,
    cv2.COLORMAP_JET
)

# Resize to normal camera size
colored_heatmap = cv2.resize(
    colored_heatmap,
    (640, 480)
)

# Save result
cv2.imwrite(
    "shopper_heatmap.jpg",
    colored_heatmap
)

print("Heatmap saved: shopper_heatmap.jpg")

print()
print("==========================================")
print("             HEATMAP SUMMARY")
print("==========================================")

if heatmap.max() > 0:

    max_position = np.unravel_index(
        np.argmax(heatmap),
        heatmap.shape
    )

    print(
        f"Highest traffic grid position: "
        f"X={max_position[1]}, "
        f"Y={max_position[0]}"
    )

else:

    print("No shopper movement detected.")

print(f"Frames analyzed: {frames}")

print("==========================================")