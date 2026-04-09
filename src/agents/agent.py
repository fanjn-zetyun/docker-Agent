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

# 默认保留最近 20 轮对话 (40 条消息)
MAX_MESSAGES = 40


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

    # 获取环境变量中的 API Key 和 Base URL
    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")

    # 初始化 LLM
    llm = ChatOpenAI(
        model=cfg['config'].get("model"),
        api_key=api_key,
        base_url=base_url,
        temperature=cfg['config'].get('temperature', 0.7),
        streaming=True,
        timeout=cfg['config'].get('timeout', 600),
        extra_body={
            "thinking": {
                "type": cfg['config'].get('thinking', 'disabled')
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
