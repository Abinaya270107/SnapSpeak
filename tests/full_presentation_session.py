import os
import sys
import time
import wave
import threading

import cv2
import numpy as np
import sounddevice as sd


PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
sys.path.insert(0, PROJECT_ROOT)


from app.content.pdf_extractor import PDFExtractor
from app.content.topic_extractor import TopicExtractor
from app.content.topic_cleanup import TopicCleanup
from app.content.content_coverage import ContentCoverageAnalyzer

from app.audio.speech_analyzer import SpeechAnalyzer

from app.vision.pose_analyzer import PoseAnalyzer

from app.analysis.posture_metrics import calculate_posture_session


PDF_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "test_presentation.pdf"
)

RAW_AUDIO_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "full_presentation_audio_raw.wav"
)

AUDIO_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "full_presentation_audio.wav"
)


SAMPLE_RATE = 44100
CHANNELS = 1

MICROPHONE_DEVICE = 18

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
        self.duration = 0

        self._stop_event = threading.Event()
        self._thread = None

    def _record(self):

        print(
            f"Using microphone device: "
            f"{self.device}"
        )

        device_info = sd.query_devices(
            self.device
        )

        print(
            f"Microphone: "
            f"{device_info['name']}"
        )

        print(
            f"Input channels available: "
            f"{device_info['max_input_channels']}"
        )

        try:

            frames = int(
                self.max_duration
                * self.sample_rate
            )

            print(
                "\nMicrophone recording started."
            )

            recording = sd.rec(
                frames,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="int16",
                device=self.device,
            )

            start_time = time.time()

            while not self._stop_event.is_set():

                elapsed = (
                    time.time()
                    - start_time
                )

                if elapsed >= self.max_duration:
                    break

                time.sleep(0.05)

            sd.stop()

            actual_frames = int(
                min(
                    time.time() - start_time,
                    self.max_duration,
                )
                * self.sample_rate
            )

            actual_frames = max(
                0,
                min(
                    actual_frames,
                    len(recording),
                ),
            )

            self.audio_data = recording[
                :actual_frames
            ].copy()

            self.duration = (
                actual_frames
                / self.sample_rate
            )

            print(
                f"\nMicrophone recording captured: "
                f"{self.duration:.2f} seconds"
            )

        except Exception as error:

            print(
                f"\nMicrophone recording error: "
                f"{error}"
            )

            self.audio_data = None
            self.duration = 0

    def start(self):

        self._stop_event.clear()

        self._thread = threading.Thread(
            target=self._record,
            daemon=True,
        )

        self._thread.start()

    def stop(self):

        self._stop_event.set()

        if self._thread is not None:

            self._thread.join()

        print(
            "Microphone recording stopped."
        )

    def save(self, output_file):

        if self.audio_data is None:

            print(
                "WARNING: No audio data recorded."
            )

            return 0.0

        audio_data = (
            self.audio_data.reshape(-1)
        )

        with wave.open(
            output_file,
            "wb",
        ) as wav_file:

            wav_file.setnchannels(
                self.channels
            )

            wav_file.setsampwidth(2)

            wav_file.setframerate(
                self.sample_rate
            )

            wav_file.writeframes(
                audio_data.tobytes()
            )

        return self.duration


