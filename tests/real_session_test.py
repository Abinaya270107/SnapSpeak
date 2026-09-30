from app.analysis.session import PresentationSession
from app.audio.speech_analyzer import SpeechAnalyzer
from app.content.pdf_extractor import PDFExtractor
from app.content.topic_extractor import TopicExtractor
from app.content.topic_cleanup import TopicCleanup
from app.content.content_coverage import ContentCoverageAnalyzer


PDF_FILE = "data/test_presentation.pdf"
AUDIO_FILE = "data/presentation_test.wav"


print("=" * 60)
print("SNAPSPEAK REAL PRESENTATION SESSION")
print("=" * 60)


# ----------------------------------------------------------
# 1. Create session
# ----------------------------------------------------------

session = PresentationSession()


# ----------------------------------------------------------
# 2. Extract presentation content
# ----------------------------------------------------------

print("\n[1/5] Extracting presentation content...")

pdf_extractor = PDFExtractor()

pages = pdf_extractor.extract(
    PDF_FILE
)

print(f"Pages extracted: {len(pages)}")


# ----------------------------------------------------------
# 3. Extract and clean presentation topics
# ----------------------------------------------------------

print("\n[2/5] Extracting presentation topics...")

topic_extractor = TopicExtractor()
topic_cleanup = TopicCleanup()

presentation_topics = (
    topic_extractor.extract_presentation_topics(
        pages,
        phrase_count=10,
        keyword_count=5
    )
)

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

print("\nTopics detected:")

for topic, frequency in topics:
    print(
        f"  - {topic} ({frequency})"
    )


session.set_presentation(
    pdf_file=PDF_FILE,
    topics=topics
)


# ----------------------------------------------------------
# 4. Analyze speech
# ----------------------------------------------------------

print("\n[3/5] Analyzing presentation speech...")

speech_analyzer = SpeechAnalyzer(
    model_name="base"
)

speech_result = speech_analyzer.analyze(
    AUDIO_FILE
)

session.set_speech_result(
    audio_file=AUDIO_FILE,
    speech_result=speech_result
)


print("\nTranscript:")
print(
    speech_result["transcript"]
)

print("\nSpeech metrics:")
print(
    speech_result["metrics"]
)


# ----------------------------------------------------------
# 5. Analyze content coverage
# ----------------------------------------------------------

print("\n[4/5] Calculating content coverage...")

coverage_analyzer = ContentCoverageAnalyzer()

coverage_result = coverage_analyzer.analyze(
    topics,
    speech_result["transcript"]
)

session.set_content_result(
    coverage_result
)

coverage_analyzer.print_report(
    coverage_result
)


# ----------------------------------------------------------
# 6. Final session summary
# ----------------------------------------------------------

print("\n[5/5] Building session summary...")

summary = session.get_summary()


print("\n" + "=" * 60)
print("SNAPSPEAK SESSION SUMMARY")
print("=" * 60)

print(
    f"\nPresentation : "
    f"{summary['pdf_file']}"
)

print(
    f"Audio        : "
    f"{summary['audio_file']}"
)

print(
    f"Topics       : "
    f"{summary['topic_count']}"
)

print(
    f"Transcript   : "
    f"{summary['transcript']}"
)

print("\nSpeech Analysis:")
print(
    summary["speech"]["metrics"]
)

print("\nContent Analysis:")
print(
    summary["content"]
)

print("\nPosture Analysis:")
print(
    "Not connected yet"
)

print("\n" + "=" * 60)
print("REAL SESSION INTEGRATION COMPLETED")
print("=" * 60)