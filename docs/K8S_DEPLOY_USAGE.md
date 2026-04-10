# K8S 部署和使用指南

本文档说明如何将 Docker Agent 部署到 Kubernetes 集群中，并如何访问和使用。

## 📋 部署方式概览

Agent 在 K8S 中提供 HTTP 服务，支持多种访问方式：

1. **端口转发（Port Forwarding）** - 最简单，适合测试
2. **NodePort Service** - 适合内部访问
3. **ClusterIP Service** - 集群内访问
4. **Ingress** - 对外暴露（推荐生产环境）

## 🚀 方式一：端口转发（Port Forwarding）

最简单的方式，适合快速测试和开发。

### 部署 Pod

```bash
# 部署到 K8S
kubectl apply -f k8s/agent-deployment.yaml

# 等待 pod 就绪
kubectl wait --for=condition=ready pod -l app=docker-agent -n llama-factory --timeout=300s

# 查看 pod 状态
kubectl get pods -n llama-factory -l app=docker-agent
```

### 端口转发

```bash
# 端口转发到本地 8000
kubectl port-forward -n llama-factory deploy/docker-agent 8000:8000

# 或者转发特定 pod
kubectl port-forward -n llama-factory <pod-name> 8000:8000
```

### 访问 Agent

端口转发后，可以通过 `http://localhost:8000` 访问：

```bash
# 健康检查
curl http://localhost:8000/health

# 同步调用
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "type": "query",
    "session_id": "test-001",
    "message": "帮我构建一个镜像",
    "content": {
      "query": {
        "prompt": [
          {
            "type": "text",
            "content": {"text": "拉取最新代码并构建镜像"}
          }
        ]
      }
    }
  }'
```

## 🌐 方式二：NodePort Service

适合集群内部访问，不需要配置 Ingress。

### 部署

```bash
# 部署包含 NodePort Service 的配置
kubectl apply -f k8s/agent-deployment.yaml
```

### 访问

通过任意节点的 `30800` 端口访问：

```bash
# 获取节点 IP
kubectl get nodes -o wide

# 访问（替换 <node-ip>）
curl http://<node-ip>:30800/health
```

## 🔒 方式三：ClusterIP + Ingress

推荐生产环境使用，支持域名访问和 HTTPS。

### 部署 Ingress

```bash
# 创建 Ingress 配置
cat > k8s/agent-ingress.yaml <<'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-docker-agent
  namespace: llama-factory
  annotations:
    # 使用你的 Ingress Controller
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
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
EOF

# 应用配置
kubectl apply -f k8s/agent-ingress.yaml
```

### 访问

```bash
# 通过域名访问
curl https://docker-agent.yourdomain.com/health
```

## 📝 API 使用示例

### 1. 健康检查

```bash
curl http://localhost:8000/health
```

### 2. 同步调用（/run）

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "type": "query",
    "session_id": "session-123",
    "message": "构建 LlamaFactory 镜像",
    "content": {
      "query": {
        "prompt": [
          {
            "type": "text",
            "content": {
              "text": "拉取代码、合并分支、构建镜像并验证"
            }
          }
        ]
      }
    }
  }'
```

### 3. 流式调用（/stream_run）- 推荐

```bash
curl -X POST http://localhost:8000/stream_run \
  -H "Content-Type: application/json" \
  -N \
  -d '{
    "type": "query",
    "session_id": "session-456",
    "message": "验证镜像",
    "content": {
      "query": {
        "prompt": [
          {
            "type": "text",
            "content": {
              "text": "验证镜像：镜像名称 registry.example.com/myapp:latest"
            }
          }
        ]
      }
    }
  }'
```

### 4. 取消运行

```bash
# 获取 run_id（从之前的响应中）
curl -X POST http://localhost:8000/cancel/<run-id>
```

### 5. OpenAI 兼容接口

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agent",
    "messages": [
      {
        "role": "user",
        "content": "帮我构建并验证镜像"
      }
    ]
  }'
```

## 🔧 配置说明

### 环境变量

在 `k8s/agent-deployment.yaml` 中配置：

```yaml
env:
  # 工作空间路径
  - name: COZE_WORKSPACE_PATH
    value: "/workspace"

  # API Key（如果使用自定义模型）
  - name: COZE_WORKLOAD_IDENTITY_API_KEY
    valueFrom:
      secretKeyRef:
        name: docker-agent-secret
        key: api-key

  # 模型服务地址
  - name: COZE_INTEGRATION_MODEL_BASE_URL
    value: "https://api.example.com/v1"
```

