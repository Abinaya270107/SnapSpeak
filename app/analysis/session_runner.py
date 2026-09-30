
import os
import time
import wave
import threading

import cv2
import numpy as np
import sounddevice as sd

from app.content.pdf_extractor import PDFExtractor
from app.content.topic_extractor import TopicExtractor
from app.content.topic_cleanup import TopicCleanup
from app.content.content_coverage import ContentCoverageAnalyzer

from app.audio.speech_analyzer import SpeechAnalyzer
from app.vision.pose_analyzer import PoseAnalyzer

from app.analysis.posture_metrics import calculate_posture_session
from app.analysis.recommendations import RecommendationEngine


SAMPLE_RATE = 44100
CHANNELS = 1
MICROPHONE_DEVICE = 1
MAX_DURATION_SECONDS = 180


class AudioRecorder:
    def __init__(
        self,
        sample_rate=SAMPLE_RATE,
        channels=CHANNELS,
        device=MICROPHONE_DEVICE,
        max_duration=MAX_DURATION_SECONDS,
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.device = device
        self.max_duration = max_duration

        self.audio_data = None
        self.duration = 0.0
        self._stop_event = threading.Event()
        self._thread = None
        self.error = None

    def _record(self):
        try:
            device_info = sd.query_devices(self.device)
            print(f"Microphone: {device_info['name']}")

            frames = int(self.max_duration * self.sample_rate)

            recording = sd.rec(
                frames,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="int16",
                device=self.device,
            )

            start_time = time.time()

            while not self._stop_event.is_set():
                elapsed = time.time() - start_time

                if elapsed >= self.max_duration:
                    break

                time.sleep(0.05)

            sd.stop()

            elapsed = min(
                time.time() - start_time,
                self.max_duration,
            )

            actual_frames = int(elapsed * self.sample_rate)
            actual_frames = max(
                0,
                min(actual_frames, len(recording)),
            )

            self.audio_data = recording[:actual_frames].copy()
            self.duration = actual_frames / self.sample_rate

            if actual_frames == 0:
                raise RuntimeError(
                    "No audio frames were captured."
                )

        except Exception as error:
            self.error = str(error)
            self.audio_data = None
            self.duration = 0.0

            print(f"Microphone recording error: {error}")

    def start(self):
        self._stop_event.clear()
        self.audio_data = None
        self.duration = 0.0
        self.error = None

        self._thread = threading.Thread(
            target=self._record,
            daemon=True,
        )
        self._thread.start()

    def stop(self):
        self._stop_event.set()

        if self._thread is not None:
            self._thread.join()

    def save(self, output_file):
        if self.audio_data is None:
            return 0.0

        if len(self.audio_data) == 0:
            return 0.0

        output_directory = os.path.dirname(
            os.path.abspath(output_file)
        )
        os.makedirs(output_directory, exist_ok=True)

        audio_data = self.audio_data.reshape(-1)

        with wave.open(output_file, "wb") as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_data.tobytes())

        return self.duration


