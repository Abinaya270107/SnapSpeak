class PresentationSession:

    def __init__(self):
        self.pdf_file = None
        self.audio_file = None

        self.presentation_topics = []
        self.transcript = ""

        self.speech_result = None
        self.posture_result = None
        self.content_result = None

    def set_presentation(self, pdf_file, topics):
        self.pdf_file = pdf_file
        self.presentation_topics = topics

    def set_speech_result(self, audio_file, speech_result):
        self.audio_file = audio_file
        self.speech_result = speech_result

        self.transcript = speech_result.get(
            "transcript",
            ""
        )

    def set_posture_result(self, posture_result):
        self.posture_result = posture_result

    def set_content_result(self, content_result):
        self.content_result = content_result

    def get_summary(self):
        return {
            "pdf_file": self.pdf_file,
            "audio_file": self.audio_file,
            "topic_count": len(
                self.presentation_topics
            ),
            "transcript": self.transcript,
            "speech": self.speech_result,
            "posture": self.posture_result,
            "content": self.content_result,
        }