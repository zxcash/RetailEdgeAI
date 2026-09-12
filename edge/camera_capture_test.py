import cv2
import time

print("Starting camera capture test...")

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("ERROR: Camera could not be opened.")
    input("Press Enter to exit...")
    exit()

print("Camera opened.")

# Give the camera a moment to initialize
time.sleep(2)

for i in range(10):
    print(f"Reading frame {i + 1}...")

    ret, frame = cap.read()

    if not ret:
        print("ERROR: Failed to read frame.")
        break

    print(f"Frame received: {frame.shape}")

    filename = f"camera_frame_{i + 1}.jpg"
    cv2.imwrite(filename, frame)

    print(f"Saved: {filename}")

cap.release()

print("Camera test completed successfully.")