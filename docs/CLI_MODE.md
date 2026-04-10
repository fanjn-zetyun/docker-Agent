# CLI 模式使用说明

## 🚀 启动 CLI 模式

### 方法一：直接运行

```bash
python src/cli.py
```

### 方法二：通过 main.py

```bash
python src/main.py -m cli
```

## 💬 使用示例

```
🐳 Docker Agent CLI 模式
============================================================

正在初始化 Agent...
✅ Agent 初始化成功！

可用的功能:
  - Git 代码同步 (拉取、切换、合并)
  - Dockerfile 分析和学习
  - Docker 镜像构建和推送
  - K8S Pod 创建和管理
  - LlamaFactory 验证

输入 'help' 查看帮助，输入 'exit' 退出
============================================================

你: 帮我构建 LlamaFactory 镜像

Agent: 好的，我来帮你构建镜像。首先让我拉取官方仓库的最新代码...
[Agent 开始执行任务...]
```

## 🔧 常用命令

| 命令 | 说明 |
|------|------|
| `help` | 显示帮助信息 |
| `exit` | 退出程序 |
| `clear` | 清空对话历史 |
| `history` | 查看对话历史 |

## 💡 常用 Agent 指令

- **构建镜像**: "帮我构建 LlamaFactory 镜像"
- **验证镜像**: "验证刚才构建的镜像"
- **查看状态**: "查看 K8S 集群状态"
- **分析 Dockerfile**: "分析 Dockerfile"
- **代码同步**: "从 GitHub 拉取最新代码"
- **诊断问题**: "诊断镜像构建失败的原因"

## ⚠️ 注意事项

1. CLI 模式需要 Agent 正确初始化
2. 确保 K8S 集群可以访问（如果使用 K8S 相关功能）
3. 确保 Docker 可以访问（如果需要构建镜像）
4. 按 Ctrl+C 可以优雅退出

## 🔍 故障排查

### 1. Agent 初始化失败

**问题**: "❌ Agent 初始化失败"

**解决**:
- 检查 `config/agent_llm_config.json` 是否正确
- 检查 API Key 是否配置
- 检查网络连接

### 2. 无法调用 Agent

**问题**: "❌ Agent 调用失败"

**解决**:
- 检查 LLM 服务是否可用
- 检查 API 地址和 Key
- 查看详细错误信息

### 3. K8S 操作失败

**问题**: "kubectl: command not found"

**解决**:
- 安装 kubectl
- 配置 kubeconfig 文件
- 确保有足够的权限
