# 用户自定义模型配置
# 此文件用于配置 Agent 使用的模型和验证阶段使用的模型

## Agent LLM 模型配置
# Agent 使用的 LLM 模型，用于理解用户意图和决策

### 方式一：使用内置模型（推荐）
# 从以下可用模型中选择一个：
# - doubao-seed-2-0-pro-260215: 旗舰级通用模型
# - doubao-seed-2-0-lite-260215: 均衡性能和成本
# - doubao-seed-2-0-mini-260215: 快速响应、低成本
# - doubao-seed-1-8-251228: 多模态 Agent 优化模型
# - doubao-seed-1-6-251015: 能力多面手
# - deepseek-v3-2-251201: DeepSeek V3.2 模型
# - kimi-k2-5-260127: Kimi 智能模型
# - glm-4-7-251222: GLM-4.7 模型

AGENT_MODEL = {
    "model": "doubao-seed-1-6-251015",
    "temperature": 0.7,
    "top_p": 0.9,
    "max_completion_tokens": 10000,
    "timeout": 600,
    "thinking": "disabled"
}

### 方式二：使用自定义模型端点
# 如果你有自己的模型端点，取消注释并配置以下内容

# AGENT_MODEL = {
#     "model": "your-custom-model-name",
#     "api_key": "your-api-key",
#     "base_url": "https://your-model-endpoint.com/v1",
#     "temperature": 0.7,
#     "top_p": 0.9,
#     "max_completion_tokens": 10000,
#     "timeout": 600,
#     "thinking": "disabled"
# }


## 验证阶段模型配置
# 用于验证 LlamaFactory 镜像时运行的模型微调任务

# 用于快速验证的模型（小模型，快速加载）
VALIDATION_QUICK_MODEL = {
    "model_name_or_path": "Qwen/Qwen2-0.5B-Instruct",
    "template": "qwen"
}

# 用于完整验证的模型（稍大，更接近实际使用）
VALIDATION_FULL_MODEL = {
    "model_name_or_path": "Qwen/Qwen2-1.5B-Instruct",
    "template": "qwen"
}

# 验证数据集配置
VALIDATION_DATASET = {
    "name": "alpaca_zh_demo",
    "max_samples": 10
}

# 验证训练参数（简化配置，快速验证）
VALIDATION_TRAINING_ARGS = {
    "stage": "sft",
    "finetuning_type": "lora",
    "lora_target": "q_proj,v_proj",
    "per_device_train_batch_size": 2,
    "gradient_accumulation_steps": 4,
    "lr_scheduler_type": "cosine",
    "logging_steps": 10,
    "save_steps": 100,
    "learning_rate": 5.0e-5,
    "num_train_epochs": 1.0,
    "plot_loss": True,
    "fp16": True
}

# 验证输出配置
VALIDATION_OUTPUT = {
    "output_dir": "/tmp/llama_factory_output"
}

## K8S 配置
# Kubernetes 相关配置

# 命名空间配置（留空则自动检测）
K8S_NAMESPACE = None  # 例如: "llama-factory-test"

# Pod 资源限制
K8S_POD_RESOURCES = {
    "cpu": "4",
    "memory": "8Gi"
}

# Pod 超时时间（秒）
K8S_POD_TIMEOUT = 600
