import sys
import os

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

import cv2

from app.vision.pose_analyzer import PoseAnalyzer
from app.analysis.coaching import CoachingEngine


print("=" * 60)
print("SNAPSPEAK LIVE POSTURE COACHING")
print("=" * 60)

print("\nLoading posture analyzer...")

pose_analyzer = PoseAnalyzer()
coaching_engine = CoachingEngine()

print("\nCamera starting...")
print("Stand in front of the camera.")
print("Press Q to finish.")

camera = cv2.VideoCapture(0)

if not camera.isOpened():

    print("\nERROR: Could not open webcam.")
    exit()


while True:

    success, frame = camera.read()

    if not success:

        print("\nERROR: Could not read webcam frame.")
        break


    # ------------------------------------------------------
    # Analyze posture
    # ------------------------------------------------------

    posture, result = pose_analyzer.analyze_frame(
        frame
    )


    # ------------------------------------------------------
    # Generate coaching feedback
    # ------------------------------------------------------

    posture_feedback = coaching_engine.analyze_posture(
        posture
    )


    # ------------------------------------------------------
    # Draw YOLO detections
    # ------------------------------------------------------

    annotated_frame = result.plot()


    # ------------------------------------------------------
    # Display posture information
    # ------------------------------------------------------

    if posture is not None:

        cv2.putText(
            annotated_frame,
            f"Posture: {posture_feedback['status']}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.putText(
            annotated_frame,
            f"Tilt: "
            f"{posture['shoulder_tilt_degrees']:.1f} deg",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.putText(
            annotated_frame,
            f"Lean: "
            f"{posture['body_lean_degrees']:.1f} deg",
            (20, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.putText(
            annotated_frame,
            posture_feedback["message"],
            (20, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )

    else:

        cv2.putText(
            annotated_frame,
            "Posture: Unknown",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.putText(
            annotated_frame,
            posture_feedback["message"],
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )


    cv2.putText(
        annotated_frame,
        "Press Q to finish",
        (20, 190),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )


    # ------------------------------------------------------
    # Display live coaching window
    # ------------------------------------------------------

    cv2.imshow(
        "SnapSpeak - Live Coaching",
        annotated_frame
    )


    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break


camera.release()
cv2.destroyAllWindows()


print("\n" + "=" * 60)
print("LIVE POSTURE COACHING COMPLETED")
print("=" * 60)