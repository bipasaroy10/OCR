import fs from "fs";

import {
  processOCR
} from "../services/ocr.service.js";


export const handwrittenOCR = async (
  req,
  res
) => {

  let filePath = null;


  try {

    // --------------------------------------------------
    // Check uploaded file
    // --------------------------------------------------

    if (!req.file) {

      return res.status(400).json({

        success: false,

        message:
          "Please upload an image or PDF."

      });

    }


    filePath =
      req.file.path;


    console.log(
      "\nOCR request received:"
    );

    console.log(
      "File:",
      req.file.originalname
    );

    console.log(
      "Type:",
      req.file.mimetype
    );


    // --------------------------------------------------
    // Send to Python Unlimited-OCR
    // --------------------------------------------------

    const result =
      await processOCR(

        filePath,

        req.file.originalname

      );


    // --------------------------------------------------
    // Return result
    // --------------------------------------------------

    return res.status(200).json({

      success: true,

      message:
        "OCR completed successfully.",

      file: {
        originalName:
          req.file.originalname,

        size:
          req.file.size,

        mimetype:
          req.file.mimetype
      },

      ocr:
        result

    });


  } catch (error) {

    console.error(
      "OCR Controller Error:",
      error
    );


    return res.status(500).json({

      success: false,

      message:
        error.message ||
        "OCR processing failed."

    });


  } finally {

    // --------------------------------------------------
    // Delete uploaded file
    // --------------------------------------------------

    if (
      filePath &&
      fs.existsSync(filePath)
    ) {

      try {

        fs.unlinkSync(
          filePath
        );

        console.log(
          "Temporary upload deleted."
        );

      } catch (cleanupError) {

        console.error(
          "Failed to delete temporary file:",
          cleanupError
        );

      }

    }

  }

};