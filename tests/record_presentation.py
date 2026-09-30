import sounddevice as sd
from scipy.io.wavfile import write


SAMPLE_RATE = 44100
DURATION = 60

print("=" * 50)
print("SNAPSPEAK PRESENTATION RECORDING")
print("=" * 50)

print("\nYou will have 60 seconds to present.")
print("Speak naturally about your presentation.")
print("Press Ctrl+C if you want to stop early.")

input("\nPress ENTER to start recording...")

print("\n🔴 RECORDING...")
print("Start presenting now!")

recording = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="int16"
)

sd.wait()

output_file = "data/presentation_test.wav"

write(
    output_file,
    SAMPLE_RATE,
    recording
)

print("\nRecording completed!")
print(f"Saved to: {output_file}")