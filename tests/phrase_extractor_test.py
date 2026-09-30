from app.content.pdf_extractor import PDFExtractor
from app.content.topic_extractor import TopicExtractor


PDF_FILE = "data/test_presentation.pdf"

pdf_extractor = PDFExtractor()
topic_extractor = TopicExtractor()

pages = pdf_extractor.extract(PDF_FILE)


print("=" * 50)
print("SNAPSPEAK MULTI-WORD TOPIC ANALYSIS")
print("=" * 50)


print("\nOVERALL PHRASES")
print("-" * 40)

phrases = topic_extractor.extract_overall_phrases(
    pages,
    top_n=20
)

for index, (phrase, count) in enumerate(
    phrases,
    start=1
):
    print(f"{index:2}. {phrase:<40} {count}")


print("\nPAGE-WISE PHRASES")
print("-" * 40)

page_phrases = topic_extractor.extract_page_phrases(
    pages,
    top_n=5
)

for page in page_phrases:

    print(f"\nPage {page['page']}:")

    if page["phrases"]:

        for phrase, count in page["phrases"]:
            print(f"  - {phrase} ({count})")

    else:
        print("  - No phrases detected")


print("\n" + "=" * 50)
print("Phrase analysis completed.")
print("=" * 50)