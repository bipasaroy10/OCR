// ============================================================
// HANDWRITTEN OCR FRONTEND
// backend/public/js/app.js
// ============================================================

"use strict";

// ============================================================
// DOM ELEMENTS
// ============================================================

const fileInput = document.getElementById("fileInput");
const browseButton = document.getElementById("browseButton");
const dropZone = document.getElementById("dropZone");

const filePreview = document.getElementById("filePreview");
const fileName = document.getElementById("fileName");
const fileSize = document.getElementById("fileSize");
const removeFile = document.getElementById("removeFile");

const processButton = document.getElementById("processButton");
const buttonText = document.getElementById("buttonText");
const loader = document.getElementById("loader");
const processing = document.getElementById("processing");

const resultSection = document.getElementById("resultSection");
const errorSection = document.getElementById("errorSection");
const errorMessage = document.getElementById("errorMessage");

const ocrResult = document.getElementById("ocrResult");
const resultFile = document.getElementById("resultFile");
const resultType = document.getElementById("resultType");

const copyButton = document.getElementById("copyButton");
const downloadButton = document.getElementById("downloadButton");

const ocrForm = document.getElementById("ocrForm");

// ============================================================
// CONFIGURATION
// ============================================================

const CONFIG = {
    apiEndpoint: "/api/ocr",

    maxFileSize: 50 * 1024 * 1024,

    // 10 minutes
    requestTimeout: 10 * 60 * 1000,

    allowedExtensions: [
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".pdf"
    ],

    allowedMimeTypes: [
        "image/jpeg",
        "image/png",
        "image/webp",
        "application/pdf"
    ]
};

// ============================================================
// STATE
// ============================================================

let selectedFile = null;
let isProcessing = false;
let lastOCRResponse = null;

// ============================================================
// INITIALIZATION
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    initializeApplication
);

function initializeApplication() {

    console.log(
        "=========================================="
    );

    console.log(
        "Handwritten OCR frontend initialized"
    );

    console.log(
        "=========================================="
    );

    if (!fileInput) {
        console.error(
            "fileInput element not found."
        );

        return;
    }

    setupBrowseButton();

    setupFileInput();

    setupDragAndDrop();

    setupRemoveButton();

    setupOCRForm();

    setupCopyButton();

    setupDownloadButton();

    resetInterface();
}

// ============================================================
// BROWSE BUTTON
// ============================================================

function setupBrowseButton() {

    if (!browseButton) {
        return;
    }

    browseButton.addEventListener(
        "click",
        function (event) {

            event.preventDefault();

            event.stopPropagation();

            fileInput.click();

        }
    );
}

// ============================================================
// FILE INPUT
// ============================================================

function setupFileInput() {

    fileInput.addEventListener(
        "change",
        function (event) {

            const files =
                event.target.files;

            if (
                !files ||
                files.length === 0
            ) {
                return;
            }

            setSelectedFile(
                files[0]
            );
        }
    );
}

// ============================================================
// DRAG AND DROP
// ============================================================

function setupDragAndDrop() {

    if (!dropZone) {
        return;
    }

    dropZone.addEventListener(
        "dragenter",
        handleDragEnter
    );

    dropZone.addEventListener(
        "dragover",
        handleDragEnter
    );

    dropZone.addEventListener(
        "dragleave",
        handleDragLeave
    );

    dropZone.addEventListener(
        "drop",
        handleDrop
    );

    dropZone.addEventListener(
        "click",
        function (event) {

            if (
                browseButton &&
                (
                    event.target ===
                    browseButton ||
                    browseButton.contains(
                        event.target
                    )
                )
            ) {
                return;
            }

            fileInput.click();

        }
    );
}

function handleDragEnter(event) {

    event.preventDefault();

    event.stopPropagation();

    if (dropZone) {
        dropZone.classList.add(
            "dragover"
        );
    }
}

function handleDragLeave(event) {

    event.preventDefault();

    event.stopPropagation();

    if (dropZone) {
        dropZone.classList.remove(
            "dragover"
        );
    }
}

function handleDrop(event) {

    event.preventDefault();

    event.stopPropagation();

    if (dropZone) {
        dropZone.classList.remove(
            "dragover"
        );
    }

    const files =
        event.dataTransfer?.files;

    if (
        !files ||
        files.length === 0
    ) {
        return;
    }

    setSelectedFile(
        files[0]
    );
}

// ============================================================
// SET SELECTED FILE
// ============================================================

