@'
# SnapSpeak — AI Presentation Coach

SnapSpeak is an AI-assisted presentation coaching application that helps users review their speaking delivery, posture, pacing, and slide-topic coverage.

## Problem

Presenters often practise without objective feedback on speaking speed, filler words, pauses, posture, or whether their speech covers the key topics in their slides. SnapSpeak combines speech analysis, pose estimation, and presentation-document analysis in one workflow.

## Features

- **Speech analysis:** Transcribes recorded speech with Whisper and estimates speaking rate in words per minute.
- **Filler-word analysis:** Identifies configured filler words in the transcript.
- **Pause analysis:** Summarizes detected pauses and their durations.
- **Posture analysis:** Uses YOLO11 pose estimation to derive visual posture-related feedback.
- **PDF slide analysis:** Extracts presentation text and identifies topics for comparison with the transcript.
- **Topic coverage:** Highlights potential gaps between extracted slide topics and the spoken transcript.
- **Actionable feedback:** Combines analysis results into presentation-improvement recommendations.
- **Interactive interface:** Provides a Streamlit-based user interface.

## Technology Stack

- Python
- Streamlit
- Whisper speech recognition
- PyTorch and YOLO11 pose estimation
- ONNX Runtime
- ONNX Runtime QNN Execution Provider for Snapdragon testing
- PDF text extraction and Python-based analysis

## Architecture

```text
Audio Recording ──> Speech Recognition ──> Transcript Analysis
                                              │
                                              ├── Speaking rate
                                              ├── Filler words
                                              └── Pause statistics

Video / Camera Input ──> YOLO11 Pose Estimation
                                   │
                                   └── Posture-related observations

Presentation PDF ──> Text Extraction ──> Topic Extraction
                                              │
Transcript + Topic Analysis ──────────────────┘
                     │
                     v
           Coaching Recommendations
                     │
                     v
              Streamlit UI

## Running the Application

Open PowerShell and run:

```powershell
cd D:\SnapSpeak
streamlit run app\ui\app.py
```

Open the local URL shown in the terminal, usually http://localhost:8501.

Install dependencies from `requirements.txt` if needed. Some features may require model files and additional configuration.

## Snapdragon Testing

The YOLO11 pose model was exported to ONNX and tested on a remote Snapdragon X Elite Compute Reference Design running Windows 11 with ARM64 Python.

Test environment:

* Python 3.12.10 ARM64
* ONNX Runtime 1.27.0
* ONNX Runtime QNN 2.6.0
* QNN HTP backend configuration

The model produced an output tensor of shape `(1, 56, 8400)`. One recorded Python-level inference run took approximately 32.26 ms.

A detailed QNN profiling report was collected and saved as `evidence/qnn_profile.csv`.

### Measurement Limitations

* Testing was performed on a remote Snapdragon reference device, not on the developer's Intel laptop.
* An unsupported Sigmoid operation was reported during an earlier run.
* The session listed both QNN and CPU execution providers.
* Current evidence does not establish that every model operation executed on the NPU.
* Profiling timings come from different measurement scopes and should not be combined into one latency figure.
* The recorded inference time is a single run, not a controlled benchmark.

These results demonstrate successful ONNX inference and collected QNN profiling evidence. Further validation is needed to establish full-graph NPU execution and reliable performance.

## Evidence Files

The `evidence` directory contains:

* `01_snapdragon_arm64.png` — ARM64 Python environment
* `02_qnn_inference.png` — ONNX inference output and timing
* `03_qnn_profile.png` — QNN profiling records
* `qnn_profile.csv` — detailed profiling output

## Limitations and Future Work

* Evaluate speech and posture feedback across more recording conditions.
* Improve topic matching between slide text and spoken content.
* Investigate unsupported operators and verify QNN node placement.
* Benchmark repeated, warmed-up inference runs.
* Improve error handling and add automated tests.
* Test packaging on supported devices.

## Privacy

Audio, video, and presentation files may contain sensitive information. Use appropriate test data for demonstrations and avoid publishing private recordings. Confirm where each component processes data before describing the application as fully offline or on-device.

## References

* Qualcomm Snapdragon AI Lab: https://www.qualcomm.com/snapdragon/ai-lab
* ONNX Runtime QNN Execution Provider: https://onnxruntime.ai/docs/execution-providers/QNN-ExecutionProvider.html
* ONNX Runtime profiling: https://onnxruntime.ai/docs/performance/tune-performance/profiling-tools.html

## Project Status

SnapSpeak is a working prototype combining speech analysis, pose estimation, presentation-document analysis, coaching recommendations, and a Streamlit interface. Snapdragon optimization and testing remain experimental, subject to the limitations described above.
