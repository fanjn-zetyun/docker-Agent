# Docker Agent Web UI 使用指南

Docker Agent Web UI 是一个基于 Streamlit 的可视化界面，让你可以通过浏览器轻松操作和监控 Agent。

## 📋 功能特性

- 💬 **聊天交互**：与 Agent 进行自然语言对话
- 📊 **任务监控**：查看对话历史和执行状态
- 🔍 **K8S 状态**：实时监控 Kubernetes 集群状态
- 📋 **日志查看**：实时查看 Agent 和 Pod 日志
- 🎨 **界面美观**：现代化的 UI 设计

## 🚀 快速开始

### 方式一：使用启动脚本（推荐）

#### Linux/Mac

```bash
# 赋予执行权限
chmod +x scripts/start_web_ui.sh

# 启动 Web UI
./scripts/start_web_ui.sh

# 自定义配置
API_BASE_URL=http://your-api:8000 ./scripts/start_web_ui.sh
```

#### Windows

```cmd
# 双击运行
scripts\start_web_ui.bat

# 或命令行运行
cd scripts
start_web_ui.bat
```

### 方式二：直接使用 streamlit

```bash
# 安装依赖
pip install streamlit

# 启动 Web UI
streamlit run src/web_ui.py

# 自定义端口和地址
streamlit run src/web_ui.py --server.port 8502 --server.address 0.0.0.0
```

### 方式三：在 K8S 中部署

如果你想将 Web UI 也部署到 K8S，可以使用以下配置：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: deploy-web-ui
  namespace: fjn
spec:
  replicas: 1
  selector:
    matchLabels:
      app: web-ui
  template:
    metadata:
      labels:
        app: web-ui
    spec:
      containers:
      - name: web-ui
        image: registry.hd-02.alayanew.com:8443/alayanew-4fd285c4-c4f3-4e92-80ee-26169717cba8/docker-agent:latest
        command: ["streamlit"]
        args: ["run", "src/web_ui.py", "--server.port", "8501", "--server.address", "0.0.0.0", "--server.headless", "true"]
        ports:
        - containerPort: 8501
        env:
        - name: API_BASE_URL
          value: "http://svc-docker-agent.fjn.svc.cluster.local:8000"
        - name: K8S_NAMESPACE
          value: "fjn"
```

## 📖 界面说明

### 侧边栏（左侧）

#### API 配置
- **API 地址**：Agent HTTP 服务的地址，默认为 `http://localhost:8000`
- **K8S 命名空间**：Kubernetes 命名空间，默认为 `fjn`

#### 快捷操作
- **刷新状态**：刷新页面和 K8S 状态
- **清空聊天**：清除当前对话历史

#### K8S 状态
显示 Agent Pod 的实时状态：
- Pod 名称
- 运行状态（Running/Stopped）
- 运行时长

#### 系统信息
- 当前命名空间
- API 地址
- 当前时间

### 主要标签页

#### 1. 💬 聊天交互

这是主要的工作区域，你可以：

- **输入指令**：在聊天输入框中输入你的指令
- **查看回复**：Agent 的回复会实时显示在聊天区域
- **查看历史**：所有对话都会保存在当前会话中

**常用指令示例**：
```
帮我构建 LlamaFactory 镜像
验证刚才构建的镜像
查看当前 K8S 集群状态
诊断镜像构建失败的原因
```

#### 2. 📊 任务监控

显示 Agent 的运行统计信息：

- **总对话数**：当前会话的对话轮数
- **当前会话**：会话计数
- **运行时长**：Agent 运行时间（待实现）

**对话历史**：
查看所有历史对话，可以展开查看详细内容。

#### 3. 🔍 K8S 状态

监控 Kubernetes 集群状态：

**Agent Pods**：
- 显示所有 Agent Pod 的详细信息
- 包括名称、状态、节点 IP 等

**健康检查**：
- 点击"检查健康状态"按钮测试 Agent 服务
- 显示健康检查结果

**服务状态**：
- 显示 Agent 服务的配置信息
- 包括 ClusterIP、NodePort 等

**资源使用**：
- 显示 CPU 和内存使用情况
- 需要 Metrics Server 支持

**Agent 日志**：
- 实时查看 Agent 日志
- 可自定义行数
- 支持滚动查看

#### 4. 📝 使用说明

详细的使用指南和常见问题解答。

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `API_BASE_URL` | Agent API 地址 | `http://localhost:8000` |
| `K8S_NAMESPACE` | K8S 命名空间 | `fjn` |
| `COZE_WORKSPACE_PATH` | 工作目录 | `/workspace/projects` |

