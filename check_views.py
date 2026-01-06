import requests
import json
import os

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

DATA_FILE = "views.json"

def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text})

def get_views():
    url = (
        "https://www.googleapis.com/youtube/v3/channels"
        "?part=statistics"
        f"&id={CHANNEL_ID}"
        f"&key={YOUTUBE_API_KEY}"
    )
    r = requests.get(url).json()

    if "items" not in r or len(r["items"]) == 0:
        send_message("⚠️ YouTube API cevap vermedi.")
        return None

    return int(r["items"][0]["statistics"]["viewCount"])

def main():
    views = get_views()
    if views is None:
        return

    # İlk çalıştırma
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({"views": views}, f)

        send_message(
            f"🤖 Bot aktif!\n"
            f"📊 Mevcut toplam izlenme: {views}"
        )
        return

    # Önceki değeri oku
    with open(DATA_FILE, "r") as f:
        old_views = json.load(f).get("views", views)

    if views > old_views:
        diff = views - old_views
        send_message(
            f"📈 YouTube izlenme arttı!\n"
            f"+{diff} izlenme\n"
            f"Toplam: {views}"
        )

    # Güncelle
    with open(DATA_FILE, "w") as f:
        json.dump({"views": views}, f)

if __name__ == "__main__":
    main()
