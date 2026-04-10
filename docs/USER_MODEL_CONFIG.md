# 用户自定义模型配置指南

本指南介绍如何配置 Agent 使用的模型，包括 Agent 自身的 LLM 模型和验证阶段使用的模型。

## 📋 配置文件位置

用户模型配置文件位于：`config/user_model_config.py`

## 🎯 配置项说明

### 1. Agent LLM 模型配置

Agent 使用的 LLM 模型，用于理解用户意图、决策和执行任务。

#### 方式一：使用内置模型（推荐）

从以下可用模型中选择一个：

| 模型名称 | 描述 |
|---------|------|
| `doubao-seed-2-0-pro-260215` | 旗舰级通用模型，复杂推理能力强 |
| `doubao-seed-2-0-lite-260215` | 均衡性能和成本，适合生产环境 |
| `doubao-seed-2-0-mini-260215` | 快速响应、低成本，适合轻量任务 |
| `doubao-seed-1-8-251228` | 多模态 Agent 优化模型 |
| `doubao-seed-1-6-251015` | 能力多面手，应用场景丰富 |
| `deepseek-v3-2-251201` | DeepSeek V3.2 模型 |
| `kimi-k2-5-260127` | Kimi 智能模型 |
| `glm-4-7-251222` | GLM-4.7 模型 |

**配置示例**：

```python
AGENT_MODEL = {
    "model": "doubao-seed-1-6-251015",
    "temperature": 0.7,
    "top_p": 0.9,
    "max_completion_tokens": 10000,
    "timeout": 600,
    "thinking": "disabled"
}
```

#### 方式二：使用自定义模型端点

如果你有自己的模型端点（如 OpenAI、本地部署的模型等），可以配置自定义端点：

```python
AGENT_MODEL = {
    "model": "your-custom-model-name",
    "api_key": "your-api-key",
    "base_url": "https://your-model-endpoint.com/v1",
    "temperature": 0.7,
    "top_p": 0.9,
    "max_completion_tokens": 10000,
    "timeout": 600,
    "thinking": "disabled"
}
```

### 2. 验证阶段模型配置

用于验证 LlamaFactory 镜像时运行的模型微调任务。

#### 快速验证模型

用于快速验证的小模型：

```python
VALIDATION_QUICK_MODEL = {
    "model_name_or_path": "Qwen/Qwen2-0.5B-Instruct",
    "template": "qwen"
}
```

#### 完整验证模型

用于完整验证的稍大模型：

```python
VALIDATION_FULL_MODEL = {
    "model_name_or_path": "Qwen/Qwen2-1.5B-Instruct",
    "template": "qwen"
}
```

#### 验证数据集配置

```python
VALIDATION_DATASET = {
    "name": "alpaca_zh_demo",
    "max_samples": 10  # 使用少量样本快速验证
}
```

### 3. Kubernetes 配置

```python
# 命名空间（留空则自动检测）
K8S_NAMESPACE = None

# Pod 资源限制
K8S_POD_RESOURCES = {
    "cpu": "4",
    "memory": "8Gi"
}

# Pod 超时时间（秒）
K8S_POD_TIMEOUT = 600
```

## 🔧 配置步骤

1. **打开配置文件**
   ```bash
   vim config/user_model_config.py
   ```

2. **编辑配置项**
   - 选择你要使用的 Agent 模型
   - 配置验证阶段使用的模型
   - 调整其他参数（如温度、超时等）

3. **保存文件**

4. **重启 Agent**
   配置会在下次 Agent 启动时自动加载

## 📝 参数说明

### Agent 模型参数

| 参数 | 说明 | 默认值 |
|-----|------|--------|
| `model` | 模型名称 | `doubao-seed-1-6-251015` |
| `temperature` | 温度参数，控制随机性 | `0.7` |
| `top_p` | Top-p 采样参数 | `0.9` |
| `max_completion_tokens` | 最大完成 token 数 | `10000` |
| `timeout` | 请求超时时间（秒） | `600` |
| `thinking` | 思考模式 | `disabled` |

### 验证参数

| 参数 | 说明 | 默认值 |
|-----|------|--------|
| `model_name_or_path` | 模型路径 | `Qwen/Qwen2-0.5B-Instruct` |
| `template` | 模板类型 | `qwen` |
| `max_samples` | 验证样本数 | `10` |

## 🚨 注意事项

1. **模型选择**
   - 选择模型时考虑计算资源和响应速度
   - 验证阶段使用小模型可以加快验证速度

2. **配置优先级**
   - 函数参数 > 用户配置 > 默认配置
   - 如果在调用工具时提供了参数，会优先使用提供的参数

3. **自定义端点**
   - 确保自定义端点可访问
   - API Key 需要有足够的权限
   - 基础 URL 必须包含 `/v1` 后缀

4. **配置文件位置**
   - 配置文件必须在 `config/user_model_config.py`
   - 文件名不能修改
   - Python 语法必须正确

## 💡 示例场景

### 场景 1：使用 DeepSeek 模型

```python
AGENT_MODEL = {
    "model": "deepseek-v3-2-251201",
    "temperature": 0.7,
    "top_p": 0.9,
    "max_completion_tokens": 10000,
    "timeout": 600,
    "thinking": "disabled"
}
```

### 场景 2：使用自定义 OpenAI 兼容端点

```python
AGENT_MODEL = {
    "model": "gpt-4",
    "api_key": "sk-xxxxxxxxxxxx",
    "base_url": "https://api.openai.com/v1",
    "temperature": 0.7,
    "top_p": 0.9,
    "max_completion_tokens": 10000,
    "timeout": 600,
    "thinking": "disabled"
}
```

### 场景 3：调整验证样本数

```python
VALIDATION_DATASET = {
    "name": "alpaca_zh_demo",
    "max_samples": 20  # 增加样本数进行更全面的验证
}
```

## 🔍 验证配置

启动 Agent 时，会显示当前使用的模型配置：

```
✅ 使用用户配置的内置模型: deepseek-v3-2-251201
```

如果配置加载失败，会显示警告并使用默认配置：

```
⚠️  加载用户模型配置失败: [错误信息]，使用默认配置
ℹ️  使用默认模型: doubao-seed-1-6-251015
```

## 📞 常见问题

### Q: 配置修改后不生效？
A: 需要重启 Agent 才能加载新配置。

### Q: 如何知道当前使用的模型？
A: 查看 Agent 启动日志，会显示当前使用的模型。

### Q: 可以配置多个模型吗？
A: 目前不支持同时使用多个模型，但可以在验证阶段配置不同的验证模型。

### Q: 自定义端点连接失败怎么办？
A: 检查：
1. API Key 是否正确
2. 基础 URL 是否可访问
3. 网络连接是否正常

## 📚 更多信息

- [LlamaFactory 官方文档](https://github.com/hiyouga/LlamaFactory)
- [模型选择指南](https://github.com/hiyouga/LlamaFactory/blob/main/README.md)
