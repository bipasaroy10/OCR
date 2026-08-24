const fileInput =
    document.getElementById("fileInput");

const dropZone =
    document.getElementById("dropZone");

const ocrButton =
    document.getElementById("ocrButton");

const selectedFile =
    document.getElementById("selectedFile");

const loading =
    document.getElementById("loading");

const errorMessage =
    document.getElementById("errorMessage");

const resultSection =
    document.getElementById("resultSection");

const ocrText =
    document.getElementById("ocrText");

const resultFileName =
    document.getElementById("resultFileName");

const pageCount =
    document.getElementById("pageCount");

const modelName =
    document.getElementById("modelName");

const copyButton =
    document.getElementById("copyButton");

const downloadButton =
    document.getElementById("downloadButton");

const historyContainer =
    document.getElementById("historyContainer");

const refreshHistory =
    document.getElementById("refreshHistory");

const historySearch =
    document.getElementById("historySearch");

const serverStatus =
    document.getElementById("serverStatus");


let selectedFileObject = null;

let historyRecords = [];


// ==========================================================
// SERVER HEALTH
// ==========================================================

async function checkServer() {

    try {

        const response =
            await fetch("/health");

        if (!response.ok) {

            throw new Error(
                "Server unavailable"
            );
        }


        const data =
            await response.json();


        if (data.success) {

            serverStatus.textContent =
                data.database === "connected"
                    ? "● Online"
                    : "● API Online";

            serverStatus.className =
                "status online";

        } else {

            throw new Error(
                "Health check failed"
            );
        }


    } catch (error) {

        serverStatus.textContent =
            "● Offline";

        serverStatus.className =
            "status offline";
    }
}


// ==========================================================
// FILE SELECT
// ==========================================================

fileInput.addEventListener(
    "change",
    function () {

        if (
            this.files &&
            this.files.length > 0
        ) {

            selectFile(
                this.files[0]
            );
        }

    }
);


// ==========================================================
// SELECT FILE
// ==========================================================

function selectFile(file) {

    selectedFileObject = file;

    selectedFile.textContent =
        `${file.name} (${formatBytes(file.size)})`;

    ocrButton.disabled = false;

    hideError();

    resultSection.classList.add(
        "hidden"
    );
}


// ==========================================================
// DRAG AND DROP
// ==========================================================

dropZone.addEventListener(
    "dragover",
    function (event) {

        event.preventDefault();

        dropZone.classList.add(
            "dragover"
        );
    }
);


dropZone.addEventListener(
    "dragleave",
    function () {

        dropZone.classList.remove(
            "dragover"
        );
    }
);


dropZone.addEventListener(
    "drop",
    function (event) {

        event.preventDefault();

        dropZone.classList.remove(
            "dragover"
        );


        const files =
            event.dataTransfer.files;


        if (files.length > 0) {

            selectFile(
                files[0]
            );
        }

    }
);


// ==========================================================
// RUN OCR
// ==========================================================

ocrButton.addEventListener(
    "click",
    runOCR
);


async function runOCR() {

    if (!selectedFileObject) {

        showError(
            "Please select a file first."
        );

        return;
    }


    const formData =
        new FormData();

    formData.append(
        "file",
        selectedFileObject
    );


    setLoading(true);

    hideError();


    try {

        const response =
            await fetch(
                "/api/ocr",
                {
                    method: "POST",
                    body: formData
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                data.message ||
                "OCR failed."
            );
        }


        if (
            !data.success ||
            !data.data
        ) {

            throw new Error(
                "Invalid OCR response."
            );
        }


        displayOCRResult(
            data.data
        );


        await loadHistory();


    } catch (error) {

        console.error(
            "OCR ERROR:",
            error
        );

        showError(
            error.message ||
            "OCR processing failed."
        );


    } finally {

        setLoading(false);
    }
}


// ==========================================================
// DISPLAY OCR RESULT
// ==========================================================

function displayOCRResult(data) {

    resultSection.classList.remove(
        "hidden"
    );


    resultFileName.textContent =
        data.originalName ||
        "Uploaded file";


    pageCount.textContent =
        data.pageCount ||
        1;


    modelName.textContent =
        data.model ||
        "Unlimited-OCR";


    /*
     * IMPORTANT:
     *
     * OCR text should normally be in:
     *
     * data.ocrText
     *
     * Some implementations may return:
     *
     * data.text
     *
     * or:
     *
     * data.rawText
     *
     */

    const text =
        data.ocrText ??
        data.text ??
        data.rawText ??
        "";


    ocrText.value =
        typeof text === "string"
            ? text
            : JSON.stringify(
                text,
                null,
                2
            );


    resultSection.scrollIntoView({
        behavior: "smooth"
    });
}


// ==========================================================
// COPY
// ==========================================================

copyButton.addEventListener(
    "click",
    async function () {

        if (!ocrText.value) {

            return;
        }


        try {

            await navigator.clipboard.writeText(
                ocrText.value
            );


            const original =
                copyButton.textContent;


            copyButton.textContent =
                "✓ Copied";


            setTimeout(
                () => {

                    copyButton.textContent =
                        original;

                },
                1500
            );


        } catch (error) {

            showError(
                "Could not copy text."
            );
        }

    }
);


