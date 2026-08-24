
# Handwritten OCR — Gemini vs Baidu Unlimited-OCR

An AI-powered handwritten OCR project that converts handwritten images into digital text and evaluates the OCR performance of two different AI models:

- Google Gemini API
- Baidu `baidu/Unlimited-OCR`

The project contains separate OCR services for each model and a dedicated benchmarking system that evaluates both models using the same handwritten dataset and manually verified ground-truth text.

---

## 📌 Project Overview

Handwritten text recognition is more challenging than traditional printed-text OCR because handwriting varies significantly between individuals.

This project has two objectives:

1. Convert handwritten documents into machine-readable text.
2. Compare the accuracy and performance of:
   - Gemini
   - Baidu `baidu/Unlimited-OCR`

The comparison is performed using the same input images and the same ground-truth transcriptions.

The benchmark calculates:

- Character Error Rate (CER)
- Word Error Rate (WER)
- Character Accuracy
- Exact Match
- Processing Latency

---

# 🏗️ Project Architecture

The repository is divided into three main components:

```text
OCR/
│
├── gemini-service/
│   ├── backend/
│   └── frontend/
│
├── handwritten-ocr-python/
│   ├── app/
│   ├── services/
│   ├── routes/
│   ├── uploads/
│   ├── templates/
│   └── static/
│
├── ocr-benchmark/
│   ├── dataset/
│   │   ├── images/
│   │   └── ground_truth/
│   │
│   ├── results/
│   │   ├── gemini/
│   │   └── unlimited_ocr/
│   │
│   ├── benchmark/
│   │   ├── run_gemini.py
│   │   └── run_unlimited_ocr.py
│   │
│   ├── evaluation/
│   │   ├── metrics.py
│   │   └── compare.py
│   │
│   └── reports/
│
└── README.md
````

---

# 🔍 Components

## 1. Gemini OCR Service

Location:

```text
gemini-service/
```

This service uses the Gemini API to analyze handwritten images and extract their text.

The Gemini service contains:

```text
gemini-service/
├── backend/
└── frontend/
```

The backend handles the OCR API while the frontend provides the user interface.

---

## 2. Baidu Unlimited-OCR Service

Location:

```text
handwritten-ocr-python/
```

This service uses:

```text
baidu/Unlimited-OCR
```

for handwritten OCR.

The application is built with FastAPI.

The main OCR endpoint is:

```text
POST /api/ocr
```

The API accepts an uploaded file using the multipart field:

```text
file
```

The application also provides:

```text
GET /health
GET /api/ocr/history
GET /api/ocr/{record_id}
```

---

## 3. OCR Benchmark

Location:

```text
ocr-benchmark/
```

The benchmark system processes the exact same handwritten images using both OCR systems.

The results are then compared against manually verified ground-truth transcriptions.

---

# 📂 Dataset Structure

The benchmark dataset is organized as:

```text
ocr-benchmark/
│
└── dataset/
    │
    ├── images/
    │   ├── image_001.jpeg
    │   ├── image_002.jpeg
    │   ├── image_003.jpeg
    │   └── image_004.jpeg
    │
    └── ground_truth/
        ├── image_001.txt
        ├── image_002.txt
        ├── image_003.txt
        └── image_004.txt
```

Each image has a corresponding ground-truth text file.

Example:

```text
image_001.jpeg
        ↓
image_001.txt
```

The `.txt` file contains the manually verified transcription of the handwritten image.

Ground truth is used as the reference when calculating OCR accuracy.

---

# ⚙️ Requirements

## Software

Recommended environment:

* Windows
* Python 3.12+
* Node.js and npm
* Git
* FastAPI
* Uvicorn

For Baidu Unlimited-OCR, a CUDA-compatible NVIDIA GPU is recommended.

The current project was tested with:

```text
GPU: NVIDIA GeForce RTX 3050
VRAM: 8 GB
```

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone https://github.com/bipasaroy10/OCR.git
```

Move into the project:

```bash
cd OCR
```

---

