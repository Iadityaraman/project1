import re
from typing import Dict, Optional, Any

# Common Electricity Discoms & Office patterns
OFFICE_PATTERNS = [
    # Haryana (User is in Sonipat!)
    r"(?:Uttar\s+Haryana\s+Bijli\s+Vitran\s+Nigam|UHBVN)",
    r"(?:Dakshin\s+Haryana\s+Bijli\s+Vitran\s+Nigam|DHBVN)",
    r"(?:उत्तर\s*हरियाणा\s*बिजली\s*वितरण\s*निगम)",
    r"(?:दक्षिण\s*हरियाणा\s*बिजली\s*वितरण\s*निगम)",
    # Delhi
    r"(?:BSES\s*(?:Rajdhani|Yamuna)?\s*Power\s*(?:Limited|Ltd)?)",
    r"(?:Tata\s*Power\s*(?:DDL|Delhi\s*Distribution)?)",
    r"(?:TPDDL)",
    # Uttar Pradesh
    r"(?:Uttar\s+Pradesh\s+Power\s+Corporation\s*(?:Limited|Ltd)?|UPPCL)",
    r"(?:Paschimanchal\s+Vidyut\s+Vitran\s+Nigam|PVVNL)",
    r"(?:Madhyanchal\s+Vidyut\s+Vitran\s+Nigam|MVVNL)",
    r"(?:Dakshinanchal\s+Vidyut\s+Vitran\s+Nigam|DVVNL)",
    r"(?:Poorvanchal\s+Vidyut\s+Vitran\s+Nigam|PuVVNL)",
    # Punjab / Rajasthan / Generic
    r"(?:Punjab\s+State\s+Power\s+Corporation\s*(?:Limited|Ltd)?|PSPCL)",
    r"(?:Jaipur\s+Vidyut\s+Vitran\s+Nigam|JVVNL)",
    # Generic Department / Board names
    r"(?:Electricity\s+(?:Department|Board|Corporation|Distribution))",
    r"(?:Power\s+Distribution\s+Corporation)",
    r"(?:Vidyut\s+Vitran\s+Nigam)",
    r"(?:विद्युत\s*वितरण\s*निगम)",
    r"(?:बिजली\s*विभाग)"
]

def extract_office(text: str) -> Optional[str]:
    """Detect electricity board or discom name from text."""
    for pattern in OFFICE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            found = match.group(0).strip()
            upper = found.upper()
            if "UHBVN" in upper or "उत्तर हरियाणा" in found:
                return "UHBVN (उत्तर हरियाणा बिजली वितरण निगम)"
            if "DHBVN" in upper or "दक्षिण हरियाणा" in found:
                return "DHBVN (दक्षिण हरियाणा बिजली वितरण निगम)"
            if "BSES" in upper:
                return "BSES Power"
            if "TPDDL" in upper or "TATA POWER" in upper:
                return "Tata Power (TPDDL)"
            if "UPPCL" in upper:
                return "UPPCL (उत्तर प्रदेश पावर कारपोरेशन)"
            if "PSPCL" in upper:
                return "PSPCL (पंजाब स्टेट पावर कॉर्पोरेशन)"
            return found
            
    # Generic fallback if 'electricity' or 'bijli' is in text
    if re.search(r"\b(?:electricity|bijli|vidyut|बिजली|विद्युत)\b", text, re.IGNORECASE):
        return "Bijli Vibhag (बिजली विभाग)"
    return None

