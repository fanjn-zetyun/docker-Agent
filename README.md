# Docker Agent - LlamaFactory 镜像构建自动化工具

Docker Agent 是一个专门用于自动化构建和验证 LlamaFactory Docker 镜像的智能 Agent 工具。它集成了 Git 版本控制、Docker 镜像构建、Kubernetes 集群管理和模型验证等功能。

## 📋 目录

- [功能特性](#功能特性)
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [使用方法](#使用方法)
- [Kubernetes 部署](#kubernetes-部署)
- [故障排查](#故障排查)
- [常见问题](#常见问题)

## ✨ 功能特性

- 🔧 **自动化镜像构建**：支持自定义 Dockerfile 分析和学习
- 🔄 **Git 代码同步**：自动拉取官方仓库代码并合并到开发分支
- 🐳 **Docker 镜像管理**：构建、推送和管理 Docker 镜像
- ☸️ **Kubernetes 集成**：在 K8S 集群中创建验证 Pod 并执行测试
- 🧪 **模型验证**：运行 LlamaFactory 微调任务验证镜像正确性
- 🤖 **智能诊断**：自动诊断镜像问题并提供修复建议
- 🔐 **权限管理**：完整的 RBAC 配置，支持 Pod 创建和管理
- ⚙️ **灵活配置**：支持自定义模型配置和 K8S 配置

## 🔧 环境要求

### 本地运行环境

- Python 3.8+
- Git
- Docker（如果需要在本地构建镜像）
- kubectl（如果需要操作 K8S 集群）

### Kubernetes 集群要求（用于部署验证 Pod）

- Kubernetes 1.20+
- 支持 GPU 节点（H100/A100 等）
- RDMA 支持（可选）
- S3 对象存储（可选）
- PVC 存储支持

## 🚀 快速开始

### 1. 克隆代码

```bash
git clone https://github.com/fanjn-zetyun/docker-Agent.git
cd docker-Agent
```

### 2. 安装依赖

```bash
# 使用 uv 安装依赖（推荐）
uv pip install -r requirements.txt
```

### 3. 配置 Agent

编辑 `config/agent_llm_config.json`，配置 Agent 模型：

```json
{
    "config": {
        "model": "doubao-seed-1-6-251015",
        "temperature": 0.7,
        "top_p": 0.9,
        "max_completion_tokens": 10000,
        "timeout": 600,
        "thinking": "disabled"
    },
    "sp": "你的系统提示词...",
    "tools": ["工具列表"]
}
```

### 4. 运行 Agent

```bash
# 命令行模式
python src/main.py -m cli

# HTTP 服务模式
python src/main.py -m http -p 8000
```

## ⚙️ 配置说明

### 1. Agent 配置（`config/agent_llm_config.json`）

#### config 字段

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| model | string | LLM 模型名称 | doubao-seed-1-6-251015 |
| temperature | float | 生成温度，范围 0-2 | 0.7 |
| top_p | float | 核采样概率，范围 0-1 | 0.9 |
| max_completion_tokens | int | 最大生成 Token 数 | 10000 |
| timeout | int | 请求超时时间（秒） | 600 |
| thinking | string | 思考模式（disabled/required/auto） | disabled |

#### sp 字段
系统提示词，定义 Agent 的角色、任务目标和工作流程。详细内容见 [Agent 系统提示词说明](#agent-系统提示词说明)。

#### tools 字段
Agent 可用的工具列表，包括：
- `git_pull` - 拉取代码
- `git_checkout` - 切换分支
- `git_merge` - 合并分支
- `analyze_dockerfile` - 分析 Dockerfile
- `build_docker_image` - 构建镜像
- `push_docker_image` - 推送镜像
- `k8s_create_validation_pod` - 创建验证 Pod
- `run_llama_factory_training` - 运行训练任务
- 等等...

### 2. 用户模型配置（`config/user_model_config.py`）

此文件用于配置用户自定义的模型。

#### 配置示例

```python
# Agent 使用的模型配置
AGENT_MODEL = {
    "model": "doubao-seed-1-6-251015",
    "temperature": 0.7,
    "top_p": 0.9
}

# 验证使用的模型配置
VALIDATION_MODEL = {
    "model": "deepseek-chat",
    "temperature": 0.7,
    "top_p": 0.9
}

# 自定义模型端点
CUSTOM_MODEL_ENDPOINT = None  # 或 "https://your-model-endpoint.com/v1"

# K8S 命名空间
K8S_NAMESPACE = "fjn"
```

#### 字段说明

| 参数 | 类型 | 说明 |
|------|------|------|
| AGENT_MODEL | dict | Agent 运行时使用的 LLM 模型配置 |
| VALIDATION_MODEL | dict | 验证 LlamaFactory 时使用的模型配置 |
| CUSTOM_MODEL_ENDPOINT | string | 自定义模型 API 地址（可选） |
| K8S_NAMESPACE | string | Kubernetes 命名空间 |

详细配置说明请参考 [用户模型配置文档](docs/USER_MODEL_CONFIG.md)。

### 3. K8S 部署配置（`config/k8s_deployment_config.py`）

此文件定义了在 K8S 集群中创建验证 Pod 的配置。

#### 主要配置项

```python
# 镜像配置
IMAGE_REGISTRY = "registry.hd-02.alayanew.com:8443"
IMAGE_PROJECT = "alayanew-4fd285c4-c4f3-4e92-80ee-26169717cba8"

# Pod 资源配置
POD_RESOURCES = {
    "limits": {
        "cpu": "8",
        "memory": "32Gi",
        "nvidia.com/gpu-h100-80gb-hbm3": "1"
    },
    "requests": {
        "cpu": "4",
        "memory": "16Gi"
    }
}

# S3 存储
S3_CONFIG = {
    "access_key": "IFFY4LH673KKYHBNGBFT",
    "secret_key": "rQT8L9VsWZ5clAKLM2qAAYR3nKWNYDMS2Bsh0u8N",
    "endpoint": "https://s3.hd-02.alayanew.com:8082"
}
```

详细配置说明请参考 [K8S 部署配置文档](docs/K8S_DEPLOYMENT.md)。

## 📖 使用方法

### 命令行模式

```bash
python src/main.py -m cli
```

进入交互式命令行后，可以直接与 Agent 对话：

```
你: 帮我构建 LlamaFactory 镜像
Agent: 好的，我来帮你构建镜像。首先让我拉取官方仓库的最新代码...
```

### HTTP 服务模式

```bash
# 启动 HTTP 服务
python src/main.py -m http -p 8000

# 测试健康检查
curl http://localhost:8000/health

# 调用 Agent
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "type": "query",
    "session_id": "session-001",
    "message": "帮我构建镜像",
    "content": {
      "query": {
        "prompt": [
          {
            "type": "text",
            "content": {
              "text": "帮我构建 LlamaFactory 镜像"
            }
          }
        ]
      }
    }
  }'
```

### 典型使用场景

#### 场景 1：构建并验证镜像

```
你: 我需要构建一个新的 LlamaFactory 镜像，我的 Dockerfile 在 ./Dockerfile
Agent: 好的，我来帮你构建。让我先分析一下 Dockerfile...
[Agent 自动执行以下步骤]
1. 拉取官方仓库最新代码
2. 切换到 online 分支
3. 合并代码
4. 分析 Dockerfile
5. 构建镜像
6. 在 K8S 中创建验证 Pod
7. 运行测试任务
8. 反馈结果
```

#### 场景 2：诊断镜像问题

```
你: 上次构建的镜像有问题，帮我诊断一下
Agent: 好的，让我查看一下上次构建的日志...
[Agent 自动执行]
1. 获取验证 Pod 日志
2. 分析错误信息
3. 提供修复建议
```

#### 场景 3：更新 Dockerfile 后重新构建

```
你: 我更新了 Dockerfile，重新构建一下
Agent: 好的，让我先学习一下新的 Dockerfile 变化...
[Agent 执行]
1. 对比新旧 Dockerfile
2. 识别变化内容
3. 构建新镜像
4. 验证新镜像
```

## ☸️ Kubernetes 部署

### 部署 Agent 到 K8S

#### 1. 修改配置

编辑 `k8s/docker-agent-deployment.yaml`，修改镜像地址：

```yaml
image: registry.hd-02.alayanew.com:8443/alayanew-4fd285c4-c4f3-4e92-80ee-26169717cba8/docker-agent:latest
```

#### 2. 部署

```bash
kubectl apply -f k8s/docker-agent-deployment.yaml
```

#### 3. 访问

**方式 A：端口转发**
```bash
kubectl port-forward -n fjn deploy/docker-agent 8000:8000
curl http://localhost:8000/health
```

**方式 B：NodePort**
```bash
curl http://<node-ip>:30800/health
```

**方式 C：Ingress**（需要配置域名）
```bash
curl http://docker-agent.yourdomain.com/health
```

详细的 K8S 部署说明请参考：
- [K8S 部署快速指南](k8s/README.md)
- [K8S 部署和使用文档](docs/K8S_DEPLOY_USAGE.md)

## 🔧 故障排查

### 常见问题

#### 1. Pod 无法启动

**检查 Pod 状态**
```bash
kubectl get pods -n fjn -l app=docker-agent
kubectl describe pod -n fjn -l app=docker-agent
kubectl logs -n fjn -l app=docker-agent
```

**可能原因**
- 镜像拉取失败：检查镜像地址和凭证
- 资源不足：检查 GPU、CPU、内存资源
- 存储挂载失败：检查 PVC 配置

#### 2. 无法访问 Agent

**检查 Service**
```bash
kubectl get svc -n fjn -l app=docker-agent
kubectl get endpoints -n fjn svc-docker-agent
```

**检查端口转发**
```bash
kubectl port-forward -n fjn deploy/docker-agent 8000:8000 --address 0.0.0.0
```

#### 3. Agent 执行失败

**查看日志**
```bash
kubectl logs -n fjn -l app=docker-agent -f
```

**检查配置**
- 确认 API Key 配置正确
- 确认模型服务地址可访问
- 确认 K8S 权限配置正确

### 日志位置

Agent 日志输出到标准输出，可以通过以下方式查看：

```bash
# 实时日志
kubectl logs -n fjn -l app=docker-agent -f

# 最近 100 行
kubectl logs -n fjn -l app=docker-agent --tail=100
```

### 权限问题

Agent 需要以下 K8S 权限：
- 创建/删除 Pod
- 获取 Pod 状态和日志
- 在 Pod 中执行命令
- 创建/删除 ConfigMap

如果权限不足，检查 `k8s/docker-agent-deployment.yaml` 中的 RBAC 配置。

## ❓ 常见问题

### Q1: 如何修改 Agent 使用的模型？

**A**: 编辑 `config/user_model_config.py` 文件：

```python
AGENT_MODEL = {
    "model": "your-model-name",  # 修改这里
    "temperature": 0.7,
    "top_p": 0.9
}
```

### Q2: 如何修改 K8S 命名空间？

**A**: 编辑 `config/user_model_config.py` 文件：

```python
K8S_NAMESPACE = "your-namespace"  # 修改这里
```

或者直接在 K8S YAML 文件中修改。

### Q3: 如何配置自己的镜像仓库？

**A**: 编辑 `config/k8s_deployment_config.py` 文件：

```python
IMAGE_REGISTRY = "your-registry.com"
IMAGE_PROJECT = "your-project"
```

同时在 K8S YAML 中更新 `imagePullSecrets`。

### Q4: 如何添加自定义工具？

**A**: 在 `src/tools/` 目录下创建新的工具文件，例如 `my_tool.py`：

```python
from langchain.tools import tool

@tool
def my_custom_tool(param: str) -> str:
    """自定义工具描述"""
    # 实现工具逻辑
    return "result"
```

然后在 `src/agents/agent.py` 中导入并注册工具。

### Q5: Agent 支持哪些 LLM 模型？

**A**: 目前支持以下模型（通过技能集成）：
- 豆包（Seed/Doubao）
- DeepSeek
- Kimi

你可以通过 `load_skill` 查看支持的完整模型列表。

### Q6: 如何查看 Agent 的执行历史？

**A**: Agent 内置了短期记忆功能，默认保留最近 20 轮对话。可以通过日志查看完整历史：

```bash
kubectl logs -n fjn -l app=docker-agent
```

### Q7: 验证 Pod 创建失败怎么办？

**A**: 检查以下几点：
1. GPU 资源是否充足
2. PVC 存储是否可用
3. 镜像是否可以拉取
4. RBAC 权限是否正确

查看详细日志：
```bash
kubectl logs -n fjn <validation-pod-name>
```

### Q8: 如何配置 Agent 使用 HTTPS？

**A**: 在 `k8s/docker-agent-deployment.yaml` 中配置 Ingress：

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-docker-agent
  namespace: fjn
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - docker-agent.yourdomain.com
    secretName: docker-agent-tls
  rules:
  - host: docker-agent.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: svc-docker-agent
            port:
              number: 8000
```

## 📚 更多文档

- [用户模型配置文档](docs/USER_MODEL_CONFIG.md) - 详细的模型配置说明
- [K8S 部署配置文档](docs/K8S_DEPLOYMENT.md) - K8S 部署配置详解
- [K8S 部署和使用文档](docs/K8S_DEPLOY_USAGE.md) - K8S 部署和使用指南
- [K8S 快速部署指南](k8s/README.md) - 快速部署到 K8S

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
