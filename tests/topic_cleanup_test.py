from app.content.topic_extractor import TopicExtractor
from app.content.topic_cleanup import TopicCleanup
from app.content.pdf_extractor import PDFExtractor


PDF_FILE = "data/test_presentation.pdf"


pdf_extractor = PDFExtractor()
topic_extractor = TopicExtractor()
cleanup = TopicCleanup()


pages = pdf_extractor.extract(
    PDF_FILE
)


topics = topic_extractor.extract_presentation_topics(
    pages,
    phrase_count=10,
    keyword_count=5
)


cleaned_topics = cleanup.clean(
    topics
)


print("=" * 60)
print("SNAPSPEAK CLEAN PRESENTATION TOPICS")
print("=" * 60)


for index, item in enumerate(
    cleaned_topics,
    start=1
):

    print(
        f"{index:2}. "
        f"{item['topic']:<40} "
        f"[{item['type']}] "
        f"frequency={item['frequency']}"
    )


print("\n" + "=" * 60)
print("Topic cleanup completed.")
print("=" * 60)