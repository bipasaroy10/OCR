import dotenv from "dotenv";

dotenv.config();


import app from "./app.js";


const PORT =
  process.env.PORT || 5000;


app.listen(
  PORT,
  () => {

    console.log(
      "=========================================="
    );

    console.log(
      "Handwritten OCR Node.js API"
    );

    console.log(
      `Server: http://localhost:${PORT}`
    );

    console.log(
      `OCR: ${
        process.env.UNLIMITED_OCR_URL
      }`
    );

    console.log(
      "=========================================="
    );

  }
);