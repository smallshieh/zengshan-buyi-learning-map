# 專案規範總清單 (Project Laws)

## ⚖️ 核心律法
1. **單一真理來源**：所有卦例數據以 [data/guali_db.json](file:///c:/Users/smallshieh/Obsidian筆記/data/guali_db.json) 為準。
2. **AI 行為限制**：AI 代理人必須遵循 [.agent/instructions.md](file:///c:/Users/smallshieh/Obsidian筆記/.agent/instructions.md) 內的指令。
3. **語言規範**：Git Commit 與核心文檔優先使用 **繁體中文**。
4. **檔案命名規範 (Naming Convention)**：
   - **卦例檔案**：必須嚴格遵循 `case_{03d}_{description}.md` 格式（如 `case_025_占遠行求財.md`）。
   - **禁止事項**：禁止使用 `case_new_`、`temp_` 或純數字作為永久檔名。
   - **執行工具**：所有新建立的卦例必須執行 `scripts/refactor_cases.py` 進行標準化與編號重排。

## 📂 維護手冊
- **功能開發/架構說明**：參閱 [project_management/AGENTS.md](file:///c:/Users/smallshieh/Obsidian筆記/project_management/AGENTS.md)
- **自動化腳本**：存放於 [scripts/](file:///c:/Users/smallshieh/Obsidian筆記/scripts/)
- **AI 提取模組**：存放於 [prompts/](file:///c:/Users/smallshieh/Obsidian筆記/prompts/)

---
*本文件為專案最高準則，修改需經由專案負責人確認。*