# 🧠 Gemini OCR Setup

Move into the Gemini backend:

```bash
cd gemini-service/backend
```

Create and activate a virtual environment if required:

### Windows

```powershell
python -m venv venv
```

Activate:

```powershell
venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create a `.env` file:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

Start the Gemini backend:

```powershell
python -m uvicorn main:app --host 0.0.0.0 --port 5000
```

Use the port configured by the Gemini service in your local setup.

---

# 🤖 Baidu Unlimited-OCR Setup

Move into:

```powershell
cd handwritten-ocr-python
```

Create a virtual environment:

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

Install the required dependencies:

```powershell
pip install -r requirements.txt
```

Start the FastAPI application:

```powershell
python -m uvicorn main:app --host 0.0.0.0 --port 5000
```

The application will be available at:

```text
http://localhost:5000
```

Swagger documentation:

```text
http://localhost:5000/docs
```

Health endpoint:

```text
http://localhost:5000/health
```

OCR endpoint:

```text
POST http://localhost:5000/api/ocr
```

---

# 📊 OCR Benchmark Setup

Move into:

```powershell
cd ocr-benchmark
```

Install benchmark dependencies:

```powershell
pip install -r requirements.txt
```

The benchmark dependencies include tools for:

* OCR API requests
* CER calculation
* WER calculation
* Excel reports
* CSV reports
* Data analysis

---

# 🧪 Running the Benchmark

## Step 1 — Prepare Dataset

Put handwritten images into:

```text
ocr-benchmark/dataset/images/
```

Example:

```text
image_001.jpeg
image_002.jpeg
image_003.jpeg
image_004.jpeg
```

Put the corresponding manually verified text into:

```text
ocr-benchmark/dataset/ground_truth/
```

Example:

```text
image_001.txt
image_002.txt
image_003.txt
image_004.txt
```

---

# Step 2 — Run Gemini OCR

From:

```text
ocr-benchmark/
```

run:

```powershell
python benchmark\run_gemini.py
```

Gemini processes every image in:

```text
dataset/images/
```

The extracted text is stored in:

```text
results/gemini/
```

Example:

```text
results/
└── gemini/
    ├── image_001.txt
    ├── image_002.txt
    ├── image_003.txt
    ├── image_004.txt
    └── metadata.json
```

The metadata contains processing time and other information required for the benchmark.

---

# Step 3 — Run Baidu Unlimited-OCR

Make sure the Baidu OCR API is running:

```text
http://localhost:5000/api/ocr
```

Then from:

```text
ocr-benchmark/
```

run:

```powershell
python benchmark\run_unlimited_ocr.py
```

The benchmark sends the same images to:

```text
POST http://localhost:5000/api/ocr
```

using the multipart field:

```text
file
```

The results are stored in:

```text
results/unlimited_ocr/
```

Example:

```text
results/
└── unlimited_ocr/
    ├── image_001.txt
    ├── image_002.txt
    ├── image_003.txt
    ├── image_004.txt
    └── metadata.json
```

---

# Step 4 — Compare Accuracy

After both OCR systems have processed all images, run:

```powershell
python evaluation\compare.py
```

The evaluation system compares:

```text
Ground Truth
     │
     ├───────────────┐
     │               │
     ▼               ▼
 Gemini Output   Unlimited-OCR Output
     │               │
     └───────┬───────┘
             ▼
        Evaluation
             │
      ┌──────┼──────┐
      ▼      ▼      ▼
     CER    WER   Accuracy
