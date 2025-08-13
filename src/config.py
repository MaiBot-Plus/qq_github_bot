"""
配置管理模块
"""

import json
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, validator


class Config(BaseModel):
    """配置类"""
    
    github_token: str
    github_repos: List[str] 
    check_interval: int = 300  # 默认5分钟
    
    openai_api_key: str
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-3.5-turbo"
    
    qq_bot_url: str
    qq_group_id: str
    
    database_path: str = "data.db"
    
    @validator('github_repos')
    def validate_repos(cls, v):
        """验证仓库格式"""
        for repo in v:
            if '/' not in repo:
                raise ValueError(f"仓库格式错误: {repo}，应为 owner/repo 格式")
        return v
    
    @validator('check_interval')
    def validate_interval(cls, v):
        """验证检查间隔"""
        if v < 60:
            raise ValueError("检查间隔不能少于60秒")
        return v
    
    @classmethod
    def from_file(cls, config_path: str) -> 'Config':
        """从配置文件加载配置"""
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        return cls(**config_data) 