function setSelectedFile(file) {

    hideError();

    const validation =
        validateFile(file);

    if (!validation.valid) {

        clearSelectedFile();

        showError(
            validation.message
        );

        return;
    }

    selectedFile = file;

    lastOCRResponse = null;

    // File name
    if (fileName) {

        fileName.textContent =
            file.name;

    }

    // File size
    if (fileSize) {

        fileSize.textContent =
            formatFileSize(
                file.size
            );

    }

    // Show preview/card
    if (filePreview) {

        filePreview.classList.remove(
            "hidden"
        );

    }

    // Enable OCR button
    if (processButton) {

        processButton.disabled =
            false;

    }

    // Remove old result
    clearOCRResult();

    console.log(
        "Selected file:",
        {
            name: file.name,
            size: file.size,
            type:
                file.type ||
                "(empty MIME type)"
        }
    );
}

// ============================================================
// VALIDATE FILE
// ============================================================

function validateFile(file) {

    if (!file) {

        return {
            valid: false,
            message:
                "Please select a file."
        };
    }

    const extension =
        getFileExtension(
            file.name
        );

    const validExtension =
        CONFIG.allowedExtensions.includes(
            extension
        );

    const validMimeType =
        CONFIG.allowedMimeTypes.includes(
            file.type
        );

    // Browser may return empty MIME
    // for some dragged files.
    if (
        !validExtension &&
        !validMimeType
    ) {

        return {
            valid: false,
            message:
                "Unsupported file type. Please upload JPG, JPEG, PNG, WEBP, or PDF."
        };
    }

    if (
        file.size <= 0
    ) {

        return {
            valid: false,
            message:
                "The selected file is empty."
        };
    }

    if (
        file.size >
        CONFIG.maxFileSize
    ) {

        return {
            valid: false,
            message:
                "File size cannot exceed 50 MB."
        };
    }

    return {
        valid: true
    };
}

// ============================================================
// REMOVE FILE BUTTON
// ============================================================

function setupRemoveButton() {

    if (!removeFile) {
        return;
    }

    removeFile.addEventListener(
        "click",
        function (event) {

            event.preventDefault();

            event.stopPropagation();

            clearSelectedFile();

        }
    );
}

// ============================================================
// CLEAR SELECTED FILE
// ============================================================

function clearSelectedFile() {

    selectedFile = null;

    lastOCRResponse = null;

    if (fileInput) {
        fileInput.value = "";
    }

    if (filePreview) {

        filePreview.classList.add(
            "hidden"
        );

    }

    if (processButton) {

        processButton.disabled =
            true;

    }

    clearOCRResult();

    hideError();

    console.log(
        "Selected file cleared."
    );
}

// ============================================================
// OCR FORM
// ============================================================

function setupOCRForm() {

    if (!ocrForm) {

        console.error(
            "ocrForm element not found."
        );

        return;
    }

    ocrForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();

            event.stopPropagation();

            if (isProcessing) {

                console.warn(
                    "OCR request already running."
                );

                return;
            }

            if (!selectedFile) {

                showError(
                    "Please select a file first."
                );

                return;
            }

            await processOCR();

        }
    );
}

// ============================================================
// PROCESS OCR
// ============================================================

