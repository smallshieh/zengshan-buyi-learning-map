#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
進度追蹤管理器 (Progress Tracker)
用於管理多 Agent 並行處理時的進度追蹤和恢復
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class ProgressTracker:
    """進度追蹤器"""
    
    def __init__(self, progress_file: str = "original/progress.json"):
        self.progress_file = Path(progress_file)
        self.data = self._load_or_create()
    
    def _load_or_create(self) -> Dict:
        """載入或創建進度檔案"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                "last_processed_page": None,
                "last_global_offset": 0,
                "last_updated": None,
                "agents": {},
                "coverage": {
                    "total_chars": 0,
                    "processed_chars": 0,
                    "percentage": 0.0
                },
                "pages_status": {}
            }
    
    def save(self):
        """保存進度"""
        self.data["last_updated"] = datetime.now().isoformat()
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def mark_page_completed(self, page: str, agent: str, tokens_used: int = 0):
        """標記分頁已完成"""
        # 初始化 agent 記錄
        if agent not in self.data["agents"]:
            self.data["agents"][agent] = {
                "pages_completed": [],
                "tokens_used": 0,
                "status": "active"
            }
        
        # 更新 agent 資訊
        if page not in self.data["agents"][agent]["pages_completed"]:
            self.data["agents"][agent]["pages_completed"].append(page)
        self.data["agents"][agent]["tokens_used"] += tokens_used
        
        # 更新頁面狀態
        self.data["pages_status"][page] = {
            "agent": agent,
            "completed_at": datetime.now().isoformat(),
            "tokens_used": tokens_used
        }
        
        # 更新最後處理的頁面
        self.data["last_processed_page"] = page
        
        self.save()
    
    def get_next_unprocessed_page(self, all_pages: List[str]) -> Optional[str]:
        """取得下一個未處理的分頁"""
        completed = set(self.data["pages_status"].keys())
        for page in sorted(all_pages):
            if page not in completed:
                return page
        return None
    
    def set_agent_status(self, agent: str, status: str):
        """設定 Agent 狀態 (active/paused/completed)"""
        if agent in self.data["agents"]:
            self.data["agents"][agent]["status"] = status
            self.save()
    
    def update_coverage(self, total_chars: int, processed_chars: int):
        """更新覆蓋率"""
        self.data["coverage"]["total_chars"] = total_chars
        self.data["coverage"]["processed_chars"] = processed_chars
        self.data["coverage"]["percentage"] = (
            processed_chars / total_chars * 100 if total_chars > 0 else 0
        )
        self.save()
    
    def get_summary(self) -> str:
        """取得進度摘要"""
        lines = [
            "=" * 60,
            "進度追蹤摘要",
            "=" * 60,
            f"最後處理頁面: {self.data['last_processed_page']}",
            f"覆蓋率: {self.data['coverage']['percentage']:.1f}%",
            f"  - 總字數: {self.data['coverage']['total_chars']:,}",
            f"  - 已處理: {self.data['coverage']['processed_chars']:,}",
            "",
            "Agent 狀態:",
        ]
        
        for agent, info in self.data["agents"].items():
            lines.append(f"  {agent}:")
            lines.append(f"    - 狀態: {info['status']}")
            lines.append(f"    - 完成頁數: {len(info['pages_completed'])}")
            lines.append(f"    - Tokens 使用: {info['tokens_used']:,}")
        
        lines.append("=" * 60)
        return "\n".join(lines)


def main():
    """測試用主程式"""
    tracker = ProgressTracker()
    
    # 模擬使用
    tracker.mark_page_completed("page_001.txt", "Claude-3.5", tokens_used=1500)
    tracker.mark_page_completed("page_002.txt", "Claude-3.5", tokens_used=1800)
    tracker.set_agent_status("Claude-3.5", "paused")
    
    tracker.mark_page_completed("page_003.txt", "DeepSeek", tokens_used=1200)
    tracker.set_agent_status("DeepSeek", "active")
    
    tracker.update_coverage(total_chars=450000, processed_chars=9000)
    
    print(tracker.get_summary())
    
    # 取得下一個待處理的頁面
    all_pages = [f"page_{i:03d}.txt" for i in range(1, 151)]
    next_page = tracker.get_next_unprocessed_page(all_pages)
    print(f"\n下一個待處理頁面: {next_page}")


if __name__ == "__main__":
    main()