def normalize_audio(
    input_file,
    output_file,
    target_peak=0.85,
):

    print(
        "\nNormalizing microphone audio..."
    )

    with wave.open(
        input_file,
        "rb",
    ) as wav_file:

        sample_rate = (
            wav_file.getframerate()
        )

        channels = (
            wav_file.getnchannels()
        )

        sample_width = (
            wav_file.getsampwidth()
        )

        frames = (
            wav_file.getnframes()
        )

        raw_audio = (
            wav_file.readframes(frames)
        )

    audio = (
        np.frombuffer(
            raw_audio,
            dtype=np.int16,
        ).astype(np.float32)
    )

    if len(audio) == 0:

        print(
            "ERROR: Audio file is empty."
        )

        return {
            "quality": "Very low",
            "original_peak": 0.0,
            "original_rms": 0.0,
            "gain": 0.0,
            "normalized_peak": 0.0,
            "normalized_rms": 0.0,
        }

    original_peak = float(
        np.max(np.abs(audio))
    )

    original_rms = float(
        np.sqrt(
            np.mean(audio ** 2)
        )
    )

    print(
        f"Original peak: "
        f"{original_peak:.2f}"
    )

    print(
        f"Original RMS: "
        f"{original_rms:.2f}"
    )

    # --------------------------------------------------
    # AUDIO QUALITY CHECK
    # --------------------------------------------------

    if original_peak == 0:

        print(
            "\nAudio quality: VERY LOW"
        )

        print(
            "No microphone signal detected."
        )

        return {
            "quality": "Very low",
            "original_peak": original_peak,
            "original_rms": original_rms,
            "gain": 0.0,
            "normalized_peak": 0.0,
            "normalized_rms": 0.0,
        }

    # These thresholds are based on the int16
    # microphone signal before normalization.
    #
    # RMS < 100:
    #     Very quiet signal.
    #
    # RMS 100-250:
    #     Low signal.
    #
    # RMS >= 250:
    #     Healthy signal for this prototype.

    if original_rms < 100:

        audio_quality = "Very low"

    elif original_rms < 250:

        audio_quality = "Low"

    else:

        audio_quality = "Good"

    print(
        f"\nAudio quality: "
        f"{audio_quality}"
    )

    if audio_quality == "Very low":

        print(
            "WARNING: Microphone input is "
            "very quiet."
        )

        print(
            "Check microphone selection, "
            "distance, and input volume."
        )

    elif audio_quality == "Low":

        print(
            "WARNING: Microphone input is "
            "quieter than expected."
        )

        print(
            "Automatic gain will be applied "
            "within the safety limit."
        )

    else:

        print(
            "Microphone input level is healthy."
        )

    desired_peak = (
        32767.0
        * target_peak
    )

    gain = (
        desired_peak
        / original_peak
    )

    MAX_GAIN = 10.0

    if gain > MAX_GAIN:

        print(
            f"\nCalculated gain "
            f"{gain:.2f}x exceeds "
            f"safety limit."
        )

        gain = MAX_GAIN

    normalized_audio = np.clip(
        audio * gain,
        -32768,
        32767,
    ).astype(np.int16)

    normalized_peak = float(
        np.max(
            np.abs(
                normalized_audio
            )
        )
    )

    normalized_rms = float(
        np.sqrt(
            np.mean(
                normalized_audio.astype(
                    np.float32
                ) ** 2
            )
        )
    )

    print(
        f"Applied gain: "
        f"{gain:.2f}x"
    )

    print(
        f"Normalized peak: "
        f"{normalized_peak:.2f}"
    )

    print(
        f"Normalized RMS: "
        f"{normalized_rms:.2f}"
    )

    with wave.open(
        output_file,
        "wb",
    ) as wav_file:

        wav_file.setnchannels(
            channels
        )

        wav_file.setsampwidth(
            sample_width
        )

        wav_file.setframerate(
            sample_rate
        )

        wav_file.writeframes(
            normalized_audio.tobytes()
        )

    print(
        f"Normalized audio saved: "
        f"{output_file}"
    )

    return {
        "quality": audio_quality,
        "original_peak": round(
            original_peak,
            2,
        ),
        "original_rms": round(
            original_rms,
            2,
        ),
        "gain": round(
            gain,
            2,
        ),
        "normalized_peak": round(
            normalized_peak,
            2,
        ),
        "normalized_rms": round(
            normalized_rms,
            2,
        ),
    }


def extract_presentation_topics(pages):

    topic_extractor = TopicExtractor()

    raw_topics = (
        topic_extractor.extract_presentation_topics(
            pages,
            phrase_count=10,
            keyword_count=5,
        )
    )

    print("\nRaw topics:")

    for topic in raw_topics:

        print(topic)

    topic_cleanup = TopicCleanup()

    cleaned_topics = (
        topic_cleanup.clean(
            raw_topics
        )
    )

    print("\nCleaned topics:")

    for topic in cleaned_topics:

        print(topic)

    return cleaned_topics