```

---

# 📏 Evaluation Metrics

## Character Error Rate (CER)

CER measures the number of character-level errors in the OCR result.

```text
CER =
(Substitutions + Deletions + Insertions)
/
Number of characters in ground truth
```

Lower CER is better.

---

## Word Error Rate (WER)

WER measures word-level OCR errors.

```text
WER =
(Substitutions + Deletions + Insertions)
/
Number of words in ground truth
```

Lower WER is better.

---

## Character Accuracy

The benchmark calculates:

```text
Character Accuracy =
(1 - CER) × 100
```

Higher accuracy is better.

---

## Exact Match

Exact Match checks whether the normalized OCR output exactly matches the normalized ground truth.

Higher is better.

---

## Processing Latency

Latency measures how long each OCR model takes to process an image.

Lower latency means faster processing.

---

# 📈 Benchmark Results

The current benchmark was performed on:

```text
4 handwritten images
```

The results are based on the current test dataset.

> Note: Four images are sufficient to verify the benchmark pipeline, but the dataset is too small to make a general claim about overall OCR superiority. A larger dataset should be used for a stronger evaluation.

---

# Per-Image Results

| Image     | Model         |    CER |    WER | Character Accuracy | Exact Match | Latency |
| --------- | ------------- | -----: | -----: | -----------------: | ----------- | ------: |
| image_001 | Gemini        | 19.27% | 28.57% |             80.73% | No          |  76.09s |
| image_002 | Gemini        | 14.93% | 31.47% |             85.07% | No          |  27.33s |
| image_003 | Gemini        | 21.86% | 43.59% |             78.14% | No          |  27.96s |
| image_004 | Gemini        | 26.20% | 48.37% |             73.80% | No          |  11.90s |
| image_001 | Unlimited-OCR | 55.88% | 74.88% |             44.12% | No          |  29.34s |
| image_002 | Unlimited-OCR | 61.28% | 60.91% |             38.72% | No          |  54.50s |
| image_003 | Unlimited-OCR | 54.47% | 65.38% |             45.53% | No          |  27.15s |
| image_004 | Unlimited-OCR | 59.35% | 78.43% |             40.65% | No          |  30.27s |

---

# 📊 Average Results

| Metric                     |      Gemini | Unlimited-OCR |
| -------------------------- | ----------: | ------------: |
| Average CER                | **20.565%** |       57.745% |
| Average WER                |  **38.00%** |        69.90% |
| Average Character Accuracy | **79.435%** |       42.255% |
| Average Latency            |      35.82s |    **35.31s** |
| Exact Matches              |           0 |             0 |

---

# 🏆 Benchmark Winners

### Character Error Rate

```text
Winner: Gemini

Gemini:         20.56%
Unlimited-OCR: 57.75%
```

Lower is better.

Gemini produced substantially fewer character-level errors on this test set.

---

### Word Error Rate

```text
Winner: Gemini

Gemini:         38.00%
Unlimited-OCR: 69.90%
```

Lower is better.

Gemini also produced substantially fewer word-level errors.

---

### Character Accuracy

```text
Winner: Gemini

Gemini:         79.44%
Unlimited-OCR: 42.26%
```

Higher is better.

Gemini achieved approximately 37.18 percentage points higher character accuracy on the current dataset.

---

### Processing Speed

```text
Winner: Unlimited-OCR

Gemini:         35.82 seconds/image
Unlimited-OCR: 35.31 seconds/image
```

Unlimited-OCR was approximately 0.51 seconds faster per image on average.

The latency difference is small compared with the accuracy difference observed in this test.

---

# 📌 Overall Result

Based on the current 4-image benchmark:

```text
                 GEMINI       UNLIMITED-OCR
                 ──────       ─────────────
CER              20.57%          57.75%
WER              38.00%          69.90%
Accuracy         79.44%          42.26%
Latency          35.82s          35.31s
```

### Accuracy Winner

🏆 **Gemini**

### Speed Winner

⚡ **Baidu Unlimited-OCR**

The current results indicate that Gemini provided considerably better OCR accuracy on this particular handwritten dataset, while Baidu Unlimited-OCR had a slightly lower average processing latency.

---

# 📁 Generated Benchmark Reports

After running:

```powershell
python evaluation\compare.py
```

the benchmark generates:

```text
results/
│
├── comparison.csv
├── summary.csv
└── ocr_comparison.xlsx
```

### `comparison.csv`

Contains per-image results:

```text
Image
Model
CER
WER
Character Accuracy
Exact Match
Latency
Ground Truth Length
Prediction Length
```

### `summary.csv`

Contains average results for each OCR model.

### `ocr_comparison.xlsx`

Excel report containing:

* Per-image results
* Summary results

---

# 🔬 Benchmark Methodology

The comparison follows the same process for both models:

```text
                 Same Dataset
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
       Gemini              Unlimited-OCR
          │                       │
          ▼                       ▼
     OCR Output              OCR Output
          │                       │
          └───────────┬───────────┘
                      │
                      ▼
                 Ground Truth
                      │
                      ▼
                 Evaluation
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
       CER           WER         Accuracy
