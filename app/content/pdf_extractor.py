import pymupdf


class PDFExtractor:
    """
    Extracts presentation text page by page from a PDF.
    """

    def extract(self, pdf_path):
        document = pymupdf.open(pdf_path)

        pages = []

        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text").strip()

            pages.append({
                "page": page_number,
                "text": text,
            })

        document.close()

        return pages

    def get_full_text(self, pdf_path):
        pages = self.extract(pdf_path)

        return "\n".join(
            page["text"]
            for page in pages
            if page["text"]
        )