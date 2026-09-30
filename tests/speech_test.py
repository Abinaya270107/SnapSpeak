import os
import wave

import whisper

from app.analysis.speech_metrics import (
    calculate_speech_metrics,
    print_speech_metrics,
)


AUDIO_FILE = "data/test_recording.wav"


print("=" * 50)
print("SNAPSPEAK REAL SPEECH ANALYSIS")
print("=" * 50)


# ----------------------------------------
# Get actual audio duration
# ----------------------------------------

with wave.open(AUDIO_FILE, "rb") as wav_file:
    frames = wav_file.getnframes()
    sample_rate = wav_file.getframerate()

duration_seconds = frames / sample_rate

print(f"\nAudio duration: {duration_seconds:.2f} seconds")


# ----------------------------------------
# Load Whisper
# ----------------------------------------

print("\nLoading Whisper Base model...")

model = whisper.load_model("base")

print("Model loaded.")


# ----------------------------------------
# Transcribe with timestamps
# ----------------------------------------

print("\nTranscribing audio...")

result = model.transcribe(
    AUDIO_FILE,
    fp16=False
)


transcript = result["text"].strip()
segments = result["segments"]


# ----------------------------------------
# Display transcript
# ----------------------------------------

print("\n" + "-" * 40)
print("TRANSCRIPT")
print("-" * 40)

print(transcript)


# ----------------------------------------
# Calculate metrics
# ----------------------------------------

metrics = calculate_speech_metrics(
    transcript=transcript,
    duration_seconds=duration_seconds,
    segments=segments
)


# ----------------------------------------
# Display analysis
# ----------------------------------------

print_speech_metrics(metrics)

print("\nSpeech analysis completed.")