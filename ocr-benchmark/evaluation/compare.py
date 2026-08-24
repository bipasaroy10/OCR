import os
import json
import pandas as pd

from metrics import (
    calculate_cer,
    calculate_wer,
    calculate_exact_match,
    calculate_character_accuracy
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

GROUND_TRUTH_DIR = os.path.join(
    BASE_DIR,
    "dataset",
    "ground_truth"
)

GEMINI_DIR = os.path.join(
    BASE_DIR,
    "results",
    "gemini"
)

UNLIMITED_DIR = os.path.join(
    BASE_DIR,
    "results",
    "unlimited_ocr"
)

RESULTS_DIR = os.path.join(
    BASE_DIR,
    "results"
)


# ============================================================
# READ TEXT FILE
# ============================================================

def read_text(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# ============================================================
# LOAD LATENCY METADATA
# ============================================================

def load_metadata(path):

    if not os.path.exists(path):

        return {}

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return {
            item["image_id"]: item
            for item in data
        }

    except Exception as error:

        print(
            f"WARNING: Could not read "
            f"{path}"
        )

        print(error)

        return {}


# ============================================================
# EVALUATE ONE MODEL
# ============================================================

def evaluate_model(
    model_name,
    result_directory,
    metadata
):

    rows = []

    image_files = []

    for filename in os.listdir(
        GROUND_TRUTH_DIR
    ):

        if filename.endswith(
            ".txt"
        ):

            image_files.append(
                filename
            )

    image_files.sort()


    for filename in image_files:

        image_id = os.path.splitext(
            filename
        )[0]


        # ----------------------------------------------------
        # Ground truth
        # ----------------------------------------------------

        ground_truth_path = os.path.join(
            GROUND_TRUTH_DIR,
            filename
        )


        # ----------------------------------------------------
        # Prediction
        # ----------------------------------------------------

        prediction_path = os.path.join(
            result_directory,
            filename
        )


        if not os.path.exists(
            prediction_path
        ):

            print(
                f"WARNING: Missing "
                f"{model_name} result for "
                f"{image_id}"
            )

            continue


        ground_truth = read_text(
            ground_truth_path
        )

        prediction = read_text(
            prediction_path
        )


        # ----------------------------------------------------
        # Metrics
        # ----------------------------------------------------

        cer = calculate_cer(
            ground_truth,
            prediction
        )

        wer_score = calculate_wer(
            ground_truth,
            prediction
        )

        character_accuracy = (
            calculate_character_accuracy(
                ground_truth,
                prediction
            )
        )

        exact_match = (
            calculate_exact_match(
                ground_truth,
                prediction
            )
        )


        # ----------------------------------------------------
        # Latency
        # ----------------------------------------------------

        model_metadata = metadata.get(
            image_id,
            {}
        )

        latency = model_metadata.get(
            "processing_time_seconds"
        )


        # ----------------------------------------------------
        # Store row
        # ----------------------------------------------------

        rows.append({

            "image_id":
                image_id,

            "model":
                model_name,

            "CER_%":
                round(
                    cer * 100,
                    2
                ),

            "WER_%":
                round(
                    wer_score * 100,
                    2
                ),

            "character_accuracy_%":
                round(
                    character_accuracy,
                    2
                ),

            "exact_match":
                exact_match,

            "latency_seconds":
                latency,

            "ground_truth_length":
                len(
                    ground_truth
                ),

            "prediction_length":
                len(
                    prediction
                )

        })


    return rows


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n"
        + "=" * 70
    )

    print(
        "       GEMINI vs UNLIMITED-OCR"
    )

    print(
        "              EVALUATION"
    )

    print(
        "=" * 70
    )


    # --------------------------------------------------------
    # Check ground truth
    # --------------------------------------------------------

    if not os.path.exists(
        GROUND_TRUTH_DIR
    ):

        print(
            "ERROR: Ground truth directory "
            "does not exist:"
        )

        print(
            GROUND_TRUTH_DIR
        )

        return


    # --------------------------------------------------------
    # Load metadata
    # --------------------------------------------------------

    gemini_metadata = load_metadata(

        os.path.join(
            GEMINI_DIR,
            "metadata.json"
        )

    )

    unlimited_metadata = load_metadata(

        os.path.join(
            UNLIMITED_DIR,
            "metadata.json"
        )

    )


    # --------------------------------------------------------
    # Evaluate Gemini
    # --------------------------------------------------------

    print(
        "\nEvaluating Gemini..."
    )

    gemini_results = evaluate_model(

        "Gemini",

        GEMINI_DIR,

        gemini_metadata

    )


    # --------------------------------------------------------
    # Evaluate Unlimited-OCR
    # --------------------------------------------------------

    print(
        "Evaluating Unlimited-OCR..."
    )

    unlimited_results = evaluate_model(

        "Unlimited-OCR",

        UNLIMITED_DIR,

        unlimited_metadata

    )


    # --------------------------------------------------------
    # Combine
    # --------------------------------------------------------

    all_results = (
        gemini_results +
        unlimited_results
    )


    if not all_results:

        print(
            "\nERROR: No results found."
        )

        return


    dataframe = pd.DataFrame(
        all_results
    )


    # ========================================================
    # SAVE RAW COMPARISON
    # ========================================================

    comparison_path = os.path.join(

        RESULTS_DIR,

        "comparison.csv"

    )

    dataframe.to_csv(

        comparison_path,

        index=False

    )


    # ========================================================
    # SUMMARY
    # ========================================================

    summary = (
        dataframe
        .groupby("model")
        .agg({

            "CER_%":
                "mean",

            "WER_%":
                "mean",

            "character_accuracy_%":
                "mean",

            "latency_seconds":
                "mean",

            "exact_match":
                "sum"

        })
        .reset_index()
    )


    summary = summary.rename(

        columns={
            "CER_%":
                "average_CER_%",

            "WER_%":
                "average_WER_%",

            "character_accuracy_%":
                "average_character_accuracy_%",

            "latency_seconds":
                "average_latency_seconds",

            "exact_match":
                "exact_match_count"

        }

    )


    # --------------------------------------------------------
    # Save summary
    # --------------------------------------------------------

    summary_path = os.path.join(

        RESULTS_DIR,

        "summary.csv"

    )

    summary.to_csv(

        summary_path,

        index=False

    )


    # ========================================================
    # PRINT RESULTS
    # ========================================================

    print(
        "\n"
        + "=" * 70
    )

    print(
        "                 RESULTS"
    )

    print(
        "=" * 70
    )

    print(
        "\nPer-image results:"
    )

    print(
        dataframe.to_string(
            index=False
        )
    )


    print(
        "\n"
        + "=" * 70
    )

    print(
        "                 SUMMARY"
    )

    print(
        "=" * 70
    )

    print(
        summary.to_string(
            index=False
        )
    )


    # ========================================================
    # DETERMINE WINNERS
    # ========================================================

    print(
        "\n"
        + "=" * 70
    )

    print(
        "                 WINNERS"
    )

    print(
        "=" * 70
    )


    # Lower CER = better

    cer_winner = summary.loc[
        summary["average_CER_%"].idxmin()
    ]

    print(
        "\nLowest CER:"
    )

    print(
        f"{cer_winner['model']} "
        f"({cer_winner['average_CER_%']:.2f}%)"
    )


    # Lower WER = better

    wer_winner = summary.loc[
        summary["average_WER_%"].idxmin()
    ]

    print(
        "\nLowest WER:"
    )

    print(
        f"{wer_winner['model']} "
        f"({wer_winner['average_WER_%']:.2f}%)"
    )


    # Higher accuracy = better

    accuracy_winner = summary.loc[
        summary[
            "average_character_accuracy_%"
        ].idxmax()
    ]

    print(
        "\nHighest character accuracy:"
    )

    print(
        f"{accuracy_winner['model']} "
        f"({accuracy_winner['average_character_accuracy_%']:.2f}%)"
    )


    # Lower latency = faster

    latency_winner = summary.loc[
        summary[
            "average_latency_seconds"
        ].idxmin()
    ]

    print(
        "\nFastest:"
    )

    print(
        f"{latency_winner['model']} "
        f"({latency_winner['average_latency_seconds']:.2f} sec)"
    )


    # ========================================================
    # EXCEL REPORT
    # ========================================================

    excel_path = os.path.join(

        RESULTS_DIR,

        "ocr_comparison.xlsx"

    )


    with pd.ExcelWriter(
        excel_path,
        engine="openpyxl"
    ) as writer:

        dataframe.to_excel(

            writer,

            sheet_name="Per Image",

            index=False

        )

        summary.to_excel(

            writer,

            sheet_name="Summary",

            index=False

        )


    # ========================================================
    # COMPLETE
    # ========================================================

    print(
        "\n"
        + "=" * 70
    )

    print(
        "             EVALUATION COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        "\nCSV:"
    )

    print(
        comparison_path
    )

    print(
        "\nSummary:"
    )

    print(
        summary_path
    )

    print(
        "\nExcel:"
    )

    print(
        excel_path
    )


if __name__ == "__main__":

    main()