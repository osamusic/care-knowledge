#!/usr/bin/env python3
"""用語集の「新着のことば」をLLMでカテゴリー分類し、各セクションへ移動する。

ローカル実行専用（APIキーを使うため GitHub Actions では動かさない）。
週1回程度 cron などから実行する想定。標準ライブラリのみで動く。

使い方:
    python3 scripts/classify_glossary.py [--dry-run]

APIキー: 環境変数 OPENROUTER_API_KEY、なければ .env → ../care-news-code/.env の順に読む。
モデル: 環境変数 CLASSIFY_MODEL（既定: deepseek/deepseek-chat）
"""

import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GLOSSARY = REPO_ROOT / "content" / "glossary.md"
NEW_SECTION = "新着のことば"
CATEGORIES = ["病気・症状", "薬・医療", "制度・サービス", "暮らし・予防"]

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

PROMPT = """あなたは認知症ケアの知識サイトの編集者です。
以下の用語を、次の4カテゴリーのいずれかに分類してください。

カテゴリー: {categories}

- 判断に迷う場合は「保留」としてください
- 出力は次の形式のJSONのみ（説明文やコードフェンスは不要）: {{"用語名": "カテゴリー名", ...}}

用語:
{terms}"""


def load_api_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if key:
        return key
    for env_path in (REPO_ROOT / ".env", REPO_ROOT.parent / "care-news-code" / ".env"):
        if env_path.is_file():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                m = re.match(r"\s*OPENROUTER_API_KEY\s*=\s*(.+?)\s*$", line)
                if m:
                    return m.group(1).strip().strip('"').strip("'")
    return ""


def parse_new_entries(text: str) -> list[dict]:
    """新着セクションの `**語**\\n: 説明` エントリを [{term, block}] で返す。"""
    section_m = re.search(rf"^## {NEW_SECTION}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not section_m:
        return []
    entries = []
    for m in re.finditer(r"^\*\*(.+?)\*\*\n(: .*?)(?=\n\s*\n|\Z)", section_m.group(1), re.M | re.S):
        entries.append({"term": m.group(1).strip(), "block": f"**{m.group(1).strip()}**\n{m.group(2).rstrip()}"})
    return entries


def classify(entries: list[dict], api_key: str, model: str) -> dict[str, str]:
    terms_text = "\n".join(f"- {e['term']}: {e['block'].splitlines()[1][2:]}" for e in entries)
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": PROMPT.format(categories="、".join(CATEGORIES), terms=terms_text)}],
        "temperature": 0,
    }
    req = urllib.request.Request(
        OPENROUTER_URL,
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as res:
        content = json.load(res)["choices"][0]["message"]["content"]
    content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip())
    result = json.loads(content)
    if not isinstance(result, dict):
        raise ValueError(f"想定外の応答形式: {content[:200]}")
    return {str(k): str(v) for k, v in result.items()}


def move_entry(text: str, block: str, category: str) -> str:
    """エントリを新着セクションから削除し、カテゴリーセクション末尾に追記する。"""
    # 新着セクションから削除（後続の空行ごと）
    text = text.replace(f"{block}\n\n", "", 1)
    # カテゴリーセクションの末尾（次の ## または末尾の --- の直前）に挿入
    header_m = re.search(rf"^## {re.escape(category)}\s*$", text, re.M)
    if not header_m:
        raise ValueError(f"セクションが見つかりません: {category}")
    rest = text[header_m.end():]
    next_m = re.search(r"^## |^---\s*$", rest, re.M)
    pos = header_m.end() + (next_m.start() if next_m else len(rest))
    return text[:pos] + f"{block}\n\n" + text[pos:]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="書き込まずに分類結果を表示")
    args = parser.parse_args()

    text = GLOSSARY.read_text(encoding="utf-8")
    entries = parse_new_entries(text)
    if not entries:
        print("新着のことばは空です。分類するものはありません。")
        return 0

    api_key = load_api_key()
    if not api_key:
        print("エラー: OPENROUTER_API_KEY が見つかりません（環境変数 / .env / ../care-news-code/.env）", file=sys.stderr)
        return 1
    model = os.environ.get("CLASSIFY_MODEL", "deepseek/deepseek-chat")

    result = classify(entries, api_key, model)

    moved = 0
    for e in entries:
        category = result.get(e["term"], "保留")
        if category not in CATEGORIES:
            print(f"保留: {e['term']}（分類: {category}）")
            continue
        print(f"{e['term']} → {category}")
        if not args.dry_run:
            text = move_entry(text, e["block"], category)
        moved += 1

    if args.dry_run:
        print(f"--dry-run: {moved} 語を移動予定（書き込みなし）")
        return 0
    if moved:
        GLOSSARY.write_text(text, encoding="utf-8")
        print(f"{moved} 語を移動しました。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
