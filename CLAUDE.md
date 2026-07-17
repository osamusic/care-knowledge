# CLAUDE.md — Yorisoi Knowledge (care-knowledge)

認知症ケアの知識ベースサイト。Hugo + PaperMod、GitHub Pages（main への push で自動デプロイ）、
ドメイン yorisoi.osamusic.org は Cloudflare プロキシ経由。
姉妹サイト: Yorisoi Daily（`../care-news`、日刊ニュース）。詳細な構成は README.md を参照。

## ビルド・確認

```sh
hugo server   # themes/PaperMod が必要（README 参照）。CI は Hugo 0.164.0 で固定
```

## 変更時の注意（重要）

- **hugo.toml**: プレーンなキー（`author` など）は必ず `[params.assets]` 等のサブテーブルより
  **前**に書く。後に書くと TOML の仕様でサブテーブル側のスコープに入り、無効になる
  （過去にこれで meta description が空になる障害があった）
- **カラーパレット**（`assets/css/extended/custom.css`）: ライトモードの
  `--primary #a8530f` / `--secondary #9a5730` は WCAG AA を満たす値。
  旧値 #d2691e / #e8935a はコントラスト不足なので戻さない
- **PaperMod 更新**: `.github/workflows/hugo.yml` の `PAPERMOD_COMMIT`（SHA 固定）を
  care-news 側と合わせて両方更新する
- **CSP**: `layouts/_partials/extend_head.html` の meta CSP は `connect-src 'self'` のまま。
  「役に立った」ボタンの API（`/likes`）は同一オリジンなので変更不要
- **security.txt** の連絡先は yorisoi.daily@gmail.com（個人アドレスにしない）

## 文体・コンテンツ

- やさしい日本語、断定しすぎない、必ず相談先（地域包括支援センター等）につなげる
- 医療・制度の記事は末尾に免責の一文
- 記事間リンクは `{{</* relref "..." */>}}`

## 自動化

- 用語集: `.github/workflows/glossary.yml` が毎日 12:45 JST に care-news の
  「きょうのことば」を取り込み。カテゴリー分類はローカル cron（日曜 13:00、
  OpenRouter API キーは `../care-news-code/.env` — **GitHub Actions に入れない**）
- 「役に立った」ボタン: `layouts/_partials/comments.html`。集計 Worker は
  `~/ai/yorisoi-likes`（`wrangler deploy` で反映）
