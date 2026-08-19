import express from "express";

import {
  upload
} from "../middleware/upload.middleware.js";

import {
  handwrittenOCR
} from "../controllers/ocr.controller.js";


const router =
  express.Router();


router.post(
  "/",
  upload.single("image"),
  handwrittenOCR
);


export default router;