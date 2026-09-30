import cv2
import sounddevice as sd

print("=" * 50)
print("SNAPSPEAK HARDWARE TEST")
print("=" * 50)

# -----------------------------
# Microphone test
# -----------------------------
print("\nAvailable audio devices:")
print(sd.query_devices())

print("\nDefault audio device:")
print(sd.query_devices(kind="input"))

# -----------------------------
# Webcam test
# -----------------------------
print("\nStarting webcam test...")
print("A camera window should appear.")
print("Press Q in the camera window to close it.")

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ERROR: Could not open webcam.")
else:
    print("SUCCESS: Webcam detected.")

    while True:
        ret, frame = camera.read()

        if not ret:
            print("ERROR: Could not read webcam frame.")
            break

        cv2.imshow("SnapSpeak - Webcam Test", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()

print("\nHardware test completed.")