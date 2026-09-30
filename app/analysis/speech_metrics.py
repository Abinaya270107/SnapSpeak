import re


FILLER_WORDS = {
    "um",
    "umm",
    "uh",
    "uhh",
    "er",
    "erm",
    "like",
    "actually",
    "basically",
}

FILLER_PHRASES = {
    "you know",
    "i mean",
    "kind of",
    "sort of",
}


def extract_words(text):
    """Extract normalized words from a transcript."""
    return re.findall(r"\b[\w']+\b", (text or "").lower())


def _get_valid_intervals(segments):
    """Extract valid start/end intervals from Whisper segments."""
    intervals = []

    for segment in segments or []:
        try:
            start = float(segment.get("start", 0))
            end = float(segment.get("end", 0))
        except (AttributeError, TypeError, ValueError):
            continue

        if start >= 0 and end > start:
            intervals.append((start, end))

    return sorted(intervals)


def _merge_intervals(intervals):
    """Merge overlapping intervals to avoid double-counting time."""
    if not intervals:
        return []

    merged = []
    current_start, current_end = intervals[0]

    for start, end in intervals[1:]:
        if start <= current_end:
            current_end = max(current_end, end)
        else:
            merged.append((current_start, current_end))
            current_start, current_end = start, end

    merged.append((current_start, current_end))
    return merged


def calculate_speech_duration(segments):
    """Calculate the total time covered by speech segments."""
    intervals = _merge_intervals(_get_valid_intervals(segments))
    return sum(end - start for start, end in intervals)


def count_filler_words(words):
    """Count configured filler words and phrases."""
    counts = {}
    phrases = sorted(
        (phrase.split() for phrase in FILLER_PHRASES),
        key=len,
        reverse=True,
    )

    i = 0

    while i < len(words):
        matched_phrase = None

        # Match phrases before individual words.
        for phrase_words in phrases:
            candidate = words[i:i + len(phrase_words)]

            if candidate == phrase_words:
                matched_phrase = " ".join(phrase_words)
                break

        if matched_phrase:
            counts[matched_phrase] = counts.get(matched_phrase, 0) + 1
            i += len(matched_phrase.split())
            continue

        word = words[i]

        if word in FILLER_WORDS:
            counts[word] = counts.get(word, 0) + 1

        i += 1

    return counts


def calculate_speech_metrics(
    transcript,
    duration_seconds,
    segments=None,
):
    """
    Calculate presentation speech metrics.

    words_per_minute:
        Recognized words divided by full recording duration.

    speech_only_words_per_minute:
        Recognized words divided by the duration covered by
        Whisper's speech segments.
    """
    text = (transcript or "").strip()

    try:
        recording_duration = max(0.0, float(duration_seconds))
    except (TypeError, ValueError):
        recording_duration = 0.0

    words = extract_words(text)
    word_count = len(words)

    if not text:
        return {
            "word_count": 0,
            "duration_seconds": round(recording_duration, 2),
            "speech_duration_seconds": 0.0,
            "words_per_minute": 0.0,
            "speech_only_words_per_minute": 0.0,
            "filler_count": 0,
            "filler_words": {},
            "pause_count": 0,
            "total_pause_seconds": 0.0,
            "longest_pause_seconds": 0.0,
        }

    intervals = _merge_intervals(_get_valid_intervals(segments))
    speech_duration = sum(
        end - start for start, end in intervals
    )

    # Fall back when segment timestamps are unavailable.
    if speech_duration <= 0:
        speech_duration = recording_duration

    overall_wpm = (
        word_count / recording_duration * 60
        if recording_duration > 0
        else 0.0
    )

    speech_only_wpm = (
        word_count / speech_duration * 60
        if speech_duration > 0
        else 0.0
    )

    filler_counts = count_filler_words(words)
    filler_count = sum(filler_counts.values())

    # Calculate pauses between merged speech intervals.
    pause_count = 0
    total_pause_seconds = 0.0
    longest_pause_seconds = 0.0

    for previous, current in zip(intervals, intervals[1:]):
        pause = current[0] - previous[1]

        # Ignore gaps shorter than 0.5 seconds.
        if pause >= 0.5:
            pause_count += 1
            total_pause_seconds += pause
            longest_pause_seconds = max(
                longest_pause_seconds,
                pause,
            )

    return {
        "word_count": word_count,
        "duration_seconds": round(recording_duration, 2),
        "speech_duration_seconds": round(speech_duration, 2),
        "words_per_minute": round(overall_wpm, 1),
        "speech_only_words_per_minute": round(speech_only_wpm, 1),
        "filler_count": filler_count,
        "filler_words": filler_counts,
        "pause_count": pause_count,
        "total_pause_seconds": round(total_pause_seconds, 2),
        "longest_pause_seconds": round(longest_pause_seconds, 2),
    }


def print_speech_metrics(metrics):
    """Display speech-analysis metrics in the terminal."""
    print("\n" + "=" * 50)
    print("SNAPSPEAK SPEECH ANALYSIS")
    print("=" * 50)

    print(f"\nWords Spoken       : {metrics['word_count']}")
    print(f"Recording Time     : {metrics['duration_seconds']} seconds")
    print(f"Speech Time        : {metrics['speech_duration_seconds']} seconds")
    print(f"Overall WPM        : {metrics['words_per_minute']}")
    print(
        "Speech-only WPM   : "
        f"{metrics.get('speech_only_words_per_minute', 0)}"
    )
    print(f"Filler Words       : {metrics['filler_count']}")

    print("\nFiller Word Breakdown:")
    if metrics["filler_words"]:
        for word, count in metrics["filler_words"].items():
            print(f"  {word}: {count}")
    else:
        print("  None detected")

    print(f"\nPauses             : {metrics['pause_count']}")
    print(f"Total Pause        : {metrics['total_pause_seconds']} seconds")
    print(f"Longest Pause      : {metrics['longest_pause_seconds']} seconds")
    print("\n" + "=" * 50)