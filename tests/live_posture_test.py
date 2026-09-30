import cv2

from app.vision.pose_analyzer import (
    PoseAnalyzer,
    draw_posture_info
)


print("=" * 50)
print("SNAPSPEAK LIVE POSTURE ANALYSIS")
print("=" * 50)

pose_analyzer = PoseAnalyzer()

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ERROR: Could not open webcam.")
    exit()

print("\nWebcam started.")
print("Stand normally in front of the camera.")
print("Press Q to quit.")

while True:
    ret, frame = camera.read()

    if not ret:
        print("ERROR: Could not read webcam frame.")
        break

    posture, result = pose_analyzer.analyze_frame(frame)

    annotated_frame = result.plot()

    annotated_frame = draw_posture_info(
        annotated_frame,
        posture
    )

    cv2.imshow(
        "SnapSpeak - Live Posture Analysis",
        annotated_frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()

print("\nLive posture analysis completed.")