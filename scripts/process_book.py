import os
import json
import subprocess
import re
import urllib.request
import hashlib
from pathlib import Path

# --- 設定路徑 ---
BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_FILE = BASE_DIR / "prompts" / "extract_case.md"
TARGET_DIR = BASE_DIR / "cases"
OUTPUT_DIR = BASE_DIR / "data"
OUTPUT_FILE = OUTPUT_DIR / "guali_db.json"
CACHE_FILE = OUTPUT_DIR / ".processing_cache.json"

# --- 效能與備援設定 ---
BATCH_SIZE = 3  # 一次處理 3 本卦例以節省 Token，平衡穩定性與效率
OLLAMA_MODEL = "huihui_ai/deepseek-r1-abliterated:32b"
OLLAMA_API_URL = "http://localhost:11434/api/generate"

def get_clean_prompt():
    """讀取提示詞並過濾掉僅供人讀取的註解"""
    try:
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            text = f.read()
        # 移除 [//]: # (註解) 格式的內容
        return re.sub(r'\[\/\/\]: # \(.*?\)\n?', '', text)
    except Exception as e:
        print(f"讀取提示詞失敗: {e}")
        return ""

def run_codex_extraction(full_prompt):
    """呼叫 Codex CLI 進行抽取"""
    try:
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
            # 尋找 JSON 區塊 ([ or {)
            start_idx = -1
            for char in ['[', '{']:
                idx = output.find(char)
                if idx != -1 and (start_idx == -1 or idx < start_idx):
                    start_idx = idx
            
            end_idx = -1
            for char in [']', '}']:
                idx = output.rfind(char)
                if idx != -1 and (end_idx == -1 or idx > end_idx):
                    end_idx = idx

            if start_idx != -1 and end_idx != -1:
                json_str = output[start_idx:end_idx+1]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    print(f"\nJSON 解析失敗: {e}")
        else:
            stderr = result.stderr.lower()
            if "usage limit" in stderr or "hit your usage limit" in stderr:
                return "LIMIT_HIT"
            print(f"\nCodex 執行錯誤: {result.stderr}")
    except Exception as e:
        print(f"Codex 處理出錯: {e}")
    return None

def run_ollama_extraction(full_prompt):
    """呼叫本地 Ollama 備援引擎"""
    print(f" -> 使用備援引擎 (Ollama: {OLLAMA_MODEL})...")
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": full_prompt,
            "stream": False,
            "keep_alive": 0,
            "format": "json"
        }
        
        data = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        req = urllib.request.Request(OLLAMA_API_URL, data=data, headers=headers)
        
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            res_json = json.loads(res_body)
            response_text = res_json.get("response", "").strip()
            
            start_idx = -1
            for char in ['[', '{']:
                idx = response_text.find(char)
                if idx != -1 and (start_idx == -1 or idx < start_idx):
                    start_idx = idx
            
            end_idx = -1
            for char in [']', '}']:
                idx = response_text.rfind(char)
                if idx != -1 and (end_idx == -1 or idx > end_idx):
                    end_idx = idx

            if start_idx != -1 and end_idx != -1:
                return json.loads(response_text[start_idx:end_idx+1])
    except Exception as e:
        print(f"\nOllama 備援失敗: {e}")
    return None

def load_existing_data(file_path):
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except: pass
    return []

