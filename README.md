# Yorisoi Knowledge — よりそいナレッジ

認知症のケア・介護・医療・制度の知識を体系的にまとめたナレッジサイト。
日刊ニュースサイト [Yorisoi Daily (care-news)](https://osamusic.github.io/care-news/) の姉妹サイトです。

## 構成

- Hugo + [PaperMod](https://github.com/adityatelange/hugo-PaperMod) テーマ（care-news と共通）
- GitHub Pages に GitHub Actions（`.github/workflows/hugo.yml`）で自動デプロイ
- テーマカラーは「よりそいオレンジ」（`assets/css/extended/custom.css`、care-news と共通）

## コンテンツ構成

```
content/
├── kiso/      基礎知識（認知症の種類、中核症状とBPSD、若年性認知症、MCIと予防）
├── care/      ケア・接し方（基本の接し方、困りごと別の対応）
├── seido/     制度・サービス（介護保険の使い方、相談窓口ガイド）
├── iryo/      医療・くすり（受診の流れ、治療薬）
├── kazoku/    家族のケア（介護者のセルフケア）
├── glossary.md  用語集（care-news の「きょうのことば」を集約していく）
└── search.md    サイト内検索（Fuse.js）
```

## ローカルでの確認

```sh
git clone https://github.com/adityatelange/hugo-PaperMod themes/PaperMod --depth=1
hugo server
```

## 記事の書き方

- 記事は各セクションのディレクトリに Markdown で追加（front matter は既存記事を参照）
- 記事間リンクは `{{</* relref "/kiso/xxx.md" */>}}` を使用
- トーンは Yorisoi Daily と同じ：やさしい言葉、断定しすぎない、必ず「相談先」につなげる
- 医療・制度の記事には末尾に免責の一文を入れる

## 用語集の自動更新

`.github/workflows/glossary.yml` が毎日 12:45 JST（care-news パイプライン 12:00 JST の後）に
`scripts/update_glossary.py` を実行し、care-news 全記事の「きょうのことば」から
用語集に未収録の語（括弧内の別名も含めて重複判定）を「新着のことば」セクションへ
出典リンク付きで追記 → コミット → デプロイする。手動実行は Actions の workflow_dispatch か:

```sh
python3 scripts/update_glossary.py --dry-run   # ローカル確認（../care-news を参照）
```

### カテゴリー自動分類（ローカル・週1回）

「新着のことば」に溜まった語は、`scripts/classify_glossary.py` が LLM（OpenRouter、
キーは環境変数 or `../care-news-code/.env` を参照）で4カテゴリーへ分類して移動する。
**APIキーを使うため GitHub Actions では動かさず、ローカル cron（毎週日曜 13:00）で
`scripts/classify_and_push.sh` を実行**（分類 → 変更があれば commit & push → 自動デプロイ）。

```sh
python3 scripts/classify_glossary.py --dry-run   # 分類結果の確認のみ
```

モデルは `CLASSIFY_MODEL` で変更可（既定: deepseek/deepseek-chat）。判断に迷う語は
「保留」として新着に残る。移動後の語が再追加されることはない。

## デプロイ

`main` ブランチへの push で GitHub Pages に自動デプロイされます。
初回はリポジトリの Settings → Pages → Source を「GitHub Actions」に設定してください。
