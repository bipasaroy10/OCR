import OCRResult from "../models/OCRResult.js";
import { processOCR } from "../services/ocr.service.js";

export const runOCR = async (req, res) => {

    try {

        if (!req.file) {

            return res.status(400).json({
                success: false,
                message: "Please upload a file."
            });
        }

        console.log(
            "Processing:",
            req.file.originalname
        );

        // ------------------------------------------
        // SEND FILE TO UNLIMITED-OCR
        // ------------------------------------------

        const ocrResponse =
            await processOCR(
                req.file.path
            );

        console.log(
            "OCR response received."
        );

        // ------------------------------------------
        // EXTRACT OCR TEXT
        // ------------------------------------------

        const ocrText =
            ocrResponse?.ocr?.rawText ||
            ocrResponse?.rawText ||
            "";

        if (!ocrText.trim()) {

            return res.status(500).json({
                success: false,
                message:
                    "OCR completed but no text was returned."
            });
        }

        // ------------------------------------------
        // SAVE TO MONGODB
        // ------------------------------------------

        const savedResult =
            await OCRResult.create({

                originalName:
                    req.file.originalname,

                fileName:
                    req.file.filename,

                fileSize:
                    req.file.size,

                mimeType:
                    req.file.mimetype,

                ocrText:
                    ocrText,

                pageCount:
                    ocrResponse?.ocr?.pageCount ||
                    1,

                model:
                    ocrResponse?.ocr?.model ||
                    "baidu/Unlimited-OCR",

                requestId:
                    ocrResponse?.ocr?.requestId ||
                    null
            });

        // ------------------------------------------
        // RETURN RESULT TO FRONTEND
        // ------------------------------------------

        return res.status(201).json({

            success: true,

            message:
                "OCR completed and saved successfully.",

            file: {
                originalName:
                    req.file.originalname,

                size:
                    req.file.size,

                mimetype:
                    req.file.mimetype
            },

            ocr: {

                id:
                    savedResult._id,

                rawText:
                    savedResult.ocrText,

                pageCount:
                    savedResult.pageCount,

                model:
                    savedResult.model,

                requestId:
                    savedResult.requestId
            }

        });

    } catch (error) {

        console.error(
            "OCR controller error:",
            error
        );

        return res.status(500).json({

            success: false,

            message:
                "Failed to process OCR.",

            error:
                error.message

        });
    }
};


export const getOCRHistory = async (req, res) => {

    try {

        const results =
            await OCRResult
                .find()
                .sort({
                    createdAt: -1
                });

        return res.json({

            success: true,

            count:
                results.length,

            results

        });

    } catch (error) {

        console.error(
            "OCR history error:",
            error
        );

        return res.status(500).json({

            success: false,

            message:
                "Failed to fetch OCR history."

        });
    }
};

export const getOCRById = async (req, res) => {

    try {

        const result =
            await OCRResult.findById(
                req.params.id
            );

        if (!result) {

            return res.status(404).json({

                success: false,

                message:
                    "OCR result not found."

            });
        }

        return res.json({

            success: true,

            result

        });

    } catch (error) {

        console.error(
            "Get OCR error:",
            error
        );

        return res.status(500).json({

            success: false,

            message:
                "Failed to fetch OCR result."

        });
    }
};