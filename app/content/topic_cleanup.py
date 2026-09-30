class TopicCleanup:

    # Phrases that are too generic or are commonly
    # produced as unnatural word combinations.
    REJECT_PHRASES = {
        "uncertainty calibration selective",
        "model ordinal loss",
    }

    # Words that are too generic to be useful as
    # standalone presentation topics.
    GENERIC_WORDS = {
        "model",
        "image",
        "quality",
        "loss",
        "deep",
        "selective",
        "uncertainty",
        "calibration",
    }

    def clean(self, topics):
        """
        Remove weak or unnatural topics while
        preserving meaningful presentation concepts.

        Input:
            [
                {
                    "topic": "...",
                    "frequency": 3,
                    "type": "phrase"
                }
            ]

        Output:
            cleaned topic list
        """

        cleaned = []

        for item in topics:

            topic = item["topic"].strip().lower()

            # Remove explicitly rejected phrases.
            if topic in self.REJECT_PHRASES:
                continue

            # Remove standalone generic words.
            if (
                item["type"] == "keyword"
                and topic in self.GENERIC_WORDS
            ):
                continue

            cleaned.append({
                "topic": topic,
                "frequency": item["frequency"],
                "type": item["type"]
            })

        return cleaned