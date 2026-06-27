# ボサノバ歌詞解析スクリプト（作成中）
## 概要
- ボサノバの歌詞でよく使われているポルトガル語の単語を出力するためのツール
- 任意のアーティストと曲名を複数指定して、そこで使用されている単語の統計をとることで頻出単語ランキングを表示可能
- 言語はpython3を使用する
- 歌詞共有サイトGeniusが提供するWeb APIを利用する
- アーティスト、曲名の指定はcvs
- 以下のフェーズでスクリプトを分けて処理を行う。
  - 検索＆登録フェーズ
  - 分析フェーズ

### 検索＆登録フェーズ
1. 歌詞検索のためのアーティスト名、曲名リストのcsvファイルを準備
1. genius = lyricsgenius.Geniusで初期化
1. genius.search_artistを使用して、指定したアーティスト名からlyricsgeniusに登録されているアーティストを特定
1. さらにgenius.search_song を使用して、特定したアーティストと指定した曲名からlyricsgeniusに登録されている曲名を特定
1. 特定したアーティスト名、曲名、曲の歌詞をデータとしてcvsファイルに登録
　以前、同じアーティスト、同じ曲名データがある場合は検索および登録をスキップ

### 分析フェーズ（スクリプト化 or AIエージェントに回答させてもOK）
1. 指定したアーティスト名と曲名の歌詞をcsvファイルから取得
1. 冠詞、前置詞や接続詞など頻出の単語を除去
1. 1曲の歌詞の中に同じ単語が繰り返し出てきた場合は、全ての回数をカウントせずに１つとして集計
1. amor amores amar amo amei などの活用形 は、区別せずに１つとして集計（SpaCyを利用）
1. 頻出の単語の統計を行い、上位１００位まで表示

## 環境構築
導入：
```bash
fetch_lyrics.py
pip install lyricsgenius pandas


pip install lyricsgenius pandas nltk wordcloud matplotlib unidecode
```

## 実行方法
実行（検索＆登録フェーズ）：

```bash
python fetch_lyrics.py
```

実行（分析フェーズ）：

```bash
python analyze_lyrics.py
```

---

# 出力されるファイル

```text
songs_list.csv
songs.csv
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

## 5. 熟語リスト

単語ではなく頻出熟語のリスト作成

---
# 注意点

* Genius APIは大量アクセスすると制限されます
* 商用利用は規約確認が必要
* 歌詞著作権に注意
* 取得失敗する曲もあります

個人学習用途で楽しむのがおすすめです。
