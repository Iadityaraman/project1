"""
Helper script to generate a sample mock electricity bill image
for quick testing of Phase 1 (MVP).
"""
import os
from PIL import Image, ImageDraw, ImageFont

def generate_sample_bill(output_path: str = "sample_notice.png"):
    # Create white canvas (width=700, height=900)
    img = Image.new("RGB", (700, 900), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Outer border
    draw.rectangle([(20, 20), (680, 880)], outline=(30, 58, 138), width=3)
    draw.rectangle([(26, 26), (674, 874)], outline=(148, 163, 184), width=1)

    # Header Box
    draw.rectangle([(26, 26), (674, 150)], fill=(238, 242, 255))
    
    # We use default font to avoid missing font issues on different OS
    # Header text
    draw.text((120, 45), "UTTAR HARYANA BIJLI VITRAN NIGAM (UHBVN)", fill=(30, 58, 138))
    draw.text((150, 75), "उत्तर हरियाणा बिजली वितरण निगम - सब डिवीजन सोनीपत", fill=(30, 58, 138))
    draw.text((220, 105), "ELECTRICITY CONSUMPTION BILL / NOTICE", fill=(71, 85, 105))

    # Divider line
    draw.line([(26, 150), (674, 150)], fill=(30, 58, 138), width=2)

    # Consumer Details Table
    y = 180
    draw.rectangle([(40, y), (660, y + 160)], outline=(203, 213, 225), width=1)
    draw.text((60, y + 20), "Consumer Name (उपभोक्ता): Ram Kumar", fill=(15, 23, 42))
    draw.text((60, y + 55), "CA Number (खाता संख्या): 1084920153", fill=(15, 23, 42))
    draw.text((60, y + 90), "Sub-Division: Sonipat City Division", fill=(15, 23, 42))
    draw.text((60, y + 125), "Address: Sector 14, Sonipat, Haryana", fill=(15, 23, 42))

    # Bill Calculation Box
    y = 380
    draw.rectangle([(40, y), (660, y + 260)], outline=(203, 213, 225), width=1)
    draw.text((60, y + 25), "Units Consumed: 320 kWh", fill=(15, 23, 42))
    draw.text((60, y + 65), "Energy Charges: Rs. 2150.00", fill=(15, 23, 42))
    draw.text((60, y + 105), "FSA & Govt Duty: Rs. 300.00", fill=(15, 23, 42))
    
    # Highlight Net Amount Payable (Big Box)
    draw.rectangle([(55, y + 155), (645, y + 235)], fill=(240, 253, 244), outline=(22, 101, 52), width=2)
    draw.text((70, y + 175), "Net Amount Payable (कुल देय राशि): Rs. 2,450.00", fill=(22, 101, 52))

    # Due Date Box
    y = 670
    draw.rectangle([(55, y), (645, y + 90)], fill=(254, 242, 242), outline=(185, 28, 28), width=2)
    draw.text((70, y + 25), "Payment Due Date (देय तिथि): 28/11/2026", fill=(185, 28, 28))
    draw.text((70, y + 55), "Notice: Pay before due date to avoid disconnection / late fee.", fill=(100, 116, 139))

    # Footer note
    draw.text((140, 800), "Save Electricity • Helpline No: 1912 • UHBVN Sonipat", fill=(148, 163, 184))

    img.save(output_path)
    print(f"Sample notice generated at: {output_path}")

if __name__ == "__main__":
    generate_sample_bill()
