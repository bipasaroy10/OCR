import re
from jiwer import wer
from Levenshtein import distance


def normalize_text(text: str) -> str:
    """
    Normalize text for fair OCR comparison.
    """

    if text is None:
        return ""

    text = text.lower()

    # Normalize line breaks and spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    # Remove leading/trailing spaces
    text = text.strip()

    return text


def calculate_cer(
    ground_truth: str,
    prediction: str
) -> float:

    ground_truth = normalize_text(
        ground_truth
    )

    prediction = normalize_text(
        prediction
    )

    if not ground_truth:

        return (
            0.0
            if not prediction
            else 1.0
        )

    edit_distance = distance(
        ground_truth,
        prediction
    )

    return (
        edit_distance /
        len(ground_truth)
    )


def calculate_wer(
    ground_truth: str,
    prediction: str
) -> float:

    ground_truth = normalize_text(
        ground_truth
    )

    prediction = normalize_text(
        prediction
    )

    if not ground_truth:

        return (
            0.0
            if not prediction
            else 1.0
        )

    return wer(
        ground_truth,
        prediction
    )


def calculate_exact_match(
    ground_truth: str,
    prediction: str
) -> bool:

    ground_truth = normalize_text(
        ground_truth
    )

    prediction = normalize_text(
        prediction
    )

    return (
        ground_truth ==
        prediction
    )


def calculate_character_accuracy(
    ground_truth: str,
    prediction: str
) -> float:

    cer = calculate_cer(
        ground_truth,
        prediction
    )

    accuracy = (
        1 - cer
    ) * 100

    return max(
        0.0,
        accuracy
    )