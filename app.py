import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

from ocr import extract_text
from extractor import parse_electricity_notice
from templates import generate_hindi_explanation

app = Flask(__name__)
app.secret_key = "notice-samjhao-secret-key-phase1"

# Upload configurations
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp", "tiff"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload

# Ensure uploads directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename: str) -> bool:
    """Check if uploaded file has a valid image extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET"])
def index():
    """Render home page with upload form and camera button."""
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    """
    Handle photo upload, perform OCR, extract fields,
    build Hindi explanation, and delete image immediately.
    """
    if "notice_photo" not in request.files:
        flash("Kripya photo select karein ya camera se khinchein.")
        return redirect(url_for("index"))

    file = request.files["notice_photo"]
    if file.filename == "":
        flash("Koi photo select nahi ki gayi.")
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        flash("Kripya sirf photo (JPG, PNG, WEBP) upload karein.")
        return redirect(url_for("index"))

    # Generate a unique temporary filename
    extension = file.filename.rsplit(".", 1)[1].lower()
    temp_filename = f"temp_{uuid.uuid4().hex}.{extension}"
    temp_filepath = os.path.join(app.config["UPLOAD_FOLDER"], temp_filename)

    try:
        # Save photo temporarily to run OCR
        file.save(temp_filepath)

        # Step 1: Run OCR (pytesseract eng+hin)
        raw_text = extract_text(temp_filepath)

        # Step 2: Extract electricity fields using regex
        extracted_data = parse_electricity_notice(raw_text)

        # Step 3: Fill fixed Hindi templates
        explanation = generate_hindi_explanation(extracted_data)

        # Render result page
        return render_template(
            "result.html",
            result=explanation,
            extracted=extracted_data
        )

    except Exception as e:
        # Catch unexpected OCR or parsing errors gracefully
        return render_template(
            "result.html",
            result={
                "success": False,
                "title": "Photo Saaf Nahi Hai",
                "message": "Photo saaf nahi hai, dobara try karein.",
                "details": f"Error: {str(e)}",
                "disclaimer": "Yeh sirf ek aasaan samjhaav hai. Kripya us office se pakka kar lein jisne yeh notice bheja hai."
            },
            extracted={"is_clear": False}
        )

    finally:
        # Core Rule 4: PRIVACY - Delete the uploaded image right after processing!
        # This executes even if an error occurred during OCR.
        if os.path.exists(temp_filepath):
            try:
                os.remove(temp_filepath)
            except OSError:
                pass

if __name__ == "__main__":
    # Run development server
    app.run(host="0.0.0.0", port=5001, debug=True)
