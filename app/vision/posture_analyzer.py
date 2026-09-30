import math


def calculate_angle(point_a, point_b, point_c):
    """
    Calculate the angle ABC in degrees.

    Each point is represented as:
        (x, y)
    """

    ba = (
        point_a[0] - point_b[0],
        point_a[1] - point_b[1]
    )

    bc = (
        point_c[0] - point_b[0],
        point_c[1] - point_b[1]
    )

    dot_product = (
        ba[0] * bc[0]
        + ba[1] * bc[1]
    )

    magnitude_ba = math.sqrt(
        ba[0] ** 2 + ba[1] ** 2
    )

    magnitude_bc = math.sqrt(
        bc[0] ** 2 + bc[1] ** 2
    )

    if magnitude_ba == 0 or magnitude_bc == 0:
        return 0.0

    cosine = dot_product / (
        magnitude_ba * magnitude_bc
    )

    # Protect against floating-point errors.
    cosine = max(-1.0, min(1.0, cosine))

    return math.degrees(
        math.acos(cosine)
    )


def calculate_shoulder_tilt(left_shoulder, right_shoulder):
    """
    Calculate the shoulder tilt angle.

    Returns:
        Absolute tilt in degrees.
    """

    dx = right_shoulder[0] - left_shoulder[0]
    dy = right_shoulder[1] - left_shoulder[1]

    if dx == 0:
        return 90.0

    angle = math.degrees(
        math.atan2(abs(dy), abs(dx))
    )

    return angle


def calculate_body_lean(
    left_shoulder,
    right_shoulder,
    left_hip,
    right_hip
):
    """
    Estimate body lean by comparing the center
    of the shoulders with the center of the hips.

    Returns:
        Lean angle in degrees.
    """

    shoulder_center = (
        (left_shoulder[0] + right_shoulder[0]) / 2,
        (left_shoulder[1] + right_shoulder[1]) / 2
    )

    hip_center = (
        (left_hip[0] + right_hip[0]) / 2,
        (left_hip[1] + right_hip[1]) / 2
    )

    dx = shoulder_center[0] - hip_center[0]
    dy = hip_center[1] - shoulder_center[1]

    if dy == 0:
        return 90.0

    return abs(
        math.degrees(
            math.atan2(dx, dy)
        )
    )


def analyze_posture(keypoints):
    """
    Analyze presenter posture from YOLO pose keypoints.

    Expected keypoint indices follow the COCO format:

        5  = left shoulder
        6  = right shoulder
        11 = left hip
        12 = right hip

    keypoints should contain (x, y) coordinates.
    """

    left_shoulder = keypoints[5]
    right_shoulder = keypoints[6]
    left_hip = keypoints[11]
    right_hip = keypoints[12]

    shoulder_tilt = calculate_shoulder_tilt(
        left_shoulder,
        right_shoulder
    )

    body_lean = calculate_body_lean(
        left_shoulder,
        right_shoulder,
        left_hip,
        right_hip
    )

    # Simple initial interpretation.
    if shoulder_tilt < 5 and body_lean < 5:
        posture_status = "Good"

    elif shoulder_tilt < 10 and body_lean < 10:
        posture_status = "Slightly misaligned"

    else:
        posture_status = "Needs adjustment"

    return {
        "shoulder_tilt_degrees": round(
            shoulder_tilt, 2
        ),
        "body_lean_degrees": round(
            body_lean, 2
        ),
        "posture_status": posture_status,
    }