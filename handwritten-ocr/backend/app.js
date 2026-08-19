import express from "express";
import cors from "cors";

import ocrRoutes
  from "./src/routes/ocr.routes.js";


const app =
  express();


app.use(
  cors()
);


app.use(
  express.json()
);


app.use(
  express.urlencoded({
    extended: true
  })
);


// --------------------------------------------------
// Health
// --------------------------------------------------

app.get(
  "/",
  (req, res) => {

    res.json({

      success: true,

      message:
        "Handwritten OCR Node.js API is running."

    });

  }
);


app.get(
  "/health",
  (req, res) => {

    res.json({

      success: true,

      service:
        "Node.js OCR API",

      pythonOCR:
        process.env.UNLIMITED_OCR_URL

    });

  }
);


// --------------------------------------------------
// OCR
// --------------------------------------------------

app.use(
  "/api/ocr",
  ocrRoutes
);


// --------------------------------------------------
// Error handler
// --------------------------------------------------

app.use(
  (err, req, res, next) => {

    console.error(
      "Express Error:",
      err
    );


    if (
      err.code ===
      "LIMIT_FILE_SIZE"
    ) {

      return res.status(400).json({

        success: false,

        message:
          "File size cannot exceed 50 MB."

      });

    }


    return res.status(500).json({

      success: false,

      message:
        err.message ||
        "Internal server error."

    });

  }
);


export default app;