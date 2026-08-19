import multer from "multer";
import path from "path";
import fs from "fs";

const uploadDirectory = path.resolve(
  "uploads"
);

if (!fs.existsSync(uploadDirectory)) {
  fs.mkdirSync(uploadDirectory, {
    recursive: true
  });
}

const storage = multer.diskStorage({

  destination: (req, file, cb) => {
    cb(null, uploadDirectory);
  },

  filename: (req, file, cb) => {

    const extension =
      path.extname(file.originalname)
        .toLowerCase();

    const filename =
      `${Date.now()}-${Math.round(
        Math.random() * 1e9
      )}${extension}`;

    cb(null, filename);
  }

});


const allowedExtensions = [
  ".jpg",
  ".jpeg",
  ".png",
  ".webp",
  ".pdf"
];


const fileFilter = (
  req,
  file,
  cb
) => {

  const extension =
    path.extname(
      file.originalname
    ).toLowerCase();

  if (
    allowedExtensions.includes(
      extension
    )
  ) {

    cb(null, true);

  } else {

    cb(
      new Error(
        "Only JPG, JPEG, PNG, WEBP and PDF files are allowed."
      ),
      false
    );

  }

};


export const upload = multer({

  storage,

  fileFilter,

  limits: {
    fileSize:
      50 * 1024 * 1024
  }

});