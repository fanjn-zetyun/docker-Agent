"""
Docker 构建和上传工具
用于管理 Docker 镜像的构建和推送到私有镜像仓库
"""
import os
import subprocess
import logging
from langchain.tools import tool

logger = logging.getLogger(__name__)


@tool
def build_docker_image(
    dockerfile_path: str,
    image_name: str,
    tag: str = "latest",
    build_context: str = None,
    build_args: dict = None
) -> str:
    """
    构建 Docker 镜像

    Args:
        dockerfile_path: Dockerfile 的路径，相对于项目根目录
        image_name: 镜像名称，例如：registry.example.com/namespace/project
        tag: 镜像标签，默认为 "latest"
        build_context: 构建上下文路径，默认为 Dockerfile 所在目录
        build_args: 构建参数，字典格式，例如：{"NODE_ENV": "production"}

    Returns:
        构建结果的详细信息，包括镜像 ID

    Example:
        build_docker_image(
            dockerfile_path="Dockerfile",
            image_name="registry.example.com/myproject",
            tag="v1.0.0"
        )
    """
    try:
        workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")

        # 获取 Dockerfile 的完整路径
        if not os.path.isabs(dockerfile_path):
            dockerfile_full_path = os.path.join(workspace_path, dockerfile_path)
        else:
            dockerfile_full_path = dockerfile_path

        # 检查 Dockerfile 是否存在
        if not os.path.exists(dockerfile_full_path):
            return f"错误：Dockerfile 不存在于路径 {dockerfile_full_path}"

        # 确定构建上下文
        if build_context is None:
            # 默认使用 Dockerfile 所在目录作为构建上下文
            build_context_path = os.path.dirname(dockerfile_full_path)
            if build_context_path == "":
                build_context_path = "."
        else:
            if not os.path.isabs(build_context):
                build_context_path = os.path.join(workspace_path, build_context)
            else:
                build_context_path = build_context

        # 构建 docker build 命令
        cmd = [
            "docker",
            "build",
            "-f", dockerfile_full_path,
            "-t", f"{image_name}:{tag}"
        ]

        # 添加构建参数
        if build_args:
            for key, value in build_args.items():
                cmd.extend(["--build-arg", f"{key}={value}"])

        # 添加构建上下文
        cmd.append(build_context_path)

        logger.info(f"执行命令: {' '.join(cmd)}")

        # 执行构建命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=workspace_path
        )

        if result.returncode == 0:
            # 从输出中提取镜像 ID
            output = result.stdout
            image_id = None
            for line in output.split('\n'):
                if "Successfully built" in line:
                    image_id = line.split()[-1]
                    break

            return (
                f"✅ Docker 镜像构建成功！\n"
                f"镜像名称: {image_name}:{tag}\n"
                f"镜像 ID: {image_id if image_id else '无法获取'}\n"
                f"构建上下文: {build_context_path}\n"
                f"Dockerfile: {dockerfile_full_path}\n\n"
                f"构建输出:\n{output}"
            )
        else:
            return (
                f"❌ Docker 镜像构建失败！\n"
                f"命令: {' '.join(cmd)}\n"
                f"错误信息:\n{result.stderr}"
            )

    except Exception as e:
        logger.error(f"构建镜像时发生异常: {str(e)}")
        return f"❌ 构建镜像时发生异常: {str(e)}"


@tool
def push_docker_image(
    image_name: str,
    tag: str = "latest",
    registry_username: str = None,
    registry_password: str = None,
    registry_url: str = None
) -> str:
    """
    推送 Docker 镜像到私有镜像仓库

    Args:
        image_name: 镜像名称，例如：registry.example.com/namespace/project
        tag: 镜像标签，默认为 "latest"
        registry_username: 镜像仓库用户名（如果需要认证）
        registry_password: 镜像仓库密码（如果需要认证）
        registry_url: 镜像仓库 URL（如果需要单独登录）

    Returns:
        推送结果的详细信息

    Example:
        push_docker_image(
            image_name="registry.example.com/myproject",
            tag="v1.0.0",
            registry_username="admin",
            registry_password="password123"
        )
    """
    try:
        workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")

        # 如果提供了认证信息，先登录
        if registry_username and registry_password:
            # 确定要登录的 registry
            login_registry = registry_url
            if login_registry is None:
                # 从 image_name 中提取 registry
                parts = image_name.split('/')
                if len(parts) > 1 and '.' in parts[0]:
                    login_registry = parts[0]
                else:
                    return "错误：无法从镜像名称中提取 registry 地址，请明确提供 registry_url"

            logger.info(f"登录到镜像仓库: {login_registry}")

            # 执行登录命令
            login_cmd = [
                "docker",
                "login",
                "-u", registry_username,
                "--password-stdin",
                login_registry
            ]

            result = subprocess.run(
                login_cmd,
                input=registry_password,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return (
                    f"❌ 登录镜像仓库失败！\n"
                    f"仓库: {login_registry}\n"
                    f"用户名: {registry_username}\n"
                    f"错误信息:\n{result.stderr}"
                )

            logger.info("镜像仓库登录成功")

        # 执行推送命令
        push_cmd = [
            "docker",
            "push",
            f"{image_name}:{tag}"
        ]

        logger.info(f"执行命令: {' '.join(cmd for cmd in push_cmd if cmd != '--password-stdin')}")

        result = subprocess.run(
            push_cmd,
            capture_output=True,
            text=True,
            cwd=workspace_path
        )

        if result.returncode == 0:
            output = result.stdout
            return (
                f"✅ Docker 镜像推送成功！\n"
                f"镜像: {image_name}:{tag}\n\n"
                f"推送输出:\n{output}"
            )
        else:
            return (
                f"❌ Docker 镜像推送失败！\n"
                f"镜像: {image_name}:{tag}\n"
                f"错误信息:\n{result.stderr}"
            )

    except Exception as e:
        logger.error(f"推送镜像时发生异常: {str(e)}")
        return f"❌ 推送镜像时发生异常: {str(e)}"
