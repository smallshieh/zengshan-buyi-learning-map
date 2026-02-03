import os
import sys

# --- Templates ---

GLOBAL_PROFILE = """# Antigravity 全域記憶錨點 (Global Profile)

## 👤 使用者核心價值與目標
*   **目標**：透過 AI 輔助，將傳統技藝（如氣功、太極）科學化、現代化，並建立高效的自動化工作流。
*   **溝通偏好**：專業、冷靜、客觀，偏好繁體中文（台灣），技術名詞可保留英文。
*   **關鍵原則**：拒絕幻覺，精準優先，注重邏輯一致性。

## 📁 專案索引
(請在此更新您的專案路徑)

## 🛠️ 共用技術棧
*   **AI 平台**：Ollama (本地運行)
*   **生圖工具**：Stable Diffusion / Krita AI Diffusion
*   **開發語言**：Python, PowerShell
*   **筆記系統**：Obsidian (Markdown)
"""

PROJECT_PROFILE_IMAGE = """# 專案記憶：Kritra 放大參數 (影像處理)

## 🎯 專案目標
*   自動化整理 Krita 生成的圖像及其對應的 Prompt 與參數 (json/txt)。
*   建立標準化的目錄結構以便於後續放大 (Upscaling) 參考。

## ⌨️ 技術細節與偏好
*   **主要工具**：Python (用於檔案組織), Krita AI Diffusion (用於生圖)。
*   **檔案結構**：`YYYYMMDD_Subject/` 格式。
"""

PROJECT_PROFILE_OBSIDIAN = """# 專案記憶：Obsidian 寫作筆記 (auto_writor)

## 🎯 專案目標
*   將傳統氣功、太極拳心法轉譯為「生物力學」與「物理學」語言。
*   維護高品質的 Obsidian 筆記庫與 Facebook 粉專文章。

## ✍️ 寫作風格定錨
*   **導師**：強調科學實驗精神。
*   **風格規範**：參考 `Writing_Style_Catalog.md` 中的四大模式。
"""

WORKFLOW_SOP = """# 標準作業程序 (SOP)：工作流引導

## 🛠️ 開發與自動化工作流
1.  **探索 (Explore)** -> 2. **計畫 (Plan)** -> 3. **執行 (Execute)** -> 4. **驗證 (Verify)** -> 5. **紀錄 (Document)**

## ✍️ 寫作與筆記工作流
1.  **定錨 (Anchor)** -> 2. **草擬 (Draft)** -> 3. **科學化檢驗 (Scientific Check)** -> 4. **連結 (Link)** -> 5. **優化 (Polish)**
"""

EXPERT_ROLES = """# 智能任務路由：專家身分定義 (Expert Roles)

## 🎨 圖像自動化專家 (Image Specialist)
*   精確度、JSON 規範、Python 腳本優先。

## 📚 Obsidian 知識管理員 (Obsidian Librarian)
*   深度觀點、連結思維、科學轉譯。
"""

def setup():
    print("🚀 Antigravity 記憶系統啟動器")
    print("-" * 30)
    
    target_dir = os.getcwd()
    gemini_dir = os.path.join(target_dir, ".gemini")
    
    if not os.path.exists(gemini_dir):
        os.makedirs(gemini_dir)
        print(f"✅ 已建立目錄: {gemini_dir}")
    else:
        print(f"ℹ️ {gemini_dir} 已存在。")

    # 選項
    print("\n請選擇此專案的專家身分:")
    print("1. 圖像自動化專家 (Krita/Python)")
    print("2. Obsidian 知識管理員 (寫作/研究)")
    print("3. 兩者皆是")
    
    choice = input("請輸入數字 (1-3): ")
    
    # 寫入檔案
    files = {
        "global_profile.md": GLOBAL_PROFILE,
        "workflow_sop.md": WORKFLOW_SOP,
        "expert_roles.md": EXPERT_ROLES
    }
    
    if choice == '1':
        files["project_profile.md"] = PROJECT_PROFILE_IMAGE
    elif choice == '2':
        files["project_profile.md"] = PROJECT_PROFILE_OBSIDIAN
    else:
        files["project_profile.md"] = PROJECT_PROFILE_IMAGE + "\n\n" + PROJECT_PROFILE_OBSIDIAN

    for filename, content in files.items():
        filepath = os.path.join(gemini_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"📝 已生成: {filename}")

    print("\n" + "-" * 30)
    print("✨ 部署完成！Antigravity 現在已具備專案覺察能力。")

if __name__ == "__main__":
    setup()