async function processOCR() {

    startProcessing();

    hideError();

    const formData =
        new FormData();

    /*
     * IMPORTANT
     *
     * Your backend expects:
     *
     * image
     *
     * Therefore do NOT change this to
     * file, pdf, document, etc.
     */

    formData.append(
        "image",
        selectedFile
    );

    console.log(
        "=========================================="
    );

    console.log(
        "STARTING OCR REQUEST"
    );

    console.log(
        "API:",
        CONFIG.apiEndpoint
    );

    console.log(
        "File:",
        selectedFile.name
    );

    console.log(
        "Size:",
        formatFileSize(
            selectedFile.size
        )
    );

    console.log(
        "Type:",
        selectedFile.type ||
        "(empty MIME type)"
    );

    console.log(
        "=========================================="
    );

    const controller =
        new AbortController();

    const timeoutId =
        setTimeout(
            function () {

                controller.abort();

            },
            CONFIG.requestTimeout
        );

    try {

        /*
         * IMPORTANT FIX
         *
         * The old code read the response twice:
         *
         * response.json()
         *
         * and then
         *
         * parseJSONResponse(response)
         *
         * That consumes the response body.
         *
         * This version reads it ONLY ONCE.
         */

        const response =
            await fetch(
                CONFIG.apiEndpoint,
                {
                    method: "POST",

                    body: formData,

                    signal:
                        controller.signal
                }
            );

        clearTimeout(
            timeoutId
        );

        const data =
            await parseJSONResponse(
                response
            );

        lastOCRResponse =
            data;

        console.log(
            "=========================================="
        );

        console.log(
            "OCR API RESPONSE"
        );

        console.log(
            "=========================================="
        );

        console.log(
            data
        );

        console.log(
            "HTTP STATUS:",
            response.status
        );

        console.log(
            "SUCCESS:",
            data?.success
        );

        console.log(
            "OCR OBJECT:",
            data?.ocr
        );

        console.log(
            "RAW TEXT:",
            data?.ocr?.rawText
        );

        console.log(
            "RAW TEXT LENGTH:",
            typeof data?.ocr?.rawText ===
            "string"
                ? data.ocr.rawText.length
                : 0
        );

        console.log(
            "PAGE COUNT:",
            data?.ocr?.pageCount
        );

        console.log(
            "=========================================="
        );

        // HTTP error
        if (!response.ok) {

            throw new Error(
                data?.message ||
                data?.error ||
                `OCR request failed with status ${response.status}.`
            );
        }

        // API returned success:false
        if (
            data?.success === false
        ) {

            throw new Error(
                data?.message ||
                data?.error ||
                "OCR processing failed."
            );
        }

        // Extract text
        const text =
            extractOCRText(
                data
            );

        console.log(
            "EXTRACTED TEXT LENGTH:",
            text.length
        );

        if (
            !text ||
            !text.trim()
        ) {

            throw new Error(
                "OCR completed successfully, but no text was returned."
            );
        }

        // Display result
        displayResult(
            data,
            text
        );

    }
    catch (error) {

        clearTimeout(
            timeoutId
        );

        console.error(
            "OCR ERROR:",
            error
        );

        if (
            error.name ===
            "AbortError"
        ) {

            showError(
                "OCR processing timed out. The PDF may be large or contain many pages."
            );

        }
        else {

            showError(
                error.message ||
                "Unable to process the file."
            );

        }

    }
    finally {

        stopProcessing();

    }
}

// ============================================================
// PARSE JSON RESPONSE
// ============================================================

async function parseJSONResponse(
    response
) {

    const contentType =
        response.headers.get(
            "content-type"
        ) || "";

    // Normal JSON response
    if (
        contentType.includes(
            "application/json"
        )
    ) {

        return await response.json();

    }

    // Fallback if backend sends text
    const text =
        await response.text();

    if (!text) {

        return {
            success:
                response.ok,

            message:
                "Server returned an empty response."
        };
    }

    try {

        return JSON.parse(
            text
        );

    }
    catch {

        return {
            success:
                response.ok,

            message:
                text
        };
    }
}

// ============================================================
// EXTRACT OCR TEXT
// ============================================================

function extractOCRText(data) {

    console.log(
        "Extracting OCR text..."
    );

    /*
     * PRIMARY FORMAT
     *
     * Your API response:
     *
     * {
     *   success: true,
     *   ocr: {
     *      rawText: "...",
     *      pageCount: 2
     *   }
     * }
     */

    if (
        typeof data?.ocr?.rawText ===
        "string"
    ) {

        console.log(
            "Found OCR text at data.ocr.rawText"
        );

        return cleanOCRText(
            data.ocr.rawText
        );
    }

    // --------------------------------------------------------
    // Other possible formats
    // --------------------------------------------------------

    if (
        typeof data?.rawText ===
        "string"
    ) {

        return cleanOCRText(
            data.rawText
        );
    }

    if (
        typeof data?.text ===
        "string"
    ) {

        return cleanOCRText(
            data.text
        );
    }

    if (
        typeof data?.result ===
        "string"
    ) {

        return cleanOCRText(
            data.result
        );
    }

    if (
        typeof data?.output ===
        "string"
    ) {

        return cleanOCRText(
            data.output
        );
    }

    // --------------------------------------------------------
    // Nested formats
    // --------------------------------------------------------

    if (
        typeof data?.data?.rawText ===
        "string"
    ) {

        return cleanOCRText(
            data.data.rawText
        );
    }

    if (
        typeof data?.data?.text ===
        "string"
    ) {

        return cleanOCRText(
            data.data.text
        );
    }

    if (
        typeof data?.data?.result ===
        "string"
    ) {

        return cleanOCRText(
            data.data.result
        );
    }

    // --------------------------------------------------------
    // Pages array
    // --------------------------------------------------------

    if (
        Array.isArray(
            data?.ocr?.pages
        )
    ) {

        return cleanOCRText(
            combinePages(
                data.ocr.pages
            )
        );
    }

    if (
        Array.isArray(
            data?.pages
        )
    ) {

        return cleanOCRText(
            combinePages(
                data.pages
            )
        );
    }

    console.error(
        "Could not find OCR text in API response:",
        data
    );

    return "";
}

