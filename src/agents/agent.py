"""
LlamaFactory 镜像构建 Agent
专门负责自动化构建和验证 LlamaFactory 的 Docker 镜像
"""
import os
import json
from typing import Annotated
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage
from coze_coding_utils.runtime_ctx.context import default_headers
from storage.memory.memory_saver import get_memory_saver

# 导入 Git 工具
from tools.git_tools import git_pull, git_checkout, git_merge, git_status

# 导入 Dockerfile 分析工具
from tools.dockerfile_analyzer import analyze_dockerfile, learn_dockerfile_pattern, validate_dockerfile

# 导入 Docker 工具
from tools.docker_tools import build_docker_image, push_docker_image

# 导入 K8S 工具
from tools.k8s_tools import (
    k8s_get_current_namespace,
    k8s_create_pod,
    k8s_get_pod_status,
    k8s_get_pod_logs,
    k8s_delete_pod,
    k8s_wait_for_pod_ready,
    k8s_exec_command
)

# 导入验证工具
from tools.llamafactory_validator import (
    verify_llama_factory_installation,
    run_llama_factory_training,
    run_quick_validation
)

LLM_CONFIG = "config/agent_llm_config.json"
USER_MODEL_CONFIG = "config/user_model_config.py"

# 默认保留最近 20 轮对话 (40 条消息)
MAX_MESSAGES = 40


def _load_user_model_config():
    """
    加载用户自定义模型配置

    Returns:
        用户配置字典，如果配置文件不存在则返回 None
    """
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    user_config_path = os.path.join(workspace_path, USER_MODEL_CONFIG)

    if not os.path.exists(user_config_path):
        return None

    try:
        # 动态导入用户配置
        import sys
        sys.path.insert(0, os.path.dirname(user_config_path))

        config_module_name = os.path.splitext(os.path.basename(user_config_path))[0]
        config_module = __import__(config_module_name)

        return config_module
    except Exception as e:
        # 如果配置文件加载失败，使用默认配置
        print(f"⚠️  加载用户模型配置失败: {str(e)}，使用默认配置")
        return None


def _windowed_messages(old, new):
    """滑动窗口: 只保留最近 MAX_MESSAGES 条消息"""
    return add_messages(old, new)[-MAX_MESSAGES:]  # type: ignore


class AgentState(MessagesState):
    messages: Annotated[list[AnyMessage], _windowed_messages]


def build_agent(ctx=None):
    """
    构建 LlamaFactory 镜像构建 Agent

    Returns:
        构建好的 Agent 实例
    """
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, LLM_CONFIG)

    # 读取配置文件
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    # 尝试加载用户自定义模型配置
    user_config = _load_user_model_config()

    # 确定使用的模型配置
    model_config = cfg['config']

    if user_config and hasattr(user_config, 'AGENT_MODEL'):
        # 检查用户是否配置了自定义模型
        user_agent_model = user_config.AGENT_MODEL

        # 检查是否是自定义端点（包含 api_key 和 base_url）
        if 'api_key' in user_agent_model and 'base_url' in user_agent_model:
            # 使用自定义模型端点
            api_key = user_agent_model['api_key']
            base_url = user_agent_model['base_url']
            model_config['model'] = user_agent_model['model']
            print(f"✅ 使用自定义模型端点: {base_url}")
        else:
            # 使用内置模型，但使用用户指定的模型名称
            model_config['model'] = user_agent_model['model']
            print(f"✅ 使用用户配置的内置模型: {model_config['model']}")

        # 更新其他配置参数
        if 'temperature' in user_agent_model:
            model_config['temperature'] = user_agent_model['temperature']
        if 'top_p' in user_agent_model:
            model_config['top_p'] = user_agent_model['top_p']
        if 'max_completion_tokens' in user_agent_model:
            model_config['max_completion_tokens'] = user_agent_model['max_completion_tokens']
        if 'timeout' in user_agent_model:
            model_config['timeout'] = user_agent_model['timeout']
        if 'thinking' in user_agent_model:
            model_config['thinking'] = user_agent_model['thinking']
    else:
        # 使用默认配置
        print(f"ℹ️  使用默认模型: {model_config['model']}")

    # 获取环境变量中的 API Key 和 Base URL（如果用户配置中没有指定）
    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")

    # 初始化 LLM
    llm = ChatOpenAI(
        model=model_config.get("model"),
        api_key=api_key,
        base_url=base_url,
        temperature=model_config.get('temperature', 0.7),
        streaming=True,
        timeout=model_config.get('timeout', 600),
        extra_body={
            "thinking": {
                "type": model_config.get('thinking', 'disabled')
            }
        },
        default_headers=default_headers(ctx) if ctx else {}
    )

    # 构建工具列表（按功能分组）
    tools = [
        # Git 操作工具
        git_pull,
        git_checkout,
        git_merge,
        git_status,

        # Dockerfile 分析工具
        analyze_dockerfile,
        learn_dockerfile_pattern,
        validate_dockerfile,

        # Docker 工具
        build_docker_image,
        push_docker_image,

        # K8S 工具
        k8s_get_current_namespace,
        k8s_create_pod,
        k8s_get_pod_status,
        k8s_get_pod_logs,
        k8s_delete_pod,
        k8s_wait_for_pod_ready,
        k8s_exec_command,

        # 验证工具
        verify_llama_factory_installation,
        run_llama_factory_training,
        run_quick_validation
    ]

    # 创建 Agent，带短期记忆功能
    agent = create_agent(
        model=llm,
        system_prompt=cfg.get("sp"),
        tools=tools,
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
    )

    return agent
