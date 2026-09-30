import re


class ContentCoverageAnalyzer:
    """
    Scores how well a transcript discusses the topics extracted
    from a presentation.

    Known SnapSpeak topics use phrase and evidence-group matching.
    Other topics use conservative text overlap.
    """

    CONCEPT_EVIDENCE = {
        "presentation coach": {
            "identity": [
                "presentation coach",
                "ai presentation coach",
                "presentation coaching",
                "presentation skills",
                "presentation skill",
            ],
            "purpose": [
                "help students",
                "help users",
                "improve presentations",
                "improve presentation skills",
                "become more confident",
                "rehearsal",
                "practice presentations",
            ],
            "delivery": [
                "speaking",
                "speakers",
                "presenting",
                "presentation",
                "delivery",
                "confidence",
            ],
        },
        "speech analysis": {
            "analysis": [
                "speech analysis",
                "analyzes speech",
                "analyses speech",
                "analyze speech",
                "analyses speaking",
                "analyzes speaking",
                "speech recognition",
                "transcription",
                "transcript",
            ],
            "measurements": [
                "speaking pace",
                "speech pace",
                "speaking speed",
                "filler words",
                "filler word",
                "filler count",
                "long pauses",
                "pause detection",
                "speech duration",
                "words per minute",
            ],
        },
        "posture analysis": {
            "posture": [
                "posture analysis",
                "analyzes posture",
                "analyses posture",
                "checks posture",
                "check posture",
                "good posture",
                "body posture",
                "posture detection",
            ],
            "visual_method": [
                "computer vision",
                "pose estimation",
                "body lean",
                "shoulder tilt",
                "body movement",
                "keypoint detection",
                "webcam analysis",
            ],
        },
        "content coverage": {
            "content": [
                "content coverage",
                "presentation content",
                "content analysis",
                "content assessment",
                "analyzes content",
                "analyses content",
            ],
            "topic_tracking": [
                "topics covered",
                "important topics",
                "topics were covered",
                "identifies topics",
                "identify topics",
                "missed topics",
                "covered topics",
                "topic coverage",
            ],
        },
        "on device ai": {
            "local_execution": [
                "on device",
                "on-device",
                "runs locally",
                "running locally",
                "local inference",
                "local processing",
                "offline inference",
                "offline processing",
            ],
            "hardware": [
                "snapdragon",
                "qualcomm",
                "qnn",
                "npu",
                "neural processing unit",
                "edge inference",
                "edge ai",
                "hardware acceleration",
            ],
        },
    }

    GENERIC_TOPIC_WORDS = {
        "ai",
        "the",
        "and",
        "for",
        "with",
        "from",
        "this",
        "that",
        "presentation",
        "content",
        "speech",
        "posture",
        "analysis",
        "computer",
        "vision",
        "body",
        "words",
        "topic",
        "topics",
    }

    def normalize_text(self, text):
        if not text:
            return ""

        text = str(text).lower().replace("’", "'")
        text = text.replace("-", " ")
        text = re.sub(r"[^a-z0-9\s']", " ", text)
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def get_words(self, text):
        return {
            word
            for word in self.normalize_text(text).split()
            if len(word) > 2
        }

    def get_topic_words(self, topic):
        return self.get_words(topic)

    def _contains_phrase(self, transcript, phrase):
        normalized_transcript = self.normalize_text(transcript)
        normalized_phrase = self.normalize_text(phrase)

        if not normalized_transcript or not normalized_phrase:
            return False

        # Match whole phrases, not fragments inside other words.
        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(normalized_phrase)
            + r"(?![a-z0-9])"
        )

        return re.search(pattern, normalized_transcript) is not None

    def calculate_word_overlap(self, topic, transcript):
        topic_words = self.get_topic_words(topic)
        transcript_words = self.get_words(transcript)

        if not topic_words:
            return 0.0

        # Generic words are weak evidence on their own.
        meaningful_words = (
            topic_words - self.GENERIC_TOPIC_WORDS
        )

        if not meaningful_words:
            meaningful_words = topic_words

        matched_words = meaningful_words.intersection(
            transcript_words
        )

        return len(matched_words) / len(meaningful_words)

    def calculate_phrase_score(self, topic, transcript):
        normalized_topic = self.normalize_text(topic)
        normalized_transcript = self.normalize_text(transcript)

        if not normalized_topic or not normalized_transcript:
            return 0.0

        if self._contains_phrase(
            normalized_transcript,
            normalized_topic,
        ):
            return 1.0

        topic_words = normalized_topic.split()
        transcript_words = set(normalized_transcript.split())

        if len(topic_words) <= 1:
            return 0.0

        matched_words = [
            word
            for word in topic_words
            if word in transcript_words
            and word not in self.GENERIC_TOPIC_WORDS
        ]

        if not matched_words:
            return 0.0

        return len(matched_words) / len(topic_words)

    def calculate_concept_score(self, topic, transcript):
        topic_key = self.normalize_text(topic)
        evidence_groups = self.CONCEPT_EVIDENCE.get(topic_key)

        if not evidence_groups:
            return 0.0

        matched_groups = 0
        total_groups = len(evidence_groups)

        for phrases in evidence_groups.values():
            if any(
                self._contains_phrase(transcript, phrase)
                for phrase in phrases
            ):
                matched_groups += 1

        if matched_groups == 0:
            return 0.0

        # A direct phrase naming the concept is strong evidence.
        if any(
            self._contains_phrase(transcript, phrase)
            for phrases in evidence_groups.values()
            for phrase in phrases
            if phrase == topic_key
        ):
            return 1.0

        # Require evidence from different aspects of a concept.
        if matched_groups == total_groups:
            return 0.95

        if matched_groups >= 2:
            return 0.75

        # One evidence group supports partial coverage, not
        # automatic full credit.
        return 0.45

    def calculate_topic_score(self, topic, transcript):
        topic_key = self.normalize_text(topic)

        # Known SnapSpeak concepts get a dedicated score.
        concept_score = self.calculate_concept_score(
            topic_key,
            transcript,
        )

        if topic_key in self.CONCEPT_EVIDENCE:
            phrase_score = self.calculate_phrase_score(
                topic_key,
                transcript,
            )
            word_score = self.calculate_word_overlap(
                topic_key,
                transcript,
            )

            # The evidence-group score carries the most weight.
            final_score = (
                0.75 * concept_score
                + 0.15 * phrase_score
                + 0.10 * word_score
            )

            return min(final_score, 1.0)

        # Fallback for topics outside the known SnapSpeak set.
        phrase_score = self.calculate_phrase_score(
            topic_key,
            transcript,
        )
        word_score = self.calculate_word_overlap(
            topic_key,
            transcript,
        )

        return min(
            0.70 * phrase_score + 0.30 * word_score,
            1.0,
        )

    def topic_is_covered(
        self,
        topic,
        transcript,
        threshold=0.35,
    ):
        return self.calculate_topic_score(
            topic,
            transcript,
        ) >= threshold

    def analyze(self, topics, transcript, threshold=0.35):
        covered_topics = []
        partial_topics = []
        missed_topics = []

        for item in topics:
            # Accept both (topic, frequency) tuples and topic
            # dictionaries returned by TopicExtractor.
            if isinstance(item, dict):
                topic = item.get("topic", "")
                frequency = item.get("frequency", 1)
            else:
                topic, frequency = item[0], item[1]

            score = self.calculate_topic_score(
                topic,
                transcript,
            )

            percentage = round(score * 100, 1)

            topic_result = {
                "topic": topic,
                "frequency": frequency,
                "overlap": percentage,
                "score": round(score, 3),
            }

            if score >= threshold:
                covered_topics.append(topic_result)
            elif score >= 0.15:
                partial_topics.append(topic_result)
            else:
                missed_topics.append(topic_result)

        total_topics = len(topics)

        if total_topics:
            coverage_percentage = (
                (
                    len(covered_topics)
                    + 0.5 * len(partial_topics)
                )
                / total_topics
            ) * 100
        else:
            coverage_percentage = 0.0

        return {
            "total_topics": total_topics,
            "covered_count": len(covered_topics),
            "partial_count": len(partial_topics),
            "missed_count": len(missed_topics),
            "coverage_percentage": round(
                coverage_percentage,
                1,
            ),
            "covered_topics": covered_topics,
            "partial_topics": partial_topics,
            "missed_topics": missed_topics,
        }