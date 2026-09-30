from app.content.pdf_extractor import PDFExtractor
from app.content.topic_extractor import TopicExtractor


PDF_FILE = "data/test_presentation.pdf"


pdf_extractor = PDFExtractor()
topic_extractor = TopicExtractor()

pages = pdf_extractor.extract(PDF_FILE)


print("=" * 50)
print("SNAPSPEAK PRESENTATION TOPIC ANALYSIS")
print("=" * 50)


print("\nOVERALL TOPICS")
print("-" * 40)

topics = topic_extractor.extract_overall_topics(
    pages,
    top_n=15
)

for index, (word, count) in enumerate(topics, start=1):
    print(f"{index:2}. {word:<30} {count}")


print("\nPAGE-WISE TOPICS")
print("-" * 40)

page_topics = topic_extractor.extract_page_topics(
    pages,
    top_n=5
)

for page in page_topics:

    print(f"\nPage {page['page']}:")

    if page["topics"]:
        for word, count in page["topics"]:
            print(f"  - {word} ({count})")
    else:
        print("  - No topics detected")


print("\n" + "=" * 50)
print("Topic analysis completed.")
print("=" * 50)