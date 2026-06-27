import os
import requests, time, csv
import pandas as pd

GENIUS_API_TOKEN = os.environ.get("GENIUS_API_TOKEN", "")
ARTIST_ID = 370933
headers = {"Authorization": f"Bearer {GENIUS_API_TOKEN}"}

# 既存 songs_list.csv のタイトルセット（小文字）
existing_df = pd.read_csv("songs_list.csv", encoding="utf-8-sig")
existing_titles = set(existing_df["title"].str.lower())

# Genius から全曲取得
print("Genius から全曲リスト取得中...", flush=True)
all_songs = []
page = 1
while True:
    resp = requests.get(
        f"https://api.genius.com/artists/{ARTIST_ID}/songs",
        headers=headers,
        params={"per_page": 50, "page": page, "sort": "popularity"}
    )
    data = resp.json()["response"]
    songs = data["songs"]
    if not songs:
        break
    all_songs.extend(songs)
    if data["next_page"] is None:
        break
    page += 1
    time.sleep(0.3)

print(f"総曲数: {len(all_songs)}", flush=True)

untaken = [s for s in all_songs if s["title"].lower() not in existing_titles]
print(f"未取得: {len(untaken)} 曲", flush=True)

# 各曲の language を取得してポルトガル語のみ抽出
print("\n言語判定中...", flush=True)
pt_songs = []
errors = 0
for i, song in enumerate(untaken):
    try:
        resp = requests.get(
            f"https://api.genius.com/songs/{song['id']}",
            headers=headers,
            timeout=10
        )
        lang = resp.json()["response"]["song"].get("language")
        if lang == "pt":
            pt_songs.append(song["title"])
            print(f"  [pt] {song['title']}", flush=True)
        if (i + 1) % 50 == 0:
            print(f"  ... {i+1}/{len(untaken)} 処理完了", flush=True)
        time.sleep(0.4)
    except Exception as e:
        errors += 1
        print(f"  [ERROR] {song['title']}: {e}", flush=True)
        time.sleep(1)

print(f"\nポルトガル語曲: {len(pt_songs)} 曲 (エラー: {errors})", flush=True)

# songs_list.csv に追記
with open("songs_list.csv", "a", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    for title in pt_songs:
        writer.writerow([title, "Antonio Carlos Jobim"])

print(f"songs_list.csv に {len(pt_songs)} 曲追加しました。", flush=True)
print("DONE.", flush=True)
