from app.analysis.session import PresentationSession


session = PresentationSession()


session.set_presentation(
    pdf_file="data/test_presentation.pdf",
    topics=[
        ("deep learning", 2),
        ("severity assessment", 3),
        ("temperature scaling", 3),
    ]
)


speech_result = {
    "transcript": "Today I will explain deep learning.",
    "metrics": {
        "word_count": 7,
        "words_per_minute": 80,
        "filler_count": 0,
    }
}


session.set_speech_result(
    audio_file="data/presentation_test.wav",
    speech_result=speech_result
)


posture_result = {
    "samples": 100,
    "good_posture_percentage": 82.0,
}


session.set_posture_result(
    posture_result
)


content_result = {
    "coverage_percentage": 66.7,
    "covered_count": 2,
    "missed_count": 1,
}


session.set_content_result(
    content_result
)


summary = session.get_summary()


print("=" * 60)
print("SNAPSPEAK PRESENTATION SESSION")
print("=" * 60)

print(f"\nPresentation : {summary['pdf_file']}")
print(f"Audio        : {summary['audio_file']}")
print(f"Topics       : {summary['topic_count']}")
print(f"Transcript   : {summary['transcript']}")

print("\nSpeech:")
print(summary["speech"])

print("\nPosture:")
print(summary["posture"])

print("\nContent:")
print(summary["content"])

print("\n" + "=" * 60)
print("Session integration test completed.")
print("=" * 60)