def extract_consumer_number(text: str) -> Optional[str]:
    """
    Extracts Account Number / CA Number / Consumer ID / K. No.
    Allows for bilingual labels like 'CA Number (खाता संख्या): 1084920153'
    where OCR might add parentheses or noisy Hindi characters in between.
    """
    ca_keywords = (
        r"(?:CA\s*(?:No|Number|#)?|Contract\s*Account|"
        r"Consumer\s*(?:No|Number|ID|#)?|"
        r"(?:Account|A/c)\s*(?:No|Number|#)?|"
        r"K\.?\s*No\.?|"
        r"उपभोक्ता\s*(?:संख्या|क्रमांक|आईडी)?|"
        r"खाता\s*(?:संख्या|नंबर)?)"
    )
    # [^\n\d]*? matches any non-digit, non-newline characters in between
    # like ' (खाता संख्या): ' or ' : '
    pattern = rf"{ca_keywords}[^\n\d]*?([A-Z0-9]{{8,14}})\b"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def extract_due_date(text: str) -> Optional[str]:
    """
    Extracts bill due date / payment last date.
    Looks for date keywords followed by common Indian date formats:
      - DD/MM/YYYY or DD-MM-YYYY or DD.MM.YYYY
      - DD-Mon-YYYY (e.g. 24-Nov-2026, 24 Nov 2026)
    Handles bilingual text in parentheses between label and date.
    """
    date_regex = (
        r"(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|"
        r"\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,-]+\d{2,4})"
    )

    due_keywords = (
        r"(?:Payment\s*Due\s*Date|Due\s*Date(?:\s*\(Cash\))?|Pay\s*By|Pay\s*Before|"
        r"Last\s*Date\s*(?:of\s*Payment)?|Due\s*Date\s*\(Cheque\)|"
        r"देय\s*तिथि|अंतिम\s*तिथि|आखिरी\s*तारीख)"
    )

    # 1. Same line match with flexible separator
    pattern = rf"{due_keywords}[^\n\d]*?{date_regex}"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # 2. Adjacent line match (label on line 1, date on line 2)
    pattern_multiline = rf"{due_keywords}[^\n]*?\n\s*{date_regex}"
    match_ml = re.search(pattern_multiline, text, re.IGNORECASE)
    if match_ml:
        return match_ml.group(1).strip()

    return None

def extract_amount(text: str) -> Optional[str]:
    """
    Extracts payable bill amount.
    Looks for amount keywords and currency symbols:
      - Net Payable / Total Amount Due / Total Due / Amount Payable / Bill Amount
      - कुल देय राशि / देय राशि / भुगतान राशि
    Handles parenthetical labels and OCR noise between keyword and amount.
    """
    # Clean up common OCR noise for rupee symbols
    cleaned = text.replace("₹", " Rs ").replace("रु", " Rs ").replace("रू", " Rs ")

    amount_keywords = (
        r"(?:Net\s*(?:Amount\s*)?Payable|Net\s*Payable|"
        r"Total\s*(?:Amount\s*)?Due|Total\s*Due|Amount\s*Payable|"
        r"Bill\s*Amount|Current\s*Bill|Total\s*Bill|"
        r"कुल\s*देय\s*राशि|देय\s*राशि|भुगतान\s*राशि)"
    )

    # Primary search: Keyword followed by optional currency symbol and digits
    # [^\n\d]*? skips things like ' (कुल देय राशि): Rs. '
    pattern = rf"{amount_keywords}[^\n\d]*?([\d,]+(?:\.\d{{1,2}})?)\b"
    match = re.search(pattern, cleaned, re.IGNORECASE)
    if match:
        raw_val = match.group(1).strip()
        clean_num = raw_val.replace(",", "")
        try:
            val = float(clean_num)
            if val > 0:
                return f"{val:,.2f}"
        except ValueError:
            pass

    # Secondary search: Any 'Due' line with 'Rs. XXX'
    fallback_pattern = r"(?:Due|Payable)\s*.*?(?:Rs\.?|INR)\s*([\d,]+(?:\.\d{1,2})?)\b"
    match_fallback = re.search(fallback_pattern, cleaned, re.IGNORECASE)
    if match_fallback:
        raw_val = match_fallback.group(1).strip()
        clean_num = raw_val.replace(",", "")
        try:
            val = float(clean_num)
            if val > 0:
                return f"{val:,.2f}"
        except ValueError:
            pass

    return None

def parse_electricity_notice(raw_text: str) -> Dict[str, Any]:
    """
    Parses OCR raw text and returns structured fields.
    Also determines if key details are present and readable.
    """
    if not raw_text or len(raw_text.strip()) < 15:
        return {
            "is_clear": False,
            "error_message": "Photo saaf nahi hai, dobara try karein",
            "raw_text": raw_text or ""
        }

    office = extract_office(raw_text)
    consumer_no = extract_consumer_number(raw_text)
    due_date = extract_due_date(raw_text)
    amount = extract_amount(raw_text)

    # Core Rule 3: If key details are missing (especially amount or due date),
    # do NOT guess! Mark as unclear.
    if not amount or not due_date:
        return {
            "is_clear": False,
            "error_message": "Photo saaf nahi hai, dobara try karein (Paise ya aakhri tareekh saaf nahi dikhi)",
            "office": office,
            "consumer_no": consumer_no,
            "due_date": due_date,
            "amount": amount,
            "raw_text": raw_text
        }

    return {
        "is_clear": True,
        "notice_type": "electricity",
        "office": office or "Bijli Vibhag (बिजली विभाग)",
        "consumer_no": consumer_no or "Notice par nahi dikha",
        "due_date": due_date,
        "amount": amount,
        "raw_text": raw_text
    }
