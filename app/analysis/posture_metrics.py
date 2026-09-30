def calculate_posture_session(metrics_history):
    """
    Calculate posture statistics for an entire presentation rehearsal.
    """

    if not metrics_history:
        return {
            "samples": 0,
            "average_shoulder_tilt": 0,
            "average_body_lean": 0,
            "good_posture_percentage": 0,
            "slightly_misaligned_percentage": 0,
            "needs_adjustment_percentage": 0,
        }

    shoulder_tilts = [
        item["shoulder_tilt_degrees"]
        for item in metrics_history
    ]

    body_leans = [
        item["body_lean_degrees"]
        for item in metrics_history
    ]

    total = len(metrics_history)

    good_count = sum(
        1
        for item in metrics_history
        if item["posture_status"] == "Good"
    )

    slightly_count = sum(
        1
        for item in metrics_history
        if item["posture_status"] == "Slightly misaligned"
    )

    needs_adjustment_count = sum(
        1
        for item in metrics_history
        if item["posture_status"] == "Needs adjustment"
    )

    return {
        "samples": total,

        "average_shoulder_tilt": round(
            sum(shoulder_tilts) / total,
            2
        ),

        "average_body_lean": round(
            sum(body_leans) / total,
            2
        ),

        "good_posture_percentage": round(
            (good_count / total) * 100,
            1
        ),

        "slightly_misaligned_percentage": round(
            (slightly_count / total) * 100,
            1
        ),

        "needs_adjustment_percentage": round(
            (needs_adjustment_count / total) * 100,
            1
        ),
    }


def print_posture_session(metrics):
    print("\n" + "=" * 50)
    print("SNAPSPEAK POSTURE SESSION REPORT")
    print("=" * 50)

    print(f"\nSamples Analyzed       : {metrics['samples']}")

    print(
        f"Average Shoulder Tilt : "
        f"{metrics['average_shoulder_tilt']}°"
    )

    print(
        f"Average Body Lean     : "
        f"{metrics['average_body_lean']}°"
    )

    print(
        f"Good Posture          : "
        f"{metrics['good_posture_percentage']}%"
    )

    print(
        f"Slightly Misaligned   : "
        f"{metrics['slightly_misaligned_percentage']}%"
    )

    print(
        f"Needs Adjustment      : "
        f"{metrics['needs_adjustment_percentage']}%"
    )

    print("\n" + "=" * 50)