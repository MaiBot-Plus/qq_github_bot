#!/usr/bin/env python3
"""
GitHub QQ Bot - 监控GitHub仓库提交并发送总结到QQ群
"""

import asyncio
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

import click
import requests
from loguru import logger
from dotenv import load_dotenv

from src.github_monitor import GitHubMonitor
from src.ai_summarizer import AISummarizer
from src.qq_bot import QQBot
from src.config import Config
from src.database import Database


# 加载环境变量
load_dotenv()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """GitHub QQ Bot - 自动监控GitHub提交并发送总结到QQ群"""
    pass


@cli.command()
@click.option('--config', '-c', default='config.json', help='配置文件路径')
def run(config):
    """运行监控服务"""
    try:
        # 加载配置
        config_obj = Config.from_file(config)
        
        # 初始化组件
        db = Database(config_obj.database_path)
        github_monitor = GitHubMonitor(config_obj.github_token)
        ai_summarizer = AISummarizer(
            config_obj.openai_api_key, 
            config_obj.openai_base_url,
            config_obj.openai_model
        )
        qq_bot = QQBot(config_obj.qq_bot_url, config_obj.qq_group_id)
        
        logger.info(f"🚀 启动GitHub QQ Bot监控服务...")
        logger.info(f"监控仓库: {', '.join(config_obj.github_repos)}")
        logger.info(f"检查间隔: {config_obj.check_interval}秒")
        
        # 主循环
        while True:
            try:
                # 检查每个仓库
                for repo in config_obj.github_repos:
                    asyncio.run(process_repo(repo, db, github_monitor, ai_summarizer, qq_bot))
                
                logger.info(f"💤 等待{config_obj.check_interval}秒后继续检查...")
                time.sleep(config_obj.check_interval)
                
            except KeyboardInterrupt:
                logger.info("👋 收到退出信号，停止服务...")
                break
            except Exception as e:
                logger.error(f"❌ 处理过程中出错: {e}")
                time.sleep(60)  # 出错后等待1分钟再继续
    
    except Exception as e:
        logger.error(f"❌ 启动失败: {e}")
        click.echo(f"错误: {e}", err=True)


async def process_repo(repo: str, db: Database, github_monitor: GitHubMonitor, 
                      ai_summarizer: AISummarizer, qq_bot: QQBot):
    """处理单个仓库的提交检查"""
    try:
        logger.info(f"🔍 检查仓库 {repo} 的新提交...")
        
        # 获取最后检查时间
        last_check = db.get_last_check_time(repo)
        
        # 获取新提交
        commits = await github_monitor.get_new_commits(repo, last_check)
        
        if not commits:
            logger.info(f"✅ {repo} 没有新提交")
            return
        
        logger.info(f"📝 发现 {len(commits)} 个新提交")
        
        # 生成提交总结
        summary = await ai_summarizer.summarize_commits(repo, commits)
        
        # 发送到QQ群
        await qq_bot.send_message(summary)
        
        # 更新最后检查时间
        db.update_last_check_time(repo, datetime.now())
        
        logger.info(f"✅ {repo} 的提交总结已发送到QQ群")
        
    except Exception as e:
        logger.error(f"❌ 处理仓库 {repo} 时出错: {e}")


@cli.command()
@click.option('--config', '-c', default='config.json', help='配置文件路径')
def init_config(config):
    """初始化配置文件"""
    config_path = Path(config)
    
    if config_path.exists():
        if not click.confirm(f"配置文件 {config} 已存在，是否覆盖？"):
            return
    
    # 创建默认配置
    default_config = {
        "github_token": "",
        "github_repos": ["owner/repo"],
        "check_interval": 300,
        "openai_api_key": "",
        "openai_base_url": "https://api.openai.com/v1",
        "openai_model": "gpt-3.5-turbo",
        "qq_bot_url": "http://127.0.0.1:5700",
        "qq_group_id": "",
        "database_path": "data.db"
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, indent=2, ensure_ascii=False)
    
    click.echo(f"✅ 配置文件已创建: {config}")
    click.echo("请编辑配置文件填入相关信息后运行监控服务")


@cli.command()
@click.argument('repo')
@click.option('--config', '-c', default='config.json', help='配置文件路径')
def test(repo, config):
    """测试指定仓库的监控功能"""
    try:
        config_obj = Config.from_file(config)
        
        # 初始化组件
        github_monitor = GitHubMonitor(config_obj.github_token)
        ai_summarizer = AISummarizer(
            config_obj.openai_api_key, 
            config_obj.openai_base_url,
            config_obj.openai_model
        )
        
        click.echo(f"🧪 测试仓库: {repo}")
        
        # 获取最近的提交
        commits = asyncio.run(github_monitor.get_recent_commits(repo, limit=3))
        
        if not commits:
            click.echo("没有找到提交记录")
            return
        
        click.echo(f"找到 {len(commits)} 个最近的提交")
        
        # 生成总结
        summary = asyncio.run(ai_summarizer.summarize_commits(repo, commits))
        
        click.echo("\n生成的总结:")
        click.echo("-" * 50)
        click.echo(summary)
        click.echo("-" * 50)
        
    except Exception as e:
        click.echo(f"测试失败: {e}", err=True)


if __name__ == '__main__':
    cli() 