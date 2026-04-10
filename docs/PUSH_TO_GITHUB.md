# 代码推送指南

## 📦 待推送的提交

当前有 5 个提交待推送到 GitHub 远程仓库：

```
c1c34b2 feat: 添加 CLI 命令行交互模式
3059063 feat: 添加 GitHub 推送辅助脚本
084e8d4 docs: 更新 README 添加 Web UI 说明
993231 docs: 添加 Web UI 使用指南
3ca0403 feat: 添加 Web UI 界面
```

## 🚀 推送方法

### 方法一：使用推送脚本（推荐）

```bash
cd /workspace/projects
./scripts/push_to_github.sh
```

脚本会提示你选择推送方式：
1. 使用 HTTPS（需要 GitHub Token）
2. 使用 SSH（需要 SSH 密钥）
3. 手动推送

### 方法二：使用 HTTPS + Token

1. **创建 GitHub Personal Access Token**
   - 访问 https://github.com/settings/tokens
   - 点击 "Generate new token (classic)"
   - 选择权限：`repo`（完整仓库访问权限）
   - 生成 Token

2. **使用 Token 推送**

```bash
cd /workspace/projects

# 设置远程 URL（使用 Token）
git remote set-url origin https://<YOUR_TOKEN>@github.com/fanjn-zetyun/docker-Agent.git

# 推送代码
git push origin dev

# 推送完成后恢复原始 URL
git remote set-url origin https://github.com/fanjn-zetyun/docker-Agent.git
```

**示例**：
```bash
# 假设你的 Token 是: ghp_xxxxxxxxxxxx
git remote set-url origin https://ghp_xxxxxxxxxxxx@github.com/fanjn-zetyun/docker-Agent.git
git push origin dev
git remote set-url origin https://github.com/fanjn-zetyun/docker-Agent.git
```

### 方法三：使用 SSH

1. **配置 SSH 密钥**
```bash
# 生成 SSH 密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 启动 ssh-agent
eval "$(ssh-agent -s)"

# 添加私钥
ssh-add ~/.ssh/id_ed25519

# 显示公钥并复制
cat ~/.ssh/id_ed25519.pub
```

2. **添加公钥到 GitHub**
   - 访问 https://github.com/settings/keys
   - 点击 "New SSH key"
   - 粘贴刚才复制的公钥

3. **推送代码**
```bash
cd /workspace/projects

# 切换到 SSH URL
git remote set-url origin git@github.com:fanjn-zetyun/docker-Agent.git

# 推送代码
git push origin dev
```

### 方法四：使用 GitHub CLI

如果你安装了 GitHub CLI (gh):

```bash
cd /workspace/projects

# 登录
gh auth login

# 推送
gh repo set-default fanjn-zetyun/docker-Agent
git push origin dev
```

## 🔍 检查状态

推送前可以查看待推送的提交：

```bash
cd /workspace/projects

# 查看状态
git status

# 查看待推送的提交
git log origin/dev..HEAD --oneline
```

## ✅ 推送后验证

推送完成后，访问 GitHub 仓库查看：

```
https://github.com/fanjn-zetyun/docker-Agent
```

## ❓ 常见问题

### 1. "could not read Username"

这是因为使用了 HTTPS 但没有提供认证信息。使用方法二或方法三。

### 2. "Permission denied (publickey)"

SSH 密钥配置有问题。检查：
- SSH 密钥是否已生成
- 公钥是否已添加到 GitHub
- 私钥是否已添加到 ssh-agent

### 3. "Authentication failed"

Token 可能过期或权限不足。重新生成 Token 并确保有 `repo` 权限。

### 4. "Updates were rejected"

远程仓库有新的提交。需要先拉取：

```bash
git pull origin dev --rebase
git push origin dev
```

## 📝 推送清单

- [ ] 确认待推送的提交（5 个）
- [ ] 选择推送方式（推荐方法一或方法二）
- [ ] 准备好 GitHub Token 或 SSH 密钥
- [ ] 执行推送命令
- [ ] 验证推送结果

## 🎯 快速推送（如果你有 GitHub Token）

```bash
# 一行命令推送（替换 YOUR_TOKEN）
cd /workspace/projects && \
git remote set-url origin https://YOUR_TOKEN@github.com/fanjn-zetyun/docker-Agent.git && \
git push origin dev && \
git remote set-url origin https://github.com/fanjn-zetyun/docker-Agent.git
```

推送完成后，你的代码就会在 GitHub 上了！
