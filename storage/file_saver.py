import os
import requests
from datetime import datetime
import certifi

def save_pdf(url, filename):
    token = os.environ["SLACK_BOT_TOKEN"]
    headers = {"Authorization": f"Bearer {token}"}
    today = datetime.today().strftime("%Y-%m-%d")
    os.makedirs(f"pdfs/{today}", exist_ok=True)

    res = requests.get(url, headers=headers, verify=certifi.where())

    if res.status_code == 200:
        with open(f"pdfs/{today}/{filename}", "wb") as f:
            f.write(res.content)
        print(f"Saved: {filename}")
    else:
        print(f"Failed to download: {filename}")
