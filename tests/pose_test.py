import cv2
from ultralytics import YOLO


print("=" * 50)
print("SNAPSPEAK YOLO11 POSE TEST")
print("=" * 50)

print("\nLoading YOLO11 Pose model...")

model = YOLO("yolo11n-pose.pt")

print("Model loaded.")

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("\nERROR: Could not open webcam.")
    exit()

print("\nWebcam started.")
print("Stand in front of the camera.")
print("Press Q to quit.")

while True:

    ret, frame = camera.read()

    if not ret:
        print("ERROR: Could not read webcam frame.")
        break

    # Run pose estimation
    results = model(
        frame,
        verbose=False
    )

    # Draw detected pose
    annotated_frame = results[0].plot()

    cv2.imshow(
        "SnapSpeak - YOLO11 Pose",
        annotated_frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


camera.release()
cv2.destroyAllWindows()

print("\nYOLO11 pose test completed.")