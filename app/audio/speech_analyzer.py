
import re
import wave

import whisper

from app.analysis.speech_metrics import calculate_speech_metrics


class SpeechAnalyzer:
    def __init__(self, model_name="small"):
        print(f"Loading Whisper {model_name} model...")
        self.model = whisper.load_model(model_name)
        print("Whisper model loaded.")

    def get_audio_duration(self, audio_file):
        with wave.open(audio_file, "rb") as wav_file:
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()

        if sample_rate <= 0:
            raise ValueError("Invalid audio sample rate.")

        return frames / sample_rate

    def clean_repeated_phrases(self, text):
        words = text.split()

        if len(words) < 12:
            return text.strip()

        cleaned_words = []
        i = 0

        while i < len(words):
            repeated = False
            max_block_size = min(20, (len(words) - i) // 2)

            for block_size in range(max_block_size, 5, -1):
                first_block = words[i:i + block_size]
                second_block = words[
                    i + block_size:i + (2 * block_size)
                ]

                if len(second_block) != block_size:
                    continue

                normalize = lambda block: [
                    re.sub(r"[^\w']", "", word.lower())
                    for word in block
                ]

                if normalize(first_block) == normalize(second_block):
                    cleaned_words.extend(first_block)
                    i += 2 * block_size
                    repeated = True
                    break

            if not repeated:
                cleaned_words.append(words[i])
                i += 1

        return " ".join(cleaned_words).strip()

    def clean_transcript(self, transcript):
        if not transcript:
            return ""

        text = re.sub(r"\s+", " ", transcript.strip())
        return self.clean_repeated_phrases(text)

    def analyze(self, audio_file):
        duration = self.get_audio_duration(audio_file)

        transcription_prompt = (
            "SnapSpeak, an AI presentation coach. "
            "Presentation coaching, speaking pace, speech analysis, "
            "filler words, posture analysis, computer vision, "
            "presentation content, on-device AI, confident speakers."
        )

        result = self.model.transcribe(
            audio_file,
            fp16=False,
            language="en",
            temperature=0,
            condition_on_previous_text=False,
            no_speech_threshold=0.6,
            compression_ratio_threshold=2.4,
            logprob_threshold=-1.0,
            initial_prompt=transcription_prompt,
        )

        raw_transcript = result.get("text", "").strip()
        transcript = self.clean_transcript(raw_transcript)
        segments = result.get("segments", [])

        metrics = calculate_speech_metrics(
            transcript=transcript,
            duration_seconds=duration,
            segments=segments,
        )

        return {
            "transcript": transcript,
            "raw_transcript": raw_transcript,
            "segments": segments,
            "metrics": metrics,
        }