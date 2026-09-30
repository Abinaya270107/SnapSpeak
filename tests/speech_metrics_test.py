from app.analysis.speech_metrics import (
    calculate_speech_metrics,
    print_speech_metrics,
)


TRANSCRIPT = """
Hello, this is SnapSpeak microphone test.
Basically, I am practicing my presentation.
Um, I want to speak clearly and confidently.
"""

DURATION_SECONDS = 10

# Simulated Whisper segments.
# Each segment has a start and end timestamp.
SEGMENTS = [
    {
        "start": 0.0,
        "end": 2.0,
        "text": "Hello, this is SnapSpeak microphone test."
    },
    {
        "start": 2.8,
        "end": 5.0,
        "text": "Basically, I am practicing my presentation."
    },
    {
        "start": 6.2,
        "end": 9.0,
        "text": "Um, I want to speak clearly and confidently."
    },
]


metrics = calculate_speech_metrics(
    TRANSCRIPT,
    DURATION_SECONDS,
    SEGMENTS
)

print_speech_metrics(metrics)