```

Both models receive the same handwritten images.

Their outputs are evaluated against the same ground-truth transcriptions.

This provides a consistent basis for comparison.

---

# ⚠️ Current Benchmark Limitations

The current benchmark contains only:

```text
4 handwritten images
```

Therefore, the results should be considered an initial experiment rather than a statistically strong general evaluation.

A larger benchmark should contain:

* Easy handwriting
* Medium handwriting
* Difficult handwriting
* Messy handwriting
* Different handwriting styles
* Numbers
* Mathematical expressions
* Different image qualities
* Different lighting conditions
* Different document layouts

A future benchmark can use:

```text
20 images
50 images
100+ images
```

for a more reliable evaluation.

---

# 🚀 Future Improvements

Planned improvements include:

* Increase benchmark dataset size
* Add handwriting difficulty categories
* Add multilingual handwriting
* Add mathematical expression evaluation
* Add table/document-layout evaluation
* Add image preprocessing experiments
* Generate accuracy comparison graphs
* Generate automated benchmark reports
* Add cost-per-image comparison
* Add throughput comparison
* Add confidence analysis
* Add frontend benchmark dashboard
* Compare additional OCR/vision-language models

---

# 💡 Key Findings

The initial benchmark demonstrates an important trade-off:

### Gemini

Advantages:

* Higher character accuracy
* Lower character error rate
* Lower word error rate
* Better overall OCR quality on the current dataset

### Baidu Unlimited-OCR

Advantages:

* Local model deployment
* No per-request external API dependency when running locally
* Slightly faster average latency in the current test

The current benchmark therefore suggests:

> **Gemini is the stronger performer for OCR accuracy on the current handwritten test set, while Baidu Unlimited-OCR provides slightly better average processing speed.**

This conclusion is limited to the current 4-image benchmark and should be re-evaluated with a larger dataset.

---

# 🛠️ Technologies Used

## Gemini Service

* Google Gemini API
* Python
* FastAPI
* Uvicorn
* JavaScript / frontend technologies

## Baidu OCR Service

* Python
* FastAPI
* Uvicorn
* `baidu/Unlimited-OCR`
* PyTorch
* CUDA
* NVIDIA GPU

## Benchmark

* Python
* Pandas
* JiWER
* Python-Levenshtein
* OpenPyXL
* Requests

---

# 🔐 Environment Variables

Do not commit API keys to GitHub.

Use a `.env` file locally:

```env
GEMINI_API_KEY=your_api_key_here
```

Make sure `.env` is included in `.gitignore`.

Example:

```gitignore
.env
venv/
__pycache__/
*.pyc
```

---


# 👨‍💻 Author

**Bipasa Roy**

GitHub:

[https://github.com/bipasaroy10](https://github.com/bipasaroy10)

```

### One recommendation before you commit this

Your repository's current README appears to contain **placeholder OCR output text** and an older API-response example, rather than the benchmark documentation above. :contentReference[oaicite:2]{index=2} Replacing it with the README above will make the repository much easier for a recruiter, interviewer, or evaluator to understand.

Also, **don't describe the 79.44% vs 42.26% result as a universal conclusion**. Your current experiment has only four images, so the README correctly frames it as an initial benchmark. The next major improvement would be getting this to **50–100 handwritten images** and then adding graphs to the README.
```

[1]: https://github.com/bipasaroy10/OCR "GitHub - bipasaroy10/OCR · GitHub"
