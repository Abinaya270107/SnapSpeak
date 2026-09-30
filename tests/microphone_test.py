import sounddevice as sd
import wave

SAMPLE_RATE = 16000
DURATION = 5
OUTPUT_FILE = "data/test_recording.wav"
print("========================================")
print("SNAPSPEAK MICROPHONE TEST")
print("========================================")
print(f"\nRecording for {DURATION} seconds...")
print("Please speak normally.")

recording = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="int16"
)

sd.wait()

print("Recording completed.")

with wave.open(OUTPUT_FILE, "wb") as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(SAMPLE_RATE)
    wav_file.writeframes(recording.tobytes())

print(f"Saved recording to: {OUTPUT_FILE}")