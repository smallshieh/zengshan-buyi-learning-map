#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量補完缺失術語
分類使用不同的模板
"""

from glossary_manager import GlossaryManager

def main():
    manager = GlossaryManager()
    
    # 重新獲取乾淨的缺失列表
    missing = manager.check_missing()
    
    # 定義分類關鍵字
    categories = {
        'yao': ['爻', '神', '鬼', '親', '世', '應', '伏', '飛'],
        'state': ['空', '破', '墓', '絕', '生', '旺', '相', '死', '囚', '進', '退', '動', '靜', '發動', '暗動'],
        'relation': ['刑', '沖', '害', '合', '克', '生'],
    }
    
    # 分類列表
    lists = {
        'yao': [],
        'state': [],
        'relation': [],
        'basic': []
    }
    
    print("\n🔍 術語自動分類中...")
    
    for term in missing:
        classified = False
        
        # 1. 檢查特定後綴/關鍵字
        for key, keywords in categories.items():
            for kw in keywords:
                if kw in term:
                    lists[key].append(term)
                    classified = True
                    break
            if classified:
                break
        
        # 2. 默認歸類為 basic
        if not classified:
            lists['basic'].append(term)
            
    # 執行批量創建
    print("\n🚀 開始批量創建...")
    
    for template, terms in lists.items():
        if not terms:
            continue
            
        print(f"\n[{template.upper()}] 模板 - {len(terms)} 個:")
        print(f"  {', '.join(terms[:5])}...")
        
        manager.batch_create(terms, template=template)

if __name__ == "__main__":
    main()
