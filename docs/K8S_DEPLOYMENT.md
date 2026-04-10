# LlamaFactory K8S 部署配置说明

本文档介绍 LlamaFactory Agent 在 Kubernetes 中的部署配置，包括生产环境和验证环境的配置差异。

## 📋 配置文件

K8S 部署配置文件位于：`config/k8s_deployment_config.py`

## 🎯 配置概览

### 镜像配置

```python
IMAGE_CONFIG = {
    "registry": "registry.hd-02.alayanew.com:8443",
    "namespace": "alayanew-4fd285c4-c4f3-4e92-80ee-26169717cba8",
    "image_name": "llamafactory-online",
}
```

### 镜像拉取密钥

```python
IMAGE_PULL_SECRET = {
    "name": "lfol-secret"
}
```

这个密钥存储了镜像仓库的认证信息。

### 资源配置

#### 验证环境配置（默认）

```python
POD_RESOURCES = {
    "limits": {
        "cpu": "8",
        "memory": "32Gi",
        "nvidia.com/gpu-h100-80gb-hbm3": "1"
    },
    "requests": {
        "cpu": "4",
        "memory": "16Gi",
        "nvidia.com/gpu-h100-80gb-hbm3": "1"
    }
}
```

#### 生产环境配置

```python
FULL_RESOURCES = {
    "limits": {
        "cpu": "26",
        "ephemeral-storage": "64Gi",
        "memory": "400Gi",
        "nvidia.com/gpu-h100-80gb-hbm3": "2",
        "rdma/rdma_shared_device_a": "1",
        "rdma/rdma_shared_device_b": "1",
        # ... RDMA 设备 a-h
    }
}
```

### 环境变量

```python
POD_ENV_VARS = {
    # S3 存储
    "S3_ACCESS_KEY": "IFFY4LH673KKYHBNGBFT",
    "S3_SECRET_KEY": "rQT8L9VsWZ5clAKLM2qAAYR3nKWNYDMS2Bsh0u8N",
    "S3_ENDPOINT": "https://s3.hd-02.alayanew.com:8082",

    # Conda 环境
    "CONDA_NAME": "lf",

    # 服务开关
    "VSCODE_ENABLED": "1",
    "JUPYTER_ENABLED": "1",
    "LF_ENABLED": "1",

    # SSH 配置
    "SSH_NAME": "abc",
    "SSH_REMOTE_PORT": "38686",
    "SSH_PASSWD": "123456",
    "SSH_SERVER_ADDR": "120.220.102.25",
    "SSH_SERVER_PORT": "55080",
}
```

### 存储挂载

```python
POD_VOLUME_MOUNTS = [
    {
        "name": "user-data",
        "mountPath": "/workspace",
        "subPath": "users/user-ExSWPUsC-604933c32aa84d3ca70ba9763e8a7824"
    },
    {
        "name": "user-data",
        "mountPath": "/market",
        "subPath": "market"
    },
    {
        "name": "user-data",
        "mountPath": "/shared-only",
        "subPath": "shared-only"
    },
    {
        "name": "dev-shm",
        "mountPath": "/dev/shm"
    }
]
```

### 端口配置

```python
POD_PORTS = [
    {"name": "llama-factory", "containerPort": 7860},
    {"name": "jupyter", "containerPort": 8888},
    {"name": "vscode", "containerPort": 8080},
]
```

## 🚀 使用方式

### 创建验证 pod

```python
# 使用验证资源配置（默认）
k8s_create_validation_pod(
    namespace="llama-test",
    pod_name="llama-factory-validation",
    image="registry.hd-02.alayanew.com:8443/alayanew-4fd285c4-c4f3-4e92-80ee-26169717cba8/llamafactory-online:lf0.9.5-tf5.5.0-torch2.8.0-cu12.6-1.0-nydus",
    use_full_resources=False  # 使用验证配置（1 GPU）
)
```

### 创建生产 pod

```python
# 使用完整生产资源配置
k8s_create_validation_pod(
    namespace="llama-test",
    pod_name="llama-factory-prod",
    image="registry.hd-02.alayanew.com:8443/alayanew-4fd285c4-c4f3-4e92-80ee-26169717cba8/llamafactory-online:lf0.9.5-tf5.5.0-torch2.8.0-cu12.6-1.0-nydus",
    use_full_resources=True  # 使用生产配置（2 GPU + RDMA）
)
```

## 📊 配置差异对比

| 配置项 | 验证环境 | 生产环境 |
|--------|----------|----------|
| CPU | 8 核 | 26 核 |
| 内存 | 32Gi | 400Gi |
| GPU | 1x H100 | 2x H100 |
| RDMA | 不使用 | 使用 (a-h 8个设备) |
| 用途 | 镜像验证 | 实际训练 |

