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

## デプロイ

`main` ブランチへの push で GitHub Pages に自動デプロイされます。
初回はリポジトリの Settings → Pages → Source を「GitHub Actions」に設定してください。
