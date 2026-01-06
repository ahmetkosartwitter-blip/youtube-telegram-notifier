import requests
import json
import os
from datetime import date

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

DATA_FILE = "stats.json"

def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text})

def get_stats():
    url = (
        "https://www.googleapis.com/youtube/v3/channels"
        "?part=statistics"
        f"&id={CHANNEL_ID}"
        f"&key={YOUTUBE_API_KEY}"
    )
    r = requests.get(url).json()

    if "items" not in r or len(r["items"]) == 0:
        return None

    s = r["items"][0]["statistics"]
    return {
        "views": int(s["viewCount"]),
        "subs": int(s["subscriberCount"])
    }

def main():
    today = str(date.today())
    current = get_stats()
    if current is None:
        return

    if not os.path.exists(DATA_FILE):
        data = {
            "views": current["views"],
            "subs": current["subs"],
            "daily_views": 0,
            "daily_subs": 0,
            "date": today
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)

        send_message(
            f"🤖 Bot aktif!\n"
            f"👀 İzlenme: {current['views']}\n"
            f"🔔 Abone: {current['subs']}"
        )
        return

    with open(DATA_FILE, "r") as f:
        old = json.load(f)

    # Gün değiştiyse günlük sayaçları sıfırla
    if old["date"] != today:
        if old["daily_views"] > 0 or old["daily_subs"] > 0:
            send_message(
                f"📊 Günlük Özet ({old['date']})\n"
                f"👀 +{old['daily_views']} izlenme\n"
                f"🔔 +{old['daily_subs']} abone"
            )

        old["daily_views"] = 0
        old["daily_subs"] = 0
        old["date"] = today

    # İzlenme artışı
    if current["views"] > old["views"]:
        diff = current["views"] - old["views"]
        old["daily_views"] += diff
        send_message(
            f"📈 İzlenme arttı!\n"
            f"+{diff} izlenme\n"
            f"Toplam: {current['views']}"
        )

    # Abone artışı
    if current["subs"] > old["subs"]:
        diff = current["subs"] - old["subs"]
        old["daily_subs"] += diff
        send_message(
            f"🔔 Yeni abone geldi!\n"
            f"+{diff} abone\n"
            f"Toplam abone: {current['subs']}"
        )

    old["views"] = current["views"]
    old["subs"] = current["subs"]

    with open(DATA_FILE, "w") as f:
        json.dump(old, f)

if __name__ == "__main__":
    main()
