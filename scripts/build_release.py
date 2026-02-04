#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
發佈包構建腳本 (Release Builder)
功能：將專案打包為乾淨的 .zip 檔，供使用者下載
"""

import os
import shutil
import zipfile
import datetime
from pathlib import Path

# ==================== 配置 ====================
BASE_DIR = Path(r"c:\Users\smallshieh\Obsidian筆記")
OUTPUT_DIR = BASE_DIR / "releases"
RELEASE_PREFIX = "ZengShanBuYi_Obsidian_v"

# 排除清單 (黑名單)
EXCLUDES = [
    # 系統目錄
    ".git", ".gitignore", ".obsidian", ".agent", ".gemini", ".idea", ".vscode", "__pycache__",
    
    # 開發工具
    "scripts", "prompts", "config", "reports", "_protype",
    
    # 暫存區/快取
    "_release_staging",
    
    # 原始大型檔案 (如果不需要)
    #"legacy_docs", 
    
    # 特定檔案
    "implementation_plan.md", "task.md", "walkthrough.md",
    "link_verification_report.txt", "requirements.txt",
    "releases"
]

# 必須包含但可能被誤刪的 (白名單)
# (已移除：使用者要求排除 json)

# ==================== 建立 README_READER ====================
READER_README_CONTENT = """# 增刪卜易 - Obsidian 學習庫

歡迎使用《增刪卜易》結構化學習庫！

## 🚀 如何開始

1. **安裝 Obsidian**：請至 [Obsidian 官網](https://obsidian.md/) 下載並安裝。
2. **開啟儲存庫**：
   - 啟動 Obsidian
   - 選擇 "Open folder as vault" (開啟資料夾作為儲存庫)
   - 選擇本資料夾
3. **進入學習**：
   - 點擊左側檔案列表中的 `000_增刪卜易_學習地圖.md`
   - 跟隨導引開始閱讀

## 📚 內容結構

- **000_增刪卜易_學習地圖.md**：您的導航中心
- **theory/**：系統化的理論章節
- **cases/**：精選的實戰卦例
- **glossary/**：互動式術語詞彙表
- **reference/**：實用的速查表

## ✨ 特色

- **雙向連結**：點擊任何藍色連結即可跳轉相關知識
- **乾淨閱讀**：無程式碼、無複雜設定，專注於內容
- **離線可用**：所有資料皆在您的電腦上

---
*版本日期：{date}*
"""

def should_exclude(path: Path, base: Path) -> bool:
    """判斷路徑是否應該被排除"""
    try:
        rel_path = path.relative_to(base)
    except ValueError:
        return True
        
    parts = rel_path.parts
    
    if not parts:
        return False
        
    # 針對根目錄本身的處理 (如果是 '.')
    if parts[0] == '.':
        return False
    
    # 檢查是否在排除清單中
    if parts[0] in EXCLUDES:
        return True
    
    # 檢查隱藏檔案
    if path.name.startswith("."):
        return True

    # 檢查檔案副檔名 (排除 .txt, .json, .py, .bat, .sh, .ps1)
    if path.is_file():
        if path.suffix.lower() in ['.txt', '.json', '.py', '.bat', '.sh', '.ps1']:
            return True
        
    return False

def create_release():
    """建立發佈包"""
    # 準備目錄
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir()
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    release_name = f"{RELEASE_PREFIX}{timestamp}"
    zip_filename = OUTPUT_DIR / f"{release_name}.zip"
    
    print(f"📦 開始構建發佈包: {release_name}")
    print(f"   來源: {BASE_DIR}")
    print(f"   目標: {zip_filename}")
    
    # 統計
    file_count = 0
    total_size = 0
    
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 遍歷目錄
            for root, dirs, files in os.walk(BASE_DIR):
                root_path = Path(root)
                
                # 排除目錄（原地修改 dirs 列表以剪枝）
                dirs[:] = [d for d in dirs if not should_exclude(root_path / d, BASE_DIR)]
                
                # 判斷當前目錄是否被排除
                if should_exclude(root_path, BASE_DIR):
                    continue
                
                for file in files:
                    file_path = root_path / file
                    
                    if should_exclude(file_path, BASE_DIR):
                        continue
                    
                    # 計算相對路徑作為 zip 內路徑
                    arcname = file_path.relative_to(BASE_DIR)
                    
                    # 寫入 zip
                    zf.write(file_path, arcname)
                    file_count += 1
                    total_size += file_path.stat().st_size
            
            # 寫入 README_READER.md
            readme_content = READER_README_CONTENT.format(date=timestamp)
            zf.writestr("README.md", readme_content)  # 覆蓋原本的開發者 README
            print("   📄 已寫入使用者版 README.md")
            
        print("\n✅ 發佈包構建成功！")
        print(f"   檔案數: {file_count}")
        print(f"   總大小: {total_size / 1024 / 1024:.2f} MB")
        print(f"   路徑: {zip_filename}")
        return True
        
    except Exception as e:
        print(f"\n❌ 建構失敗: {e}")
        return False

if __name__ == "__main__":
    create_release()
