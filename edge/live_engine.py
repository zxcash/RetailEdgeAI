import cv2
import time
import requests

from pathlib import Path
from ultralytics import YOLO


# ============================================================
# RETAILEDGE AI - LIVE EDGE ENGINE
# ============================================================

print("=" * 50)
print("       RETAILEDGE AI - LIVE ENGINE")
print("=" * 50)


# ============================================================
# API
# ============================================================

API_URL = "http://127.0.0.1:8000/api/live"

VIDEO_API_URL = (
    "http://127.0.0.1:8000/api/video/frame"
)


# ============================================================
# YOLO MODEL
# ============================================================

print("Loading YOLO model...")

MODEL_PATH = (
    Path(__file__).resolve().parent
    / "yolo11n.pt"
)

model = YOLO(
    str(MODEL_PATH)
)

print("YOLO loaded.")


# ============================================================
# CAMERA
# ============================================================

print("Opening laptop camera...")

cap = cv2.VideoCapture(0)


if not cap.isOpened():

    print("ERROR: Could not open camera.")

    raise SystemExit(1)


print("Camera connected.")


# ============================================================
# CAMERA SETTINGS
# ============================================================

cap.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    1280
)

cap.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    720
)

cap.set(
    cv2.CAP_PROP_FPS,
    30
)


# ============================================================
# TRACKING
# ============================================================

frame_count = 0

start_time = time.time()

last_api_update = 0


# ============================================================
# START
# ============================================================

print()
print("Live AI processing started.")
print(
    "Camera feed is being sent to FastAPI."
)
print(
    "Press Q inside the camera window to stop."
)
print()


try:

    while True:

        # ----------------------------------------------------
        # READ CAMERA
        # ----------------------------------------------------

        success, frame = cap.read()


        if not success:

            print(
                "ERROR: Could not read camera frame."
            )

            break


        frame_count += 1


        # ----------------------------------------------------
        # YOLO TRACKING
        # ----------------------------------------------------

        results = model.track(
            frame,
            persist=True,
            classes=[0],
            verbose=False,
        )


        # ----------------------------------------------------
        # DRAW YOLO RESULTS
        # ----------------------------------------------------

        annotated_frame = results[0].plot()


        # ----------------------------------------------------
        # COUNT PEOPLE
        # ----------------------------------------------------

        current_shoppers = 0

        tracking_ids = []


        boxes = results[0].boxes


        if boxes is not None:

            current_shoppers = len(boxes)


            if boxes.id is not None:

                tracking_ids = [
                    int(x)
                    for x in boxes.id.tolist()
                ]


        # ----------------------------------------------------
        # SEND SHOPPER DATA
        # ----------------------------------------------------

        current_time = time.time()


        if current_time - last_api_update >= 0.2:

            try:

                response = requests.post(
                    API_URL,
                    json={
                        "current_shoppers": (
                            current_shoppers
                        ),
                        "tracking_ids": (
                            tracking_ids
                        ),
                    },
                    timeout=1,
                )

                if response.ok:

                    print(
                        "API UPDATE | "
                        f"Shoppers: "
                        f"{current_shoppers} | "
                        f"IDs: "
                        f"{tracking_ids}"
                    )

                else:

                    print(
                        "LIVE API ERROR | "
                        f"{response.status_code}"
                    )

            except requests.RequestException as e:

                print(
                    "LIVE API CONNECTION ERROR | "
                    f"{e}"
                )

            last_api_update = current_time


        # ----------------------------------------------------
        # SEND VIDEO FRAME
        #
        # IMPORTANT:
        # Send raw JPEG bytes with explicit
        # Content-Type: image/jpeg.
        # ----------------------------------------------------

        try:

            encode_success, jpeg = cv2.imencode(
                ".jpg",
                annotated_frame,
                [
                    cv2.IMWRITE_JPEG_QUALITY,
                    80,
                ],
            )


            if encode_success:

                video_response = requests.post(
                    VIDEO_API_URL,
                    data=jpeg.tobytes(),
                    headers={
                        "Content-Type": "image/jpeg",
                    },
                    timeout=1,
                )


                if (
                    not video_response.ok
                    and frame_count % 30 == 0
                ):

                    print(
                        "VIDEO API ERROR | "
                        f"{video_response.status_code}"
                    )


        except requests.RequestException as e:

            if frame_count % 30 == 0:

                print(
                    "VIDEO API CONNECTION ERROR | "
                    f"{e}"
                )


        # ----------------------------------------------------
        # DISPLAY LOCAL CAMERA WINDOW
        # ----------------------------------------------------

        cv2.imshow(
            "RetailEdge AI - Live Camera",
            annotated_frame
        )


        # ----------------------------------------------------
        # Q TO STOP
        # ----------------------------------------------------

        key = cv2.waitKey(1) & 0xFF


        if key == ord("q"):

            print()
            print("Q pressed. Stopping...")

            break


finally:

    cap.release()

    cv2.destroyAllWindows()


# ============================================================
# SUMMARY
# ============================================================

runtime = time.time() - start_time

print()
print("=" * 50)
print("        SESSION SUMMARY")
print("=" * 50)

print(
    f"Frames processed : {frame_count}"
)

print(
    f"Runtime          : {runtime:.1f} seconds"
)

if runtime > 0:

    print(
        f"Average FPS      : "
        f"{frame_count / runtime:.1f}"
    )

print("=" * 50)