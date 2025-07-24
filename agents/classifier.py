# agents/classifier.py

import fitz

def classify_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()

    print(f"Text from {file_path}:\n{text}")
    lowered = text.lower()

    # Order slip detection – match any of these individually
    order_keywords = [
        "colorimetrics",           # present in all order slips
        "order #",                 # appears like 'Order #46299'
        "thank you for shopping",  # consistent closing line
        "roidtest.com",            # store's domain
        "items",                   # present alone
        "quantity",                # present alone
        "test kit",                # e.g., "Testosterone Test Kit"
        "ship to",                 # appears in both order & label but with other keywords it's safe
        "bill to",
    ]

    amazon_keywords = [
        "amazon marketplace",
        "order id:",
        "thank you for buying from colorimetrics",
        "sku:",
        "asin:",
        "https://www.amazon.com/returns",
        "label purchase",
    ]

    if any(kw in lowered for kw in order_keywords):
        return "order_slip"
    elif any(kw in lowered for kw in amazon_keywords):
        return "amazon_slip"
    else:
        return "unknown"
