import axios from "axios";
import FormData from "form-data";
import fs from "fs";

const OCR_URL =
  process.env.UNLIMITED_OCR_URL ||
  "http://127.0.0.1:8000/ocr";


export const processOCR = async (
  filePath,
  originalFilename
) => {

  const form = new FormData();

  form.append(
    "image",
    fs.createReadStream(filePath),
    {
      filename: originalFilename
    }
  );


  try {

    const response =
      await axios.post(
        OCR_URL,
        form,
        {
          headers: {
            ...form.getHeaders()
          },

          maxContentLength:
            Infinity,

          maxBodyLength:
            Infinity,

          timeout:
            15 * 60 * 1000
        }
      );


    return response.data;


  } catch (error) {

    console.error(
      "Unlimited-OCR error:"
    );

    console.error(
      error.response?.data ||
      error.message
    );


    throw new Error(
      error.response?.data?.message ||
      "Failed to communicate with Unlimited-OCR server."
    );

  }

};