// ============================================================
// CLEAN OCR TEXT
// ============================================================

function cleanOCRText(text) {

    if (
        typeof text !==
        "string"
    ) {

        return "";
    }

    /*
     * We intentionally DO NOT remove:
     *
     * <PAGE>
     *
     * line breaks
     *
     * equations
     *
     * symbols
     *
     * because these are part of the OCR output.
     */

    return text
        .replace(
            /\r\n/g,
            "\n"
        )
        .replace(
            /\r/g,
            "\n"
        )
        .replace(
            /\u0000/g,
            ""
        )
        .trim();
}

// ============================================================
// COMBINE PAGE RESULTS
// ============================================================

function combinePages(
    pages
) {

    if (
        !Array.isArray(
            pages
        )
    ) {

        return "";
    }

    return pages
        .map(
            function (page) {

                if (
                    typeof page ===
                    "string"
                ) {

                    return page;
                }

                if (
                    typeof page?.text ===
                    "string"
                ) {

                    return page.text;
                }

                if (
                    typeof page?.rawText ===
                    "string"
                ) {

                    return page.rawText;
                }

                if (
                    typeof page?.result ===
                    "string"
                ) {

                    return page.result;
                }

                return "";

            }
        )
        .filter(
            Boolean
        )
        .join(
            "\n\n<PAGE>\n\n"
        );
}

// ============================================================
// DISPLAY RESULT
// ============================================================

function displayResult(
    data,
    text
) {

    console.log(
        "=========================================="
    );

    console.log(
        "DISPLAYING OCR RESULT"
    );

    console.log(
        "CHARACTERS:",
        text.length
    );

    console.log(
        "PAGES:",
        data?.ocr?.pageCount ||
        "Unknown"
    );

    console.log(
        "=========================================="
    );

    // --------------------------------------------------------
    // Check result element
    // --------------------------------------------------------

    if (!ocrResult) {

        console.error(
            'Element with id="ocrResult" was not found.'
        );

        showError(
            'OCR result box was not found. Make sure index.ejs contains id="ocrResult".'
        );

        return;
    }

    // --------------------------------------------------------
    // Check text
    // --------------------------------------------------------

    if (
        !text ||
        !text.trim()
    ) {

        ocrResult.value =
            "OCR completed, but no text was returned.";

        showError(
            "OCR completed successfully, but no usable text was returned."
        );

        return;
    }

    // --------------------------------------------------------
    // THIS IS THE IMPORTANT PART
    // --------------------------------------------------------

    /*
     * Put the COMPLETE OCR result into textarea.
     *
     * This preserves:
     *
     * <PAGE>
     *
     * line breaks
     *
     * equations
     *
     * symbols
     *
     * handwritten text
     */

    ocrResult.value =
        text;

    // Start from beginning
    ocrResult.scrollTop =
        0;

    // --------------------------------------------------------
    // File information
    // --------------------------------------------------------

    if (resultFile) {

        resultFile.textContent =
            data?.file?.originalName ||
            selectedFile?.name ||
            "File";

    }

    if (resultType) {

        resultType.textContent =
            (
                data?.file?.mimetype ||
                selectedFile?.type ||
                getMimeTypeFromExtension(
                    selectedFile?.name
                ) ||
                "DOCUMENT"
            ).toUpperCase();

    }

    // --------------------------------------------------------
    // Show result section
    // --------------------------------------------------------

    if (resultSection) {

        resultSection.classList.remove(
            "hidden"
        );

    }

    // --------------------------------------------------------
    // Scroll to result
    // --------------------------------------------------------

    setTimeout(
        function () {

            if (resultSection) {

                resultSection.scrollIntoView(
                    {
                        behavior:
                            "smooth",

                        block:
                            "start"
                    }
                );

            }

        },
        150
    );

    console.log(
        "OCR TEXT SUCCESSFULLY DISPLAYED"
    );

    console.log(
        "Characters displayed:",
        text.length
    );
}

