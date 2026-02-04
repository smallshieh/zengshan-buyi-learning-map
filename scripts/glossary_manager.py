#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
術語管理工具
管理 glossary 資料夾中的術語檔案
⚡ Token 優化版：改用 guali_db.json 而非掃描所有 .md 檔案
"""

import argparse
import yaml
import json
from pathlib import Path
from typing import List, Dict, Set
import re

BASE_DIR = Path(r"c:\Users\smallshieh\Obsidian筆記")
GLOSSARY_DIR = BASE_DIR / "glossary"
CONFIG_DIR = BASE_DIR / "config"
DB_FILE = BASE_DIR / "data" / "guali_db.json"

class GlossaryManager:
    def __init__(self):
        self.glossary_dir = GLOSSARY_DIR
        self.config_file = CONFIG_DIR / "glossary_templates.yaml"
        self.templates = self.load_templates()
    
    def load_templates(self) -> Dict:
        """載入術語模板"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def check_missing(self, scan_dir: Path = None) -> Set[str]:
        """
        檢查缺失的術語
        ⚡ Token 優化：改用 guali_db.json 而非掃描所有 .md 檔案
        """
        # 收集所有 [[glossary/XXX]] 連結
        referenced_terms = set()
        
        # 優先從 guali_db.json 讀取（Token 優化）
        if DB_FILE.exists():
            print("📖 從 guali_db.json 讀取術語引用（Token 優化模式）...")
            try:
                with open(DB_FILE, 'r', encoding='utf-8') as f:
                    db = json.load(f)
                
                for case in db:
                    content = case.get('content', '')
                    # 匹配 [[glossary/XXX]]
                    matches = re.findall(r'\[\[glossary/([^\]]+)\]\]', content)
                    # 處理別名 [[glossary/Term|Alias]] -> Term
                    for m in matches:
                        term = m.split('|')[0]
                        referenced_terms.add(term)
                
                print(f"   ✅ 從資料庫找到 {len(referenced_terms)} 個術語引用")
            except Exception as e:
                print(f"   ⚠️  讀取 guali_db.json 失敗: {e}")
                print("   ℹ️  退回到掃描模式...")
                # 若 JSON 讀取失敗，才退回掃描模式
                if scan_dir is None:
                    scan_dir = BASE_DIR
                for md_file in scan_dir.rglob("*.md"):
                    try:
                        content = md_file.read_text(encoding='utf-8')
                        matches = re.findall(r'\[\[glossary/([^\]]+)\]\]', content)
                        for m in matches:
                            term = m.split('|')[0]
                            referenced_terms.add(term)
                    except:
                        continue
        else:
            print(f"⚠️  找不到 guali_db.json，使用掃描模式...")
            if scan_dir is None:
                scan_dir = BASE_DIR
            for md_file in scan_dir.rglob("*.md"):
                try:
                    content = md_file.read_text(encoding='utf-8')
                    matches = re.findall(r'\[\[glossary/([^\]]+)\]\]', content)
                    for m in matches:
                        term = m.split('|')[0]
                        referenced_terms.add(term)
                except:
                    continue
        
        # 檢查哪些術語檔案不存在
        existing_terms = set()
        for term_file in self.glossary_dir.glob("*.md"):
            existing_terms.add(term_file.stem)
        
        missing_terms = referenced_terms - existing_terms
        
        print(f"\n📊 術語檢查結果")
        print("=" * 60)
        print(f"引用的術語: {len(referenced_terms)}")
        print(f"已存在術語: {len(existing_terms)}")
        print(f"缺失術語: {len(missing_terms)}")
        
        if missing_terms:
            print(f"\n❌ 缺失的術語:")
            for term in sorted(missing_terms):
                print(f"   - {term}")
        else:
            print(f"\n✅ 所有術語都已存在")
        
        return missing_terms
    
    def create_term(self, term_name: str, template: str = "basic", dry_run: bool = False):
        """創建術語檔案"""
        term_file = self.glossary_dir / f"{term_name}.md"
        
        if term_file.exists():
            print(f"❌ 術語已存在: {term_name}")
            return False
        
        # 獲取模板
        template_content = self.templates.get(template, self.templates.get("basic", ""))
        if not template_content:
            template_content = f"# {term_name}\n\n## 定義\n\n[待補充]\n"
        else:
            template_content = template_content.replace("{{term}}", term_name)
        
        print(f"\n📝 創建術語: {term_name}")
        print(f"   模板: {template}")
        
        if dry_run:
            print("   ⚠️  DRY RUN - 不實際創建")
            print(f"\n內容預覽:\n{template_content[:200]}...")
            return True
        
        term_file.write_text(template_content, encoding='utf-8')
        print(f"   ✅ 已創建: {term_file}")
        
        return True
    
    def batch_create(self, terms: List[str], template: str = "basic", dry_run: bool = False):
        """批次創建術語"""
        print(f"\n📦 批次創建 {len(terms)} 個術語")
        
        created = 0
        skipped = 0
        
        for term in terms:
            if self.create_term(term, template, dry_run):
                created += 1
            else:
                skipped += 1
        
        print(f"\n✅ 創建: {created}, ⏭️  跳過: {skipped}")
    
    def build_index(self, output_file: str = "glossary/README.md"):
        """建立術語索引"""
        terms = []
        for term_file in sorted(self.glossary_dir.glob("*.md")):
            if term_file.name == "README.md":
                continue
            
            term_name = term_file.stem
            # 讀取第一行作為簡短描述
            try:
                first_line = term_file.read_text(encoding='utf-8').split('\n')[0]
                desc = first_line.replace('#', '').strip()
            except:
                desc = term_name
            
            terms.append({
                'name': term_name,
                'desc': desc,
                'file': term_file.name
            })
        
        # 生成索引
        index_content = "# 術語索引\n\n"
        index_content += f"總計: {len(terms)} 個術語\n\n"
        
        # 按首字母分組
        groups = {}
        for term in terms:
            first_char = term['name'][0]
            if first_char not in groups:
                groups[first_char] = []
            groups[first_char].append(term)
        
        for char in sorted(groups.keys()):
            index_content += f"\n## {char}\n\n"
            for term in sorted(groups[char], key=lambda x: x['name']):
                index_content += f"- [[{term['name']}]] - {term['desc']}\n"
        
        index_path = BASE_DIR / output_file
        index_path.write_text(index_content, encoding='utf-8')
        
        print(f"\n✅ 索引已建立: {index_path}")
        print(f"   術語數: {len(terms)}")

