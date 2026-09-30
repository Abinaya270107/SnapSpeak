import cv2

from app.analysis.session import PresentationSession
from app.analysis.posture_metrics import calculate_posture_session
from app.vision.pose_analyzer import PoseAnalyzer


print("=" * 60)
print("SNAPSPEAK LIVE POSTURE SESSION")
print("=" * 60)

print("\nLoading posture analyzer...")

pose_analyzer = PoseAnalyzer()

session = PresentationSession()

metrics_history = []

print("\nCamera starting...")
print("Stand in front of the camera.")
print("Press Q to end the session.")

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("\nERROR: Could not open webcam.")
    exit()

while True:

    success, frame = camera.read()

    if not success:
        print("\nERROR: Could not read webcam frame.")
        break

    posture, result = pose_analyzer.analyze_frame(
        frame
    )

    # Store posture metrics when a person is detected.
    if posture is not None:
        metrics_history.append(posture)

    # Draw YOLO detections.
    annotated_frame = result.plot()

    # Display SnapSpeak posture information.
    if posture is not None:

        cv2.putText(
            annotated_frame,
            f"Posture: {posture['posture_status']}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.putText(
            annotated_frame,
            f"Shoulder Tilt: "
            f"{posture['shoulder_tilt_degrees']:.1f}",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.putText(
            annotated_frame,
            f"Body Lean: "
            f"{posture['body_lean_degrees']:.1f}",
            (20, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

    else:

        cv2.putText(
            annotated_frame,
            "No person detected",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

    cv2.imshow(
        "SnapSpeak - Live Posture",
        annotated_frame
    )

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break


camera.release()
cv2.destroyAllWindows()


# ----------------------------------------------------------
# Calculate final posture session metrics
# ----------------------------------------------------------

print("\nCalculating posture session metrics...")

posture_result = calculate_posture_session(
    metrics_history
)


# ----------------------------------------------------------
# Store posture result in PresentationSession
# ----------------------------------------------------------

session.set_posture_result(
    posture_result
)


# ----------------------------------------------------------
# Display results
# ----------------------------------------------------------

print("\n" + "=" * 60)
print("POSTURE SESSION RESULT")
print("=" * 60)

print(
    f"\nSamples Analyzed       : "
    f"{posture_result['samples']}"
)

print(
    f"Average Shoulder Tilt : "
    f"{posture_result['average_shoulder_tilt']}°"
)

print(
    f"Average Body Lean     : "
    f"{posture_result['average_body_lean']}°"
)

print(
    f"Good Posture          : "
    f"{posture_result['good_posture_percentage']}%"
)

print(
    f"Slightly Misaligned   : "
    f"{posture_result['slightly_misaligned_percentage']}%"
)

print(
    f"Needs Adjustment      : "
    f"{posture_result['needs_adjustment_percentage']}%"
)


# ----------------------------------------------------------
# Verify PresentationSession
# ----------------------------------------------------------

summary = session.get_summary()

print("\n" + "=" * 60)
print("SESSION POSTURE INTEGRATION")
print("=" * 60)

print("\nStored posture result:")
print(summary["posture"])

print("\n" + "=" * 60)
print("LIVE POSTURE → SESSION INTEGRATION COMPLETED")
print("=" * 60)