// ============================================================
// COPY BUTTON
// ============================================================

function setupCopyButton() {

    if (!copyButton) {
        return;
    }

    copyButton.addEventListener(
        "click",
        async function () {

            const text =
                ocrResult?.value ||
                "";

            if (
                !text.trim()
            ) {

                showError(
                    "There is no OCR text to copy."
                );

                return;
            }

            try {

                await copyText(
                    text
                );

                const originalText =
                    copyButton.textContent;

                copyButton.textContent =
                    "Copied!";

                setTimeout(
                    function () {

                        copyButton.textContent =
                            originalText;

                    },
                    1500
                );

            }
            catch (error) {

                console.error(
                    "Copy error:",
                    error
                );

                showError(
                    "Unable to copy the OCR text."
                );
            }
        }
    );
}

// ============================================================
// COPY TEXT
// ============================================================

async function copyText(
    text
) {

    // Modern browser
    if (
        navigator.clipboard &&
        window.isSecureContext
    ) {

        await navigator.clipboard.writeText(
            text
        );

        return;
    }

    // Fallback
    const textarea =
        document.createElement(
            "textarea"
        );

    textarea.value =
        text;

    textarea.style.position =
        "fixed";

    textarea.style.left =
        "-9999px";

    textarea.style.top =
        "0";

    document.body.appendChild(
        textarea
    );

    textarea.focus();

    textarea.select();

    const successful =
        document.execCommand(
            "copy"
        );

    textarea.remove();

    if (!successful) {

        throw new Error(
            "Copy operation failed."
        );
    }
}

// ============================================================
// DOWNLOAD BUTTON
// ============================================================

function setupDownloadButton() {

    if (!downloadButton) {
        return;
    }

    downloadButton.addEventListener(
        "click",
        function () {

            const text =
                ocrResult?.value ||
                "";

            if (
                !text.trim()
            ) {

                showError(
                    "There is no OCR text to download."
                );

                return;
            }

            downloadOCRText(
                text
            );
        }
    );
}

// ============================================================
// DOWNLOAD OCR TEXT
// ============================================================