def main():

    print("=" * 60)
    print(
        "SNAPSPEAK - FULL PRESENTATION SESSION"
    )
    print("=" * 60)

    print("\nPDF:")
    print(PDF_FILE)

    print("\nRaw audio:")
    print(RAW_AUDIO_FILE)

    print("\nProcessed audio:")
    print(AUDIO_FILE)

    # --------------------------------------------------
    # STEP 1 - PRESENTATION CONTENT
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print(
        "STEP 1 - PRESENTATION CONTENT"
    )
    print("=" * 60)

    pdf_extractor = PDFExtractor()

    pages = pdf_extractor.extract(
        PDF_FILE
    )

    print(
        f"\nPages extracted: "
        f"{len(pages)}"
    )

    full_text = "\n".join(
        page["text"]
        for page in pages
        if page["text"]
    )

    print(
        f"Total text characters: "
        f"{len(full_text)}"
    )

    print(
        "\nExtracting presentation topics..."
    )

    presentation_topics = (
        extract_presentation_topics(
            pages
        )
    )

    print(
        f"\nFinal topic count: "
        f"{len(presentation_topics)}"
    )

    # --------------------------------------------------
    # STEP 2 - LOAD MODELS
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print(
        "STEP 2 - LOADING AI MODELS"
    )
    print("=" * 60)

    print("\nLoading Whisper...")

    speech_analyzer = SpeechAnalyzer(
        model_name="small"
    )

    print(
        "\nLoading YOLO11 Pose..."
    )

    pose_analyzer = PoseAnalyzer()

    # --------------------------------------------------
    # STEP 3 - START PRESENTATION
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print(
        "STEP 3 - STARTING PRESENTATION"
    )
    print("=" * 60)

    print("\nOpening webcam...")

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print(
            "\nERROR: Could not open webcam."
        )

        return

    recorder = AudioRecorder()

    print(
        "\nStarting microphone recording..."
    )

    recorder.start()

    print("\n" + "-" * 60)

    print(
        "PRESENT YOUR TOPIC NOW"
    )

    print(
        "Press Q in the webcam window "
        "to finish."
    )

    print("-" * 60)

    posture_history = []

    session_start = time.time()

    try:

        while True:

            success, frame = (
                camera.read()
            )

            if not success:

                print(
                    "\nERROR: Could not "
                    "read webcam frame."
                )

                break

            elapsed = (
                time.time()
                - session_start
            )

            if (
                elapsed
                >= MAX_DURATION_SECONDS
            ):

                print(
                    "\nMaximum presentation "
                    "duration reached."
                )

                break

            # ------------------------------------------
            # POSTURE ANALYSIS
            # ------------------------------------------

            posture, result = (
                pose_analyzer.analyze_frame(
                    frame
                )
            )

            if posture is not None:

                posture_history.append(
                    posture
                )

            # ------------------------------------------
            # DISPLAY
            # ------------------------------------------

            annotated_frame = (
                result.plot()
            )

            if posture is not None:

                cv2.putText(
                    annotated_frame,
                    (
                        f"Posture: "
                        f"{posture['posture_status']}"
                    ),
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

            key = (
                cv2.waitKey(1)
                & 0xFF
            )

            if key == ord("q"):

                print(
                    "\nQ pressed. "
                    "Ending presentation..."
                )

                break

    finally:

        camera.release()

        cv2.destroyAllWindows()

        print(
            "\nStopping microphone "
            "recording..."
        )

        recorder.stop()

    # --------------------------------------------------
    # STEP 4 - AUDIO PROCESSING
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print(
        "STEP 4 - AUDIO PROCESSING"
    )
    print("=" * 60)

    raw_duration = recorder.save(
        RAW_AUDIO_FILE
    )

    print(
        f"\nRaw audio saved: "
        f"{RAW_AUDIO_FILE}"
    )

    print(
        f"Raw recorded duration: "
        f"{raw_duration:.2f} seconds"
    )

    audio_quality = normalize_audio(
        input_file=RAW_AUDIO_FILE,
        output_file=AUDIO_FILE,
    )

    print("\nAudio summary:")
    print("-" * 60)

    print(
        f"Audio quality: "
        f"{audio_quality['quality']}"
    )

    print(
        f"Original RMS: "
        f"{audio_quality['original_rms']}"
    )

    print(
        f"Applied gain: "
        f"{audio_quality['gain']}x"
    )

    print(
        "\nAnalyzing normalized speech "
        "with Whisper Small..."
    )

    speech_result = (
        speech_analyzer.analyze(
            AUDIO_FILE
        )
    )

    transcript = speech_result[
        "transcript"
    ]

    speech_metrics = speech_result[
        "metrics"
    ]

    print("\nTranscript:")
    print("-" * 60)
    print(transcript)

    print("\nSpeech metrics:")
    print("-" * 60)

    print(
        f"Words spoken: "
        f"{speech_metrics['word_count']}"
    )

    print(
        f"Duration: "
        f"{speech_metrics['duration_seconds']} sec"
    )

    print(
        f"WPM: "
        f"{speech_metrics['words_per_minute']}"
    )

    print(
        f"Filler words: "
        f"{speech_metrics['filler_count']}"
    )

    print(
        f"Pause count: "
        f"{speech_metrics['pause_count']}"
    )

    print(
        f"Total pause time: "
        f"{speech_metrics['total_pause_seconds']} sec"
    )

    # --------------------------------------------------
    # STEP 5 - VISUAL ANALYSIS
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print(
        "STEP 5 - VISUAL ANALYSIS"
    )
    print("=" * 60)

    posture_metrics = (
        calculate_posture_session(
            posture_history
        )
    )

    print(
        "\nPosture session metrics:"
    )

    print("-" * 60)

    print(
        f"Samples: "
        f"{posture_metrics['samples']}"
    )

    print(
        f"Average shoulder tilt: "
        f"{posture_metrics['average_shoulder_tilt']} deg"
    )

    print(
        f"Average body lean: "
        f"{posture_metrics['average_body_lean']} deg"
    )

    print(
        f"Good posture: "
        f"{posture_metrics['good_posture_percentage']}%"
    )

    print(
        f"Slightly misaligned: "
        f"{posture_metrics['slightly_misaligned_percentage']}%"
    )

    print(
        f"Needs adjustment: "
        f"{posture_metrics['needs_adjustment_percentage']}%"
    )

    # --------------------------------------------------
    # STEP 6 - CONTENT COVERAGE
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print(
        "STEP 6 - CONTENT COVERAGE"
    )
    print("=" * 60)

    content_topics = [
        (
            item["topic"],
            item["frequency"],
        )
        for item in presentation_topics
    ]

    content_analyzer = (
        ContentCoverageAnalyzer()
    )

    content_result = (
        content_analyzer.analyze(
            topics=content_topics,
            transcript=transcript,
            threshold=0.35,
        )
    )

    print("\nContent coverage:")
    print("-" * 60)

    print(
        f"Total topics: "
        f"{content_result['total_topics']}"
    )

    print(
        f"Covered topics: "
        f"{content_result['covered_count']}"
    )

    print(
        f"Partially covered topics: "
        f"{content_result['partial_count']}"
    )

    print(
        f"Missed topics: "
        f"{content_result['missed_count']}"
    )

    print(
        f"Coverage: "
        f"{content_result['coverage_percentage']}%"
    )

    print("\nCovered topics:")

    if content_result[
        "covered_topics"
    ]:

        for item in content_result[
            "covered_topics"
        ]:

            print(
                f"  - {item['topic']} "
                f"({item['overlap']}%)"
            )

    else:

        print("  None")

    print(
        "\nPartially covered topics:"
    )

    if content_result[
        "partial_topics"
    ]:

        for item in content_result[
            "partial_topics"
        ]:

            print(
                f"  - {item['topic']} "
                f"({item['overlap']}%)"
            )

    else:

        print("  None")

    print("\nMissed topics:")

    if content_result[
        "missed_topics"
    ]:

        for item in content_result[
            "missed_topics"
        ]:

            print(
                f"  - {item['topic']} "
                f"({item['overlap']}%)"
            )

    else:

        print("  None")

    # --------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print(
        "SNAP-SPEAK SESSION SUMMARY"
    )
    print("=" * 60)

    print(
        f"\nPresentation pages: "
        f"{len(pages)}"
    )

    print(
        f"Presentation topics: "
        f"{len(presentation_topics)}"
    )

    print(
        f"Speech duration: "
        f"{speech_metrics['duration_seconds']} sec"
    )

    print(
        f"Words spoken: "
        f"{speech_metrics['word_count']}"
    )

    print(
        f"Speaking pace: "
        f"{speech_metrics['words_per_minute']} WPM"
    )

    print(
        f"Filler words: "
        f"{speech_metrics['filler_count']}"
    )

    print(
        f"Audio quality: "
        f"{audio_quality['quality']}"
    )

    print(
        f"Good posture: "
        f"{posture_metrics['good_posture_percentage']}%"
    )

    print(
        f"Content coverage: "
        f"{content_result['coverage_percentage']}%"
    )

    print("\n" + "=" * 60)
    print("SESSION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()