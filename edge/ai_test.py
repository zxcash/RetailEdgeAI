import cv2
from ultralytics import YOLO

print("Loading YOLO...")
model = YOLO("yolo11n.pt")

print("Opening camera...")
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("ERROR: Camera could not be opened.")
    exit()

print("Camera opened.")
print("Capturing one frame...")

ret, frame = cap.read()

if not ret:
    print("ERROR: Could not capture frame.")
    cap.release()
    exit()

print("Frame captured successfully.")

print("Running YOLO...")

results = model(
    frame,
    classes=[0],
    conf=0.4,
    imgsz=320,
    verbose=False
)

people = len(results[0].boxes)

print(f"People detected: {people}")

annotated = results[0].plot()

cv2.imwrite("ai_detection_result.jpg", annotated)

print("Saved: ai_detection_result.jpg")

cap.release()

print("Camera released.")
print("AI test completed.")