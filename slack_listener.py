from slack_sdk.web import WebClient
from slack_sdk.signature import SignatureVerifier
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from storage.file_saver import save_pdf

load_dotenv()


client = WebClient(token = os.environ['SLACK_BOT_TOKEN'])
verifier = SignatureVerifier(os.environ['SLACK_SIGNING_SECRET'])

app = Flask(__name__)

@app.route("/slack/events", methods=["POST"])
def slack_events():
    if not verifier.is_valid_request(request.get_data(), request.headers):
        return "Invalid request", 400

    data = request.get_json()
    print("EVENT RECEIVED:", data)  # 👈 Add this line for debug

    if data.get("type") == "url_verification":
        return jsonify({"challenge": data["challenge"]})

    event = data.get("event", {})
    if event.get("type") == "file_shared":
        file_id = event.get("file_id")
        file_info = client.files_info(file=file_id)
        url = file_info["file"]["url_private_download"]
        filename = file_info["file"]["name"]
        save_pdf(url, filename)

    return "OK", 200

if __name__ == "__main__":
    app.run(port = 8080)