function downloadOCRText(
    text
) {

    const blob =
        new Blob(
            [text],
            {
                type:
                    "text/plain;charset=utf-8"
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

    link.href =
        url;

    link.download =
        createDownloadName();

    document.body.appendChild(
        link
    );

    link.click();

    link.remove();

    setTimeout(
        function () {

            URL.revokeObjectURL(
                url
            );

        },
        1000
    );

    console.log(
        "OCR text downloaded."
    );
}

// ============================================================
// CREATE DOWNLOAD FILE NAME
// ============================================================

function createDownloadName() {

    if (!selectedFile) {

        return "ocr-result.txt";
    }

    const originalName =
        selectedFile.name;

    const lastDot =
        originalName.lastIndexOf(
            "."
        );

    let baseName =
        lastDot > 0
            ? originalName.substring(
                0,
                lastDot
            )
            : originalName;

    baseName =
        baseName
            .replace(
                /[^a-zA-Z0-9-_ ]/g,
                "_"
            )
            .trim();

    return (
        (
            baseName ||
            "ocr-result"
        ) +
        "-ocr.txt"
    );
}

// ============================================================
// START PROCESSING
// ============================================================

function startProcessing() {

    isProcessing =
        true;

    if (processButton) {

        processButton.disabled =
            true;

    }

    if (buttonText) {

        buttonText.classList.add(
            "hidden"
        );

    }

    if (loader) {

        loader.classList.remove(
            "hidden"
        );

    }

    if (processing) {

        processing.classList.remove(
            "hidden"
        );

    }

    if (resultSection) {

        resultSection.classList.add(
            "hidden"
        );

    }

    hideError();

    console.log(
        "OCR processing started..."
    );
}

// ============================================================
// STOP PROCESSING
// ============================================================

function stopProcessing() {

    isProcessing =
        false;

    if (processButton) {

        processButton.disabled =
            !selectedFile;

    }

    if (buttonText) {

        buttonText.classList.remove(
            "hidden"
        );

    }

    if (loader) {

        loader.classList.add(
            "hidden"
        );

    }

    if (processing) {

        processing.classList.add(
            "hidden"
        );

    }

    console.log(
        "OCR processing finished."
    );
}

// ============================================================
// CLEAR OCR RESULT
// ============================================================

function clearOCRResult() {

    if (ocrResult) {

        ocrResult.value =
            "";

    }

    if (resultFile) {

        resultFile.textContent =
            "";

    }

    if (resultType) {

        resultType.textContent =
            "";

    }

    if (resultSection) {

        resultSection.classList.add(
            "hidden"
        );

    }

    lastOCRResponse =
        null;
}

// ============================================================
// SHOW ERROR
// ============================================================

function showError(
    message
) {

    console.error(
        "OCR Frontend Error:",
        message
    );

    if (!errorSection) {

        alert(
            message
        );

        return;
    }

    if (errorMessage) {

        errorMessage.textContent =
            message;

    }

    errorSection.classList.remove(
        "hidden"
    );

    errorSection.scrollIntoView(
        {
            behavior:
                "smooth",

            block:
                "center"
        }
    );
}

// ============================================================
// HIDE ERROR
// ============================================================

function hideError() {

    if (!errorSection) {
        return;
    }

    errorSection.classList.add(
        "hidden"
    );
}

// ============================================================
// RESET INTERFACE
// ============================================================

function resetInterface() {

    selectedFile =
        null;

    isProcessing =
        false;

    lastOCRResponse =
        null;

    if (fileInput) {

        fileInput.value =
            "";

    }

    if (filePreview) {

        filePreview.classList.add(
            "hidden"
        );

    }

    if (processButton) {

        processButton.disabled =
            true;

    }

    if (resultSection) {

        resultSection.classList.add(
            "hidden"
        );

    }

    if (processing) {

        processing.classList.add(
            "hidden"
        );

    }

    if (loader) {

        loader.classList.add(
            "hidden"
        );

    }

    if (buttonText) {

        buttonText.classList.remove(
            "hidden"
        );

    }

    if (ocrResult) {

        ocrResult.value =
            "";

    }

    hideError();
}

// ============================================================
// GET FILE EXTENSION
// ============================================================

function getFileExtension(
    filename
) {

    if (
        !filename ||
        !filename.includes(".")
    ) {

        return "";
    }

    return (
        "." +
        filename
            .split(".")
            .pop()
            .toLowerCase()
    );
}

// ============================================================
// GET MIME TYPE FROM EXTENSION
// ============================================================

function getMimeTypeFromExtension(
    filename
) {

    const extension =
        getFileExtension(
            filename
        );

    const types = {

        ".jpg":
            "image/jpeg",

        ".jpeg":
            "image/jpeg",

        ".png":
            "image/png",

        ".webp":
            "image/webp",

        ".pdf":
            "application/pdf"

    };

    return (
        types[extension] ||
        ""
    );
}

// ============================================================
// FORMAT FILE SIZE
// ============================================================

function formatFileSize(
    bytes
) {

    if (
        !Number.isFinite(
            bytes
        ) ||
        bytes <= 0
    ) {

        return "0 Bytes";
    }

    const units = [
        "Bytes",
        "KB",
        "MB",
        "GB"
    ];

    const index =
        Math.floor(
            Math.log(bytes) /
            Math.log(1024)
        );

    const safeIndex =
        Math.min(
            index,
            units.length - 1
        );

    const value =
        bytes /
        Math.pow(
            1024,
            safeIndex
        );

    return (
        parseFloat(
            value.toFixed(2)
        ) +
        " " +
        units[safeIndex]
    );
}

// ============================================================
// DEBUG INFORMATION
// ============================================================

function getOCRDebugInfo() {

    return {

        apiEndpoint:
            CONFIG.apiEndpoint,

        selectedFile:
            selectedFile?.name ||
            null,

        fileSize:
            selectedFile?.size ||
            null,

        fileType:
            selectedFile?.type ||
            null,

        isProcessing:
            isProcessing,

        lastOCRResponse:
            lastOCRResponse

    };
}

// ============================================================
// GLOBAL DEBUG ACCESS
// ============================================================

window.handwrittenOCR = {

    processOCR:

        processOCR,

    getLastResponse:

        function () {
            return lastOCRResponse;
        },

    getDebugInfo:

        getOCRDebugInfo,

    clearFile:

        clearSelectedFile,

    clearResult:

        clearOCRResult

};

// ============================================================
// END
// ============================================================

console.log(
    "Handwritten OCR app.js loaded successfully."
);