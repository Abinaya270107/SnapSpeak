class CoachingEngine:

    def analyze_pace(self, words_per_minute):
        if words_per_minute == 0:
            return {
                "status": "No speech detected",
                "message": "Start speaking to begin pace analysis."
            }

        if words_per_minute < 100:
            return {
                "status": "Slow",
                "message": "Try speaking a little faster."
            }

        if words_per_minute <= 160:
            return {
                "status": "Good",
                "message": "Your speaking pace is good."
            }

        return {
            "status": "Fast",
            "message": "Try slowing down slightly."
        }


    def analyze_fillers(self, filler_count):
        if filler_count == 0:
            return {
                "status": "Good",
                "message": "No filler words detected."
            }

        if filler_count <= 3:
            return {
                "status": "Low",
                "message": "A few filler words detected."
            }

        return {
            "status": "High",
            "message": "Try reducing filler words."
        }


    def analyze_posture(self, posture):
        if posture is None:
            return {
                "status": "Unknown",
                "message": "Make sure you are visible to the camera."
            }

        status = posture["posture_status"]

        if status == "Good":
            return {
                "status": "Good",
                "message": "Your posture looks good."
            }

        if status == "Slightly misaligned":
            return {
                "status": "Attention",
                "message": "Try to straighten your posture slightly."
            }

        return {
            "status": "Needs adjustment",
            "message": "Try to sit or stand more upright."
        }


    def generate_feedback(
        self,
        words_per_minute,
        filler_count,
        posture
    ):
        pace_feedback = self.analyze_pace(
            words_per_minute
        )

        filler_feedback = self.analyze_fillers(
            filler_count
        )

        posture_feedback = self.analyze_posture(
            posture
        )

        return {
            "pace": pace_feedback,
            "fillers": filler_feedback,
            "posture": posture_feedback
        }


    def print_feedback(self, feedback):

        print("\n" + "=" * 60)
        print("SNAPSPEAK LIVE COACHING")
        print("=" * 60)

        print("\nPACE")
        print(
            f"Status  : {feedback['pace']['status']}"
        )
        print(
            f"Feedback: {feedback['pace']['message']}"
        )

        print("\nFILLER WORDS")
        print(
            f"Status  : {feedback['fillers']['status']}"
        )
        print(
            f"Feedback: {feedback['fillers']['message']}"
        )

        print("\nPOSTURE")
        print(
            f"Status  : {feedback['posture']['status']}"
        )
        print(
            f"Feedback: {feedback['posture']['message']}"
        )

        print("\n" + "=" * 60)