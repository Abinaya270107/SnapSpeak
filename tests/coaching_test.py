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

from app.analysis.coaching import CoachingEngine


engine = CoachingEngine()


posture = {
    "posture_status": "Slightly misaligned"
}


feedback = engine.generate_feedback(
    words_per_minute=145,
    filler_count=2,
    posture=posture
)


engine.print_feedback(feedback)