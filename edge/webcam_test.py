import cv2
from ultralytics import YOLO

print("Loading RetailEdge AI...")

model = YOLO("yolo11n.pt")

print("YOLO loaded.")
print("Opening laptop camera...")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Could not open camera.")
    print("Check that your webcam is available.")
    exit()

print("Camera started.")
print("Press Q to quit.")

while True:
    success, frame = cap.read()

    if not success:
        print("ERROR: Could not read camera frame.")
        break

    results = model(
        frame,
        classes=[0],
        conf=0.4,
        verbose=False
    )

    annotated_frame = results[0].plot()

    cv2.imshow(
        "RetailEdge AI - Live Shopper Detection",
        annotated_frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

print("RetailEdge AI stopped.")