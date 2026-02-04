#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Obsidian 資料夾管理工具
統一處理資料夾的合併、重命名、移動等操作
"""

import argparse
import shutil
import yaml
from pathlib import Path
from typing import Dict, List, Optional
import re

BASE_DIR = Path(r"c:\Users\smallshieh\Obsidian筆記")
CONFIG_DIR = BASE_DIR / "config"

class FolderManager:
    def __init__(self, base_dir: Path = BASE_DIR):
        self.base_dir = base_dir
        self.config_file = CONFIG_DIR / "folder_mappings.yaml"
        
    def load_mappings(self) -> Dict:
        """載入資料夾對照配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def save_mappings(self, mappings: Dict):
        """儲存資料夾對照配置"""
        CONFIG_DIR.mkdir(exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(mappings, f, allow_unicode=True, sort_keys=False)
    
    def merge_folders(self, source: str, target: str, update_links: bool = True, dry_run: bool = False):
        """合併資料夾"""
        source_path = self.base_dir / "cases" / source
        target_path = self.base_dir / "cases" / target
        
        if not source_path.exists():
            print(f"❌ 來源資料夾不存在: {source}")
            return False
        
        if not target_path.exists():
            print(f"❌ 目標資料夾不存在: {target}")
            return False
        
        # 移動檔案
        files = list(source_path.glob("*.md"))
        print(f"\n📂 合併: {source} → {target}")
        print(f"   檔案數: {len(files)}")
        
        if dry_run:
            print("   ⚠️  DRY RUN - 不實際移動")
            for f in files:
                print(f"      {f.name}")
            return True
        
        for file in files:
            target_file = target_path / file.name
            if target_file.exists():
                print(f"   ⚠️  檔案已存在: {file.name}")
                continue
            shutil.move(str(file), str(target_file))
            print(f"   ✅ {file.name}")
        
        # 刪除空資料夾
        if not list(source_path.glob("*")):
            source_path.rmdir()
            print(f"   🗑️  刪除空資料夾: {source}")
        
        # 更新對照表
        if update_links:
            mappings = self.load_mappings()
            if 'merges' not in mappings:
                mappings['merges'] = []
            mappings['merges'].append({
                'source': source,
                'target': target,
                'date': str(Path.ctime(target_path))
            })
            self.save_mappings(mappings)
        
        return True
    
    def rename_folder(self, old_name: str, new_name: str, update_links: bool = True, dry_run: bool = False):
        """重命名資料夾"""
        old_path = self.base_dir / "cases" / old_name
        new_path = self.base_dir / "cases" / new_name
        
        if not old_path.exists():
            print(f"❌ 資料夾不存在: {old_name}")
            return False
        
        if new_path.exists():
            print(f"❌ 目標資料夾已存在: {new_name}")
            return False
        
        print(f"\n📝 重命名: {old_name} → {new_name}")
        
        if dry_run:
            print("   ⚠️  DRY RUN - 不實際重命名")
            return True
        
        old_path.rename(new_path)
        print(f"   ✅ 完成")
        
        # 更新對照表
        if update_links:
            mappings = self.load_mappings()
            if 'renames' not in mappings:
                mappings['renames'] = []
            mappings['renames'].append({
                'old': old_name,
                'new': new_name,
                'date': str(Path.ctime(new_path))
            })
            self.save_mappings(mappings)
        
        return True
    
    def analyze_structure(self, output_file: Optional[str] = None):
        """分析資料夾結構"""
        cases_dir = self.base_dir / "cases"
        folders = sorted([f for f in cases_dir.iterdir() if f.is_dir()])
        
        print("\n📊 資料夾結構分析")
        print("=" * 60)
        
        total_cases = 0
        stats = []
        
        for folder in folders:
            files = list(folder.glob("*.md"))
            case_files = [f for f in files if f.name.startswith("case_")]
            total_cases += len(case_files)
            
            stats.append({
                'name': folder.name,
                'cases': len(case_files),
                'total_files': len(files)
            })
            
            print(f"{folder.name:20} | {len(case_files):3} 個卦例")
        
        print("=" * 60)
        print(f"總計: {len(folders)} 個資料夾, {total_cases} 個卦例")
        
        if output_file:
            report_path = self.base_dir / output_file
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("# 資料夾結構分析報告\n\n")
                for stat in stats:
                    f.write(f"- **{stat['name']}**: {stat['cases']} 個卦例\n")
                f.write(f"\n**總計**: {len(folders)} 個資料夾, {total_cases} 個卦例\n")
            print(f"\n💾 報告已儲存: {report_path}")
        
        return stats

def main():
    parser = argparse.ArgumentParser(description='Obsidian 資料夾管理工具')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # merge 命令
    merge_parser = subparsers.add_parser('merge', help='合併資料夾')
    merge_parser.add_argument('--source', required=True, help='來源資料夾')
    merge_parser.add_argument('--target', required=True, help='目標資料夾')
    merge_parser.add_argument('--no-update-links', action='store_true', help='不更新對照表')
    merge_parser.add_argument('--dry-run', action='store_true', help='模擬執行')
    
    # rename 命令
    rename_parser = subparsers.add_parser('rename', help='重命名資料夾')
    rename_parser.add_argument('--old', required=True, help='舊名稱')
    rename_parser.add_argument('--new', required=True, help='新名稱')
    rename_parser.add_argument('--no-update-links', action='store_true', help='不更新對照表')
    rename_parser.add_argument('--dry-run', action='store_true', help='模擬執行')
    
    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='分析資料夾結構')
    analyze_parser.add_argument('--output', help='輸出報告檔案')
    
    args = parser.parse_args()
    
    manager = FolderManager()
    
    if args.command == 'merge':
        manager.merge_folders(
            args.source, 
            args.target, 
            update_links=not args.no_update_links,
            dry_run=args.dry_run
        )
    elif args.command == 'rename':
        manager.rename_folder(
            args.old, 
            args.new,
            update_links=not args.no_update_links,
            dry_run=args.dry_run
        )
    elif args.command == 'analyze':
        manager.analyze_structure(args.output)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
