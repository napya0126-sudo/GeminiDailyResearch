#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DATE=$(date +%Y-%m-%d)
DAY=$(date +%u)  # 1=Mon, 7=Sun

case $DAY in
  1) THEME="AI・テクノロジーニュース" ; THEME_EN="ai-tech" ;;
  2) THEME="動物・獣医業界のDX" ;       THEME_EN="animal-dx" ;;
  3) THEME="SaaS・カスタマーサクセス" ; THEME_EN="saas-cs" ;;
  4) THEME="海外農業・畜産テクノロジー" ; THEME_EN="agri-tech" ;;
  5) THEME="キャリア・自己成長" ;        THEME_EN="career" ;;
  6) THEME="英語・グローバルキャリア" ;  THEME_EN="english" ;;
  7) THEME="メンタルヘルス・習慣・生産性" ; THEME_EN="mental" ;;
esac

echo "📅 日付: $DATE"
echo "🔍 テーマ: $THEME"

PROMPT="あなたはリサーチアナリストです。今日のテーマ「${THEME}」について、最新情報をGoogle検索で調べ、日本語でレポートを作成してください。

以下のMarkdown形式のみで出力してください（前置き・後書き不要）：

# ${THEME}

## 概要
（200字程度で今日の全体的なトレンドを説明）

## 主要トピック

### 1. （トピックタイトル）
（詳細説明100〜200字）

### 2. （トピックタイトル）
（詳細説明100〜200字）

### 3. （トピックタイトル）
（詳細説明100〜200字）

### 4. （トピックタイトル）
（詳細説明100〜200字）

### 5. （トピックタイトル）
（詳細説明100〜200字）

## 今日のキーポイント
- キーポイント1
- キーポイント2
- キーポイント3

## 参考情報
（参考にしたURLや情報源があれば記載、なければ省略）"

echo "🤖 Geminiで検索中..."
RESULT=$(gemini -p "$PROMPT" --yolo -o text 2>/dev/null \
  | grep -v "^YOLO mode" \
  | grep -v "^Loaded cached" \
  | grep -v "^Warning")

if [ -z "$RESULT" ]; then
  echo "❌ Geminiの出力が空でした"
  exit 1
fi

RESULT_FILE="/tmp/gemini_result_${DATE}.md"
printf '%s' "$RESULT" > "$RESULT_FILE"

echo "✅ 検索完了（$(wc -c < "$RESULT_FILE") bytes）"
echo "📄 HTML生成中..."

python3 "$SCRIPT_DIR/build.py" "$RESULT_FILE" "$THEME" "$DATE" "$PROJECT_DIR"

echo "📤 Git push中..."
cd "$PROJECT_DIR"
git add public/
git diff --cached --quiet && echo "変更なし。スキップ。" && exit 0
git commit -m "Daily: ${THEME} (${DATE})"
git push

echo "🚀 Vercel自動デプロイ開始（GitHub連携済みの場合）"