// ==========================================================
// DOWNLOAD
// ==========================================================

downloadButton.addEventListener(
    "click",
    function () {

        const text =
            ocrText.value;


        if (!text) {

            return;
        }


        const blob =
            new Blob(
                [text],
                {
                    type: "text/plain"
                }
            );


        const url =
            URL.createObjectURL(
                blob
            );


        const link =
            document.createElement(
                "a"
            );


        link.href = url;

        link.download =
            "ocr-result.txt";


        document.body.appendChild(
            link
        );


        link.click();

        link.remove();


        URL.revokeObjectURL(
            url
        );
    }
);


// ==========================================================
// HISTORY
// ==========================================================

async function loadHistory() {

    try {

        const response =
            await fetch(
                "/api/ocr/history"
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Failed to load history."
            );
        }


        historyRecords =
            data.data || [];


        renderHistory(
            historyRecords
        );


    } catch (error) {

        console.error(
            "HISTORY ERROR:",
            error
        );


        historyContainer.innerHTML = `
            <p class="empty">
                Unable to load OCR history.
            </p>
        `;
    }
}


// ==========================================================
// RENDER HISTORY
// ==========================================================

function renderHistory(records) {

    if (!records.length) {

        historyContainer.innerHTML = `
            <p class="empty">
                No OCR records found.
            </p>
        `;

        return;
    }


    historyContainer.innerHTML =
        records.map(
            record => {

                const id =
                    record._id ||
                    record.id;


                const name =
                    escapeHTML(
                        record.originalName ||
                        "Unknown file"
                    );


                const pages =
                    record.pageCount ||
                    1;


                const date =
                    formatDate(
                        record.createdAt
                    );


                return `
                    <div class="history-item">

                        <div>

                            <div class="history-name">
                                ${name}
                            </div>

                            <div class="history-meta">
                                ${pages} page(s)
                                •
                                ${date}
                            </div>

                        </div>

                        <button
                            class="view-button"
                            onclick="viewOCR('${id}')"
                        >
                            View
                        </button>

                    </div>
                `;

            }
        ).join("");
}


// ==========================================================
// VIEW ONE OCR
// ==========================================================

async function viewOCR(id) {

    if (!id) {

        showError(
            "OCR record ID is missing."
        );

        return;
    }


    try {

        const response =
            await fetch(
                `/api/ocr/${id}`
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to load OCR result."
            );
        }


        if (
            !data.success ||
            !data.data
        ) {

            throw new Error(
                "Invalid OCR response."
            );
        }


        displayOCRResult(
            data.data
        );


    } catch (error) {

        console.error(
            "VIEW OCR ERROR:",
            error
        );


        showError(
            error.message
        );
    }
}


// ==========================================================
// SEARCH HISTORY
// ==========================================================

historySearch.addEventListener(
    "input",
    function () {

        const query =
            this.value
                .toLowerCase()
                .trim();


        if (!query) {

            renderHistory(
                historyRecords
            );

            return;
        }


        const filtered =
            historyRecords.filter(
                record => {

                    const name =
                        (
                            record.originalName ||
                            ""
                        ).toLowerCase();


                    const text =
                        (
                            record.ocrText ||
                            record.text ||
                            ""
                        ).toLowerCase();


                    return (
                        name.includes(query) ||
                        text.includes(query)
                    );
                }
            );


        renderHistory(
            filtered
        );
    }
);


// ==========================================================
// REFRESH HISTORY
// ==========================================================

refreshHistory.addEventListener(
    "click",
    loadHistory
);


// ==========================================================
// LOADING
// ==========================================================

function setLoading(isLoading) {

    if (isLoading) {

        loading.classList.remove(
            "hidden"
        );

        ocrButton.disabled = true;

        ocrButton.textContent =
            "Processing...";

    } else {

        loading.classList.add(
            "hidden"
        );

        ocrButton.disabled =
            !selectedFileObject;

        ocrButton.textContent =
            "Run OCR";
    }
}


// ==========================================================
// ERROR
// ==========================================================

function showError(message) {

    errorMessage.textContent =
        message;

    errorMessage.classList.remove(
        "hidden"
    );
}


function hideError() {

    errorMessage.classList.add(
        "hidden"
    );

    errorMessage.textContent =
        "";
}


// ==========================================================
// FORMAT FILE SIZE
// ==========================================================

function formatBytes(bytes) {

    if (!bytes) {

        return "0 B";
    }


    const units = [
        "B",
        "KB",
        "MB",
        "GB"
    ];


    const index =
        Math.floor(
            Math.log(bytes) /
            Math.log(1024)
        );


    return (
        `${(
            bytes /
            Math.pow(
                1024,
                index
            )
        ).toFixed(2)} ${units[index]}`
    );
}


// ==========================================================
// FORMAT DATE
// ==========================================================

function formatDate(date) {

    if (!date) {

        return "Unknown date";
    }


    try {

        return new Date(
            date
        ).toLocaleString();

    } catch {

        return "Unknown date";
    }
}


// ==========================================================
// HTML ESCAPE
// ==========================================================

function escapeHTML(value) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


// ==========================================================
// INITIALIZE
// ==========================================================

checkServer();

loadHistory();