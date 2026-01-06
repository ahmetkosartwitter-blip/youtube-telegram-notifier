import requests
import json
import os
from datetime import date

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

DATA_FILE = "full_stats.json"

def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text})

def get_channel_stats():
    url = (
        "https://www.googleapis.com/youtube/v3/channels"
        "?part=statistics"
        f"&id={CHANNEL_ID}"
        f"&key={YOUTUBE_API_KEY}"
    )
    r = requests.get(url).json()
    if not r.get("items"):
        return None
    s = r["items"][0]["statistics"]
    return {
        "views": int(s["viewCount"]),
        "subs": int(s["subscriberCount"])
    }

def get_videos():
    url = (
        "https://www.googleapis.com/youtube/v3/search"
        "?part=snippet"
        f"&channelId={CHANNEL_ID}"
        "&order=date"
        "&type=video"
        "&maxResults=5"
        f"&key={YOUTUBE_API_KEY}"
    )
    r = requests.get(url).json()
    videos = []
    for i in r.get("items", []):
        videos.append({
            "id": i["id"]["videoId"],
            "title": i["snippet"]["title"]
        })
    return videos

def get_video_views(video_id):
    url = (
        "https://www.googleapis.com/youtube/v3/videos"
        "?part=statistics"
        f"&id={video_id}"
        f"&key={YOUTUBE_API_KEY}"
    )
    r = requests.get(url).json()
    if not r.get("items"):
        return 0
    return int(r["items"][0]["statistics"]["viewCount"])

def main():
    today = str(date.today())
    channel = get_channel_stats()
    if channel is None:
        return

    videos = get_videos()
    video_views = {}
    for v in videos:
        video_views[v["id"]] = {
            "title": v["title"],
            "views": get_video_views(v["id"])
        }

    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({
                "date": today,
                "views": channel["views"],
                "subs": channel["subs"],
                "videos": video_views
            }, f)

        send_message(
            f"🤖 Bot aktif!\n"
            f"👀 İzlenme: {channel['views']}\n"
            f"🔔 Abone: {channel['subs']}"
        )
        return

    with open(DATA_FILE, "r") as f:
        old = json.load(f)

    # ANLIK kanal izlenme
    if channel["views"] > old["views"]:
        diff = channel["views"] - old["views"]
        send_message(
            f"📈 İzlenme arttı!\n"
            f"+{diff} izlenme\n"
            f"Toplam: {channel['views']}"
        )

    # ANLIK abone
    if channel["subs"] > old["subs"]:
        diff = channel["subs"] - old["subs"]
        send_message(
            f"🔔 Yeni abone geldi!\n"
            f"+{diff} abone\n"
            f"Toplam: {channel['subs']}"
        )

    # GÜNLÜK video raporu
    if old["date"] != today:
        report = f"📊 Günlük Video Raporu ({old['date']})\n\n"
        for vid, data in video_views.items():
            old_views = old["videos"].get(vid, {}).get("views", data["views"])
            diff = data["views"] - old_views
            if diff > 0:
                report += f"🎥 {data['title']}\n👀 +{diff} izlenme\n\n"

        if report.strip() != f"📊 Günlük Video Raporu ({old['date']})":
            send_message(report.strip())

        old["date"] = today

    old["views"] = channel["views"]
    old["subs"] = channel["subs"]
    old["videos"] = video_views

    with open(DATA_FILE, "w") as f:
        json.dump(old, f)

if __name__ == "__main__":
    main()
