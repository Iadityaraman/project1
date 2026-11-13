from typing import Dict, Any

MANDATORY_DISCLAIMER = "Yeh sirf ek aasaan samjhaav hai. Kripya us office se pakka kar lein jisne yeh notice bheja hai."

UNCLEAR_MESSAGE = "Photo saaf nahi hai, dobara try karein."

def generate_hindi_explanation(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Takes extracted fields and generates a safe, fixed-template Hindi explanation.
    Never uses free-form LLM generation to ensure 100% safety and predictability.
    """
    if not data.get("is_clear"):
        return {
            "success": False,
            "title": "Photo Saaf Nahi Hai",
            "message": UNCLEAR_MESSAGE,
            "details": data.get("error_message", UNCLEAR_MESSAGE),
            "disclaimer": MANDATORY_DISCLAIMER
        }

    amount = data.get("amount", "N/A")
    due_date = data.get("due_date", "N/A")
    consumer_no = data.get("consumer_no", "Notice par nahi dikha")
    office = data.get("office", "Bijli Vibhag")

    # Fixed Hindi explanation cards
    explanation = {
        "success": True,
        # Section 1: Yeh kya hai
        "what_is_this": f"Yeh aapka bijli ka bill ya bijli vibhag ({office}) ka notice hai.",

        # Section 2: Kitna paisa
        "how_much_money": f"Aapko kul ₹{amount} jama karne hain.",

        # Section 3: Aakhri tareekh
        "last_date": f"Yeh paise {due_date} tak ya usse pehle jama karne hain.",

        # Section 4: Ab kya karna hai
        "what_to_do": (
            f"Aakhri tareekh ({due_date}) se pehle ₹{amount} ka bhugtan online portal par karein ya "
            f"apne paas wale bijli ghar (sub-division office) jaakar counter par jama karein. "
            f"Samay par jama na karne par late fee (jurmana) lag sakti hai ya bijli ka connection kat sakta hai."
        ),

        # Section 5: Kis se milna hai
        "who_to_contact": f"{office} ke paas wale sub-division ya bill payment counter par contact karein.",

        # Extra Reference
        "consumer_number": consumer_no,
        "office_name": office,

        # Mandatory ending rule
        "disclaimer": MANDATORY_DISCLAIMER
    }

    return explanation
