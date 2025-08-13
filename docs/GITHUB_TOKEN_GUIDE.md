# GitHub Token 配置指南

## 访问组织仓库的Token权限设置

### 1. 创建Personal Access Token (Classic)

1. 登录GitHub后访问：[Settings > Developer settings > Personal access tokens > Tokens (classic)](https://github.com/settings/tokens)

2. 点击 "Generate new token" → "Generate new token (classic)"

### 2. 必需的权限设置

#### 基础权限（所有情况必需）
- ✅ `public_repo` - 访问公共仓库
- ✅ `repo:status` - 访问仓库状态
- ✅ `repo_deployment` - 访问部署状态

#### 访问私有仓库（如需要）
- ✅ `repo` - 完整的仓库访问权限（包括私有仓库）

#### 访问组织仓库（重要）
- ✅ `read:org` - 读取组织成员身份和仓库访问权限
- ✅ `repo` - 如果组织仓库是私有的

### 3. 组织级别的访问控制

#### 检查组织设置
1. 进入组织页面：`https://github.com/orgs/{组织名}/settings`
2. 在左侧菜单选择 "Third-party access"
3. 确保允许Personal Access Token访问

#### 如果组织启用了SSO
1. 创建token后，需要在组织页面授权
2. 点击token旁边的 "Enable SSO" 按钮
3. 选择要授权的组织

### 4. 验证Token权限

创建一个测试脚本来验证token是否能访问组织仓库：

```python
import requests

def test_github_token(token, org, repo):
    """测试GitHub Token是否能访问指定组织仓库"""
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # 测试访问组织信息
    org_url = f"https://api.github.com/orgs/{org}"
    org_response = requests.get(org_url, headers=headers)
    
    if org_response.status_code == 200:
        print(f"✅ 成功访问组织: {org}")
    else:
        print(f"❌ 无法访问组织: {org} (状态码: {org_response.status_code})")
        return False
    
    # 测试访问具体仓库
    repo_url = f"https://api.github.com/repos/{org}/{repo}"
    repo_response = requests.get(repo_url, headers=headers)
    
    if repo_response.status_code == 200:
        print(f"✅ 成功访问仓库: {org}/{repo}")
        
        # 测试获取提交记录
        commits_url = f"https://api.github.com/repos/{org}/{repo}/commits"
        commits_response = requests.get(commits_url, headers=headers, params={"per_page": 1})
        
        if commits_response.status_code == 200:
            print(f"✅ 成功获取提交记录")
            return True
        else:
            print(f"❌ 无法获取提交记录 (状态码: {commits_response.status_code})")
    else:
        print(f"❌ 无法访问仓库: {org}/{repo} (状态码: {repo_response.status_code})")
        return False

# 使用示例
if __name__ == "__main__":
    token = "ghp_your_token_here"  # 替换为你的token
    org = "your-org"              # 替换为组织名
    repo = "your-repo"            # 替换为仓库名
    
    test_github_token(token, org, repo)
```

### 5. 常见问题和解决方案

#### 问题1: 403 Forbidden
**原因**: Token权限不足或组织限制了第三方应用访问
**解决**: 
- 检查token是否包含 `read:org` 权限
- 联系组织管理员开启第三方应用访问

#### 问题2: 404 Not Found 
**原因**: 仓库不存在或token无权限访问
**解决**:
- 确认仓库路径正确 (`组织名/仓库名`)
- 确保token有 `repo` 权限（私有仓库）

#### 问题3: 401 Unauthorized
**原因**: Token无效或过期
**解决**:
- 重新生成token
- 检查token格式是否正确

### 6. 安全最佳实践

1. **最小权限原则**: 只授予必需的权限
2. **定期轮换**: 定期更新token
3. **环境变量**: 不要硬编码token，使用环境变量
4. **访问日志**: 定期检查token使用情况

### 7. 在机器人中使用

配置文件示例：
```json
{
  "github_token": "ghp_your_actual_token_here",
  "github_repos": [
    "your-org/repo1",
    "your-org/repo2",
    "your-personal-account/repo3"
  ]
}
```

环境变量示例：
```bash
export GITHUB_TOKEN="ghp_your_actual_token_here"
``` 