def main():
    parser = argparse.ArgumentParser(description='術語管理工具 (Token 優化版)')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # check-missing 命令
    check_parser = subparsers.add_parser('check-missing', help='檢查缺失術語')
    
    # create 命令
    create_parser = subparsers.add_parser('create', help='創建術語')
    create_parser.add_argument('term', help='術語名稱')
    create_parser.add_argument('--template', default='basic', help='模板類型')
    create_parser.add_argument('--dry-run', action='store_true', help='模擬執行')
    
    # batch-create 命令
    batch_parser = subparsers.add_parser('batch-create', help='批次創建術語')
    batch_parser.add_argument('--template', default='basic', help='模板類型')
    batch_parser.add_argument('--dry-run', action='store_true', help='模擬執行')
    
    # build-index 命令
    index_parser = subparsers.add_parser('build-index', help='建立術語索引')
    index_parser.add_argument('--output', default='glossary/README.md', help='輸出檔案')
    
    args = parser.parse_args()
    
    manager = GlossaryManager()
    
    if args.command == 'check-missing':
        missing = manager.check_missing()
        if missing:
            print(f"\n💡 使用以下命令批次創建:")
            print(f"   python scripts/glossary_manager.py batch-create")
    
    elif args.command == 'create':
        manager.create_term(args.term, args.template, args.dry_run)
    
    elif args.command == 'batch-create':
        missing = manager.check_missing()
        if missing:
            manager.batch_create(list(missing), args.template, args.dry_run)
        else:
            print("✅ 無缺失術語")
    
    elif args.command == 'build-index':
        manager.build_index(args.output)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
