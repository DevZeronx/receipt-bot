from fpdf import FPDF
import qrcode
import io
import base64
import json
from datetime import datetime
import random

def generate_receipt(products):
    shop_name = random.choice(["Urban Mart", "Smart Bazaar", "Quick Store", "Modern Market"])
    invoice_id = f"INV-{random.randint(100000,999999)}"
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subtotal = sum(p['price'] for p in products)
    tax_rate = 5
    tax = (subtotal * tax_rate) / 100
    total = subtotal + tax

    qr = qrcode.make(invoice_id)
    qr_io = io.BytesIO(); qr.save(qr_io, format='PNG'); qr_io.seek(0)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, shop_name, ln=1, align="C")
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 8, f"Invoice ID: {invoice_id}", ln=1, align="C")
    pdf.cell(200, 8, f"Date: {date}", ln=1, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    for idx, p in enumerate(products, start=1):
        pdf.cell(0, 8, f"{idx}. {p['name']} — ৳{p['price']:.2f}", ln=1)
    pdf.ln(5)
    pdf.cell(0, 8, f"Subtotal: ৳{subtotal:.2f}", ln=1)
    pdf.cell(0, 8, f"Tax ({tax_rate}%): +৳{tax:.2f}", ln=1)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Total: ৳{total:.2f}", ln=1)
    pdf.image(qr_io, x=80, y=pdf.get_y() + 10, w=50)

    bio = io.BytesIO()
    pdf.output(bio); bio.seek(0)
    return bio.read()

def handler(request):
    try:
        body = request.get_json() or {}
        products = body.get("products") or []
        if not products:
            return {"statusCode": 400, "body": "No products found"}

        pdf_bytes = generate_receipt(products)
        encoded = base64.b64encode(pdf_bytes).decode()

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/pdf",
                "Content-Disposition": "inline; filename=receipt.pdf"
            },
            "isBase64Encoded": True,
            "body": encoded
        }
    except Exception as e:
        return {"statusCode": 500, "body": str(e)}
