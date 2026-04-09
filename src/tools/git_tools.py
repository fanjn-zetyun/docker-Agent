"""
Git 操作工具
用于拉取代码、切换分支、合并分支等 Git 操作
"""
import os
import subprocess
import logging
from langchain.tools import tool

logger = logging.getLogger(__name__)


@tool
def git_pull(remote: str = "origin", branch: str = "main") -> str:
    """
    从远程仓库拉取最新代码

    Args:
        remote: 远程仓库名称，默认为 "origin"
        branch: 要拉取的分支名称，默认为 "main"

    Returns:
        拉取操作的详细结果

    Example:
        git_pull(remote="origin", branch="main")
    """
    try:
        workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")

        # 检查是否在 Git 仓库中
        if not os.path.exists(os.path.join(workspace_path, ".git")):
            return f"错误：当前目录 {workspace_path} 不是 Git 仓库"

        # 执行 git pull 命令
        cmd = ["git", "pull", remote, branch]

        logger.info(f"执行命令: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=workspace_path
        )

        if result.returncode == 0:
            output = result.stdout
            return (
                f"✅ 成功从远程仓库拉取最新代码！\n"
                f"远程仓库: {remote}\n"
                f"分支: {branch}\n\n"
                f"拉取输出:\n{output}"
            )
        else:
            return (
                f"❌ 拉取代码失败！\n"
                f"命令: {' '.join(cmd)}\n"
                f"错误信息:\n{result.stderr}"
            )

    except Exception as e:
        logger.error(f"执行 git pull 时发生异常: {str(e)}")
        return f"❌ 执行 git pull 时发生异常: {str(e)}"


@tool
def git_checkout(branch_name: str, create_new: bool = False) -> str:
    """
    切换到指定分支，或创建并切换到新分支

    Args:
        branch_name: 分支名称
        create_new: 是否创建新分支，默认为 False

    Returns:
        切换分支的操作结果

    Example:
        git_checkout(branch_name="dev", create_new=True)
    """
    try:
        workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")

        # 检查是否在 Git 仓库中
        if not os.path.exists(os.path.join(workspace_path, ".git")):
            return f"错误：当前目录 {workspace_path} 不是 Git 仓库"

        # 执行 git checkout 命令
        if create_new:
            cmd = ["git", "checkout", "-b", branch_name]
            logger.info(f"创建并切换到新分支: {branch_name}")
        else:
            cmd = ["git", "checkout", branch_name]
            logger.info(f"切换到分支: {branch_name}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=workspace_path
        )

        if result.returncode == 0:
            output = result.stdout
            # 获取当前分支
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                cwd=workspace_path
            )
            current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "未知"

            action = "创建并切换" if create_new else "切换"
            return (
                f"✅ 成功{action}到分支！\n"
                f"分支名称: {branch_name}\n"
                f"当前分支: {current_branch}\n\n"
                f"输出:\n{output}"
            )
        else:
            return (
                f"❌ 切换分支失败！\n"
                f"命令: {' '.join(cmd)}\n"
                f"错误信息:\n{result.stderr}"
            )

    except Exception as e:
        logger.error(f"执行 git checkout 时发生异常: {str(e)}")
        return f"❌ 执行 git checkout 时发生异常: {str(e)}"


@tool
def git_merge(source_branch: str, strategy: str = None) -> str:
    """
    将指定分支合并到当前分支

    Args:
        source_branch: 要合并的源分支名称
        strategy: 合并策略，可选值：None（默认）、"no-ff"（不快进合并）、"squash"（压缩合并）

    Returns:
        合并操作的详细结果

    Example:
        git_merge(source_branch="main", strategy="no-ff")
    """
    try:
        workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")

        # 检查是否在 Git 仓库中
        if not os.path.exists(os.path.join(workspace_path, ".git")):
            return f"错误：当前目录 {workspace_path} 不是 Git 仓库"

        # 获取当前分支
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            cwd=workspace_path
        )

        if branch_result.returncode != 0:
            return f"错误：无法获取当前分支信息"

        current_branch = branch_result.stdout.strip()

        # 构建合并命令
        cmd = ["git", "merge"]

        if strategy:
            if strategy == "no-ff":
                cmd.append("--no-ff")
            elif strategy == "squash":
                cmd.append("--squash")

        cmd.append(source_branch)

        logger.info(f"执行命令: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=workspace_path
        )

        if result.returncode == 0:
            output = result.stdout
            return (
                f"✅ 成功合并分支！\n"
                f"源分支: {source_branch}\n"
                f"目标分支: {current_branch}\n"
                f"合并策略: {strategy if strategy else '默认'}\n\n"
                f"合并输出:\n{output}"
            )
        else:
            # 检查是否有冲突
            if "CONFLICT" in result.stderr or "CONFLICT" in result.stdout:
                return (
                    f"⚠️  合并产生冲突！\n"
                    f"源分支: {source_branch}\n"
                    f"目标分支: {current_branch}\n\n"
                    f"错误信息:\n{result.stderr}\n\n"
                    f"请解决冲突后执行：\n"
                    f"1. git add <解决冲突的文件>\n"
                    f"2. git commit -m '解决冲突'\n"
                )
            else:
                return (
                    f"❌ 合并失败！\n"
                    f"命令: {' '.join(cmd)}\n"
                    f"错误信息:\n{result.stderr}"
                )

    except Exception as e:
        logger.error(f"执行 git merge 时发生异常: {str(e)}")
        return f"❌ 执行 git merge 时发生异常: {str(e)}"


@tool
def git_status() -> str:
    """
    查看 Git 仓库状态，包括当前分支、未提交的更改等

    Returns:
        Git 仓库的详细状态信息

    Example:
        git_status()
    """
    try:
        workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")

        # 检查是否在 Git 仓库中
        if not os.path.exists(os.path.join(workspace_path, ".git")):
            return f"错误：当前目录 {workspace_path} 不是 Git 仓库"

        # 获取当前分支
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            cwd=workspace_path
        )

        # 获取远程分支信息
        remote_result = subprocess.run(
            ["git", "remote", "-v"],
            capture_output=True,
            text=True,
            cwd=workspace_path
        )

        # 获取状态
        status_result = subprocess.run(
            ["git", "status", "-sb"],
            capture_output=True,
            text=True,
            cwd=workspace_path
        )

        current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "未知"
        remote_info = remote_result.stdout if remote_result.returncode == 0 else "无"
        status_info = status_result.stdout if status_result.returncode == 0 else ""

        return (
            f"📊 Git 仓库状态\n\n"
            f"当前分支: {current_branch}\n\n"
            f"📡 远程仓库:\n{remote_info}\n\n"
            f"📝 仓库状态:\n{status_info}"
        )

    except Exception as e:
        logger.error(f"获取 git status 时发生异常: {str(e)}")
        return f"❌ 获取 git status 时发生异常: {str(e)}"
