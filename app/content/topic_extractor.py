import re
from collections import Counter


STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then",
    "is", "are", "was", "were", "be", "been", "being",
    "to", "of", "in", "on", "for", "with", "from",
    "by", "as", "at", "this", "that", "these", "those",
    "it", "its", "their", "there", "here",
    "we", "our", "you", "your", "they", "them",
    "he", "she", "his", "her",
    "can", "could", "may", "might", "will", "would",
    "should", "do", "does", "did",
    "have", "has", "had",
    "not", "no", "yes",
    "than", "also", "more", "most",
    "into", "over", "under", "about",
    "which", "what", "when", "where", "who", "how",
}

NOISE_WORDS = {
    "figure", "fig", "table", "page", "pages",
    "proc", "et", "al", "journal", "volume", "issue",
    "copyright", "doi", "arxiv", "using", "based",
    "shown", "shows", "results", "method", "methods",
    "approach",
}

# Unicode bullet symbols, including characters that may be
# encountered in extracted PDF text.
BULLET_CHARS = "\u2022\u25e6\u25aa\u25a0\u25cf\u25cb\u25a1"


class TopicExtractor:

    def clean_text(self, text):
        text = (text or "").lower()

        words = re.findall(
            r"\b[a-zA-Z][a-zA-Z0-9-]{2,}\b",
            text,
        )

        return [
            word
            for word in words
            if word not in STOP_WORDS
            and word not in NOISE_WORDS
        ]

    def extract_keywords(self, text, top_n=10):
        words = self.clean_text(text)
        return Counter(words).most_common(top_n)

    def extract_phrases(self, text, top_n=10):
        words = self.clean_text(text)

        if len(words) < 2:
            return []

        bigrams = [
            f"{words[i]} {words[i + 1]}"
            for i in range(len(words) - 1)
        ]

        counts = Counter(bigrams)
        scored_phrases = []

        for phrase, count in counts.items():
            if count < 2:
                continue

            scored_phrases.append(
                (phrase, count, count * 2)
            )

        scored_phrases.sort(
            key=lambda item: item[2],
            reverse=True,
        )

        selected = []

        for phrase, count, score in scored_phrases:
            phrase_words = set(phrase.split())

            contained = False

            for existing_phrase, _, _ in selected:
                existing_words = set(existing_phrase.split())

                if phrase_words.issubset(existing_words):
                    contained = True
                    break

            if not contained:
                selected.append((phrase, count, score))

            if len(selected) >= top_n:
                break

        return [
            (phrase, count)
            for phrase, count, _ in selected
        ]

    def extract_page_topics(self, pages, top_n=5):
        page_topics = []

        for page in pages:
            topics = self.extract_keywords(
                page.get("text", ""),
                top_n=top_n,
            )

            page_topics.append({
                "page": page.get("page"),
                "topics": topics,
            })

        return page_topics

    def extract_page_phrases(self, pages, top_n=5):
        page_phrases = []

        for page in pages:
            phrases = self.extract_phrases(
                page.get("text", ""),
                top_n=top_n,
            )

            page_phrases.append({
                "page": page.get("page"),
                "phrases": phrases,
            })

        return page_phrases

    def extract_overall_topics(self, pages, top_n=15):
        full_text = "\n".join(
            page.get("text", "")
            for page in pages
            if page.get("text")
        )

        return self.extract_keywords(
            full_text,
            top_n=top_n,
        )

    def extract_overall_phrases(self, pages, top_n=15):
        full_text = "\n".join(
            page.get("text", "")
            for page in pages
            if page.get("text")
        )

        return self.extract_phrases(
            full_text,
            top_n=top_n,
        )

    def clean_heading(self, line):
        line = (line or "").strip()

        if not line:
            return ""

        line = re.sub(
            r"^[0-9]+[\.\):\-]\s*",
            "",
            line,
        )

        line = re.sub(r"\s+", " ", line)

        return line.strip()

    def is_bullet_line(self, line):
        stripped = (line or "").strip()

        if not stripped:
            return False

        # Bullet glyphs and common dash/list markers.
        if stripped[0] in BULLET_CHARS:
            return True

        return bool(
            re.match(r"^[-\u2013\u2014]\s+", stripped)
            or re.match(r"^\*\s+", stripped)
        )

    def is_valid_heading(self, line):
        line = (line or "").strip()

        if not line or self.is_bullet_line(line):
            return False

        words = line.split()

        # Avoid using long body paragraphs as headings.
        if not 1 <= len(words) <= 6:
            return False

        if not self.clean_text(line):
            return False

        return True

    def extract_heading_from_page(self, page_text):
        for line in (page_text or "").splitlines():
            cleaned_line = self.clean_heading(line)

            if self.is_valid_heading(cleaned_line):
                return cleaned_line

        return ""

    def extract_page_description(self, page_text):
        for line in (page_text or "").splitlines():
            if not self.is_bullet_line(line):
                continue

            cleaned = line.strip()

            if cleaned and cleaned[0] in BULLET_CHARS:
                cleaned = cleaned[1:].strip()
            else:
                cleaned = re.sub(
                    r"^[-\u2013\u2014]\s+",
                    "",
                    cleaned,
                )
                cleaned = re.sub(
                    r"^\*\s+",
                    "",
                    cleaned,
                )

            if cleaned:
                return cleaned

        return ""

    def extract_presentation_topics(
        self,
        pages,
        phrase_count=10,
        keyword_count=5,
    ):
        topics = []

        # 1. Slide headings are the primary topic source.
        for page in pages:
            page_text = page.get("text", "")

            heading = self.extract_heading_from_page(
                page_text
            )

            if not heading:
                continue

            normalized_heading = re.sub(
                r"\s+",
                " ",
                heading.lower(),
            ).strip()

            # A product-name-only title is not a useful topic.
            if normalized_heading == "snapspeak":
                description = self.extract_page_description(
                    page_text
                )
                description_lower = description.lower()

                if (
                    "presentation coach" in description_lower
                    or (
                        "presentation" in description_lower
                        and "coach" in description_lower
                    )
                ):
                    normalized_heading = "presentation coach"

            if any(
                item["topic"] == normalized_heading
                for item in topics
            ):
                continue

            topics.append({
                "topic": normalized_heading,
                "frequency": 1,
                "type": "heading",
            })

        # 2. Repeated phrases are a fallback when headings
        # do not provide enough topics.
        if len(topics) < 3:
            phrases = self.extract_overall_phrases(
                pages,
                top_n=phrase_count,
            )

            for phrase, count in phrases:
                normalized_phrase = phrase.lower().strip()
                phrase_words = set(normalized_phrase.split())

                duplicate = False

                for existing in topics:
                    existing_words = set(
                        existing["topic"].split()
                    )

                    if (
                        normalized_phrase == existing["topic"]
                        or phrase_words.issubset(existing_words)
                        or existing_words.issubset(phrase_words)
                    ):
                        duplicate = True
                        break

                if duplicate:
                    continue

                topics.append({
                    "topic": normalized_phrase,
                    "frequency": count,
                    "type": "phrase",
                })

                if len(topics) >= phrase_count:
                    break

        # 3. Keywords are the final fallback.
        if len(topics) < 3:
            keywords = self.extract_overall_topics(
                pages,
                top_n=keyword_count,
            )

            for keyword, count in keywords:
                keyword = keyword.lower().strip()

                if any(
                    keyword in item["topic"].split()
                    for item in topics
                ):
                    continue

                topics.append({
                    "topic": keyword,
                    "frequency": count,
                    "type": "keyword",
                })

        return topics