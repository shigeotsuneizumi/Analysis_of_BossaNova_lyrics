# ボサノバ歌詞解析スクリプト

## 実行方法

```bash
pip install lyricsgenius pandas nltk wordcloud matplotlib unidecode
```

実行：

```bash
python analysis_of_bossanova_lirics.py
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
