from app.content.pdf_extractor import PDFExtractor


PDF_FILE = "data/test_presentation.pdf"

extractor = PDFExtractor()

pages = extractor.extract(PDF_FILE)

print("=" * 50)
print("SNAPSPEAK PDF CONTENT EXTRACTION")
print("=" * 50)

print(f"\nPages found: {len(pages)}")

for page in pages:
    print("\n" + "-" * 40)
    print(f"PAGE {page['page']}")
    print("-" * 40)

    text = page["text"]

    if text:
        print(text[:1000])
    else:
        print("[No text detected]")


print("\nPDF extraction completed.")