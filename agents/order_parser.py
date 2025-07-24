import re
import fitz

def parse_order_slip(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()

    lowered = text.lower()

    if "amazon marketplace" in lowered or "order id:" in lowered:
        return parse_amazon_slip(text)
    elif "colorimetrics order #" in lowered or "roidtest.com" in lowered:
        return parse_shopify_slip(text)
    else:
        return {"items": []}


# 🟠 AMAZON PACKING SLIP PARSER
def parse_amazon_slip(text):
    items = []
    lines = text.splitlines()

    for i, line in enumerate(lines):
        # Look for quantity line (often just "1")
        if re.match(r"^\s*\d{1,3}\s*$", line.strip()):
            # Try to get next non-empty line as item name
            for j in range(i + 1, i + 4):  # up to 3 lines ahead
                if j < len(lines) and lines[j].strip():
                    item_name = lines[j].strip()
                    quantity = int(line.strip())
                    # Confirm it isn't a header like "Unit price"
                    if "unit price" not in item_name.lower():
                        items.append({
                            "item_name": item_name,
                            "quantity": quantity
                        })
                    break

    return {"items": items}


# 🟢 Shopify Format Parsing (Colorimetrics.com)
def parse_shopify_slip(text):
    items = []
    lines = text.splitlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Only match lines with likely product names (exclude emails/URLs)
        if (
            "test kit" in line.lower() and
            "@" not in line and
            "roidtest.com" not in line.lower()
        ):
            item_name = line
            qty_1 = 1
            qty_2 = 1

            # Try to get quantity from next 2 lines
            if i + 1 < len(lines):
                match1 = re.search(r"\b(\d{1,2})\s+(test kit|kits?)", lines[i + 1].lower())
                if match1:
                    qty_1 = int(match1.group(1))

            if i + 2 < len(lines):
                match2 = re.search(r"\b(\d{1,2})\s+of\s+(\d{1,2})", lines[i + 2].lower())
                if match2:
                    qty_2 = int(match2.group(1))

            # Apply quantity logic
            if qty_1 > 1 and qty_2 > 1:
                quantity = qty_1 * qty_2
            else:
                quantity = max(qty_1, qty_2)

            items.append({
                "item_name": item_name,
                "quantity": quantity
            })

            i += 3  # Skip block
        else:
            i += 1

    return {"items": items}


