class RecommendationEngine:

    def generate(
        self,
        speech_metrics,
        posture_metrics,
        content_result
    ):
        recommendations = []

        # --------------------------------------------------
        # Speech pace
        # --------------------------------------------------

        wpm = speech_metrics.get(
            "words_per_minute",
            0
        )

        word_count = speech_metrics.get(
            "word_count",
            0
        )

        if word_count == 0 or wpm == 0:
            recommendations.append(
                "No speech was detected. Check the microphone input and try the presentation again."
            )

        elif wpm > 160:
            recommendations.append(
                "Your speaking pace was quite fast. Slow down slightly and add short pauses between important points."
            )

        elif wpm < 80:
            recommendations.append(
                "Your speaking pace was quite slow. Try speaking slightly faster while keeping your words clear."
            )

        elif wpm < 100:
            recommendations.append(
                "Your speaking pace was slightly slow. A little more pace could make the presentation feel more engaging."
            )

        else:
            recommendations.append(
                "Your speaking pace was within a comfortable range for a presentation."
            )

        # --------------------------------------------------
        # Filler words
        # --------------------------------------------------

        filler_count = speech_metrics.get(
            "filler_count",
            0
        )

        if word_count == 0:
            pass

        elif filler_count > 5:
            recommendations.append(
                "You used several filler words. Replace them with short intentional pauses to make your delivery more confident."
            )

        elif filler_count > 0:
            recommendations.append(
                "A few filler words were detected. Try replacing them with short pauses when organizing your thoughts."
            )

        else:
            recommendations.append(
                "No filler words were detected in your speech."
            )

        # --------------------------------------------------
        # Pauses
        # --------------------------------------------------

        pause_count = speech_metrics.get(
            "pause_count",
            0
        )

        longest_pause = speech_metrics.get(
            "longest_pause_seconds",
            0
        )

        if word_count > 0:

            if longest_pause >= 5:
                recommendations.append(
                    "You had a few long pauses. Try maintaining a smoother flow or prepare transitions between major points."
                )

            elif pause_count >= 3:
                recommendations.append(
                    "You used several pauses. Keep them intentional so they emphasize important points rather than interrupting your flow."
                )

        # --------------------------------------------------
        # Posture
        # --------------------------------------------------

        if posture_metrics:

            good_percentage = posture_metrics.get(
                "good_posture_percentage",
                0
            )

            slightly_percentage = posture_metrics.get(
                "slightly_misaligned_percentage",
                0
            )

            needs_adjustment_percentage = posture_metrics.get(
                "needs_adjustment_percentage",
                0
            )

            if needs_adjustment_percentage >= 20:

                recommendations.append(
                    "Your posture needed adjustment during a significant part of the session. Try keeping your shoulders level and your body more upright."
                )

            elif good_percentage < 50:

                recommendations.append(
                    "Your posture was stable for less than half of the session. Try maintaining a more upright and balanced stance."
                )

            elif slightly_percentage > 40:

                recommendations.append(
                    "Your posture was generally acceptable, but it was slightly misaligned for a noticeable part of the session. Try to maintain a more consistent stance."
                )

            else:

                recommendations.append(
                    "Your posture was stable for most of the presentation."
                )

        # --------------------------------------------------
        # Content coverage
        # --------------------------------------------------

        coverage = content_result.get(
            "coverage_percentage",
            0
        )

        covered_topics = content_result.get(
            "covered_topics",
            []
        )

        partial_topics = content_result.get(
            "partial_topics",
            []
        )

        missed_topics = content_result.get(
            "missed_topics",
            []
        )

        if coverage < 50:

            recommendations.append(
                "A large portion of the presentation content was missed. Review the important topics and make sure they are addressed."
            )

        elif coverage < 80:

            recommendations.append(
                "You covered several important topics, but some content could be explained more completely."
            )

        else:

            recommendations.append(
                "You covered most of the important presentation topics."
            )

        # --------------------------------------------------
        # Specific content feedback
        # --------------------------------------------------

        if missed_topics:

            missed_names = [
                item["topic"]
                for item in missed_topics
            ]

            recommendations.append(
                "Missed topics: "
                + ", ".join(missed_names)
                + "."
            )

        if partial_topics:

            partial_names = [
                item["topic"]
                for item in partial_topics
            ]

            recommendations.append(
                "Partially covered topics: "
                + ", ".join(partial_names)
                + ". Try explaining these topics in more detail."
            )

        return recommendations


def print_recommendations(recommendations):

    print("\n" + "=" * 60)
    print("SNAPSPEAK RECOMMENDATIONS")
    print("=" * 60)

    for index, recommendation in enumerate(
        recommendations,
        start=1
    ):
        print(
            f"\n{index}. {recommendation}"
        )

    print("\n" + "=" * 60)