
import os
import sys

import streamlit as st


# --------------------------------------------------
# Project path
# --------------------------------------------------

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


from app.content.pdf_extractor import PDFExtractor
from app.content.topic_extractor import TopicExtractor
from app.content.topic_cleanup import TopicCleanup

from app.analysis.session_runner import (
    run_presentation_session,
)

from app.analysis.edge_mode import (
    get_edge_summary,
)


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="SnapSpeak",
    page_icon="S",
    layout="wide",
)


# --------------------------------------------------
# Styling
# --------------------------------------------------

st.markdown(
    """
    <style>
    .main {
        padding-top: 2rem;
    }

    .hero {
        padding: 1.5rem 0 2rem 0;
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 750;
        margin-bottom: 0.2rem;
        letter-spacing: -1px;
    }

    .hero-subtitle {
        font-size: 1.15rem;
        color: #6b7280;
        margin-bottom: 1rem;
    }

    .section-title {
        font-size: 1.4rem;
        font-weight: 650;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
    }

    .metric-card {
        padding: 1.25rem;
        border-radius: 14px;
        background-color: #f7f8fa;
        border: 1px solid #e5e7eb;
        min-height: 135px;
        text-align: center;
    }

    .metric-card-title {
        font-size: 0.88rem;
        color: #6b7280;
        margin-bottom: 0.45rem;
    }

    .metric-card-value {
        font-size: 2rem;
        font-weight: 750;
        line-height: 1.1;
        margin-bottom: 0.45rem;
    }

    .metric-card-status {
        font-size: 0.85rem;
        font-weight: 600;
        color: #374151;
    }

    .topic-card {
        padding: 0.8rem 1rem;
        border-radius: 10px;
        background-color: #f7f8fa;
        border: 1px solid #e5e7eb;
        margin-bottom: 0.5rem;
    }

    .recommendation-card {
        padding: 0.9rem 1rem;
        border-radius: 10px;
        background-color: #f7f8fa;
        border: 1px solid #e5e7eb;
        margin-bottom: 0.6rem;
    }

    .result-banner {
        padding: 1rem 1.2rem;
        border-radius: 12px;
        background-color: #f7f8fa;
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
    }

    .result-banner-title {
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }

    .result-banner-text {
        color: #6b7280;
        font-size: 0.92rem;
    }

    .edge-card {
        padding: 1.25rem;
        border-radius: 14px;
        background-color: #f7f8fa;
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
    }

    .edge-title {
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 0.35rem;
    }

    .edge-subtitle {
        color: #6b7280;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }

    .edge-label {
        font-size: 0.78rem;
        color: #6b7280;
        margin-bottom: 0.2rem;
    }

    .edge-value {
        font-size: 1.05rem;
        font-weight: 650;
    }

    .edge-note {
        margin-top: 1rem;
        padding: 0.8rem 1rem;
        border-radius: 10px;
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        color: #6b7280;
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def get_pace_status(wpm):
    """
    Classify speaking pace using the same bands as
    RecommendationEngine.

    Below 90 WPM: potentially slow
    90-130 WPM: comfortable
    Above 130-160 WPM: faster side
    Above 160 WPM: fast

    These are configurable coaching thresholds, not
    universal standards for every speaker.
    """
    try:
        wpm = float(wpm)
    except (TypeError, ValueError):
        return "Pace unavailable"

    if wpm <= 0:
        return "No speech detected"

    if wpm < 90:
        return "Potentially slow pace"

    if wpm <= 130:
        return "Comfortable overall pace"

    if wpm <= 160:
        return "Faster than typical pace"

    return "Fast pace"


def get_filler_status(count):
    if count == 0:
        return "No fillers detected"

    if count <= 5:
        return "A few detected"

    return "Needs attention"


def get_posture_status(percentage):
    if percentage >= 80:
        return "Excellent posture"

    if percentage >= 50:
        return "Mostly good"

    return "Needs improvement"


def get_content_status(percentage):
    """
    Describe content coverage using consistent score bands.

    90-100%: Excellent coverage
    75-89.9%: Good coverage
    50-74.9%: Good progress
    Below 50%: More topics needed
    """
    if percentage >= 90:
        return "Excellent coverage"

    if percentage >= 75:
        return "Good coverage"

    if percentage >= 50:
        return "Good progress"

    return "More topics needed"


def get_speaking_wpm(speech_metrics):
    """
    Prefer speech-only WPM for the main pace result.
    Fall back to overall WPM if speech-only WPM is unavailable.
    """
    wpm = speech_metrics.get(
        "speech_only_words_per_minute"
    )

    if wpm is None:
        wpm = speech_metrics.get(
            "words_per_minute",
            0,
        )

    try:
        return float(wpm)
    except (TypeError, ValueError):
        return 0.0


# --------------------------------------------------
# Header
# --------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">SnapSpeak</div>
        <div class="hero-subtitle">
            On-device multimodal AI presentation coach
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Snapdragon Edge Mode
# --------------------------------------------------

edge_summary = get_edge_summary()

st.markdown(
    '<div class="section-title">'
    'Snapdragon Edge Mode'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="edge-card">
        <div class="edge-title">
            Qualcomm AI deployment profile
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="edge-subtitle">
        SnapSpeak is designed for local AI inference on
        Snapdragon-powered Windows PCs.
    </div>
    """,
    unsafe_allow_html=True,
)