### 配置文件

使用 ConfigMap 管理配置：

```yaml
configMap:
  name: docker-agent-config
data:
  agent_llm_config.json: |
    {
      "config": {
        "model": "doubao-seed-1-6-251015",
        ...
      }
    }
```

### 存储挂载

```yaml
volumeMounts:
- name: workspace
  mountPath: /workspace
- name: config
  mountPath: /workspace/config
  readOnly: true
```

## 🎯 部署到现有的 LlamaFactory Pod

如果你想在现有的 LlamaFactory Pod 中运行 Agent（使用同一个 Pod）：

### 方案 1：Sidecar 容器

在你的 Deployment 中添加 Agent 容器：

```yaml
spec:
  template:
    spec:
      containers:
      # LlamaFactory 主容器
      - name: llama-factory
        image: registry.hd-02.alayanew.com:8443/.../llamafactory-online:latest
        ...

      # Agent Sidecar 容器
      - name: docker-agent
        image: registry.hd-02.alayanew.com:8443/your-namespace/docker-agent:latest
        command: ["python", "src/main.py"]
        args: ["-m", "http", "-p", "8000"]
        ports:
        - containerPort: 8000
```

### 方案 2：共享存储的独立 Deployment

将 Agent 部署为独立的 Deployment，共享 PVC：

```yaml
volumes:
- name: shared-workspace
  persistentVolumeClaim:
    claimName: pvc-shared-workspace  # 与 LlamaFactory 共享
```

## 📊 监控和日志

### 查看日志

```bash
# 查看 Agent 日志
kubectl logs -n llama-factory -l app=docker-agent -f

# 查看特定 pod 日志
kubectl logs -n llama-factory <pod-name> -f
```

### 查看状态

```bash
# 查看 pod 状态
kubectl get pods -n llama-factory -l app=docker-agent

# 查看 Service
kubectl get svc -n llama-factory -l app=docker-agent

# 查看 Ingress
kubectl get ingress -n llama-factory
```

### 监控指标

```bash
# 实时监控
kubectl top pod -n llama-factory -l app=docker-agent
```

## 🔒 安全性

### 1. 使用 Service Account

```yaml
spec:
  template:
    spec:
      serviceAccountName: docker-agent-sa
```

### 2. 限制网络访问

```yaml
# NetworkPolicy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: docker-agent-netpol
  namespace: llama-factory
spec:
  podSelector:
    matchLabels:
      app: docker-agent
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: llama-factory
    ports:
    - protocol: TCP
      port: 8000
```

### 3. RBAC 权限

Agent 需要 K8S 权限来创建和管理 pod：

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: docker-agent-role
  namespace: llama-factory
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log", "pods/exec"]
  verbs: ["get", "list", "create", "delete", "exec"]
- apiGroups: [""]
  resources: ["pods/status"]
  verbs: ["get"]
```

## 🆘 故障排查

### Pod 无法启动

```bash
# 查看事件
kubectl describe pod -n llama-factory -l app=docker-agent

# 查看日志
kubectl logs -n llama-factory <pod-name>
```

### 无法访问服务

```bash
# 检查 Service
kubectl describe svc svc-docker-agent -n llama-factory

# 检查 Endpoint
kubectl get endpoints svc-docker-agent -n llama-factory

# 检查端口转发
kubectl port-forward -n llama-factory <pod-name> 8000:8000
```

### Agent 执行失败

```bash
# 查看详细日志
kubectl logs -n llama-factory <pod-name> --tail=100

# 进入容器调试
kubectl exec -it -n llama-factory <pod-name> -- bash
```

## 🎉 总结

### 推荐部署方式

| 场景 | 推荐方式 | 端口 |
|------|----------|------|
| 本地开发测试 | Port Forwarding | 8000 |
| 集群内部访问 | ClusterIP | 8000 |
| 生产环境 | Ingress + HTTPS | 443 |
| 快速访问 | NodePort | 30800 |

### 关键点

1. ✅ Agent 暴露 HTTP 端口 8000
2. ✅ 需要配置 RBAC 权限（创建/删除 pod）
3. ✅ 使用 ConfigMap 管理配置
4. ✅ 使用 Secret 管理敏感信息
5. ✅ 考虑与 LlamaFactory 共享存储或使用 Sidecar

根据你的需求选择合适的部署方式！
