from app.audio.speech_analyzer import SpeechAnalyzer
from app.analysis.speech_metrics import print_speech_metrics


AUDIO_FILE = "data/test_recording.wav"


print("=" * 50)
print("SNAPSPEAK SPEECH ANALYZER TEST")
print("=" * 50)


analyzer = SpeechAnalyzer(model_name="base")

print("\nAnalyzing audio...")

result = analyzer.analyze(AUDIO_FILE)


print("\n" + "-" * 40)
print("TRANSCRIPT")
print("-" * 40)

print(result["transcript"])


print_speech_metrics(result["metrics"])


print("\nSpeech analyzer test completed.")