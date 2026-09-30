from app.content.pdf_extractor import PDFExtractor
from app.content.topic_extractor import TopicExtractor
from app.content.content_coverage import ContentCoverageAnalyzer
from app.content.topic_cleanup import TopicCleanup
from app.audio.speech_analyzer import SpeechAnalyzer


PDF_FILE = "data/test_presentation.pdf"
AUDIO_FILE = "data/presentation_test.wav"

print("=" * 60)
print("SNAPSPEAK CONTENT INTELLIGENCE PIPELINE")
print("=" * 60)


# --------------------------------------------------
# STEP 1: Extract presentation content
# --------------------------------------------------

print("\n[1/4] Extracting presentation content...")

pdf_extractor = PDFExtractor()

pages = pdf_extractor.extract(
    PDF_FILE
)

print(
    f"Pages extracted: {len(pages)}"
)


# --------------------------------------------------
# STEP 2: Extract presentation topics
# --------------------------------------------------

print("\n[2/4] Extracting presentation topics...")

topic_extractor = TopicExtractor()
from app.content.topic_cleanup import TopicCleanup


presentation_topics = topic_extractor.extract_presentation_topics(
    pages,
    phrase_count=10,
    keyword_count=5
)

topic_cleanup = TopicCleanup()

cleaned_topics = topic_cleanup.clean(
    presentation_topics
)

topics = [
    (
        item["topic"],
        item["frequency"]
    )
    for item in cleaned_topics
]

print("\nPresentation topics:")

for topic, count in topics:
    print(f"  - {topic} ({count})")


# --------------------------------------------------
# STEP 3: Transcribe speech
# --------------------------------------------------

print("\n[3/4] Transcribing presentation audio...")

speech_analyzer = SpeechAnalyzer(
    model_name="base"
)

speech_result = speech_analyzer.analyze(
    AUDIO_FILE
)

transcript = speech_result["transcript"]

print("\nTranscript:")
print(transcript)


# --------------------------------------------------
# STEP 4: Calculate content coverage
# --------------------------------------------------

print("\n[4/4] Calculating content coverage...")

coverage_analyzer = ContentCoverageAnalyzer()

coverage_result = coverage_analyzer.analyze(
    topics,
    transcript
)

coverage_analyzer.print_report(
    coverage_result
)


print("\nContent intelligence pipeline completed.")