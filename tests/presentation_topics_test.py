from app.content.pdf_extractor import PDFExtractor
from app.content.topic_extractor import TopicExtractor


PDF_FILE = "data/test_presentation.pdf"


pdf_extractor = PDFExtractor()
topic_extractor = TopicExtractor()


pages = pdf_extractor.extract(
    PDF_FILE
)


print("=" * 60)
print("SNAPSPEAK PRESENTATION-AWARE TOPIC EXTRACTION")
print("=" * 60)


topics = topic_extractor.extract_presentation_topics(
    pages,
    phrase_count=10,
    keyword_count=5
)


print("\nIMPORTANT PRESENTATION TOPICS")
print("-" * 60)


for index, item in enumerate(topics, start=1):

    print(
        f"{index:2}. "
        f"{item['topic']:<40} "
        f"[{item['type']}] "
        f"frequency={item['frequency']}"
    )


print("\n" + "=" * 60)
print("Presentation topic extraction completed.")
print("=" * 60)