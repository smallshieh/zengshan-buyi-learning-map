# Scripts 工具說明

## 核心工具 (保留)

### 連結管理
- `verify_links.py` - 驗證連結有效性,支持抽樣檢查
- `update_links.py` - 通用連結更新工具
- `fix_links.py` - 修復特定連結問題

### 資料夾管理
- (已整合到一次性操作中,未來需要時現場創建)

### 知識庫
- `build_knowledge_index.py` - 建立知識索引
- `link_knowledge.py` - 知識連結工具
- `process_book.py` - 書籍處理

### 資料處理
- `extract_from_index.py` - 從索引提取內容
- `sync_json_to_md.py` - JSON 與 Markdown 同步
- `repair_db_paths.py` - 修復資料庫路徑

### 其他工具
- `split_chapters.py` - 章節分割
- `validate_standards.py` - 標準驗證
- `debug_read.py` - 除錯工具
- `extract_batch2.py` - 批次提取
- `search_batch2.py` - 批次搜尋

## 已刪除

### 重複版本
- ~~rename_folders_v2.py~~
- ~~debug_read_v2.py~~
- ~~extract_batch2_v2.py~~
- ~~search_batch2_v2.py~~

### 重複的連結工具
- ~~update_all_links.py~~
- ~~update_links_final.py~~
- ~~fix_readme_links.py~~
- ~~check_links.py~~
- ~~validate_links.py~~

### 一次性腳本
- ~~force_move.py~~
- ~~cleanup_categories.py~~
- ~~refactor_cases.py~~
- ~~analyze_folders.py~~
- ~~check_case_classification.py~~
- ~~merge_folders.py~~
- ~~move_cases.py~~
- ~~rename_folders.py~~

## 使用建議

**連結驗證**:
```bash
python scripts\verify_links.py --sample 30
```

**連結更新** (需要配置 FOLDER_MAPPINGS):
```bash
python scripts\update_links.py --dry-run
python scripts\update_links.py --commit
```

**知識索引**:
```bash
python scripts\build_knowledge_index.py
```
