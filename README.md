# ボサノバ歌詞 50曲解析 完成版スクリプト

```python
import lyricsgenius
import pandas as pd
import re
from collections import Counter
from unidecode import unidecode
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from pathlib import Path

# ==================================================
# 設定
# ==================================================

GENIUS_API_TOKEN = "YOUR_GENIUS_API_TOKEN"

ARTISTS = [
    "Antonio Carlos Jobim",
    "Joao Gilberto",
    "Vinicius de Moraes",
    "Marcos Valle",
    "Nara Leao"
]

SONGS_PER_ARTIST = 10

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ==================================================
# Genius API 初期化
# ==================================================

genius = lyricsgenius.Genius(
    GENIUS_API_TOKEN,
    skip_non_songs=True,
    excluded_terms=["(Remix)", "(Live)"],
    remove_section_headers=True
)

# ==================================================
# 歌詞取得
# ==================================================

all_song_data = []
all_lyrics = []

print("===================================")
print("Loading Bossa Nova Lyrics...")
print("===================================")

for artist_name in ARTISTS:

    print(f"\nArtist: {artist_name}")

    try:
        artist = genius.search_artist(
            artist_name,
            max_songs=SONGS_PER_ARTIST,
            sort="popularity"
        )

        if artist is None:
            print("  -> artist not found")
            continue

        for song in artist.songs:

            title = song.title
            lyrics = song.lyrics

            print(f"  Loaded: {title}")

            all_song_data.append({
                "artist": artist_name,
                "title": title,
                "lyrics": lyrics
            })

            all_lyrics.append(lyrics)

    except Exception as e:
        print(f"ERROR: {artist_name}")
        print(e)

print("\n===================================")
print(f"Total songs: {len(all_song_data)}")
print("===================================")

# ==================================================
# DataFrame保存
# ==================================================

songs_df = pd.DataFrame(all_song_data)

songs_csv = OUTPUT_DIR / "bossa_nova_songs.csv"
songs_df.to_csv(songs_csv, index=False)

print(f"\nSaved: {songs_csv}")

# ==================================================
# テキスト結合
# ==================================================

text = " ".join(all_lyrics)

# 小文字化
text = text.lower()

# アクセント除去
text = unidecode(text)

# [Chorus] など除去
text = re.sub(r"\[.*?\]", "", text)

# 記号除去
text = re.sub(r"[^a-zA-Z\s]", " ", text)

# 余分空白除去
text = re.sub(r"\s+", " ", text)

words = text.split()

print(f"\nTotal words: {len(words)}")

# ==================================================
# ポルトガル語ストップワード
# ==================================================

stopwords_pt = {

    # 基本
    "de","da","do","das","dos",
    "a","o","as","os",
    "e","em","um","uma",
    "que","com","na","no",
    "eu","voce","pra","pro",

    # 頻出助詞
    "me","te","se","lhe","nos",
    "por","para","ao","aos",
    "como","mais","mas","foi",
    "ser","ter","ha","ja",

    # 英語ノイズ
    "lyrics","embed","song"
}

filtered_words = [

    w for w in words
    if w not in stopwords_pt
    and len(w) > 2
]

print(f"Filtered words: {len(filtered_words)}")

# ==================================================
# 頻度分析
# ==================================================

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
freq_csv = OUTPUT_DIR / "bossa_nova_top50.csv"
freq_df.to_csv(freq_csv, index=False)

print(f"\nSaved: {freq_csv}")

# ==================================================
# WordCloud生成
# ==================================================

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

wordcloud_png = OUTPUT_DIR / "bossa_nova_wordcloud.png"

plt.savefig(wordcloud_png, bbox_inches="tight")

print(f"Saved: {wordcloud_png}")

plt.show()

# ==================================================
# アーティスト別分析
# ==================================================

print("\n===================================")
print("ARTIST ANALYSIS")
print("===================================")

for artist_name in ARTISTS:

    artist_text = " "

    for item in all_song_data:

        if item["artist"] == artist_name:
            artist_text += item["lyrics"]

    artist_text = artist_text.lower()
    artist_text = unidecode(artist_text)
    artist_text = re.sub(r"[^a-zA-Z\s]", " ", artist_text)

    artist_words = artist_text.split()

    artist_words = [

        w for w in artist_words
        if w not in stopwords_pt
        and len(w) > 2
    ]

    artist_counter = Counter(artist_words)

    print(f"\n--- {artist_name} ---")

    for word, count in artist_counter.most_common(10):
        print(f"{word:<15} {count}")

# ==================================================
# 共起分析（簡易版）
# ==================================================

TARGET_WORD = "amor"

print("\n===================================")
print(f"WORDS NEAR '{TARGET_WORD}'")
print("===================================")

window_size = 3

near_words = []

for i, word in enumerate(filtered_words):

    if word == TARGET_WORD:

        start = max(i - window_size, 0)
        end = min(i + window_size + 1, len(filtered_words))

        near_words.extend(filtered_words[start:end])

near_counter = Counter(near_words)

for word, count in near_counter.most_common(20):

    if word != TARGET_WORD:
        print(f"{word:<15} {count}")

print("\nDONE.")
```

---

# 実行方法

```bash
pip install lyricsgenius pandas nltk wordcloud matplotlib unidecode
```

実行：

```bash
python bossa_analysis.py
```

---

# 出力されるファイル

```text
output/
├── bossa_nova_songs.csv
├── bossa_nova_top50.csv
└── bossa_nova_wordcloud.png
```

---

# 期待される頻出単語

おそらく以下が大量に出ます：

* amor
* saudade
* coracao
* mar
* noite
* olhar
* sol
* samba
* menina
* felicidade

かなり「ボサノバ空気」が見えます。

---

# 発展アイデア

## 1. Spotify API連携

人気曲だけ取得。

---

## 2. TF-IDF分析

「Jobimだけ異常に多い単語」

---

## 3. 感情分析

```python
from textblob import TextBlob
```

---

## 4. NetworkXで単語ネットワーク

```python
import networkx as nx
```

---

## 5. ボサノバ歌詞ジェネレータ

```python
import markovify
```

で：

```text
Noite de verão
Meu coração no mar
```

みたいな生成が可能。

---

# 注意点

* Genius APIは大量アクセスすると制限されます
* 商用利用は規約確認が必要
* 歌詞著作権に注意
* 取得失敗する曲もあります

個人学習用途で楽しむのがおすすめです。