edge_col1, edge_col2, edge_col3, edge_col4 = st.columns(4)

with edge_col1:
    st.markdown(
        f"""
        <div>
            <div class="edge-label">
                Current Runtime
            </div>
            <div class="edge-value">
                {edge_summary["current_mode"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with edge_col2:
    st.markdown(
        """
        <div>
            <div class="edge-label">
                Target Device
            </div>
            <div class="edge-value">
                Snapdragon X Elite
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with edge_col3:
    st.markdown(
        f"""
        <div>
            <div class="edge-label">
                Compute
            </div>
            <div class="edge-value">
                {edge_summary["compute_unit"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with edge_col4:
    st.markdown(
        f"""
        <div>
            <div class="edge-label">
                Runtime
            </div>
            <div class="edge-value">
                {edge_summary["runtime"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

edge_model_col1, edge_model_col2, edge_model_col3 = st.columns(3)

with edge_model_col1:
    st.metric(
        "Model",
        "YOLO11 Pose",
    )

with edge_model_col2:
    st.metric(
        "AI Hub Inference",
        f'{edge_summary["inference_ms"]} ms',
    )

with edge_model_col3:
    st.metric(
        "Peak Memory",
        f'{edge_summary["peak_memory_mb"]} MB',
    )

st.markdown(
    f"""
    <div class="edge-note">
        <strong>Evidence source:</strong>
        {edge_summary["source"]}.
        The inference and memory values shown above are
        Qualcomm AI Hub profile measurements for the
        Snapdragon deployment target. They are not measurements
        from the current development laptop.
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Presentation upload
# --------------------------------------------------

st.markdown(
    '<div class="section-title">1. Presentation</div>',
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Upload your presentation",
    type=["pdf"],
    help="Upload the PDF you will present.",
)


# --------------------------------------------------
# Process uploaded PDF
# --------------------------------------------------

if uploaded_file is not None:
    st.success(
        f"Presentation loaded: {uploaded_file.name}"
    )

    temp_pdf_path = os.path.join(
        PROJECT_ROOT,
        "data",
        "uploaded_presentation.pdf",
    )

    os.makedirs(
        os.path.dirname(temp_pdf_path),
        exist_ok=True,
    )

    with open(temp_pdf_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    try:
        pdf_extractor = PDFExtractor()
        pages = pdf_extractor.extract(temp_pdf_path)

        topic_extractor = TopicExtractor()

        raw_topics = topic_extractor.extract_presentation_topics(
            pages,
            phrase_count=10,
            keyword_count=5,
        )

        topic_cleanup = TopicCleanup()
        presentation_topics = topic_cleanup.clean(raw_topics)

        st.markdown(
            '<div class="section-title">'
            'Presentation Overview'
            '</div>',
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Pages",
                len(pages),
            )

        with col2:
            st.metric(
                "Topics Detected",
                len(presentation_topics),
            )

        if presentation_topics:
            st.markdown("**Detected topics:**")

            for item in presentation_topics:
                st.markdown(
                    f"""
                    <div class="topic-card">
                        <strong>{item["topic"].title()}</strong>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.warning(
                "No presentation topics were detected."
            )

        st.session_state["presentation_topics"] = presentation_topics
        st.session_state["presentation_pdf"] = temp_pdf_path

    except Exception as error:
        st.error(
            "Could not analyze the uploaded presentation."
        )
        st.exception(error)

else:
    st.info(
        "Upload a PDF presentation to begin your session."
    )


# --------------------------------------------------
# Presentation session
# --------------------------------------------------

st.markdown(
    '<div class="section-title">'
    '2. Presentation Session'
    '</div>',
    unsafe_allow_html=True,
)

if uploaded_file is None:
    st.button(
        "Start Presentation",
        use_container_width=True,
        type="primary",
        disabled=True,
    )

else:
    start_button = st.button(
        "Start Presentation",
        use_container_width=True,
        type="primary",
    )

    if start_button:
        raw_audio_file = os.path.join(
            PROJECT_ROOT,
            "data",
            "ui_presentation_audio_raw.wav",
        )

        audio_file = os.path.join(
            PROJECT_ROOT,
            "data",
            "ui_presentation_audio.wav",
        )

        st.session_state["session_running"] = True

        st.info(
            "Presentation session starting. "
            "The webcam window will open. "
            "Present your topic and press Q in "
            "the webcam window when you finish."
        )

        try:
            with st.spinner(
                "Running SnapSpeak analysis..."
            ):
                session_result = run_presentation_session(
                    pdf_file=st.session_state["presentation_pdf"],
                    raw_audio_file=raw_audio_file,
                    audio_file=audio_file,
                )

            st.session_state["session_result"] = session_result
            st.session_state["session_running"] = False

            st.success(
                "Presentation analysis complete."
            )

        except Exception as error:
            st.session_state["session_running"] = False

            st.error(
                "The presentation session could not be completed."
            )
            st.exception(error)


# --------------------------------------------------
# Results
# --------------------------------------------------

session_result = st.session_state.get("session_result")


if session_result is not None:
    speech_metrics = session_result["speech_metrics"]
    posture_metrics = session_result["posture_metrics"]
    content_result = session_result["content_result"]
    audio_quality = session_result["audio_quality"]
    recommendations = session_result["recommendations"]

    # --------------------------------------------------
    # Session summary
    # --------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        '3. Session Results'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="result-banner">
            <div class="result-banner-title">
                Your presentation has been analyzed
            </div>
            <div class="result-banner-text">
                SnapSpeak combined speech, visual posture,
                and presentation-content analysis to generate
                personalized feedback.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    # Use speech-only WPM for both the displayed pace and
    # the pace-status classification.
    # This keeps the metric consistent with recommendations.
    wpm = get_speaking_wpm(speech_metrics)

    filler_count = speech_metrics["filler_count"]

    posture_percentage = posture_metrics[
        "good_posture_percentage"
    ]

    coverage_percentage = content_result[
        "coverage_percentage"
    ]

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-card-title">
                    Speaking Pace
                </div>
                <div class="metric-card-value">
                    {wpm:.1f} WPM
                </div>
                <div class="metric-card-status">
                    {get_pace_status(wpm)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-card-title">
                    Filler Words
                </div>
                <div class="metric-card-value">
                    {filler_count}
                </div>
                <div class="metric-card-status">
                    {get_filler_status(filler_count)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-card-title">
                    Good Posture
                </div>
                <div class="metric-card-value">
                    {posture_percentage}%
                </div>
                <div class="metric-card-status">
                    {get_posture_status(posture_percentage)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-card-title">
                    Content Coverage
                </div>
                <div class="metric-card-value">
                    {coverage_percentage}%
                </div>
                <div class="metric-card-status">
                    {get_content_status(coverage_percentage)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------
    # Speech analysis
    # --------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        'Speech Analysis'
        '</div>',
        unsafe_allow_html=True,
    )

    (
        speech_col1,
        speech_col2,
        speech_col3,
        speech_col4,
        speech_col5,
    ) = st.columns(5)

    with speech_col1:
        st.metric(
            "Words Spoken",
            speech_metrics["word_count"],
        )

    with speech_col2:
        st.metric(
            "Recording Duration",
            f'{speech_metrics["duration_seconds"]} sec',
        )

    with speech_col3:
        st.metric(
            "Speech Duration",
            f'{speech_metrics["speech_duration_seconds"]} sec',
        )

    with speech_col4:
        st.metric(
            "Speech-Only WPM",
            f'{wpm:.1f}',
            help=(
                "The main Speaking Pace metric uses this value "
                "when it is available."
            ),
        )

    # This quality field is based on the original input RMS.
    # It indicates signal level, not overall audio clarity.
    with speech_col5:
        st.metric(
            "Raw Input Level",
            audio_quality["quality"],
            help=(
                "Based on the original microphone recording's "
                "RMS level before normalization. This measures "
                "signal level, not overall audio clarity."
            ),
        )

    # --------------------------------------------------
    # Audio level details
    # --------------------------------------------------

    with st.expander("Audio Level Details"):
        st.caption(
            "The raw input level is measured before normalization. "
            "Normalization increases the signal level for processing, "
            "but does not by itself establish audio clarity."
        )

        audio_col1, audio_col2, audio_col3, audio_col4 = (
            st.columns(4)
        )

        with audio_col1:
            st.metric(
                "Raw RMS",
                audio_quality.get("original_rms", "--"),
            )

        with audio_col2:
            st.metric(
                "Normalized RMS",
                audio_quality.get("normalized_rms", "--"),
            )

        with audio_col3:
            st.metric(
                "Raw Peak",
                audio_quality.get("original_peak", "--"),
            )

        with audio_col4:
            st.metric(
                "Normalized Peak",
                audio_quality.get("normalized_peak", "--"),
            )

        st.caption(
            "RMS and peak values use 16-bit PCM sample units. "
            "Higher values indicate a stronger signal, not "
            "necessarily better audio quality."
        )

    transcript = session_result["speech_result"]["transcript"]

    with st.expander("View Transcript"):
        st.write(transcript)

    # --------------------------------------------------
    # Posture
    # --------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        'Visual Analysis'
        '</div>',
        unsafe_allow_html=True,
    )

    posture_col1, posture_col2, posture_col3 = st.columns(3)

    with posture_col1:
        st.metric(
            "Average Shoulder Tilt",
            f'{posture_metrics["average_shoulder_tilt"]} degrees',
        )

    with posture_col2:
        st.metric(
            "Average Body Lean",
            f'{posture_metrics["average_body_lean"]} degrees',
        )

    with posture_col3:
        st.metric(
            "Needs Adjustment",
            f'{posture_metrics["needs_adjustment_percentage"]}%',
        )

    # --------------------------------------------------
    # Content coverage
    # --------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        'Content Coverage'
        '</div>',
        unsafe_allow_html=True,
    )

    coverage_col1, coverage_col2, coverage_col3 = st.columns(3)

    with coverage_col1:
        st.metric(
            "Covered",
            content_result["covered_count"],
        )

    with coverage_col2:
        st.metric(
            "Partial",
            content_result["partial_count"],
        )

    with coverage_col3:
        st.metric(
            "Missed",
            content_result["missed_count"],
        )

    if content_result["covered_topics"]:
        st.markdown("**Covered topics**")

        for item in content_result["covered_topics"]:
            st.write(
                f'Covered - {item["topic"].title()} '
                f'- {item["overlap"]}%'
            )

    if content_result["partial_topics"]:
        st.markdown("**Partially covered topics**")

        for item in content_result["partial_topics"]:
            st.write(
                f'Partial - {item["topic"].title()} '
                f'- {item["overlap"]}%'
            )

    if content_result["missed_topics"]:
        st.markdown("**Missed topics**")

        for item in content_result["missed_topics"]:
            st.write(
                f'Missed - {item["topic"].title()}'
            )

    # --------------------------------------------------
    # Recommendations
    # --------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        '4. Personalized Feedback'
        '</div>',
        unsafe_allow_html=True,
    )

    if recommendations:
        for index, recommendation in enumerate(
            recommendations,
            start=1,
        ):
            st.markdown(
                f"""
                <div class="recommendation-card">
                    <strong>{index}.</strong>
                    {recommendation}
                </div>
                """,
                unsafe_allow_html=True,
            )

    else:
        st.info(
            "No recommendations were generated."
        )


# --------------------------------------------------
# Initial live-analysis placeholder
# --------------------------------------------------

elif uploaded_file is not None:
    st.markdown(
        '<div class="section-title">'
        '3. Live Analysis'
        '</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Speaking Pace",
            "-- WPM",
        )

    with col2:
        st.metric(
            "Filler Words",
            "--",
        )

    with col3:
        st.metric(
            "Posture",
            "--",
        )

    with col4:
        st.metric(
            "Content Coverage",
            "--%",
        )

    st.info(
        "Start the presentation to generate "
        "your live analysis and final report."
    )


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "SnapSpeak - On-device AI presentation coaching"
)