### Streamlit 配置

你可以在 `.streamlit/config.toml` 文件中自定义配置：

```toml
[server]
port = 8501
address = "0.0.0.0"
headless = true

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1e88e5"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

## 🎨 界面预览

### 主界面
```
┌─────────────────────────────────────────────────────────────┐
│  🐳 Docker Agent                                            │
│  ┌─────────────────┐  ┌──────────────────────────────────┐ │
│  │  侧边栏         │  │  主内容区                         │ │
│  │                 │  │  ┌────────────────────────────┐  │ │
│  │  API 配置       │  │  │ 💬 聊天交互                │  │ │
│  │  快捷操作       │  │  │ 📊 任务监控                │  │ │
│  │  K8S 状态       │  │  │ 🔍 K8S 状态                │  │ │
│  │  系统信息       │  │  │ 📝 使用说明                │  │ │
│  └─────────────────┘  └──────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 聊天界面
```
┌─────────────────────────────────────────────────────────────┐
│  💬 聊天交互                                                 │
├─────────────────────────────────────────────────────────────┤
│  👤 用户                                                     │
│  帮我构建 LlamaFactory 镜像                                  │
│                                                             │
│  🤖 Agent                                                    │
│  好的，我来帮你构建镜像。首先让我拉取官方仓库的最新代码...     │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 输入你的指令...                                      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🔍 故障排查

### 1. 无法连接到 Agent 服务

**问题**：显示"无法连接到 Agent 服务"

**解决**：
- 检查 API 地址是否正确
- 确认 Agent 服务正在运行
- 检查防火墙设置

### 2. K8S 状态无法显示

**问题**：K8S 状态显示错误或空白

**解决**：
- 确认 kubectl 已正确配置
- 检查是否有访问 K8S 的权限
- 确认命名空间名称正确

### 3. 日志无法获取

**问题**：点击"获取日志"失败

**解决**：
- 检查 Pod 是否正在运行
- 确认有足够的权限访问日志
- 检查网络连接

### 4. 页面样式异常

**问题**：界面显示不正常或样式错乱

**解决**：
- 清除浏览器缓存
- 尝试使用 Chrome 或 Edge 浏览器
- 检查 Streamlit 版本

## 💡 使用技巧

### 1. 自动刷新

Streamlit 会自动检测文件变化并刷新页面。如果不想自动刷新，可以：

```bash
streamlit run src/web_ui.py --server.fileWatcherType none
```

### 2. 端口自定义

如果 8501 端口被占用，可以使用其他端口：

```bash
streamlit run src/web_ui.py --server.port 8502
```

### 3. 日志保存

可以将 Streamlit 日志保存到文件：

```bash
streamlit run src/web_ui.py > streamlit.log 2>&1
```

### 4. 后台运行

在 Linux/Mac 上，可以使用 nohup 后台运行：

```bash
nohup streamlit run src/web_ui.py > /dev/null 2>&1 &
```

## 📱 移动端访问

Web UI 支持移动端访问，但建议使用以下方式：

### 端口转发 + VPN

```bash
# 本地端口转发
kubectl port-forward -n fjn svc/docker-agent 8000:8000
kubectl port-forward -n fjn svc/web-ui 8501:8501

# 然后通过 VPN 访问
```

### 使用 Ingress

配置 Ingress 暴露 Web UI：

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-web-ui
  namespace: fjn
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: web-ui.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: svc-web-ui
            port:
              number: 8501
```

## 🔐 安全建议

### 1. 访问控制

在生产环境中，建议添加身份验证：

```python
import streamlit as st

def check_password():
    def password_entered():
        if st.session_state["password"] == "your_password":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        return True

if not check_password():
    st.stop()
```

### 2. HTTPS

在生产环境中，建议使用 HTTPS：

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-web-ui
  namespace: fjn
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - web-ui.yourdomain.com
    secretName: web-ui-tls
```

### 3. 限制访问

使用 NetworkPolicy 限制访问来源：

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-ui-netpol
  namespace: fjn
spec:
  podSelector:
    matchLabels:
      app: web-ui
  policyTypes:
  - Ingress
  ingress:
  - from:
    - ipBlock:
        cidr: 10.0.0.0/8
    ports:
    - protocol: TCP
      port: 8501
```

## 🎉 总结

Docker Agent Web UI 提供了一个简单易用的可视化界面，让你可以：

✅ 轻松与 Agent 对话
✅ 实时监控任务状态
✅ 查看 K8S 集群状态
✅ 查看实时日志
✅ 美观的用户界面

开始使用吧！如果遇到问题，请参考故障排查部分。
