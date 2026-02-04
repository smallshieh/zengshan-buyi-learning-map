#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
執行檔案移動 (設定 dry_run=False)
"""
import sys
sys.path.insert(0, r'c:\Users\smallshieh\Obsidian筆記\scripts')

from auto_categorize_cases import process_files

if __name__ == "__main__":
    print("開始執行實際移動...")
    moves = process_files(dry_run=False)
    print(f"\n完成! 共移動 {len(moves)} 個檔案")
