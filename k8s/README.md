# Docker Agent K8S 部署快速指南

## 🚀 快速部署

### 1. 修改镜像地址

打开 `k8s/docker-agent-deployment.yaml`，找到并修改：

```yaml
# 第 150 行左右
image: registry.hd-02.alayanew.com:8443/alayanew-4fd285c4-c4f3-4e92-80ee-26169717cba8/docker-agent:latest
```

修改为你构建好的镜像地址。

### 2. 一键部署

```bash
# 部署到 K8S
kubectl apply -f k8s/docker-agent-deployment.yaml

# 查看部署状态
kubectl get pods -n llama-factory -l app=docker-agent
```

### 3. 访问 Agent

#### 方式 A：端口转发（推荐用于测试）

```bash
# 端口转发到本地
kubectl port-forward -n llama-factory deploy/docker-agent 8000:8000

# 新开一个终端测试
curl http://localhost:8000/health
```

#### 方式 B：NodePort

```bash
# 获取节点 IP
kubectl get nodes -o wide

# 通过节点 IP:30800 访问
curl http://<node-ip>:30800/health
```

#### 方式 C：ClusterIP（集群内）

```bash
# 在集群内的其他 pod 中访问
curl http://svc-docker-agent.llama-factory.svc.cluster.local:8000/health
```

## 📋 配置说明

### 需要修改的内容

| 配置项 | 位置 | 说明 |
|--------|------|------|
| 镜像地址 | Deployment spec | 修改为你的镜像地址 |
| API Key | Secret | 如果使用自定义模型 |
| S3 配置 | Secret | 如果需要 S3 存储 |
| 存储类 | PVC spec | 根据你的集群修改 storageClassName |

### 默认配置

- **命名空间**: `llama-factory`
- **Service**: ClusterIP + NodePort (30800)
- **资源**: 2-4 CPU, 4-8Gi 内存
- **存储**: 20Gi 工作空间

## 🧪 测试 Agent

### 健康检查

```bash
curl http://localhost:8000/health
```

### 测试调用

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "type": "query",
    "session_id": "test-001",
    "message": "测试 Agent",
    "content": {
      "query": {
        "prompt": [
          {
            "type": "text",
            "content": {
              "text": "你好，请介绍一下你的功能"
            }
          }
        ]
      }
    }
  }'
```

## 📊 监控和日志

### 查看日志

```bash
# 实时日志
kubectl logs -n llama-factory -l app=docker-agent -f

# 查看 pod 名称
kubectl get pods -n llama-factory -l app=docker-agent

# 查看特定 pod 日志
kubectl logs -n llama-factory <pod-name> -f
```

### 查看状态

```bash
# Pod 状态
kubectl get pods -n llama-factory -l app=docker-agent

# Service 状态
kubectl get svc -n llama-factory -l app=docker-agent

# 详细信息
kubectl describe pod -n llama-factory -l app=docker-agent
```

## 🔧 常用操作

### 重启 Agent

```bash
kubectl rollout restart deployment/deploy-docker-agent -n llama-factory
```

### 扩容

```bash
kubectl scale deployment/deploy-docker-agent --replicas=3 -n llama-factory
```

### 更新镜像

```yaml
# 修改 YAML 中的镜像版本，然后
kubectl apply -f k8s/docker-agent-deployment.yaml
```

### 删除部署

```bash
kubectl delete -f k8s/docker-agent-deployment.yaml
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
kubectl get svc -n llama-factory -l app=docker-agent

# 检查 Endpoint
kubectl get endpoints -n llama-factory svc-docker-agent
```

### 权限问题

Agent 需要 RBAC 权限来创建和管理 pod。YAML 中已配置，但如果失败：

```bash
# 检查 RoleBinding
kubectl get rolebinding -n llama-factory docker-agent-rolebinding -o yaml
```

## 📝 配置示例

### 使用自定义模型

1. 修改 Secret 中的 api-key

```yaml
stringData:
  api-key: "your-actual-api-key"
```

2. 取消注释环境变量

```yaml
env:
- name: COZE_INTEGRATION_MODEL_BASE_URL
  value: "https://your-model-endpoint.com/v1"
```

3. 应用配置

```bash
kubectl apply -f k8s/docker-agent-deployment.yaml
```

### 与 LlamaFactory 共享存储

默认已配置共享存储挂载：

```yaml
volumeMounts:
- name: shared-data
  mountPath: /shared-only
  readOnly: false

volumes:
- name: shared-data
  persistentVolumeClaim:
    claimName: pvc-capacity-userdata
```

## ✅ 部署检查清单

- [ ] 修改镜像地址为你的镜像
- [ ] 确认 PVC 的 storageClassName 正确
- [ ] 确认镜像拉取密钥 `lfol-secret` 存在
- [ ] 部署 YAML 文件
- [ ] 等待 Pod 就绪
- [ ] 测试健康检查
- [ ] 测试 Agent 调用

## 🎉 完成！

部署完成后，Agent 就可以通过 HTTP API 访问了！

详细的使用文档请参考 `docs/K8S_DEPLOY_USAGE.md`。
