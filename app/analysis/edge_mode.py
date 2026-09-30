"""
SnapSpeak Edge Mode

Stores the Snapdragon deployment profile used by SnapSpeak.

Important:
- The current development laptop runs the fallback CPU path.
- Snapdragon performance numbers below come from Qualcomm AI Hub
  profiles and are not measured on the developer laptop.
"""


# --------------------------------------------------
# Snapdragon deployment profiles
# --------------------------------------------------

SNAPDRAGON_PROFILES = {
    "YOLO11 Pose": {
        "model": "yolov11_pose",
        "device": "Snapdragon X Elite CRD",
        "os": "Windows 11",
        "compute": "NPU",
        "runtime": "QNN",
        "inference_ms": 5.19,
        "peak_memory_mb": 2,
        "source": "Qualcomm AI Hub",
    },

    "YOLO11 Pose - alternate profile": {
        "model": "yolov11_pose",
        "device": "Snapdragon X Elite CRD",
        "os": "Windows 11",
        "compute": "NPU",
        "runtime": "QNN",
        "inference_ms": 6.52,
        "peak_memory_mb": 9,
        "source": "Qualcomm AI Hub",
    },
}


# --------------------------------------------------
# Runtime modes
# --------------------------------------------------

RUNTIME_MODES = {
    "CPU Fallback": {
        "description": (
            "Local development mode using the available CPU/GPU "
            "runtime on the current PC."
        ),
        "verified_locally": True,
    },

    "Snapdragon NPU": {
        "description": (
            "Deployment target using Qualcomm QNN on a "
            "Snapdragon NPU."
        ),
        "verified_locally": False,
    },
}


# --------------------------------------------------
# Public helpers
# --------------------------------------------------

def get_runtime_mode():
    """
    Return the runtime mode used by the current development build.

    The current development machine does not contain a Snapdragon
    NPU, so the application uses the CPU fallback path.
    """

    return "CPU Fallback"


def get_snapdragon_profile(model_name="YOLO11 Pose"):
    """
    Return Qualcomm AI Hub deployment evidence for a model.
    """

    return SNAPDRAGON_PROFILES.get(model_name)


def get_edge_summary():
    """
    Return a compact summary suitable for the Streamlit UI.
    """

    profile = get_snapdragon_profile()

    return {
        "current_mode": get_runtime_mode(),
        "target_device": profile["device"],
        "target_os": profile["os"],
        "compute_unit": profile["compute"],
        "runtime": profile["runtime"],
        "model": profile["model"],
        "inference_ms": profile["inference_ms"],
        "peak_memory_mb": profile["peak_memory_mb"],
        "source": profile["source"],
        "locally_verified": RUNTIME_MODES[
            "CPU Fallback"
        ]["verified_locally"],
    }


def print_edge_summary():
    """
    Print the Edge Mode deployment information.
    """

    summary = get_edge_summary()

    print("\n" + "=" * 55)
    print("SNAPSPEAK EDGE MODE")
    print("=" * 55)

    print(
        f"\nCurrent Runtime : "
        f"{summary['current_mode']}"
    )

    print(
        f"Target Device   : "
        f"{summary['target_device']}"
    )

    print(
        f"Target OS       : "
        f"{summary['target_os']}"
    )

    print(
        f"Compute Unit    : "
        f"{summary['compute_unit']}"
    )

    print(
        f"Runtime         : "
        f"{summary['runtime']}"
    )

    print(
        f"Model           : "
        f"{summary['model']}"
    )

    print(
        f"AI Hub Inference: "
        f"{summary['inference_ms']} ms"
    )

    print(
        f"Peak Memory     : "
        f"{summary['peak_memory_mb']} MB"
    )

    print(
        f"Evidence Source : "
        f"{summary['source']}"
    )

    print(
        "\nNote: Snapdragon performance values are "
        "Qualcomm AI Hub profile measurements."
    )

    print(
        "They are not measurements from the current "
        "development laptop."
    )

    print("\n" + "=" * 55)


if __name__ == "__main__":
    print_edge_summary()