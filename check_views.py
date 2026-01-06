import requests
import json
import os

YOUTUBE_API_KEY = os.environ["YOUTUBE_API_KEY"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

DATA_FILE = "views.json"

def get_views():
    url = (
        "https://www.googleapis.com/youtube/v3/channels"
        "?part=statistics"
        f"&id={CHANNEL_ID}"
        f"&key={YOUTUBE_API_KEY}"
    )
    r = requests.get(url).json()
    return int(r["items"][0]["statistics"]["viewCount"])

def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text})

def main():
    views = get_views()

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            old_views = json.load(f)["views"]
    else:
        old_views = views

    if views > old_views:
        diff = views - old_views
        send_message(f"📈 YouTube izlenme arttı!\n+{diff} izlenme\nToplam: {views}")

    with open(DATA_FILE, "w") as f:
        json.dump({"views": views}, f)

main()
