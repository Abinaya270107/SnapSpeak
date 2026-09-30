import sounddevice as sd
import wave
import numpy as np

OUTPUT_FILE = "data/mic_test.wav"

SAMPLE_RATE = 44100
CHANNELS = 1
DURATION = 10

print("=" * 50)
print("SNAPSPEAK MICROPHONE TEST")
print("=" * 50)

print("\nRecording for 10 seconds...")
print("Speak normally now.")

audio = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    dtype="int16"
)

sd.wait()

print("\nRecording completed.")

with wave.open(OUTPUT_FILE, "wb") as wav_file:
    wav_file.setnchannels(CHANNELS)
    wav_file.setsampwidth(2)
    wav_file.setframerate(SAMPLE_RATE)
    wav_file.writeframes(audio.tobytes())

print(f"Audio saved to: {OUTPUT_FILE}")