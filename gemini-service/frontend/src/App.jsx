import { useState } from "react";
import "./App.css";

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [extractedText, setExtractedText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (event) => {
    const file = event.target.files[0];

    if (!file) {
      return;
    }

    setSelectedFile(file);
    setExtractedText("");
    setError("");

    const previewUrl = URL.createObjectURL(file);
    setPreview(previewUrl);
  };

  const handleExtractText = async () => {
    if (!selectedFile) {
      setError("Please select a handwritten image first.");
      return;
    }

    setLoading(true);
    setError("");
    setExtractedText("");

    try {
      const formData = new FormData();

      formData.append("file", selectedFile);

      const response = await fetch(
        "http://127.0.0.1:8000/api/ocr/handwritten",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to extract text."
        );
      }

      setExtractedText(data.text || "");
    } catch (error) {
      console.error("OCR ERROR:", error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyText = async () => {
    if (!extractedText) {
      return;
    }

    try {
      await navigator.clipboard.writeText(extractedText);
      alert("Text copied successfully!");
    } catch (error) {
      console.error("COPY ERROR:", error);
    }
  };

  return (
    <div className="app">

      <div className="container">

        <h1>Handwritten OCR</h1>

        <p className="subtitle">
          Convert handwritten images into digital text using Gemini AI.
        </p>

        {/* Upload Section */}

        <div className="upload-section">

          <label htmlFor="file-upload" className="upload-box">

            {preview ? (
              <img
                src={preview}
                alt="Handwritten preview"
                className="preview-image"
              />
            ) : (
              <>
                <div className="upload-icon">
                  📄
                </div>

                <p>
                  Click to select handwritten image
                </p>

                <span>
                  JPG, PNG or WEBP
                </span>
              </>
            )}

          </label>

          <input
            id="file-upload"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={handleFileChange}
          />

        </div>

        {/* Selected File */}

        {selectedFile && (
          <p className="file-name">
            Selected: {selectedFile.name}
          </p>
        )}

        {/* Extract Button */}

        <button
          className="extract-button"
          onClick={handleExtractText}
          disabled={loading || !selectedFile}
        >
          {loading
            ? "Extracting..."
            : "Extract Text"}
        </button>

        {/* Error */}

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        {/* Result */}

        {extractedText && (
          <div className="result-section">

            <div className="result-header">

              <h2>
                Extracted Text
              </h2>

              <button
                className="copy-button"
                onClick={handleCopyText}
              >
                Copy Text
              </button>

            </div>

            <textarea
              value={extractedText}
              onChange={(event) =>
                setExtractedText(event.target.value)
              }
              className="result-text"
            />

          </div>
        )}

      </div>

    </div>
  );
}

export default App;