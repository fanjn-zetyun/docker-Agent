# 使用 Bundle 文件推送代码

由于当前环境缺少 SSH 客户端，无法直接推送到 GitHub。我已经创建了一个 **Git Bundle** 文件，你可以在你的本地电脑上使用它来推送代码。

## 📦 Bundle 文件

**文件位置**: `/workspace/projects/docker-agent.bundle`

这个文件包含了需要推送的所有提交（5 个提交）。

## 🚀 推送方法（在你的本地电脑上）

### 方法一：使用推送脚本（推荐）

#### Linux/Mac

```bash
# 1. 下载 bundle 文件
# 从你的工作目录复制 docker-agent.bundle 文件

# 2. 运行推送脚本
chmod +x scripts/push_bundle.sh
./scripts/push_bundle.sh docker-agent.bundle
```

#### Windows

```cmd
# 1. 下载 bundle 文件
# 从你的工作目录复制 docker-agent.bundle 文件

# 2. 运行推送脚本
python scripts\push_bundle.py docker-agent.bundle
```

### 方法二：手动推送

```bash
# 1. 创建临时目录
mkdir temp-push
cd temp-push

# 2. 克隆远程仓库
git clone git@github.com:fanjn-zetyun/docker-Agent.git repo
cd repo

# 3. 拉取 bundle 文件（修改路径为实际路径）
git pull /path/to/docker-agent.bundle dev

# 4. 推送到 GitHub
git push origin dev

# 5. 清理
cd ..
rm -rf temp-push
```

### 方法三：使用 GitHub Token（最简单）

```bash
# 1. 克隆仓库
git clone https://github.com/fanjn-zetyun/docker-Agent.git
cd docker-Agent

# 2. 创建 Personal Access Token
# 访问: https://github.com/settings/tokens
# 生成 token 并选择 repo 权限

# 3. 拉取最新代码
git checkout dev
git pull origin dev

# 4. 创建本地分支并推送
git checkout -b feature/web-ui
git push origin feature/web-ui

# 5. 在 GitHub 上创建 Pull Request
# 访问: https://github.com/fanjn-zetyun/docker-Agent/compare/dev...feature/web-ui
```

## 📋 Bundle 文件内容

这个 bundle 包含以下 5 个提交：

```
c1c34b2 feat: 添加 CLI 命令行交互模式
3059063 feat: 添加 GitHub 推送辅助脚本
084e8d4 docs: 更新 README 添加 Web UI 说明
993231 docs: 添加 Web UI 使用指南
3ca0403 feat: 添加 Web UI 界面
```

## 🔍 验证 Bundle 内容

```bash
# 查看 bundle 中的提交
git log docker-agent.bundle

# 查看 bundle 中的文件
git ls-tree -r --name-only docker-agent.bundle
```

## ✅ 推送后验证

推送完成后，访问 GitHub 仓库查看：

```
https://github.com/fanjn-zetyun/docker-Agent
```

确认以下内容已推送：
- ✅ `src/cli.py` - CLI 交互模式
- ✅ `src/web_ui.py` - Web UI 界面
- ✅ `scripts/start_web_ui.sh` - Web UI 启动脚本
- ✅ `scripts/start_web_ui.bat` - Windows 启动脚本
- ✅ `scripts/push_bundle.sh` - Bundle 推送脚本
- ✅ `scripts/push_bundle.py` - Python Bundle 推送脚本
- ✅ `docs/CLI_MODE.md` - CLI 使用文档
- ✅ `docs/WEB_UI_GUIDE.md` - Web UI 使用文档
- ✅ `docs/PUSH_TO_GITHUB.md` - 推送指南
- ✅ 更新的 `README.md`

## 📝 推送脚本说明

### push_bundle.sh (Linux/Mac)

自动执行以下步骤：
1. 创建临时目录
2. 克隆远程仓库
3. 拉取 bundle 文件
4. 推送到 GitHub
5. 清理临时文件

### push_bundle.py (Windows/跨平台)

功能与 shell 脚本相同，但使用 Python 实现，支持 Windows。

## 💡 常见问题

### 1. "Permission denied (publickey)"

SSH 密钥配置问题。检查：
- SSH 密钥是否已添加到 GitHub
- 本地 SSH 配置是否正确

### 2. "fatal: not a git repository"

不在 git 仓库中。确保在正确的目录执行命令。

### 3. "error: invalid bundle"

Bundle 文件损坏。重新生成 bundle：

```bash
cd /workspace/projects
git bundle create docker-agent.bundle origin/dev..HEAD
```

### 4. "Already up to date"

远程仓库已经是最新的，无需推送。

## 🎯 快速开始

**最简单的方法** - 使用 GitHub Token：

```bash
# 1. 克隆仓库
git clone https://github.com/fanjn-zetyun/docker-Agent.git
cd docker-Agent

# 2. 切换到 dev 分支
git checkout dev

# 3. 拉取最新代码
git pull origin dev

# 4. 推送（会提示输入用户名和 Token）
git push origin dev
# Username: fanjn-zetyun
# Password: <你的 GitHub Token>
```

## 📚 相关文档

- `docs/PUSH_TO_GITHUB.md` - 详细的推送指南
- `docs/WEB_UI_GUIDE.md` - Web UI 使用文档
- `docs/CLI_MODE.md` - CLI 模式文档

## 🆘 需要帮助？

如果推送过程中遇到问题，检查：
1. GitHub Token 是否有正确的权限（repo）
2. 网络连接是否正常
3. 仓库地址是否正确
4. SSH 密钥是否已添加到 GitHub

推送成功后，你就可以使用 Web UI 和 CLI 模式了！