def save_data(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_file_hash(file_path):
    """計算檔案內容的 SHA256 雜湊值"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def load_cache():
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {}

def save_cache_file(cache_data):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, indent=2)

def main():
    if not OUTPUT_DIR.exists(): OUTPUT_DIR.mkdir()
    all_data = load_existing_data(OUTPUT_FILE)
    processed_files = {item["_source_file"] for item in all_data if "_source_file" in item}
    
    md_files = [f for f in TARGET_DIR.rglob("*.md") if f.name.lower() != "readme.md"]
    pending_files = [f for f in md_files if str(f.relative_to(BASE_DIR)) not in processed_files]
    
    print(f"找到 {len(md_files)} 個檔案。已處理: {len(processed_files)}。待處理: {len(pending_files)}")
    
    # --- 優化: 檢查雜湊快取 ---
    cache = load_cache()
    files_to_process = []
    
    print("正在比對雜湊快取...")
    for f in pending_files:
        rel_path = str(f.relative_to(BASE_DIR))
        current_hash = get_file_hash(f)
        
        # 如果快取中有紀錄且雜湊值相同，則跳過 (視為已處理/無變化)
        if rel_path in cache and cache[rel_path] == current_hash:
            continue
            
        files_to_process.append(f)
    
    print(f"快取比對後，實際需處理: {len(files_to_process)} 個檔案 (節省: {len(pending_files) - len(files_to_process)})")
    
    if not files_to_process: return
    pending_files = files_to_process # 更新待處理清單


    system_prompt = get_clean_prompt()

    # 按 BATCH_SIZE 分組處理
    i = 0
    while i < len(pending_files):
        # 決定當前批次的大小 (預設先用 Codex 的 BATCH_SIZE = 5)
        current_batch_size = 5
        batch = pending_files[i:i + current_batch_size]
        
        print(f"\n[進度 {i+1}/{len(pending_files)}] 正在嘗試處理 {len(batch)} 個檔案 (以 Codex 優先)...")
        
        # 組合批次文本
        combined_text = ""
        batch_meta = []
        for idx, f_path in enumerate(batch):
            rel_path = str(f_path.relative_to(BASE_DIR))
            with open(f_path, "r", encoding="utf-8") as f:
                content = f.read()
            combined_text += f"\n--- 資料 {idx+1}: {f_path.name} ---\n{content}\n"
            batch_meta.append({"rel_path": rel_path})

        full_prompt = f"{system_prompt}\n\n請依次抽取以下 {len(batch)} 個卦例文本，並輸出一個 JSON 陣列：\n{combined_text}"
        
        # 1. 嘗試 Codex
        result = run_codex_extraction(full_prompt)
        
        if result == "LIMIT_HIT":
            # 2. 如果 Codex 限流，改用 Ollama (一次處理 1 個以確保穩定)
            print(" -> Codex 限流。改用 Ollama 逐一處理...")
            for f_path in batch:
                rel_path = str(f_path.relative_to(BASE_DIR))
                with open(f_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                ollama_prompt = f"{system_prompt}\n\n請抽取以下文本：\n{content}"
                res_ollama = run_ollama_extraction(ollama_prompt)
                
                if res_ollama and isinstance(res_ollama, dict):
                    res_ollama["_source_file"] = rel_path
                    res_ollama["_ai_model"] = f"Ollama ({OLLAMA_MODEL})"
                    all_data.append(res_ollama)
                    save_data(OUTPUT_FILE, all_data)
                    # 更新快取
                    cache[rel_path] = get_file_hash(f_path)
                    save_cache_file(cache)
                    print(f" -> {f_path.name} 抽取成功 (Ollama)。")
            i += len(batch)
            continue
        
        # 3. 處理 Codex 成功獲取的資料
        if isinstance(result, list) and len(result) == len(batch):
            for idx, extracted_item in enumerate(result):
                extracted_item["_source_file"] = batch_meta[idx]["rel_path"]
                extracted_item["_ai_model"] = "OpenAI Codex"
                all_data.append(extracted_item)
            save_data(OUTPUT_FILE, all_data)
            
            # 更新批次快取
            for idx, item in enumerate(batch_meta):
                f_path = BASE_DIR / item["rel_path"]
                if f_path.exists():
                    cache[item["rel_path"]] = get_file_hash(f_path)
            save_cache_file(cache)
            
            print(f" -> 批次處理成功 (Codex)。已累計: {len(all_data)} 筆。")
            i += len(batch)
        else:
            # 如果 Codex 批次失敗，可能是格式問題，嘗試降級為逐一處理
            print(" -> [!] 批次結果格式不符。嘗試逐一使用 Codex 處理...")
            for f_path in batch:
                rel_path = str(f_path.relative_to(BASE_DIR))
                with open(f_path, "r", encoding="utf-8") as f:
                    content = f.read()
                single_prompt = f"{system_prompt}\n\n請抽取以下文本：\n{content}"
                res_single = run_codex_extraction(single_prompt)
                
                if res_single == "LIMIT_HIT":
                    # 這裡如果還是 LIMIT_HIT 就跳出交給 Ollama 循環
                    i -= (len(batch) - batch.index(f_path)) # 回退進度
                    break 

                if res_single and isinstance(res_single, dict):
                    res_single["_source_file"] = rel_path
                    res_single["_ai_model"] = "OpenAI Codex"
                    all_data.append(res_single)
                    save_data(OUTPUT_FILE, all_data)
                    # 更新快取
                    cache[rel_path] = get_file_hash(f_path)
                    save_cache_file(cache)
                    print(f" -> {f_path.name} 抽取成功 (Codex Single)。")
            i += len(batch)

    print(f"\n處理結束！資料庫更新至: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
