#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
連結更新腳本
更新所有指向舊資料夾名稱的連結(去除「占」字)
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

# ==================== 配置 ====================
BASE_DIR = Path(r"c:\Users\smallshieh\Obsidian筆記")

# 資料夾重命名對照表(舊名稱 → 新名稱)
FOLDER_RENAME_MAP = {
    "占僕何日回": "僕何日回",
    "占兄病": "兄病",
    "占出門": "出門",
    "占升遷": "升遷",
    "占南行": "南行",
    "占壽元": "壽元",
    "占夢": "夢",
    "占女痘": "女痘",
    "占妹臨產": "妹臨產",
    "占妻病": "妻病",
    "占家宅吉凶": "家宅吉凶",
    "占將來有官": "將來有官",
    "占延師": "延師",
    "占弟被訟": "弟被訟",
    "占後遇功名": "後遇功名",
    "占悔婚": "悔婚",
    "占掣簽": "掣簽",
    "占會試": "會試",
    "占求婚": "求婚",
    "占求財": "求財",
    "占父何日歸": "父何日歸",
    "占父病": "父病",
    "占生產": "生產",
    "占產期": "產期",
    "占索債": "索債",
    "占終身功名": "終身功名",
    "占終身財福": "終身財福",
    "占自陳": "自陳",
    "占舟行": "舟行",
    "占謁貴": "謁貴",
    "占買賣六畜": "買賣六畜",
    "占迎父": "迎父",
    "占遠行求財": "遠行求財",
    "占遷居": "遷居",
    "占鄉試": "鄉試",
    "占開鋪面": "開鋪面",
    "占風水": "風水",
}

# ==================== 連結更新函數 ====================
def update_links_in_content(content: str) -> Tuple[str, int]:
    """更新內容中的連結"""
    updated_content = content
    changes_count = 0
    
    # 更新 Obsidian 連結格式: [[path/to/file]]
    for old_name, new_name in FOLDER_RENAME_MAP.items():
        # 匹配 cases/占XX/ 格式的連結
        pattern1 = re.compile(rf'\[\[cases/{re.escape(old_name)}/')
        if pattern1.search(updated_content):
            updated_content = pattern1.sub(f'[[cases/{new_name}/', updated_content)
            changes_count += len(pattern1.findall(content))
        
        # 匹配 ../占XX/ 格式的相對路徑
        pattern2 = re.compile(rf'\.\./\.\./cases/{re.escape(old_name)}/')
        if pattern2.search(updated_content):
            updated_content = pattern2.sub(f'../../cases/{new_name}/', updated_content)
            changes_count += len(pattern2.findall(content))
        
        # 匹配 ../占XX/ 格式的相對路徑(單層)
        pattern3 = re.compile(rf'\.\.\/{re.escape(old_name)}/')
        if pattern3.search(updated_content):
            updated_content = pattern3.sub(f'../{new_name}/', updated_content)
            changes_count += len(pattern3.findall(content))
    
    return updated_content, changes_count

def update_file(file_path: Path, dry_run: bool = False) -> Dict:
    """更新單個檔案中的連結"""
    result = {
        'file': str(file_path.relative_to(BASE_DIR)),
        'changes': 0,
        'success': False,
        'error': None
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        updated_content, changes_count = update_links_in_content(original_content)
        
        if changes_count > 0:
            result['changes'] = changes_count
            
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
        
        result['success'] = True
        
    except Exception as e:
        result['error'] = str(e)
    
    return result

# ==================== 主程式 ====================
def main(dry_run: bool = False):
    """主執行流程"""
    print("=" * 60)
    print("連結更新腳本 - 資料夾重命名後")
    print("=" * 60)
    
    if dry_run:
        print("\n⚠️  DRY RUN 模式:不會實際修改檔案\n")
    
    # 收集所有 .md 檔案
    print("📂 掃描所有 Markdown 檔案...")
    md_files = list(BASE_DIR.rglob("*.md"))
    print(f"   找到 {len(md_files)} 個檔案\n")
    
    print("=" * 60)
    print("開始更新連結...")
    print("=" * 60 + "\n")
    
    results = []
    total_changes = 0
    
    for file_path in md_files:
        result = update_file(file_path, dry_run)
        
        if result['changes'] > 0:
            results.append(result)
            total_changes += result['changes']
            print(f"  ✏️  {result['file']}")
            print(f"      更新 {result['changes']} 個連結")
        
        if result['error']:
            print(f"  ❌ {result['file']}")
            print(f"      錯誤: {result['error']}")
    
    # 統計報告
    print("\n" + "=" * 60)
    print("更新報告")
    print("=" * 60)
    
    print(f"\n掃描檔案: {len(md_files)}")
    print(f"修改檔案: {len(results)}")
    print(f"更新連結: {total_changes}")
    
    if dry_run:
        print("\n💡 這是 DRY RUN,實際檔案未被修改")
        print("   若要執行實際更新,請使用: python update_links.py --commit")
    else:
        print("\n💾 已完成所有連結更新")
        print("   建議執行: git diff 查看變更")
    
    print("=" * 60)
    
    # 儲存報告
    report_path = BASE_DIR / "link_update_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("連結更新報告\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"掃描檔案: {len(md_files)}\n")
        f.write(f"修改檔案: {len(results)}\n")
        f.write(f"更新連結: {total_changes}\n\n")
        
        if results:
            f.write("修改的檔案:\n")
            for result in results:
                f.write(f"\n{result['file']}\n")
                f.write(f"  更新連結數: {result['changes']}\n")
    
    print(f"\n💾 報告已儲存至: {report_path}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='更新資料夾重命名後的連結')
    parser.add_argument('--dry-run', action='store_true', help='模擬執行,不實際修改檔案')
    parser.add_argument('--commit', action='store_true', help='執行實際更新')
    
    args = parser.parse_args()
    
    # 預設為 dry run(安全起見)
    if args.commit:
        main(dry_run=False)
    else:
        main(dry_run=True)
