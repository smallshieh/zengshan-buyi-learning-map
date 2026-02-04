import json
import os
from pathlib import Path

BASE_DIR = Path(r"c:\Users\smallshieh\Obsidian筆記")
DB_FILE = BASE_DIR / "data" / "guali_db.json"
CASES_DIR = BASE_DIR / "cases"

def sync_db_paths():
    if not DB_FILE.exists():
        print("Database not found.")
        return

    with open(DB_FILE, 'r', encoding='utf-8') as f:
        db_data = json.load(f)

    # 建立目前實體檔案的對應表 (用問事內容作為 key)
    # 或者用原始檔名。但最準確的是重新從 Markdown 提取。
    
    new_db = []
    processed_files = set()
    
    print(f"原始數據庫條目: {len(db_data)}")
    
    # 掃描目前的實體檔案
    for root, dirs, files in os.walk(CASES_DIR):
        for file in files:
            if not file.endswith(".md"): continue
            
            filepath = Path(root) / file
            rel_path = str(filepath.relative_to(BASE_DIR))
            
            # 從 Markdown 提取基本資訊以保持 JSON 同步
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 簡單提取問事與時間 (如果存在 YAML)
                import re
                q_match = re.search(r'question:\s*"(.*?)"', content)
                t_match = re.search(r'date_lunar:\s*"(.*?)"', content)
                q = q_match.group(1) if q_match else ""
                t = t_match.group(1) if t_match else ""
                
                # 在舊數據庫中尋找匹配項 (優先比對路徑，次之比對問事)
                match = None
                for entry in db_data:
                    # 如果路徑完全一樣，直接用
                    if entry.get("_source_file") == rel_path:
                        match = entry
                        break
                    # 如果問事跟時間一樣，可能是搬移過的
                    if entry.get("subject") == q and entry.get("time") == t:
                        match = entry
                        match["_source_file"] = rel_path
                        break
                
                if match:
                    new_db.append(match)
                else:
                    # 如果沒找到，可能需要重新提取 (這裡先標記為新檔案)
                    # 正常情況下 refactor 只是改名，內容不會變
                    pass
                
                processed_files.add(rel_path)
            except:
                continue

    print(f"更新後數據庫條目: {len(new_db)}")
    
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_db, f, ensure_ascii=False, indent=2)
    print("數據庫路徑已同步。")

if __name__ == "__main__":
    sync_db_paths()
