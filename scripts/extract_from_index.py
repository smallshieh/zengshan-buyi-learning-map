import json
import argparse
from pathlib import Path
import re
import subprocess
import urllib.request

# Configuration
BASE_DIR = Path(__file__).resolve().parent.parent
CHAPTERS_DIR = BASE_DIR / "reference" / "chapters"
TABLE_OF_CONTENTS = BASE_DIR / "reference" / "keyword_index.json"
CASES_DIR = BASE_DIR / "cases"
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "deepseek-r1:latest" # Updated to available model

SYSTEM_PROMPT = """你是一個專業的《增刪卜易》卦例整理助手。
請閱讀以下章節內容，找出其中的「卦例」（通常包含年月、問事、卦象、斷語）。
請將每個卦例轉換為 Markdown 格式，並以 JSON 陣列回傳。
務必只回傳 JSON 格式，不要包含其他解釋文字。

JSON 格式要求：
[
  {
    "filename": "case_new_category_brief_desc.md",
    "content": "..."
  }
]
"""

def load_index():
    with open(TABLE_OF_CONTENTS, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_cases_from_text(chapter_name, text, category="General"):
    """使用 Codex CLI 從文字中抽取卦例"""
    prompt = f"請從以下《增刪卜易》的章節中提取卦例。類別：{category}。\n\n章節內容：\n{text[:15000]}" # Limit context
    full_prompt = SYSTEM_PROMPT + "\n\n" + prompt

    try:
        # 使用 Codex CLI (與 process_book.py 相同的邏輯)
        result = subprocess.run(
            ["codex", "exec"],
            input=full_prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            shell=True
        )

        if result.returncode == 0:
            output = result.stdout.strip()
            # Robust JSON extraction
            start_idx = output.find('[')
            end_idx = output.rfind(']')
            
            if start_idx != -1 and end_idx != -1:
                json_str = output[start_idx:end_idx+1]
                return json.loads(json_str)
            else:
                print(f"    [Warning] No JSON found in Codex output for {chapter_name}")
                return []
        else:
            print(f"    [Error] Codex failed: {result.stderr}")
            return []

    except Exception as e:
        print(f"Error extracting from {chapter_name}: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description="RAG Extraction")
    parser.add_argument("categories", nargs="+", help="Categories to extract (e.g. 失物 天時)")
    args = parser.parse_args()

    index = load_index()
    if not CASES_DIR.exists(): CASES_DIR.mkdir()

    for cat in args.categories:
        if cat not in index:
            print(f"Category '{cat}' not found in index.")
            continue
        
        print(f"--- Processing Category: {cat} ---")
        chapters = index[cat]
        print(f"Found {len(chapters)} relevant chapters.")
        
        for chap_file in chapters:
            chap_path = CHAPTERS_DIR / chap_file
            if not chap_path.exists(): continue
            
            print(f"Reading {chap_file}...")
            with open(chap_path, "r", encoding="utf-8") as f:
                text = f.read()
            
            # Simple heuristic: Only process if it likely contains cases (keyword search for common case markers?)
            # But "Keyword Index" already filters for topic.
            
            extracted_items = extract_cases_from_text(chap_file, text, cat)
            
            if extracted_items:
                print(f"  > Extracted {len(extracted_items)} cases.")
                for item in extracted_items:
                    fname = item.get("filename", "temp.md")
                    # Clean filename
                    fname = re.sub(r'[\\/*?:"<>|]', "", fname) 
                    fname = f"case_new_{cat}_{fname}" # Force prefix
                    
                    out_path = CASES_DIR / fname
                    with open(out_path, "w", encoding="utf-8") as out_f:
                        out_f.write(item.get("content", ""))
                    print(f"    Saved: {fname}")
            else:
                print("  > No cases found.")

if __name__ == "__main__":
    main()
