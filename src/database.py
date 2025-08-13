"""
数据库模块 - 使用SQLite存储检查状态
"""

import sqlite3
from datetime import datetime
from typing import Optional
from pathlib import Path


class Database:
    """简单的SQLite数据库管理"""
    
    def __init__(self, db_path: str = "data.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS repo_checks (
                    repo TEXT PRIMARY KEY,
                    last_check_time TEXT,
                    last_commit_sha TEXT
                )
            """)
            conn.commit()
    
    def get_last_check_time(self, repo: str) -> Optional[datetime]:
        """获取指定仓库的最后检查时间"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT last_check_time FROM repo_checks WHERE repo = ?",
                (repo,)
            )
            result = cursor.fetchone()
            
            if result and result[0]:
                return datetime.fromisoformat(result[0])
            return None
    
    def update_last_check_time(self, repo: str, check_time: datetime, last_commit_sha: str = None):
        """更新仓库的最后检查时间"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO repo_checks 
                (repo, last_check_time, last_commit_sha) 
                VALUES (?, ?, ?)
            """, (repo, check_time.isoformat(), last_commit_sha))
            conn.commit()
    
    def get_last_commit_sha(self, repo: str) -> Optional[str]:
        """获取最后处理的提交SHA"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT last_commit_sha FROM repo_checks WHERE repo = ?",
                (repo,)
            )
            result = cursor.fetchone()
            return result[0] if result else None 