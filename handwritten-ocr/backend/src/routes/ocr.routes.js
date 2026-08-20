import express from "express";

import {
    runOCR,
    getOCRHistory,
    getOCRById
} from "../controllers/ocr.controller.js";

import { upload } from "../middleware/upload.middleware.js";



const router =
    express.Router();

// Upload + OCR + MongoDB
router.post(
    "/",
    upload.single("image"),
    runOCR
);

// Get all OCR results
router.get(
    "/history",
    getOCRHistory
);

// Get one OCR result
router.get(
    "/:id",
    getOCRById
);



export default router;