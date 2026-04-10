"""
Docker Agent Web UI
使用 Streamlit 构建的交互式界面
"""

import streamlit as st
import requests
import json
import os
import time
from datetime import datetime
import subprocess

# 页面配置
st.set_page_config(
    page_title="Docker Agent 控制台",
    page_icon="🐳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 配置
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
K8S_NAMESPACE = os.getenv("K8S_NAMESPACE", "fjn")

# 自定义 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e88e5;
        margin-bottom: 1rem;
    }
    .status-badge {
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
    }
    .status-running {
        background-color: #d4edda;
        color: #155724;
    }
    .status-stopped {
        background-color: #f8d7da;
        color: #721c24;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 2rem;
    }
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 2rem;
    }
    .log-container {
        background-color: #1e1e1e;
        color: #d4d4d4;
        padding: 1rem;
        border-radius: 0.5rem;
        font-family: monospace;
        font-size: 0.9rem;
        max-height: 400px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.title("🐳 Docker Agent")
    st.markdown("---")

    # API 配置
    st.subheader("API 配置")
    api_url = st.text_input("API 地址", value=API_BASE_URL)
    namespace = st.text_input("K8S 命名空间", value=K8S_NAMESPACE)

    st.markdown("---")

    # 快捷操作
    st.subheader("快捷操作")
    if st.button("🔄 刷新状态", use_container_width=True):
        st.rerun()

    if st.button("🧹 清空聊天", use_container_width=True):
        if "messages" in st.session_state:
            st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    # K8S 状态
    st.subheader("K8S 状态")
    try:
        # 检查 Agent Pod 状态
        result = subprocess.run(
            ["kubectl", "get", "pods", "-n", namespace, "-l", "app=docker-agent"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                pods = lines[1:]
                for pod in pods:
                    parts = pod.split()
                    if len(parts) >= 3:
                        pod_name, status, age = parts[0], parts[2], parts[-1]
                        st.markdown(f"**{pod_name[:20]}...**")
                        st.markdown(f"<span class='status-badge status-{status.lower()}'>{status}</span>",
                                   unsafe_allow_html=True)
                        st.caption(f"运行时长: {age}")
            else:
                st.warning("未找到 Agent Pod")
        else:
            st.error("无法连接 K8S")
    except Exception as e:
        st.error(f"K8S 错误: {str(e)}")

    st.markdown("---")

    # 系统信息
    st.subheader("系统信息")
    st.markdown(f"**命名空间**: {namespace}")
    st.markdown(f"**API 地址**: {api_url}")
    st.markdown(f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 主界面
st.markdown('<div class="main-header">🤖 Docker Agent 控制台</div>', unsafe_allow_html=True)

# 创建 Tab
tab1, tab2, tab3, tab4 = st.tabs(["💬 聊天交互", "📊 任务监控", "🔍 K8S 状态", "📝 使用说明"])

# Tab 1: 聊天交互
with tab1:
    st.subheader("与 Docker Agent 对话")

    # 初始化聊天历史
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 显示聊天历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 聊天输入
    if prompt := st.chat_input("输入你的指令..."):
        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 调用 Agent API
        with st.chat_message("assistant"):
            with st.spinner("Agent 正在处理..."):
                try:
                    # 构建请求
                    request_data = {
                        "type": "query",
                        "session_id": f"web-{int(time.time())}",
                        "message": prompt,
                        "content": {
                            "query": {
                                "prompt": [
                                    {
                                        "type": "text",
                                        "content": {
                                            "text": prompt
                                        }
                                    }
                                ]
                            }
                        }
                    }

                    # 发送请求
                    response = requests.post(
                        f"{api_url}/run",
                        json=request_data,
                        timeout=120
                    )

                    if response.status_code == 200:
                        result = response.json()
                        # 提取回复内容
                        if "data" in result and "output" in result["data"]:
                            output = result["data"]["output"]
                            content = output.get("choices", [{}])[0].get("message", {}).get("content", "")
                            if not content and "content" in output:
                                content = output["content"]

                            st.markdown(content)
                            st.session_state.messages.append({"role": "assistant", "content": content})
                        else:
                            st.error("无法解析响应内容")
                    else:
                        st.error(f"请求失败: {response.status_code}")
                        st.error(response.text)

                except requests.exceptions.ConnectionError:
                    st.error("无法连接到 Agent 服务，请检查 API 地址")
                except Exception as e:
                    st.error(f"发生错误: {str(e)}")

# Tab 2: 任务监控
with tab2:
    st.subheader("Agent 运行状态")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("总对话数", len(st.session_state.get("messages", [])))

    with col2:
        st.metric("当前会话", st.session_state.get("session_count", 1))

    with col3:
        st.metric("运行时长", "N/A")

    st.markdown("---")

    # 聊天历史
    st.subheader("对话历史")
    if st.session_state.get("messages"):
        for i, msg in enumerate(st.session_state.messages):
            role = "👤 用户" if msg["role"] == "user" else "🤖 Agent"
            with st.expander(f"{role} - {i+1}"):
                st.markdown(msg["content"])
    else:
        st.info("暂无对话历史")

# Tab 3: K8S 状态
with tab3:
    st.subheader("Kubernetes 集群状态")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📦 Agent Pods")
        try:
            result = subprocess.run(
                ["kubectl", "get", "pods", "-n", namespace, "-l", "app=docker-agent", "-o", "wide"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                st.code(result.stdout, language="bash")
            else:
                st.error("无法获取 Pod 信息")
        except Exception as e:
            st.error(f"错误: {str(e)}")

        st.markdown("### 🏥 健康检查")
        if st.button("检查健康状态"):
            try:
                response = requests.get(f"{api_url}/health", timeout=5)
                if response.status_code == 200:
                    st.success("✅ Agent 服务正常")
                    st.json(response.json())
                else:
                    st.error("❌ Agent 服务异常")
            except Exception as e:
                st.error(f"无法连接: {str(e)}")

    with col2:
        st.markdown("### 🚀 服务状态")
        try:
            result = subprocess.run(
                ["kubectl", "get", "svc", "-n", namespace, "-l", "app=docker-agent"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                st.code(result.stdout, language="bash")
            else:
                st.error("无法获取 Service 信息")
        except Exception as e:
            st.error(f"错误: {str(e)}")

        st.markdown("### 📊 资源使用")
        try:
            result = subprocess.run(
                ["kubectl", "top", "pod", "-n", namespace, "-l", "app=docker-agent"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                st.code(result.stdout, language="bash")
            else:
                st.warning("资源指标未启用或 Pod 未就绪")
        except Exception as e:
            st.warning(f"错误: {str(e)}")

    st.markdown("---")
    st.markdown("### 📋 Agent 日志")

    # 日志配置
    log_col1, log_col2, log_col3 = st.columns([2, 1, 1])
    with log_col1:
        pod_name = st.text_input("Pod 名称", value="docker-agent", placeholder="输入 Pod 名称")
    with log_col2:
        tail_lines = st.number_input("行数", min_value=10, max_value=1000, value=50)
    with log_col3:
        if st.button("获取日志"):
            pass

    if st.button("📥 获取最新日志"):
        try:
            result = subprocess.run(
                ["kubectl", "logs", "-n", namespace, "-l", "app=docker-agent", "--tail", str(tail_lines)],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                st.markdown('<div class="log-container">' + result.stdout + '</div>', unsafe_allow_html=True)
            else:
                st.error(f"无法获取日志: {result.stderr}")
        except Exception as e:
            st.error(f"错误: {str(e)}")

# Tab 4: 使用说明
with tab4:
    st.subheader("📖 使用说明")

    st.markdown("""
    ### 快速开始

    1. **配置 API 地址**
       - 在左侧侧边栏输入 Agent API 地址
       - 默认地址: `http://localhost:8000`

    2. **与 Agent 对话**
       - 在聊天界面输入指令
       - 例如: "帮我构建 LlamaFactory 镜像"

    3. **查看状态**
       - 在"任务监控"标签查看对话历史
       - 在"K8S 状态"标签查看集群状态

    ### 常用指令示例

    - **构建镜像**: "帮我构建 LlamaFactory 镜像"
    - **验证镜像**: "验证刚才构建的镜像"
    - **查看状态**: "查看当前 K8S 集群状态"
    - **诊断问题**: "诊断镜像构建失败的原因"

    ### 注意事项

    1. 确保 Agent 服务正在运行
    2. 确保 kubectl 已配置并能访问 K8S 集群
    3. 确保有足够的权限执行 K8S 操作

    ### 技术支持

    - GitHub: https://github.com/fanjn-zetyun/docker-Agent
    """)

# 底部信息
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Docker Agent Web UI v1.0 | Powered by Streamlit</p>
</div>
""", unsafe_allow_html=True)
