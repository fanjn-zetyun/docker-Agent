"""
Docker Agent CLI 交互模式
提供命令行交互界面
"""

import asyncio
import json
import sys
from typing import Dict, Any
from pathlib import Path

# 添加项目路径到 PythonPath
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from coze_coding_utils.runtime_ctx.context import new_context
from coze_coding_utils.log.write_log import setup_logging, request_context, LOG_FILE
from coze_coding_utils.log.config import LOG_LEVEL
import logging

# 配置日志
setup_logging(
    log_file=LOG_FILE,
    max_bytes=100 * 1024 * 1024,
    backup_count=5,
    log_level=LOG_LEVEL,
    use_json_format=True,
    console_output=False  # CLI 模式不输出 JSON 日志到控制台
)

logger = logging.getLogger(__name__)

from src.agents.agent import build_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


class CLISession:
    """CLI 会话管理"""

    def __init__(self):
        self.agent = None
        self.session_id = "cli-session"
        self.message_history = []

    async def initialize(self):
        """初始化 Agent"""
        print("\n" + "=" * 60)
        print("🐳 Docker Agent CLI 模式")
        print("=" * 60)
        print("\n正在初始化 Agent...")

        try:
            ctx = new_context(method="cli_init")
            request_context.set(ctx)
            self.agent = build_agent(ctx)

            print("✅ Agent 初始化成功！")
            print("\n可用的功能:")
            print("  - Git 代码同步 (拉取、切换、合并)")
            print("  - Dockerfile 分析和学习")
            print("  - Docker 镜像构建和推送")
            print("  - K8S Pod 创建和管理")
            print("  - LlamaFactory 验证")
            print("\n输入 'help' 查看帮助，输入 'exit' 退出")
            print("=" * 60 + "\n")

        except Exception as e:
            print(f"❌ Agent 初始化失败: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    async def run(self):
        """运行 CLI 会话"""
        await self.initialize()

        while True:
            try:
                # 读取用户输入
                user_input = input("\n你: ").strip()

                # 处理特殊命令
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\n👋 再见！")
                    break

                if user_input.lower() == 'help':
                    self.show_help()
                    continue

                if user_input.lower() == 'clear':
                    self.message_history = []
                    print("✅ 对话历史已清空")
                    continue

                if user_input.lower() == 'history':
                    self.show_history()
                    continue

                if not user_input:
                    continue

                # 调用 Agent
                print("\nAgent: ", end='', flush=True)
                await self.query_agent(user_input)

            except KeyboardInterrupt:
                print("\n\n按 Ctrl+C 退出？(y/n): ", end='', flush=True)
                confirm = input().strip().lower()
                if confirm == 'y':
                    print("\n👋 再见！")
                    break
            except EOFError:
                print("\n👋 再见！")
                break
            except Exception as e:
                print(f"\n❌ 发生错误: {str(e)}")
                import traceback
                traceback.print_exc()

    async def query_agent(self, query: str):
        """调用 Agent"""
        try:
            ctx = new_context(method="cli_query")
            request_context.set(ctx)

            # 准备输入
            messages = [
                SystemMessage(content=config["sp"])
            ] + self.message_history + [
                HumanMessage(content=query)
            ]

            # 创建配置
            config = {
                "configurable": {
                    "thread_id": self.session_id,
                }
            }

            # 调用 Agent（流式输出）
            full_response = ""
            async for chunk in self.agent.astream(
                {"messages": messages},
                config=config,
                stream_mode="updates"
            ):
                # 提取 AI 回复
                for node_name, node_output in chunk.items():
                    if "messages" in node_output:
                        for msg in node_output["messages"]:
                            if isinstance(msg, AIMessage):
                                content = msg.content
                                if content:
                                    print(content, end='', flush=True)
                                    full_response += content

            print()  # 换行

            # 保存到历史
            self.message_history.extend([
                HumanMessage(content=query),
                AIMessage(content=full_response)
            ])

        except Exception as e:
            print(f"❌ Agent 调用失败: {str(e)}")
            import traceback
            traceback.print_exc()

    def show_help(self):
        """显示帮助信息"""
        print("\n" + "=" * 60)
        print("📖 帮助信息")
        print("=" * 60)
        print("\n🔧 常用指令:")
        print("  - help        显示此帮助信息")
        print("  - exit        退出程序")
        print("  - clear       清空对话历史")
        print("  - history     查看对话历史")
        print("\n💬 常用 Agent 指令:")
        print("  - 帮我构建 LlamaFactory 镜像")
        print("  - 验证刚才构建的镜像")
        print("  - 查看 K8S 集群状态")
        print("  - 分析 Dockerfile")
        print("  - 从 GitHub 拉取最新代码")
        print("\n" + "=" * 60)

    def show_history(self):
        """显示对话历史"""
        if not self.message_history:
            print("\n📝 暂无对话历史")
            return

        print("\n" + "=" * 60)
        print("📝 对话历史")
        print("=" * 60)

        for i, msg in enumerate(self.message_history):
            if isinstance(msg, HumanMessage):
                print(f"\n👤 [{i//2 + 1}] 你: {msg.content}")
            elif isinstance(msg, AIMessage):
                print(f"\n🤖 [{i//2 + 1}] Agent: {msg.content}")

        print("\n" + "=" * 60)


def load_config():
    """加载 Agent 配置"""
    config_path = Path(__file__).parent.parent / "config" / "agent_llm_config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


async def main():
    """主函数"""
    global config
    config = load_config()

    session = CLISession()
    await session.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
    except Exception as e:
        print(f"\n❌ 程序异常退出: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
