from app.vision.posture_analyzer import analyze_posture


# Simulated upright presenter.
keypoints = [None] * 17

keypoints[5] = (100, 100)   # left shoulder
keypoints[6] = (200, 100)   # right shoulder

keypoints[11] = (110, 200)  # left hip
keypoints[12] = (190, 200)  # right hip


result = analyze_posture(keypoints)


print("=" * 50)
print("SNAPSPEAK POSTURE ANALYSIS TEST")
print("=" * 50)

print(f"\nShoulder Tilt : {result['shoulder_tilt_degrees']}°")
print(f"Body Lean     : {result['body_lean_degrees']}°")
print(f"Posture       : {result['posture_status']}")

print("\nPosture analysis completed.")