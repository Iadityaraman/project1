import os
import shutil
from PIL import Image
import pytesseract

# Auto-detect Tesseract binary path on macOS / Linux / Windows
def configure_tesseract():
    """Locate tesseract executable and set it in pytesseract."""
    # If tesseract is already found on system PATH, nothing more is needed
    if shutil.which("tesseract"):
        return True

    # Common macOS Homebrew paths (Apple Silicon & Intel)
    common_mac_paths = [
        "/opt/homebrew/bin/tesseract",
        "/usr/local/bin/tesseract"
    ]
    for path in common_mac_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            return True

    # Common Linux paths
    if os.path.exists("/usr/bin/tesseract"):
        pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
        return True

    return False

# Initialize configuration on import
configure_tesseract()

def extract_text(image_path: str, lang: str = "eng+hin") -> str:
    """
    Reads an image file from disk and returns the raw OCR text.
    Uses English + Hindi language data.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at: {image_path}")

    # Open image using Pillow
    with Image.open(image_path) as img:
        # pytesseract performs OCR using both English and Hindi models
        # --psm 6 or default handles structured blocks of text well
        text = pytesseract.image_to_string(img, lang=lang)
    
    return text.strip()
