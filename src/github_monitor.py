"""
GitHub监控模块 - 获取仓库提交信息
"""

import aiohttp
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Optional
from loguru import logger


class GitHubMonitor:
    """GitHub仓库监控器"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-QQ-Bot/1.0"
        }
    
    async def get_new_commits(self, repo: str, since: Optional[datetime] = None) -> List[Dict]:
        """获取指定时间之后的新提交"""
        url = f"{self.base_url}/repos/{repo}/commits"
        params = {"per_page": 10}
        
        if since:
            # GitHub API需要ISO格式的时间
            params["since"] = since.isoformat()
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        commits_data = await response.json()
                        return self._format_commits(commits_data)
                    elif response.status == 404:
                        logger.error(f"仓库不存在或无权限访问: {repo}")
                        return []
                    elif response.status == 403:
                        logger.error("GitHub API访问被限制，请检查token权限")
                        return []
                    else:
                        logger.error(f"GitHub API请求失败: {response.status}")
                        return []
            except Exception as e:
                logger.error(f"请求GitHub API时出错: {e}")
                return []
    
    async def get_recent_commits(self, repo: str, limit: int = 5) -> List[Dict]:
        """获取最近的提交（用于测试）"""
        url = f"{self.base_url}/repos/{repo}/commits"
        params = {"per_page": limit}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        commits_data = await response.json()
                        return self._format_commits(commits_data)
                    else:
                        logger.error(f"获取提交记录失败: {response.status}")
                        return []
            except Exception as e:
                logger.error(f"获取提交记录时出错: {e}")
                return []
    
    def _format_commits(self, commits_data: List[Dict]) -> List[Dict]:
        """格式化提交数据"""
        formatted_commits = []
        
        for commit in commits_data:
            try:
                formatted_commit = {
                    "sha": commit["sha"][:7],  # 短SHA
                    "full_sha": commit["sha"],
                    "message": commit["commit"]["message"],
                    "author": commit["commit"]["author"]["name"],
                    "author_email": commit["commit"]["author"]["email"],
                    "date": commit["commit"]["author"]["date"],
                    "url": commit["html_url"]
                }
                
                # 解析提交文件变更
                if "files" in commit:
                    formatted_commit["files"] = [
                        {
                            "filename": file["filename"],
                            "status": file["status"],  # added, modified, removed
                            "additions": file.get("additions", 0),
                            "deletions": file.get("deletions", 0)
                        }
                        for file in commit["files"]
                    ]
                
                formatted_commits.append(formatted_commit)
                
            except KeyError as e:
                logger.warning(f"提交数据格式异常: {e}")
                continue
        
        return formatted_commits 