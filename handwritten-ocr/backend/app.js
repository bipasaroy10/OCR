import express from "express";
import dotenv from "dotenv";
import path from "path";

import { connectDB } from "./src/config/db.js";
import ocrRoutes from "./src/routes/ocr.routes.js";

dotenv.config();

const app = express();

app.set("view engine", "ejs");

app.set(
    "views",
    path.join(process.cwd(), "views")
);

const PORT =
    process.env.PORT || 5000;

// ============================================================
// DATABASE
// ============================================================

await connectDB();

// ============================================================
// MIDDLEWARE
// ============================================================

app.use(
    express.json()
);

app.use(
    express.urlencoded({
        extended: true
    })
);

// ============================================================
// STATIC FILES
// ============================================================

app.use(
    express.static(
        path.resolve("public")
    )
);

app.get("/", (req, res) => {
    res.render("index", {
        title: "Handwritten OCR"
    });
});
// ============================================================
// OCR ROUTES
// ============================================================

app.use(
    "/api/ocr",
    ocrRoutes
);

// ============================================================
// SERVER
// ============================================================

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
            `OCR: ${process.env.OCR_API_URL}`
        );

        console.log(
            "MongoDB: Connected"
        );

        console.log(
            "=========================================="
        );
    }
);

export default app;