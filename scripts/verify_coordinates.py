#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
座標驗證腳本 (Coordinate Verification Script)
用於驗證提取內容的座標正確性
"""
import json
import yaml
from pathlib import Path
from typing import List, Dict, Tuple


class CoordinateVerifier:
    """座標驗證器"""
    
    def __init__(self, manifest_file: str = "original/manifest.json"):
        self.manifest = self._load_manifest(manifest_file)
    
    def _load_manifest(self, manifest_file: str) -> Dict:
        """載入座標地圖"""
        with open(manifest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def verify_file(self, file_path: str) -> Tuple[bool, List[str]]:
        """驗證單個檔案"""
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 檢查 YAML Frontmatter
            if not content.startswith('---'):
                errors.append("Missing YAML frontmatter")
                return False, errors
            
            # 解析 YAML
            parts = content.split('---')
            if len(parts) < 3:
                errors.append("Invalid YAML structure")
                return False, errors
            
            metadata = yaml.safe_load(parts[1])
            
            # 驗證必要欄位
            required_fields = ['source_page', 'local_start', 'local_length', 'agent']
            for field in required_fields:
                if field not in metadata:
                    errors.append(f"Missing required field: {field}")
            
            # 驗證時間戳記
            if 'extracted_at' in metadata:
                try:
                    from datetime import datetime
                    # 嘗試解析 ISO 8601 格式
                    datetime.fromisoformat(metadata['extracted_at'].replace('Z', '+00:00'))
                except ValueError as e:
                    errors.append(f"Invalid timestamp format: {metadata['extracted_at']} - {str(e)}")
            else:
                errors.append("Missing extracted_at timestamp (建議加入)")
            
            # 驗證座標
            page_name = metadata.get('source_page')
            local_start = metadata.get('local_start')
            local_length = metadata.get('local_length')
            
            if page_name and local_start is not None and local_length is not None:
                # 查找頁面資訊
                page_info = next(
                    (p for p in self.manifest['pages'] if p['filename'] == page_name),
                    None
                )
                
                if not page_info:
                    errors.append(f"Page not found in manifest: {page_name}")
                else:
                    # 驗證範圍
                    if local_start < 0:
                        errors.append(f"Invalid local_start: {local_start}")
                    
                    if local_length <= 0:
                        errors.append(f"Invalid local_length: {local_length}")
                    
                    if local_start + local_length > page_info['length']:
                        errors.append(
                            f"Coordinates exceed page length: "
                            f"{local_start + local_length} > {page_info['length']}"
                        )
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Error processing file: {str(e)}")
            return False, errors
    
    def verify_directory(self, directory: str) -> Dict:
        """驗證整個目錄"""
        results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        
        for file_path in Path(directory).glob('*.md'):
            results['total'] += 1
            success, errors = self.verify_file(str(file_path))
            
            if success:
                results['passed'] += 1
            else:
                results['failed'] += 1
                results['errors'].append({
                    'file': file_path.name,
                    'errors': errors
                })
        
        return results
    
    def check_overlaps(self, directory: str, page_name: str) -> List[Dict]:
        """檢查同一頁面的提取是否有重疊"""
        extractions = []
        
        # 收集所有針對此頁面的提取
        for file_path in Path(directory).glob('*.md'):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '---' in content:
                parts = content.split('---')
                if len(parts) >= 3:
                    metadata = yaml.safe_load(parts[1])
                    if metadata.get('source_page') == page_name:
                        extractions.append({
                            'file': file_path.name,
                            'start': metadata['local_start'],
                            'end': metadata['local_start'] + metadata['local_length']
                        })
        
        # 檢查重疊
        overlaps = []
        for i, ext1 in enumerate(extractions):
            for ext2 in extractions[i+1:]:
                if ext1['start'] < ext2['end'] and ext2['start'] < ext1['end']:
                    overlaps.append({
                        'file1': ext1['file'],
                        'file2': ext2['file'],
                        'overlap': f"{max(ext1['start'], ext2['start'])}-{min(ext1['end'], ext2['end'])}"
                    })
        
        return overlaps


def main():
    """主程式"""
    import sys
    
    verifier = CoordinateVerifier()
    
    if len(sys.argv) < 2:
        print("Usage: python verify_coordinates.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    
    print("=" * 60)
    print("座標驗證報告")
    print("=" * 60)
    
    results = verifier.verify_directory(directory)
    
    print(f"\n總計: {results['total']}")
    print(f"通過: {results['passed']}")
    print(f"失敗: {results['failed']}")
    
    if results['failed'] > 0:
        print("\n錯誤詳情:")
        for error in results['errors']:
            print(f"\n  檔案: {error['file']}")
            for err in error['errors']:
                print(f"    - {err}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
