# ============================================================
# Bossa Nova Lyrics Analysis
# 2. 分析フェーズ
#
# 必要ライブラリ:
# pip install pandas wordcloud matplotlib unidecode
#
# 事前に fetch_lyrics.py を実行して output/songs.csv を生成すること
#
# 実行:
# python analyze_lyrics.py
# ============================================================

import pandas as pd
import re
from collections import Counter
from unidecode import unidecode
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# 出力ディレクトリ
# ============================================================

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================
# songs.csv 読み込み
# ============================================================

songs_csv = OUTPUT_DIR / "songs.csv"

if not songs_csv.exists():
    raise FileNotFoundError(
        f"{songs_csv} が見つかりません。"
        " 先に fetch_lyrics.py を実行してください。"
    )

songs_df = pd.read_csv(songs_csv, encoding="utf-8-sig")

all_song_data = songs_df.to_dict(orient="records")
all_lyrics = songs_df["lyrics"].dropna().tolist()

print("===================================")
print(f"Loaded songs: {len(all_song_data)}")
print("===================================")

# ============================================================
# 全歌詞結合・テキスト前処理
# ============================================================

text = " ".join(all_lyrics)

text = text.lower()
text = unidecode(text)
text = re.sub(r"\[.*?\]", "", text)   # [Verse] など削除
text = re.sub(r"[^a-zA-Z\s]", " ", text)
text = re.sub(r"\s+", " ", text)

words = text.split()

print(f"\nTotal words: {len(words)}")

# ============================================================
# ポルトガル語ストップワード
# ============================================================

stopwords_pt = {

    # 冠詞
    "a", "o", "as", "os",
    "um", "uma", "uns", "umas",

    # 前置詞
    "de", "da", "do", "das", "dos",
    "em", "no", "na", "nos", "nas",
    "por", "para", "pra", "pro",
    "com", "sem",

    # 接続詞
    "e", "ou", "mas", "que",

    # 代名詞
    "eu", "voce", "me", "te",
    "se", "nos", "lhe",

    # よく出る不要語
    "vai", "vem", "foi", "ser",
    "ter", "ha", "ja", "mais",

    # Geniusノイズ
    "lyrics", "embed", "song",
}

filtered_words = [
    w for w in words
    if w not in stopwords_pt
    and len(w) > 2
]

print(f"Filtered words: {len(filtered_words)}")

# ============================================================
# 単語頻度分析 TOP50
# ============================================================

counter = Counter(filtered_words)

top50 = counter.most_common(50)

freq_df = pd.DataFrame(top50, columns=["word", "count"])

print("\n===================================")
print("TOP 50 WORDS")
print("===================================")
print(freq_df.to_string(index=False))

freq_csv = OUTPUT_DIR / "top50_words.csv"
freq_df.to_csv(freq_csv, index=False, encoding="utf-8-sig")
print(f"\nSaved: {freq_csv}")

# ============================================================
# WordCloud 生成
# ============================================================

print("\nGenerating WordCloud...")

wordcloud = WordCloud(
    width=1600,
    height=800,
    background_color="white",
    collocations=False
).generate(" ".join(filtered_words))

plt.figure(figsize=(18, 9))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")

wordcloud_png = OUTPUT_DIR / "wordcloud.png"
plt.savefig(wordcloud_png, bbox_inches="tight")
print(f"Saved: {wordcloud_png}")

plt.show()

# ============================================================
# 曲ごとの頻出語 TOP10
# ============================================================

print("\n===================================")
print("SONG ANALYSIS")
print("===================================")

for item in all_song_data:

    title = item["title"]

    if not isinstance(item.get("lyrics"), str):
        continue

    song_text = item["lyrics"].lower()
    song_text = unidecode(song_text)
    song_text = re.sub(r"[^a-zA-Z\s]", " ", song_text)

    song_words = [
        w for w in song_text.split()
        if w not in stopwords_pt
        and len(w) > 2
    ]

    song_counter = Counter(song_words)

    print(f"\n--- {title} ---")
    for word, count in song_counter.most_common(10):
        print(f"  {word:<15} {count}")

# ============================================================
# 指定ワードの周辺語分析
# ============================================================

TARGET_WORD = "amor"
WINDOW_SIZE = 3

near_words = []

for i, word in enumerate(filtered_words):

    if word == TARGET_WORD:

        start = max(i - WINDOW_SIZE, 0)
        end = min(i + WINDOW_SIZE + 1, len(filtered_words))
        near_words.extend(filtered_words[start:end])

near_counter = Counter(near_words)

print("\n===================================")
print(f"WORDS NEAR '{TARGET_WORD}'")
print("===================================")

for word, count in near_counter.most_common(20):
    if word != TARGET_WORD:
        print(f"  {word:<15} {count}")

print("\nDONE.")
