import sys
import os

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from app.analysis.recommendations import (
    RecommendationEngine,
    print_recommendations
)
engine = RecommendationEngine()

speech_metrics = {
    "words_per_minute": 175,
    "filler_count": 5
}

posture_metrics = {
    "good_posture_percentage": 35
}

content_result = {
    "coverage_percentage": 62.5
}

recommendations = engine.generate(
    speech_metrics,
    posture_metrics,
    content_result
)

print_recommendations(recommendations)