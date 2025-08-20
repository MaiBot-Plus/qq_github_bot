#!/usr/bin/env python3
"""
设置验证脚本 - 验证所有依赖和配置是否正确
"""

import sys
import importlib.util
from pathlib import Path
import json

def check_dependencies():
    """检查所有依赖包是否安装"""
    required_packages = [
        'requests', 'schedule', 'openai', 'python-dotenv', 
        'loguru', 'click', 'pydantic', 'aiohttp'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        spec = importlib.util.find_spec(package.replace('-', '_'))
        if spec is None:
            missing_packages.append(package)
        else:
            print(f"✅ {package} 已安装")
    
    if missing_packages:
        print("\n❌ 缺少以下依赖包:")
        for package in missing_packages:
            print(f"   - {package}")
        print(f"\n请运行: pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_config():
    """检查配置文件"""
    config_file = Path("config.json")
    
    if not config_file.exists():
        print("❌ config.json 不存在")
        print("请运行: python main.py init-config")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        required_fields = [
            'github_token', 'github_repos', 'check_interval',
            'openai_api_key', 'openai_base_url', 'openai_model',
            'qq_bot_url', 'qq_group_id', 'database_path'
        ]
        
        missing_fields = []
        empty_fields = []
        
        for field in required_fields:
            if field not in config:
                missing_fields.append(field)
            elif not config[field] or (isinstance(config[field], str) and config[field].startswith(("your_", "123456789", "owner/repo"))):
                empty_fields.append(field)
        
        if missing_fields:
            print(f"❌ 配置文件缺少字段: {', '.join(missing_fields)}")
            return False
        
        if empty_fields:
            print(f"⚠️  以下配置需要填写实际值: {', '.join(empty_fields)}")
            return False
        
        print("✅ 配置文件格式正确")
        return True
        
    except json.JSONDecodeError:
        print("❌ 配置文件格式错误")
        return False

def check_modules():
    """检查项目模块导入"""
    try:
        from src.config import Config
        from src.database import Database
        from src.github_monitor import GitHubMonitor
        from src.ai_summarizer import AISummarizer
        from src.qq_bot import QQBot
        
        print("✅ 所有项目模块导入成功")
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def main():
    print("🔍 GitHub QQ Bot 设置验证")
    print("=" * 40)
    
    checks = [
        ("依赖包检查", check_dependencies),
        ("项目模块检查", check_modules),
        ("配置文件检查", check_config)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}:")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 40)
    
    if all_passed:
        print("🎉 所有检查通过！可以开始使用了")
        print("\n📖 下一步:")
        print("1. 编辑 config.json 填入真实的API密钥")
        print("2. 运行 python main.py test owner/repo 测试功能")
        print("3. 运行 python main.py run 启动监控服务")
    else:
        print("❌ 部分检查失败，请根据提示解决问题")
        sys.exit(1)

if __name__ == '__main__':
    main() 