#!/bin/bash
# 週次: 用語集「新着のことば」をLLM分類してカテゴリーへ移動し、変更があれば push する
# （push で GitHub Pages のデプロイが自動起動する）
set -euo pipefail
cd "$(dirname "$0")/.."

python3 scripts/classify_glossary.py

if git diff --quiet content/glossary.md; then
  echo "変更なし。"
  exit 0
fi

git add content/glossary.md
git commit -m "用語集: 新着のことばをカテゴリーへ分類 ($(date +%Y-%m-%d))"
git push
