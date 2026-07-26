#!/bin/bash
# 週次: 用語集「新着のことば」をLLM分類してカテゴリーへ移動し、変更があれば push する
# （push で GitHub Pages のデプロイが自動起動する）
set -euo pipefail
cd "$(dirname "$0")/.."

# GitHub Actions（毎日の「きょうのことば」取り込み）が先に main を進めているので、
# 分類前に必ず remote を取り込む。取り込まないと push が non-fast-forward で落ちる
git pull --rebase --autostash

python3 scripts/classify_glossary.py

if git diff --quiet content/glossary.md; then
  echo "変更なし。"
  exit 0
fi

git add content/glossary.md
git commit -m "用語集: 新着のことばをカテゴリーへ分類 ($(date +%Y-%m-%d))"

# 実行中に Actions が push していた場合に備えて 1 度だけ引き直して再試行する
if ! git push; then
  echo "push に失敗。pull --rebase して再試行します。"
  git pull --rebase
  git push
fi
