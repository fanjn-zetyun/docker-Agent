# LlamaFactory K8S 部署配置
# 此配置文件用于定义在 K8S 中创建验证 pod 的配置

## 镜像配置
IMAGE_CONFIG = {
    # 镜像仓库配置
    "registry": "registry.hd-02.alayanew.com:8443",
    "namespace": "alayanew-4fd285c4-c4f3-4e92-80ee-26169717cba8",
    "image_name": "llamafactory-online",
    # 构建时会自动设置 tag
}

## 镜像拉取密钥
IMAGE_PULL_SECRET = {
    "name": "lfol-secret"
}

## Pod 资源配置
# 验证时的资源配置（可适当降低以节省资源）
POD_RESOURCES = {
    "limits": {
        "cpu": "8",  # 降低 CPU
        "memory": "32Gi",  # 降低内存
        "nvidia.com/gpu-h100-80gb-hbm3": "1"  # 使用 1 个 GPU 进行验证
    },
    "requests": {
        "cpu": "4",
        "memory": "16Gi",
        "nvidia.com/gpu-h100-80gb-hbm3": "1"
    }
}

# 完整资源配置（用于生产环境）
FULL_RESOURCES = {
    "limits": {
        "cpu": "26",
        "ephemeral-storage": "64Gi",
        "memory": "400Gi",
        "nvidia.com/gpu-h100-80gb-hbm3": "2",
        "rdma/rdma_shared_device_a": "1",
        "rdma/rdma_shared_device_b": "1",
        "rdma/rdma_shared_device_c": "1",
        "rdma/rdma_shared_device_d": "1",
        "rdma/rdma_shared_device_e": "1",
        "rdma/rdma_shared_device_f": "1",
        "rdma/rdma_shared_device_g": "1",
        "rdma/rdma_shared_device_h": "1"
    },
    "requests": {
        "cpu": "26",
        "ephemeral-storage": "64Gi",
        "memory": "400Gi",
        "nvidia.com/gpu-h100-80gb-hbm3": "2",
        "rdma/rdma_shared_device_a": "1",
        "rdma/rdma_shared_device_b": "1",
        "rdma/rdma_shared_device_c": "1",
        "rdma/rdma_shared_device_d": "1",
        "rdma/rdma_shared_device_e": "1",
        "rdma/rdma_shared_device_f": "1",
        "rdma/rdma_shared_device_g": "1",
        "rdma/rdma_shared_device_h": "1"
    }
}

## Pod 环境变量
POD_ENV_VARS = {
    # S3 配置
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

## Pod 端口配置
POD_PORTS = [
    {"name": "llama-factory", "containerPort": 7860, "protocol": "TCP"},
    {"name": "jupyter", "containerPort": 8888, "protocol": "TCP"},
    {"name": "vscode", "containerPort": 8080, "protocol": "TCP"},
]

## Pod 存储配置
POD_VOLUME_MOUNTS = [
    # 用户数据目录
    {
        "name": "user-data",
        "mountPath": "/workspace",
        "subPath": "users/user-ExSWPUsC-604933c32aa84d3ca70ba9763e8a7824"
    },
    # 市场数据
    {
        "name": "user-data",
        "mountPath": "/market",
        "subPath": "market"
    },
    # 共享数据
    {
        "name": "user-data",
        "mountPath": "/shared-only",
        "subPath": "shared-only"
    },
    # 共享内存
    {
        "name": "dev-shm",
        "mountPath": "/dev/shm"
    }
]

POD_VOLUMES = [
    {
        "name": "user-data",
        "persistentVolumeClaim": {
            "claimName": "pvc-capacity-userdata"
        }
    },
    {
        "name": "dev-shm",
        "emptyDir": {
            "medium": "Memory",
            "sizeLimit": "100Gi"
        }
    }
]

## Pod 健康检查配置
READINESS_PROBE = {
    "exec": {
        "command": [
            "/bin/bash",
            "-c",
            """
            curl -sSf http://0.0.0.0:7860/ &&
            curl -sSf http://0.0.0.0:8888/ &&
            curl -sSf http://0.0.0.0:8080/
            """
        ]
    },
    "failureThreshold": 50,
    "initialDelaySeconds": 5,
    "periodSeconds": 3,
    "successThreshold": 1,
    "timeoutSeconds": 5
}

## Pod 启动命令
# 默认启动命令（用于验证）
POD_COMMAND = ["/bin/bash", "-c", "sleep infinity"]

## 验证特定的配置
VALIDATION_CONFIG = {
    # 是否使用 GPU
    "use_gpu": True,

    # GPU 数量
    "gpu_count": 1,

    # 是否使用 RDMA
    "use_rdma": False,  # 验证时通常不需要 RDMA

    # 验证超时时间（秒）
    "timeout": 1800,  # 30分钟
}

## 数据集路径
DATASET_CONFIG = {
    "dataset_dir": "/workspace/llamafactory/data",
    "model_dir": "/shared-only/models",
    "output_dir": "/workspace/user-data/models/output"
}
