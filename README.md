# ボサノバ歌詞分析ツール

トム・ジョビン（Antônio Carlos Jobim）のボサノバ歌詞を Genius API から収集し、頻出単語を分析するツールです。

---

## ファイル構成

```
.
├── songs_list.csv          # 取得対象の曲リスト（title, artist の2列）
├── fetch_lyrics.py         # フェーズ1：歌詞取得スクリプト
├── filter_pt_songs.py      # フェーズ1.5：ポルトガル語曲フィルタスクリプト
├── analyze_lyrics.py       # フェーズ2：歌詞分析スクリプト
└── output/
    ├── lyrics_database.csv      # 取得した歌詞データベース（分析対象）
    ├── lyrics_database_others.csv # ジョビン以外のアーティストの歌詞
    ├── top50_words.csv          # 頻出単語 TOP50
    ├── top50_words_pt.csv       # 頻出単語 TOP50（ポルトガル語曲のみ）
    ├── wordcloud.png            # ワードクラウド画像
    ├── wordcloud_pt.png         # ワードクラウド画像（ポルトガル語曲のみ）
    └── top50_table_sns.png      # SNS投稿用 TOP50 テーブル画像
```

---

## セットアップ

### 1. 仮想環境の作成

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. 依存ライブラリのインストール

```bash
pip install lyricsgenius pandas langdetect wordcloud matplotlib unidecode
```

### 3. Genius API トークンの取得

1. [https://genius.com/api-clients](https://genius.com/api-clients) にアクセス
2. アカウント登録後、「New API Client」でアプリを作成
3. 発行された **Client Access Token** をコピー

### 4. トークンを設定

`fetch_lyrics.py` と `filter_pt_songs.py` の以下の行にトークンを貼り付けます：

```python
GENIUS_API_TOKEN = "ここにトークンを貼る"
```

---

## 使い方

### フェーズ 1：歌詞取得

`songs_list.csv` に記載された曲の歌詞を Genius API から取得し、`output/lyrics_database.csv` に保存します。

```bash
python fetch_lyrics.py
```

- 既に取得済みの曲はスキップされます（差分取得）
- 取得できなかった曲は `NOT FOUND` として表示されます

**songs_list.csv のフォーマット：**

```csv
title,artist
Garota de Ipanema,Antonio Carlos Jobim
Wave,Antonio Carlos Jobim
```

---

### フェーズ 1.5：Genius 上のポルトガル語曲を一括追加

指定アーティストの Genius 登録曲を全件スキャンし、ポルトガル語の曲のみ `songs_list.csv` に追加します。その後 `fetch_lyrics.py` を実行して歌詞を取得します。

```bash
python filter_pt_songs.py
python fetch_lyrics.py
```

- Genius API を全ページ取得（アーティスト ID は `filter_pt_songs.py` 内の `ARTIST_ID` で指定）
- 各曲の言語を `/songs/{id}` エンドポイントで確認し、`language == "pt"` の曲のみ追加
- 既に `songs_list.csv` に存在するタイトルはスキップ

---

### フェーズ 2：歌詞分析

`output/lyrics_database.csv` の歌詞を分析し、頻出単語 TOP50 とワードクラウドを生成します。

```bash
python analyze_lyrics.py
```

**出力ファイル：**

| ファイル | 内容 |
|----------|------|
| `output/top50_words.csv` | 頻出単語 TOP50 |
| `output/wordcloud.png` | ワードクラウド画像 |

**ポルトガル語曲のみで分析する場合（推奨）：**

`langdetect` で各曲の言語を判定してフィルタします。`analyze_lyrics.py` を参考に以下を追加してください：

```python
from langdetect import detect, LangDetectException

def is_portuguese(lyrics):
    try:
        return detect(lyrics) == "pt"
    except LangDetectException:
        return False

songs_df = songs_df[songs_df["lyrics"].apply(is_portuguese)]
```

---

## データ管理の注意点

### 歌詞データベースの分割

ジョビン以外のアーティストの曲は分析から除外し、別ファイルに保存することを推奨します：

```python
import pandas as pd

df = pd.read_csv("output/lyrics_database.csv", encoding="utf-8-sig")
jobim = df[df["artist"].isin(["Antonio Carlos Jobim", "Tom Jobim"])]
others = df[~df["artist"].isin(["Antonio Carlos Jobim", "Tom Jobim"])]

jobim.to_csv("output/lyrics_database.csv", index=False, encoding="utf-8-sig")
others.to_csv("output/lyrics_database_others.csv", index=False, encoding="utf-8-sig")
```

### 重複歌詞の除去

Genius には同じ歌詞が複数のタイトルで登録されている場合があります。MD5 ハッシュで除去します：

```python
import hashlib

df["lyrics_hash"] = df["lyrics"].apply(
    lambda x: hashlib.md5(str(x).encode()).hexdigest()
)
df = df.drop_duplicates(subset="lyrics_hash", keep="first")
df = df.drop(columns="lyrics_hash")
```

---

## 分析結果（トム・ジョビン 123曲）

### TOP 10 頻出単語

| 順位 | 単語 | 意味 | 出現回数 |
|------|------|------|---------|
| 1 | nao | ない | 294 |
| 2 | meu | 私の | 153 |
| 3 | amor | 愛 | 152 |
| 4 | vou | 行く/する | 117 |
| 5 | vida | 人生 | 89 |
| 6 | tem | ある/持つ | 81 |
| 7 | mim | 私に | 79 |
| 8 | sei | 知っている | 77 |
| 9 | como | ように | 72 |
| 10 | minha | 私の(女) | 66 |

> ストップワード・英語歌詞除去済み

---

## 注意事項

- Genius API は大量リクエストでレート制限がかかる場合があります。`time.sleep()` によるリクエスト間隔の調整を推奨します
- 一部の曲は歌詞ではなく別のテキスト（書籍等）が誤って登録されている場合があります
- 歌詞の著作権は各権利者に帰属します。個人の学習・研究目的での利用を推奨します
- 商用利用は Genius の利用規約を確認してください
