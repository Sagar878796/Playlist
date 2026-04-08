import requests
import os

PORTAL = "http://starshare.one:80/c/"
MAC = "00:1A:79:00:3E:1F"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": PORTAL,
    "Accept": "*/*",
    "Cookie": f"mac={MAC}; stb_lang=en; timezone=Asia/Kolkata;"
}

def get_token():
    try:
        url = PORTAL.replace("/c/", "/server/load.php?type=stb&action=handshake&JsHttpRequest=1-xml")
        res = requests.get(url, headers=HEADERS, timeout=10)

        print("Handshake:", res.text)

        return res.json()["js"]["token"]
    except Exception as e:
        print("Token Error:", e)
        return None

def get_channels(token):
    try:
        headers = HEADERS.copy()
        headers["Authorization"] = f"Bearer {token}"

        url = PORTAL.replace("/c/", "/server/load.php?type=itv&action=get_all_channels&JsHttpRequest=1-xml")
        res = requests.get(url, headers=headers, timeout=10)

        print("Channels Response:", res.text[:500])

        data = res.json()
        return data["js"]["data"]
    except Exception as e:
        print("Channel Error:", e)
        return []

def generate_m3u(channels):
    m3u = "#EXTM3U\n"
    for ch in channels:
        name = ch.get("name", "No Name")
        cmd = ch.get("cmd", "")

        if "http" in cmd:
            stream = cmd.split(" ")[-1]
            m3u += f'#EXTINF:-1,{name}\n{stream}\n'

    return m3u

def save_playlist(content):
    path = "Playlist/Star.m3u"
    os.makedirs(path, exist_ok=True)

    with open(f"{path}/index.html", "w", encoding="utf-8") as f:
        f.write(content)

    print("Playlist Saved ✅")

if __name__ == "__main__":
    token = get_token()

    if token:
        channels = get_channels(token)
        playlist = generate_m3u(channels)
        save_playlist(playlist)
    else:
        print("Failed to get token ❌")
