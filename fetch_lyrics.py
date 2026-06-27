# ============================================================
# Bossa Nova Lyrics Analysis
# 1. 検索＆登録フェーズ
#
# 必要ライブラリ:
# pip install lyricsgenius pandas
#
# 実行:
# python fetch_lyrics.py
# ============================================================

import os
import lyricsgenius
import pandas as pd
import re
from pathlib import Path

# ============================================================
# Genius API TOKEN
# https://genius.com/api-clients
# ============================================================

GENIUS_API_TOKEN = os.environ.get("GENIUS_API_TOKEN", "")

# ============================================================
# 解析する曲リストCSV
# CSVフォーマット: title,artist (1行目はヘッダー)
# ============================================================

SONGS_CSV = Path("songs_list.csv")

if not SONGS_CSV.exists():
    raise FileNotFoundError(
        f"{SONGS_CSV} が見つかりません。"
        " title,artist の2列を持つCSVを用意してください。"
    )

songs_list_df = pd.read_csv(SONGS_CSV, encoding="utf-8-sig")

SONGS = list(zip(songs_list_df["title"], songs_list_df["artist"]))

# ============================================================
# 出力ディレクトリ
# ============================================================

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================
# Genius API 初期化
# ============================================================

genius = lyricsgenius.Genius(
    GENIUS_API_TOKEN,
    skip_non_songs=True,
    excluded_terms=["(Remix)", "(Live)"],
    remove_section_headers=True
)

# ============================================================
# 歌詞取得
# ============================================================

all_song_data = []

# 既存データのキーセットを作成
songs_csv = OUTPUT_DIR / "lyrics_database.csv"
existing_keys = set()
if songs_csv.exists():
    existing_df = pd.read_csv(songs_csv, encoding="utf-8-sig")
    existing_keys = set(zip(existing_df["title"], existing_df["artist"]))
    print(f"既存データ: {len(existing_keys)} 曲")

print("===================================")
print("Loading songs...")
print("===================================")

for title, artist in SONGS:

    if (title, artist) in existing_keys:
        print(f"\nSkipped (already exists): {title} / {artist}")
        continue


    print(f"\nLoading: {title} / {artist}")

    try:
        song = genius.search_song(
            title=title,
            artist=artist
        )

        if song is None:
            print("  -> NOT FOUND")
            continue

        lyrics = song.lyrics

        # 余計なEmbedなど除去
        lyrics = re.sub(r"\d*Embed$", "", lyrics)

        all_song_data.append({
            "title": title,
            "artist": artist,
            "lyrics": lyrics
        })

        print("  -> SUCCESS")

    except Exception as e:

        print("  -> ERROR")
        print(e)

print("\n===================================")
print(f"Loaded songs: {len(all_song_data)}")
print("===================================")

# ============================================================
# DataFrame保存（既存データとマージ）
# ============================================================

new_df = pd.DataFrame(all_song_data)

if songs_csv.exists():
    existing_df = pd.read_csv(songs_csv, encoding="utf-8-sig")
    merged_df = pd.concat([existing_df, new_df], ignore_index=True)
    merged_df = merged_df.drop_duplicates(subset=["title", "artist"], keep="first")
else:
    merged_df = new_df

merged_df.to_csv(
    songs_csv,
    index=False,
    encoding="utf-8-sig"
)

print(f"\nSaved: {songs_csv}")
print("\nDONE.")
