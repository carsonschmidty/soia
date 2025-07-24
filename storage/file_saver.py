import os
import requests
from datetime import datetime
import certifi

def save_pdf(url, filename):
    token = os.environ["SLACK_BOT_TOKEN"]
    headers = {"Authorization": f"Bearer {token}"}
    today = datetime.today().strftime("%Y-%m-%d")
    save_dir = f"pdfs/{today}"
    os.makedirs(save_dir, exist_ok=True)
    full_path = f"{save_dir}/{filename}"

    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        with open(full_path, "wb") as f:
            f.write(res.content)
        print(f"Saved: {filename}")
        return full_path  # ✅ return this
    else:
        print(f"Failed to download: {filename}")
        return None