def normalize_audio(
    input_file,
    output_file,
    target_peak=0.85,
):
    """
    Normalize a newly recorded 16-bit PCM WAV file.

    Raises an exception for missing, empty, silent, or unsupported
    input instead of allowing a previous output file to be reused.
    """

    input_path = os.path.abspath(input_file)
    output_path = os.path.abspath(output_file)

    if os.path.normcase(input_path) == os.path.normcase(output_path):
        raise ValueError(
            "Input and output audio paths must be different."
        )

    # Remove an old normalized file before processing.
    # If processing fails, an old recording cannot be mistaken
    # for the output of the current session.
    if os.path.exists(output_path):
        os.remove(output_path)

    if not os.path.isfile(input_path):
        raise FileNotFoundError(
            f"Recorded audio file was not created: {input_path}"
        )

    if os.path.getsize(input_path) == 0:
        raise ValueError(
            "The recorded audio file is empty."
        )

    with wave.open(input_path, "rb") as wav_file:
        sample_rate = wav_file.getframerate()
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        frames = wav_file.getnframes()
        raw_audio = wav_file.readframes(frames)

    if sample_width != 2:
        raise ValueError(
            "Expected 16-bit PCM audio, but the recording "
            "uses an unsupported sample width."
        )

    if frames <= 0 or len(raw_audio) == 0:
        raise ValueError(
            "The recorded audio contains no frames."
        )

    if channels <= 0 or sample_rate <= 0:
        raise ValueError(
            "The recorded audio has invalid WAV metadata."
        )

    audio = np.frombuffer(
        raw_audio,
        dtype="<i2",
    ).astype(np.float32)

    if len(audio) == 0:
        raise ValueError(
            "No usable audio samples were found."
        )

    original_peak = float(np.max(np.abs(audio)))

    original_rms = float(
        np.sqrt(np.mean(audio ** 2))
    )

    if original_peak == 0:
        raise ValueError(
            "The microphone recording is completely silent. "
            "Check the selected microphone and try again."
        )

    if original_rms < 100:
        audio_quality = "Very low"
    elif original_rms < 200:
        audio_quality = "Low"
    else:
        audio_quality = "Good"

    if not 0 < target_peak <= 1:
        raise ValueError(
            "target_peak must be greater than 0 and at most 1."
        )

    desired_peak = 32767.0 * target_peak
    gain = desired_peak / original_peak

    MAX_GAIN = 10.0
    gain = min(gain, MAX_GAIN)

    normalized_audio = np.clip(
        audio * gain,
        -32768,
        32767,
    ).astype(np.int16)

    normalized_peak = float(
        np.max(np.abs(normalized_audio.astype(np.float32)))
    )

    normalized_rms = float(
        np.sqrt(
            np.mean(
                normalized_audio.astype(np.float32) ** 2
            )
        )
    )

    output_directory = os.path.dirname(output_path)
    os.makedirs(output_directory, exist_ok=True)

    with wave.open(output_path, "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(normalized_audio.tobytes())

    if (
        not os.path.isfile(output_path)
        or os.path.getsize(output_path) == 0
    ):
        raise RuntimeError(
            "The normalized audio file could not be created."
        )

    return {
        "quality": audio_quality,
        "original_peak": round(original_peak, 2),
        "original_rms": round(original_rms, 2),
        "gain": round(gain, 2),
        "normalized_peak": round(normalized_peak, 2),
        "normalized_rms": round(normalized_rms, 2),
    }


def extract_presentation_topics(pages):
    topic_extractor = TopicExtractor()

    raw_topics = topic_extractor.extract_presentation_topics(
        pages,
        phrase_count=10,
        keyword_count=5,
    )

    topic_cleanup = TopicCleanup()

    return topic_cleanup.clean(raw_topics)


def _remove_previous_audio_files(raw_audio_file, audio_file):
    """
    Remove designated temporary audio files from earlier sessions.

    The two paths must be different because the raw recording
    must remain available while the normalized file is created.
    """

    raw_path = os.path.abspath(raw_audio_file)
    normalized_path = os.path.abspath(audio_file)

    if os.path.normcase(raw_path) == os.path.normcase(normalized_path):
        raise ValueError(
            "Raw and normalized audio files must use different paths."
        )

    for path in (raw_path, normalized_path):
        if os.path.exists(path):
            os.remove(path)


def run_presentation_session(
    pdf_file,
    raw_audio_file,
    audio_file,
):
    # --------------------------------------------------
    # Validate paths and clear stale audio
    # --------------------------------------------------

    _remove_previous_audio_files(
        raw_audio_file,
        audio_file,
    )

    # --------------------------------------------------
    # Presentation content
    # --------------------------------------------------

    pdf_extractor = PDFExtractor()

    pages = pdf_extractor.extract(pdf_file)

    presentation_topics = extract_presentation_topics(pages)

    # --------------------------------------------------
    # Load AI models
    # --------------------------------------------------

    speech_analyzer = SpeechAnalyzer(
        model_name="small"
    )

    pose_analyzer = PoseAnalyzer()

    # --------------------------------------------------
    # Camera
    # --------------------------------------------------

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        camera.release()
        raise RuntimeError(
            "Could not open webcam. Check that your camera "
            "is connected and is not being used by another app."
        )

    recorder = AudioRecorder()
    posture_history = []
    session_start = time.time()

    try:
        recorder.start()

        while True:
            success, frame = camera.read()

            if not success:
                print(
                    "Warning: Could not read a webcam frame. "
                    "Ending the presentation session."
                )
                break

            elapsed = time.time() - session_start

            if elapsed >= MAX_DURATION_SECONDS:
                break

            posture, result = pose_analyzer.analyze_frame(frame)

            if posture is not None:
                posture_history.append(posture)

            annotated_frame = result.plot()

            if posture is not None:
                cv2.putText(
                    annotated_frame,
                    f"Posture: {posture['posture_status']}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2,
                )

                cv2.putText(
                    annotated_frame,
                    (
                        f"Tilt: "
                        f"{posture['shoulder_tilt_degrees']:.1f} deg"
                    ),
                    (20, 75),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )

                cv2.putText(
                    annotated_frame,
                    (
                        f"Lean: "
                        f"{posture['body_lean_degrees']:.1f} deg"
                    ),
                    (20, 110),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )

            else:
                cv2.putText(
                    annotated_frame,
                    "Posture: Person not detected",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2,
                )

            cv2.putText(
                annotated_frame,
                "Press Q to finish",
                (20, 150),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            cv2.imshow(
                "SnapSpeak - Presentation Session",
                annotated_frame,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()
        recorder.stop()

    # --------------------------------------------------
    # Save and validate the current recording
    # --------------------------------------------------

    raw_duration = recorder.save(raw_audio_file)

    if recorder.error is not None:
        raise RuntimeError(
            "Microphone recording failed: "
            f"{recorder.error}. Check the selected microphone "
            "and its Windows permissions, then try again."
        )

    if (
        recorder.audio_data is None
        or raw_duration <= 0
        or not os.path.isfile(raw_audio_file)
        or os.path.getsize(raw_audio_file) == 0
    ):
        raise RuntimeError(
            "No new audio recording was saved. "
            "Check your microphone, then record the presentation again."
        )

    # --------------------------------------------------
    # Normalize and validate the current recording
    # --------------------------------------------------

    audio_quality = normalize_audio(
        input_file=raw_audio_file,
        output_file=audio_file,
    )

    # --------------------------------------------------
    # Speech analysis
    # --------------------------------------------------

    speech_result = speech_analyzer.analyze(audio_file)

    transcript = speech_result["transcript"]
    speech_metrics = speech_result["metrics"]

    if not transcript or not transcript.strip():
        raise RuntimeError(
            "Speech recognition returned an empty transcript. "
            "Check the microphone recording and try again."
        )

    # --------------------------------------------------
    # Posture analysis
    # --------------------------------------------------

    posture_metrics = calculate_posture_session(
        posture_history
    )

    # --------------------------------------------------
    # Content coverage
    # --------------------------------------------------

    content_topics = [
        (item["topic"], item["frequency"])
        for item in presentation_topics
    ]

    content_analyzer = ContentCoverageAnalyzer()

    content_result = content_analyzer.analyze(
        topics=content_topics,
        transcript=transcript,
        threshold=0.35,
    )

    # --------------------------------------------------
    # Recommendations
    # --------------------------------------------------

    recommendation_engine = RecommendationEngine()

    recommendations = recommendation_engine.generate(
        speech_metrics=speech_metrics,
        posture_metrics=posture_metrics,
        content_result=content_result,
    )

    # --------------------------------------------------
    # Return complete session result
    # --------------------------------------------------

    return {
        "pages": pages,
        "presentation_topics": presentation_topics,
        "audio_quality": audio_quality,
        "raw_duration": round(raw_duration, 2),
        "speech_result": speech_result,
        "speech_metrics": speech_metrics,
        "posture_metrics": posture_metrics,
        "content_result": content_result,
        "recommendations": recommendations,
    }