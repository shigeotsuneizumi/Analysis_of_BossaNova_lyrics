# ============================================================
# Bossa Nova Lyrics Analysis
# 曲リスト指定版
#
# 必要ライブラリ:
# pip install lyricsgenius pandas wordcloud matplotlib unidecode
#
# 実行:
# python bossa_song_analysis.py
# ============================================================

import lyricsgenius
import pandas as pd
import re
from collections import Counter
from unidecode import unidecode
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# Genius API TOKEN
# https://genius.com/api-clients
# ============================================================

GENIUS_API_TOKEN = "YOUR_GENIUS_API_TOKEN"

# ============================================================
# 解析したい曲を自分で指定
# (曲名, アーティスト名)
# ============================================================

SONGS = [

    ("Garota de Ipanema", "Antonio Carlos Jobim"),
    ("Chega de Saudade", "Joao Gilberto"),
    ("Corcovado", "Antonio Carlos Jobim"),
    ("Desafinado", "Joao Gilberto"),
    ("Wave", "Antonio Carlos Jobim"),
    ("O Barquinho", "Roberto Menescal"),
    ("Samba de Verao", "Marcos Valle"),
    ("Agua de Beber", "Antonio Carlos Jobim"),
    ("Dindi", "Antonio Carlos Jobim"),
    ("Triste", "Tom Jobim"),

    # 好きなだけ追加可能
]

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
all_lyrics = []

print("===================================")
print("Loading songs...")
print("===================================")

for title, artist in SONGS:

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

        all_lyrics.append(lyrics)

        print("  -> SUCCESS")

    except Exception as e:

        print("  -> ERROR")
        print(e)

print("\n===================================")
print(f"Loaded songs: {len(all_song_data)}")
print("===================================")

# ============================================================
# DataFrame保存
# ============================================================

songs_df = pd.DataFrame(all_song_data)

songs_csv = OUTPUT_DIR / "songs.csv"

songs_df.to_csv(
    songs_csv,
    index=False,
    encoding="utf-8-sig"
)

print(f"\nSaved: {songs_csv}")

# ============================================================
# 全歌詞結合
# ============================================================

text = " ".join(all_lyrics)

# 小文字化
text = text.lower()

# アクセント除去
text = unidecode(text)

# [Verse] など削除
text = re.sub(r"\[.*?\]", "", text)

# 記号除去
text = re.sub(r"[^a-zA-Z\s]", " ", text)

# 余分空白除去
text = re.sub(r"\s+", " ", text)

words = text.split()

print(f"\nTotal words: {len(words)}")

# ============================================================
# ポルトガル語ストップワード
# ============================================================

stopwords_pt = {

    # 冠詞
    "a","o","as","os",
    "um","uma","uns","umas",

    # 前置詞
    "de","da","do","das","dos",
    "em","no","na","nos","nas",
    "por","para","pra","pro",
    "com","sem",

    # 接続詞
    "e","ou","mas","que",

    # 代名詞
    "eu","voce","me","te",
    "se","nos","lhe",

    # よく出る不要語
    "vai","vem","foi","ser",
    "ter","ha","ja","mais",

    # Geniusノイズ
    "lyrics","embed","song"
}

filtered_words = [

    w for w in words
    if w not in stopwords_pt
    and len(w) > 2
]

print(f"Filtered words: {len(filtered_words)}")

# ============================================================
# 単語頻度分析
# ============================================================

counter = Counter(filtered_words)

top50 = counter.most_common(50)

freq_df = pd.DataFrame(
    top50,
    columns=["word", "count"]
)

print("\n===================================")
print("TOP 50 WORDS")
print("===================================")

print(freq_df)

# CSV保存
freq_csv = OUTPUT_DIR / "top50_words.csv"

freq_df.to_csv(
    freq_csv,
    index=False,
    encoding="utf-8-sig"
)

print(f"\nSaved: {freq_csv}")

# ============================================================
# WordCloud生成
# ============================================================

print("\nGenerating WordCloud...")

wordcloud = WordCloud(
    width=1600,
    height=800,
    background_color="white",
    collocations=False
).generate(" ".join(filtered_words))

plt.figure(figsize=(18, 9))

plt.imshow(
    wordcloud,
    interpolation="bilinear"
)

plt.axis("off")

wordcloud_png = OUTPUT_DIR / "wordcloud.png"

plt.savefig(
    wordcloud_png,
    bbox_inches="tight"
)

print(f"Saved: {wordcloud_png}")

plt.show()

# ============================================================
# 曲ごとのTOP10
# ============================================================

print("\n===================================")
print("SONG ANALYSIS")
print("===================================")

for item in all_song_data:

    title = item["title"]

    song_text = item["lyrics"].lower()

    song_text = unidecode(song_text)

    song_text = re.sub(
        r"[^a-zA-Z\s]",
        " ",
        song_text
    )

    song_words = song_text.split()

    song_words = [

        w for w in song_words
        if w not in stopwords_pt
        and len(w) > 2
    ]

    song_counter = Counter(song_words)

    print(f"\n--- {title} ---")

    for word, count in song_counter.most_common(10):

        print(f"{word:<15} {count}")

# ============================================================
# "amor" の近くに出る単語
# ============================================================

TARGET_WORD = "amor"

window_size = 3

near_words = []

for i, word in enumerate(filtered_words):

    if word == TARGET_WORD:

        start = max(i - window_size, 0)
        end = min(i + window_size + 1, len(filtered_words))

        near_words.extend(
            filtered_words[start:end]
        )

near_counter = Counter(near_words)

print("\n===================================")
print(f"WORDS NEAR '{TARGET_WORD}'")
print("===================================")

for word, count in near_counter.most_common(20):

    if word != TARGET_WORD:

        print(f"{word:<15} {count}")

print("\nDONE.")