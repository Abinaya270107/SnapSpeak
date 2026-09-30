from app.content.content_coverage import (
    ContentCoverageAnalyzer
)


analyzer = ContentCoverageAnalyzer()


topics = [
    ("deep learning", 5),
    ("chest x-ray", 4),
    ("uncertainty quantification", 3),
    ("severity assessment", 3),
]


transcript = """
Today I will explain our deep learning approach
for chest x-ray analysis. The system is designed
to assess the severity of disease from medical images.
"""


result = analyzer.analyze(
    topics,
    transcript
)

analyzer.print_report(result)