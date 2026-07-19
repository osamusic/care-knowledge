#!/usr/bin/env python3
"""care-news の日報から「きょうのことば」を抽出し、用語集に未収録の語を追記する。

使い方:
    python3 scripts/update_glossary.py [--news-dir ../care-news] [--dry-run]

- care-news/content/posts/yorisoi-*.md の「## きょうのことば」を全記事から抽出
- 用語集 (content/glossary.md) にある語（表記ゆれは括弧内の別名も含めて比較）は除外
- 新しい語は「## 新着のことば」セクションに出典リンク付きで追記する（冪等）
"""

import argparse
import re
import sys
from pathlib import Path

NEWS_SITE_URL = "https://yorisoi-news.osamusic.org"
NEW_SECTION_HEADER = "## 新着のことば"
NEW_SECTION_INTRO = (
    f"[Yorisoi Daily]({NEWS_SITE_URL}/) の「きょうのことば」から自動で追加された用語です。"
    "整理のうえ、順次下のカテゴリーへ移していきます。"
)


def name_tokens(name: str) -> set[str]:
    """用語名を比較用トークンに分解する。「MCI（軽度認知障害）」→ {mci, 軽度認知障害}"""
    tokens = set()
    for part in re.split(r"[（）()]", name):
        part = re.sub(r"[\s・、〜～:：]", "", part).lower()
        if part:
            tokens.add(part)
    return tokens


def existing_tokens(glossary_text: str) -> set[str]:
    """用語集内の定義語（行頭の **語**）からトークン集合を作る。"""
    tokens = set()
    for m in re.finditer(r"^\*\*(.+?)\*\*\s*$", glossary_text, re.M):
        tokens |= name_tokens(m.group(1))
    return tokens


def parse_post(path: Path) -> tuple[str, str, list[tuple[str, str]]]:
    """記事から (タイトル, URL, [(用語, 説明), ...]) を返す。"""
    text = path.read_text(encoding="utf-8")
    title_m = re.search(r'^title:\s*"(.+?)"', text, re.M)
    title = title_m.group(1) if title_m else path.stem
    url = f"{NEWS_SITE_URL}/posts/{path.stem}/"

    section_m = re.search(r"^## きょうのことば\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not section_m:
        return title, url, []

    entries = []
    lines = section_m.group(1).splitlines()
    i = 0
    while i < len(lines):
        m = re.match(r"^\*\*(.+?)\*\*\s*(.*)$", lines[i])
        if not m:
            i += 1
            continue
        # care-news 側は「**用語:** 説明」形式のことがあり、コロンが太字内に残る
        term, definition = m.group(1).strip().rstrip(":："), m.group(2).strip()
        i += 1
        if not definition:
            # 用語だけの行: 続く行を空行または次の用語まで説明として読む
            parts = []
            while i < len(lines):
                line = lines[i].strip()
                if not line or line.startswith("**"):
                    break
                parts.append(line)
                i += 1
            definition = " ".join(parts)
        if definition:
            entries.append((term, definition))
    return title, url, entries


def insert_new_section(glossary_text: str) -> str:
    """「## 新着のことば」セクションがなければ最初の ## の前に挿入する。"""
    if re.search(rf"^{re.escape(NEW_SECTION_HEADER)}\s*$", glossary_text, re.M):
        return glossary_text
    block = f"{NEW_SECTION_HEADER}\n\n{NEW_SECTION_INTRO}\n\n"
    m = re.search(r"^## ", glossary_text, re.M)
    pos = m.start() if m else len(glossary_text)
    return glossary_text[:pos] + block + glossary_text[pos:]


def append_entries(glossary_text: str, formatted: list[str]) -> str:
    """新着セクションの末尾（次の ## の直前）にエントリを追記する。"""
    header_m = re.search(rf"^{re.escape(NEW_SECTION_HEADER)}\s*$", glossary_text, re.M)
    next_m = re.search(r"^## ", glossary_text[header_m.end():], re.M)
    pos = header_m.end() + (next_m.start() if next_m else len(glossary_text) - header_m.end())
    body = "".join(f"{e}\n\n" for e in formatted)
    return glossary_text[:pos] + body + glossary_text[pos:]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--news-dir", default="../care-news", help="care-news リポジトリのパス")
    parser.add_argument("--glossary", default=None, help="用語集ファイル（既定: リポジトリの content/glossary.md）")
    parser.add_argument("--dry-run", action="store_true", help="書き込まずに追加予定の語を表示")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    glossary_path = Path(args.glossary) if args.glossary else repo_root / "content" / "glossary.md"
    posts_dir = Path(args.news_dir) / "content" / "posts"
    if not posts_dir.is_dir():
        print(f"エラー: 記事ディレクトリが見つかりません: {posts_dir}", file=sys.stderr)
        return 1

    glossary_text = glossary_path.read_text(encoding="utf-8")
    known = existing_tokens(glossary_text)

    new_entries = []
    for post in sorted(posts_dir.glob("yorisoi-*.md")):
        title, url, entries = parse_post(post)
        for term, definition in entries:
            toks = name_tokens(term)
            if toks & known:
                continue
            known |= toks
            new_entries.append(f"**{term}**\n: {definition} —— [{title}]({url})")
            print(f"追加: {term}  ({post.name})")

    if not new_entries:
        print("新しい用語はありません。")
        return 0

    glossary_text = insert_new_section(glossary_text)
    glossary_text = append_entries(glossary_text, new_entries)

    if args.dry_run:
        print(f"--dry-run: {len(new_entries)} 語を追加予定（書き込みなし）")
        return 0

    glossary_path.write_text(glossary_text, encoding="utf-8")
    print(f"{len(new_entries)} 語を {glossary_path} に追加しました。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