## 🔧 自定义配置

### 修改资源配置

编辑 `config/k8s_deployment_config.py`：

```python
# 降低验证资源配置
POD_RESOURCES = {
    "limits": {
        "cpu": "4",  # 从 8 降低到 4
        "memory": "16Gi",  # 从 32Gi 降低到 16Gi
        "nvidia.com/gpu-h100-80gb-hbm3": "1"
    }
}
```

### 修改存储挂载

```python
# 更换不同的用户数据目录
POD_VOLUME_MOUNTS = [
    {
        "name": "user-data",
        "mountPath": "/workspace",
        "subPath": "users/your-user-id-here"  # 修改这里
    }
]
```

### 添加新的环境变量

```python
POD_ENV_VARS = {
    # ... 现有变量
    "NEW_ENV_VAR": "value",  # 添加新变量
}
```

## 🎯 验证流程

### 完整验证流程

1. **创建验证 pod**
   ```python
   k8s_create_validation_pod(namespace, pod_name, image)
   ```

2. **等待 pod 就绪**
   ```python
   k8s_wait_for_pod_ready(namespace, pod_name, timeout=1800)
   ```

3. **验证 LlamaFactory 安装**
   ```python
   verify_llama_factory_installation(namespace, pod_name)
   ```

4. **运行快速验证**
   ```python
   run_quick_validation(namespace, pod_name)
   ```

5. **运行完整微调验证**
   ```python
   run_llama_factory_training(namespace, pod_name)
   ```

6. **清理测试 pod**
   ```python
   k8s_delete_pod(namespace, pod_name)
   ```

## 📝 注意事项

### 1. GPU 资源分配

- 验证环境：使用 1 个 GPU 节省资源
- 生产环境：使用 2 个 GPU 提升性能

### 2. RDMA 设备

- 验证环境通常不需要 RDMA
- 生产环境使用 RDMA 提升多 GPU 通信效率

### 3. 存储路径

- `/workspace`: 用户数据目录
- `/market`: 市场数据
- `/shared-only`: 共享模型数据
- `/dev/shm`: 共享内存（100Gi）

### 4. 网络配置

- `7860`: LlamaFactory API
- `8888`: Jupyter Notebook
- `8080`: VSCode Server

### 5. 健康检查

Pod 会自动检查三个服务是否正常运行：
- LlamaFactory API (7860)
- Jupyter (8888)
- VSCode (8080)

## 🔍 故障排查

### Pod 启动失败

```bash
# 查看 pod 状态
kubectl get pod -n <namespace> <pod_name>

# 查看详细信息
kubectl describe pod -n <namespace> <pod_name>

# 查看日志
kubectl logs -n <namespace> <pod_name>
```

### 镜像拉取失败

1. 检查镜像拉取密钥是否正确
2. 检查网络连接
3. 确认镜像名称和标签正确

### GPU 不可用

```bash
# 检查 GPU 资源
kubectl describe node <node-name> | grep -A 10 "Allocated resources"

# 检查 pod 的 GPU 请求
kubectl get pod -n <namespace> <pod_name> -o jsonpath='{.spec.containers[*].resources}'
```

### 存储挂载失败

1. 确认 PVC 存在
2. 检查 subPath 是否正确
3. 确认权限设置

## 📚 相关文档

- [Kubernetes Pod 文档](https://kubernetes.io/docs/concepts/workloads/pods/)
- [NVIDIA GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/)
- [LlamaFactory 官方文档](https://github.com/hiyouga/LlamaFactory)

## 🆘 常见问题

### Q: 如何切换到生产配置？
A: 调用 `k8s_create_validation_pod` 时设置 `use_full_resources=True`

### Q: 可以同时运行多个验证 pod 吗？
A: 可以，但需要确保有足够的 GPU 资源

### Q: 验证完成后会自动删除 pod 吗？
A: 不会，需要手动调用 `k8s_delete_pod` 清理

### Q: 如何修改超时时间？
A: 在 `config/k8s_deployment_config.py` 中修改 `VALIDATION_CONFIG["timeout"]`

## 🎉 总结

通过这个配置文件，Agent 可以：

1. ✅ 创建与生产环境一致的验证 pod
2. ✅ 使用正确的资源配额和存储挂载
3. ✅ 访问 S3 存储和其他服务
4. ✅ 完整验证 LlamaFactory 镜像功能
5. ✅ 节省验证时的资源消耗

确保配置正确后，Agent 就可以自动化地完成镜像构建和验证流程！
