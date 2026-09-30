import cv2
from ultralytics import YOLO

from app.vision.posture_analyzer import analyze_posture


class PoseAnalyzer:

    def __init__(
        self,
        model_path="yolo11n-pose.pt",
        smoothing_alpha=0.25,
    ):

        print(
            f"Loading pose model: {model_path}"
        )

        self.model = YOLO(model_path)

        self.smoothing_alpha = smoothing_alpha

        self.previous_keypoints = None

        print("Pose model loaded.")

    def smooth_keypoints(self, keypoints):

        keypoints = keypoints.astype("float32")

        if self.previous_keypoints is None:

            self.previous_keypoints = keypoints.copy()

            return keypoints

        alpha = self.smoothing_alpha

        smoothed_keypoints = (
            alpha * keypoints
            + (1 - alpha)
            * self.previous_keypoints
        )

        self.previous_keypoints = (
            smoothed_keypoints.copy()
        )

        return smoothed_keypoints

    def analyze_frame(self, frame):

        results = self.model(
            frame,
            verbose=False,
        )

        result = results[0]

        if result.keypoints is None:

            return None, result

        if result.keypoints.xy is None:

            return None, result

        keypoints_data = result.keypoints.xy

        if len(keypoints_data) == 0:

            return None, result

        keypoints = (
            keypoints_data[0]
            .cpu()
            .numpy()
        )

        required_indices = [
            5,
            6,
            11,
            12,
        ]

        for index in required_indices:

            if index >= len(keypoints):

                return None, result

        keypoints = self.smooth_keypoints(
            keypoints
        )

        posture = analyze_posture(
            keypoints
        )

        return posture, result


def draw_posture_info(
    frame,
    posture,
):

    if posture is None:

        cv2.putText(
            frame,
            "No person detected",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2,
        )

        return frame

    cv2.putText(
        frame,
        (
            f"Shoulder Tilt: "
            f"{posture['shoulder_tilt_degrees']:.1f} deg"
        ),
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )

    cv2.putText(
        frame,
        (
            f"Body Lean: "
            f"{posture['body_lean_degrees']:.1f} deg"
        ),
        (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )

    cv2.putText(
        frame,
        (
            f"Posture: "
            f"{posture['posture_status']}"
        ),
        (20, 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )

    return frame