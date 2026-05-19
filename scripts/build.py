#!/usr/bin/env python3
"""Gemini出力(Markdown)からHTMLページを生成し、index.htmlを更新する"""

import sys
import os
import re
import json
from datetime import datetime

THEME_COLORS = {
    "AI・テクノロジーニュース":      "#6366f1",
    "動物・獣医業界のDX":            "#10b981",
    "SaaS・カスタマーサクセス":      "#f59e0b",
    "海外農業・畜産テクノロジー":    "#3b82f6",
    "キャリア・自己成長":            "#ec4899",
    "英語・グローバルキャリア":      "#8b5cf6",
    "メンタルヘルス・習慣・生産性":  "#14b8a6",
}

THEME_ICONS = {
    "AI・テクノロジーニュース":      "🤖",
    "動物・獣医業界のDX":            "🐾",
    "SaaS・カスタマーサクセス":      "📊",
    "海外農業・畜産テクノロジー":    "🌾",
    "キャリア・自己成長":            "🚀",
    "英語・グローバルキャリア":      "🌍",
    "メンタルヘルス・習慣・生産性":  "🧘",
}


def md_to_html(text: str) -> str:
    lines = text.split("\n")
    out = []
    in_ul = False

    for line in lines:
        # h3
        if line.startswith("### "):
            if in_ul:
                out.append("</ul>"); in_ul = False
            out.append(f'<h3>{escape(line[4:])}</h3>')
        # h2
        elif line.startswith("## "):
            if in_ul:
                out.append("</ul>"); in_ul = False
            out.append(f'<h2>{escape(line[3:])}</h2>')
        # h1 (skip — used as page title)
        elif line.startswith("# "):
            pass
        # list item
        elif line.startswith("- ") or line.startswith("* "):
            if not in_ul:
                out.append("<ul>"); in_ul = True
            out.append(f'<li>{inline_md(line[2:])}</li>')
        # blank line
        elif line.strip() == "":
            if in_ul:
                out.append("</ul>"); in_ul = False
            out.append("")
        # normal paragraph
        else:
            if in_ul:
                out.append("</ul>"); in_ul = False
            out.append(f'<p>{inline_md(line)}</p>')

    if in_ul:
        out.append("</ul>")
    return "\n".join(out)


def inline_md(text: str) -> str:
    # links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
                  r'<a href="\2" target="_blank" rel="noopener">\1</a>', text)
    # bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    return text


def escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_entry_page(md_content: str, theme: str, date: str) -> str:
    color = THEME_COLORS.get(theme, "#6366f1")
    icon = THEME_ICONS.get(theme, "📌")
    body_html = md_to_html(md_content)
    dt = datetime.strptime(date, "%Y-%m-%d")
    date_jp = dt.strftime("%Y年%-m月%-d日")

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{icon} {theme} — {date_jp}</title>
<link rel="stylesheet" href="../style.css">
<style>:root {{ --accent: {color}; }}</style>
</head>
<body>
<header>
  <a href="../index.html" class="back">← 一覧へ</a>
  <div class="theme-badge" style="background:{color}">{icon} {theme}</div>
  <time>{date_jp}</time>
</header>
<main class="entry-body">
{body_html}
</main>
<footer>
  <p>Powered by Gemini CLI × はせぴょんデイリーリサーチ</p>
</footer>
</body>
</html>"""


def update_index(public_dir: str, theme: str, date: str):
    dt = datetime.strptime(date, "%Y-%m-%d")
    date_jp = dt.strftime("%Y年%-m月%-d日")
    color = THEME_COLORS.get(theme, "#6366f1")
    icon = THEME_ICONS.get(theme, "📌")
    entry_path = f"entries/{date}.html"

    index_path = os.path.join(public_dir, "index.html")

    new_card = f"""      <a class="card" href="{entry_path}" style="--card-accent:{color}">
        <span class="card-icon">{icon}</span>
        <span class="card-theme">{theme}</span>
        <time class="card-date">{date_jp}</time>
      </a>"""

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 同じ日付のカードがあれば置き換え、なければ先頭に追加
    pattern = rf'<a class="card"[^>]+href="{re.escape(entry_path)}".*?</a>'
    if re.search(pattern, html, re.DOTALL):
        html = re.sub(pattern, new_card, html, flags=re.DOTALL)
    else:
        html = html.replace("<!-- ENTRIES_START -->",
                            f"<!-- ENTRIES_START -->\n{new_card}")

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    if len(sys.argv) < 5:
        print("Usage: build.py <md_file> <theme> <date> <project_dir>")
        sys.exit(1)

    md_file, theme, date, project_dir = sys.argv[1:5]
    public_dir = os.path.join(project_dir, "public")
    entries_dir = os.path.join(public_dir, "entries")
    os.makedirs(entries_dir, exist_ok=True)

    with open(md_file, "r", encoding="utf-8") as f:
        md_content = f.read()

    html = build_entry_page(md_content, theme, date)
    out_path = os.path.join(entries_dir, f"{date}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  → {out_path}")

    update_index(public_dir, theme, date)
    print(f"  → index.html 更新完了")


if __name__ == "__main__":
    main()
