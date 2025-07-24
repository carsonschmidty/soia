from slack_sdk.web import WebClient
from slack_sdk.signature import SignatureVerifier
from flask import Flask, request, jsonify
import os

from dotenv import load_dotenv
from storage.file_saver import save_pdf
from agents.classifier import classify_pdf
from agents.order_parser import parse_order_slip

load_dotenv()

client = WebClient(token = os.environ['SLACK_BOT_TOKEN'])
verifier = SignatureVerifier(os.environ['SLACK_SIGNING_SECRET'])

app = Flask(__name__)

@app.route("/slack/events", methods=["POST"])
def slack_events():
    if not verifier.is_valid_request(request.get_data(), request.headers):
        print("❌ Invalid Slack signature.")
        return "Invalid request", 400

    data = request.get_json()
    
    # Respond to Slack URL verification challenge
    if data.get("type") == "url_verification":
        return jsonify({"challenge": data["challenge"]})

    event = data.get("event", {})
    print(f"📨 Received Slack event: {event.get('type')}")

    if event.get("type") == "file_shared":
        try:
            file_id = event.get("file_id")
            file_info = client.files_info(file=file_id)
            file_obj = file_info["file"]
            url = file_obj["url_private_download"]
            filename = file_obj["name"]

            print(f"⬇️ Downloading file: {filename}")
            saved_path = save_pdf(url, filename)

            # Classify file type
            doc_type = classify_pdf(saved_path)
            print(f"📂 Classified as: {doc_type}")

            if doc_type == "shipping_label":
                print("🖨️ Send to printer (printer integration not yet implemented).")

            elif doc_type == "order_slip":
                result = parse_order_slip(saved_path)
                print("🧾 Parsed Order Slip:")
                for item in result["items"]:
                    print(f"  - {item['item_name']} × {item['quantity']}")

            else:
                print("❓ Unknown document type.")

        except Exception as e:
            print(f"❗ Error handling file: {e}")

    return "OK", 200

if __name__ == "__main__":
    app.run(port = 8080)