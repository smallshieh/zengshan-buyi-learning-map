#!/bin/bash

# 設定輸入與輸出目錄
INPUT_DIR="./legacy_docs"
OUTPUT_DIR="./obsidian_vault/Inbox"
PROMPT_FILE="./obsidian_refactor_prompt.md"

mkdir -p "$OUTPUT_DIR"

# 讀取提示詞模板
PROMPT_TEMPLATE=$(cat "$PROMPT_FILE")

# 迴圈處理每一個 .txt 檔案 (依需求可改為 .md 或其他格式)
for file in "$INPUT_DIR"/*.txt; do
    filename=$(basename "$file" .txt)
    content=$(cat "$file")
    
    echo "正在處理: $filename ..."
    
    # 組合提示詞與內容，並呼叫 gemini CLI
    # 注意：這裡假設 gemini cli 接受標準輸入或參數，請依您實際安裝的版本調整語法
    # 這裡示範將 prompt 與 content 拼貼後送出
    
    echo -e "$PROMPT_TEMPLATE\n\n$content" | gemini chat > "$OUTPUT_DIR/${filename}_v2.md"
    
    echo "✅ 已儲存: $OUTPUT_DIR/${filename}_v2.md"
    
    # 避免觸發 API Rate Limit，稍微暫停一下
    sleep 2
done