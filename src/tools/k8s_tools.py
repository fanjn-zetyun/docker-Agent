"""
Kubernetes 操作工具
用于在 K8S 集群中管理 pod，验证镜像构建结果
"""
import os
import subprocess
import logging
import time
import json
import yaml
import tempfile
from langchain.tools import tool

logger = logging.getLogger(__name__)


def _load_k8s_config():
    """
    加载 K8S 部署配置

    Returns:
        配置模块，如果不存在则返回 None
    """
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, "config/k8s_deployment_config.py")

    if not os.path.exists(config_path):
        return None

    try:
        import sys
        sys.path.insert(0, os.path.dirname(config_path))

        config_module_name = os.path.splitext(os.path.basename(config_path))[0]
        config_module = __import__(config_module_name)

        return config_module
    except Exception:
        return None


def _get_current_namespace() -> str:
    """
    获取当前命名空间

    优先级：
    1. 环境变量 POD_NAMESPACE
    2. kubectl config 获取
    3. 默认返回 'default'

    Returns:
        命名空间名称
    """
    # 1. 优先使用环境变量
    namespace = os.getenv("POD_NAMESPACE")
    if namespace:
        return namespace

    # 2. 使用 kubectl config
    try:
        result = subprocess.run(
            ["kubectl", "config", "view", "--minify", "--output", "jsonpath={..namespace}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass

    # 3. 默认值
    return "default"


@tool
def k8s_get_current_namespace() -> str:
    """
    获取当前 K8S 命名空间

    Returns:
        当前命名空间名称

    Example:
        k8s_get_current_namespace()
    """
    namespace = _get_current_namespace()
    return (
        f"📍 当前命名空间: {namespace}\n\n"
        f"获取方式: {'环境变量 POD_NAMESPACE' if os.getenv('POD_NAMESPACE') else 'kubectl config'}\n"
    )


@tool
def k8s_create_validation_pod(
    namespace: str,
    pod_name: str,
    image: str,
    use_full_resources: bool = False
) -> str:
    """
    创建用于验证的 LlamaFactory pod，使用完整的生产环境配置

    Args:
        namespace: K8S 命名空间
        pod_name: pod 名称
        image: 镜像名称（包含标签）
        use_full_resources: 是否使用完整资源配置（默认 False，使用验证配置）

    Returns:
        创建操作的结果

    Example:
        k8s_create_validation_pod(
            namespace="llama-test",
            pod_name="llama-factory-validation",
            image="registry.hd-02.alayanew.com:8443/alayanew-4fd285c4-c4f3-4e92-80ee-26169717cba8/llamafactory-online:lf0.9.5-tf5.5.0-torch2.8.0-cu12.6-1.0-nydus"
        )
    """
    try:
        # 加载 K8S 配置
        k8s_config = _load_k8s_config()

        # 构建 pod YAML
        pod_yaml = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": pod_name,
                "namespace": namespace,
                "labels": {
                    "app": "llama-factory-validation",
                    "purpose": "image-validation"
                }
            },
            "spec": {
                "restartPolicy": "OnFailure",
                "containers": [{
                    "name": "llama-factory-validation",
                    "image": image,
                    "imagePullPolicy": "IfNotPresent",
                }]
            }
        }

        # 添加镜像拉取密钥
        if k8s_config and hasattr(k8s_config, 'IMAGE_PULL_SECRET'):
            pod_yaml["spec"]["imagePullSecrets"] = [
                {"name": k8s_config.IMAGE_PULL_SECRET["name"]}
            ]

        # 添加启动命令
        if k8s_config and hasattr(k8s_config, 'POD_COMMAND'):
            pod_yaml["spec"]["containers"][0]["command"] = k8s_config.POD_COMMAND

        # 添加环境变量
        env_vars = {}
        if k8s_config and hasattr(k8s_config, 'POD_ENV_VARS'):
            env_vars = k8s_config.POD_ENV_VARS.copy()
        pod_yaml["spec"]["containers"][0]["env"] = [
            {"name": k, "value": str(v)} for k, v in env_vars.items()
        ]

        # 添加端口
        if k8s_config and hasattr(k8s_config, 'POD_PORTS'):
            pod_yaml["spec"]["containers"][0]["ports"] = k8s_config.POD_PORTS

        # 添加资源配置
        if use_full_resources and k8s_config and hasattr(k8s_config, 'FULL_RESOURCES'):
            pod_yaml["spec"]["containers"][0]["resources"] = k8s_config.FULL_RESOURCES
        elif k8s_config and hasattr(k8s_config, 'POD_RESOURCES'):
            pod_yaml["spec"]["containers"][0]["resources"] = k8s_config.POD_RESOURCES
        else:
            # 默认配置
            pod_yaml["spec"]["containers"][0]["resources"] = {
                "limits": {"cpu": "4", "memory": "16Gi"},
                "requests": {"cpu": "2", "memory": "8Gi"}
            }

        # 添加存储卷挂载
        if k8s_config and hasattr(k8s_config, 'POD_VOLUME_MOUNTS'):
            pod_yaml["spec"]["containers"][0]["volumeMounts"] = k8s_config.POD_VOLUME_MOUNTS

        if k8s_config and hasattr(k8s_config, 'POD_VOLUMES'):
            pod_yaml["spec"]["volumes"] = k8s_config.POD_VOLUMES

        # 添加健康检查
        if k8s_config and hasattr(k8s_config, 'READINESS_PROBE'):
            pod_yaml["spec"]["containers"][0]["readinessProbe"] = k8s_config.READINESS_PROBE

        # 写入临时 YAML 文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml_file = f.name
            yaml.dump(pod_yaml, f, default_flow_style=False)

        logger.info(f"创建验证 pod: {pod_name} in namespace: {namespace}")

        # 执行 kubectl create 命令
        cmd = ["kubectl", "apply", "-f", yaml_file]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        # 删除临时文件
        try:
            os.unlink(yaml_file)
        except:
            pass

        if result.returncode == 0:
            return (
                f"✅ 成功创建验证 pod！\n"
                f"Pod 名称: {pod_name}\n"
                f"命名空间: {namespace}\n"
                f"镜像: {image}\n"
                f"资源配置: {'完整' if use_full_resources else '验证'}\n"
                f"GPU: {pod_yaml['spec']['containers'][0]['resources'].get('limits', {}).get('nvidia.com/gpu-h100-80gb-hbm3', '0')}\n\n"
                f"输出:\n{result.stdout}\n\n"
                f"提示：使用 k8s_wait_for_pod_ready 等待 pod 就绪"
            )
        else:
            return (
                f"❌ 创建 pod 失败！\n"
                f"命令: {' '.join(cmd)}\n"
                f"错误信息:\n{result.stderr}"
            )

    except Exception as e:
        logger.error(f"创建验证 pod 时发生异常: {str(e)}")
        return f"❌ 创建验证 pod 时发生异常: {str(e)}"


@tool
def k8s_create_pod(
    namespace: str,
    pod_name: str,
    image: str,
    command: list = None,
    args: list = None,
    env_vars: dict = None,
    resources: dict = None,
    labels: dict = None
) -> str:
    """
    在指定命名空间创建 pod

    Args:
        namespace: K8S 命名空间
        pod_name: pod 名称
        image: 镜像名称（包含标签）
        command: 容器启动命令（可选）
        args: 容器启动参数（可选）
        env_vars: 环境变量字典（可选）
        resources: 资源限制，例如 {"cpu": "2", "memory": "4Gi"}
        labels: pod 标签（可选）

    Returns:
        创建操作的结果

    Example:
        k8s_create_pod(
            namespace="llama-test",
            pod_name="llama-factory-test",
            image="registry.example.com/llama-factory:latest",
            resources={"cpu": "4", "memory": "8Gi"}
        )
    """
    try:
        # 构建 pod YAML
        pod_yaml = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": pod_name,
                "namespace": namespace,
                "labels": labels or {"app": "llama-factory-test"}
            },
            "spec": {
                "containers": [{
                    "name": "llama-factory",
                    "image": image,
                    "imagePullPolicy": "IfNotPresent",
                }]
            }
        }

        # 添加命令和参数
        if command:
            pod_yaml["spec"]["containers"][0]["command"] = command
        if args:
            pod_yaml["spec"]["containers"][0]["args"] = args

        # 添加环境变量
        if env_vars:
            env_list = [{"name": k, "value": str(v)} for k, v in env_vars.items()]
            pod_yaml["spec"]["containers"][0]["env"] = env_list

        # 添加资源限制
        if resources:
            pod_yaml["spec"]["containers"][0]["resources"] = {
                "limits": resources,
                "requests": resources
            }

        # 重启策略
        pod_yaml["spec"]["restartPolicy"] = "OnFailure"

        # 写入临时 YAML 文件
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml_file = f.name
            # 使用 yaml 库或简单格式化
            import yaml
            yaml.dump(pod_yaml, f, default_flow_style=False)

        logger.info(f"创建 pod: {pod_name} in namespace: {namespace}")

        # 执行 kubectl create 命令
        cmd = ["kubectl", "apply", "-f", yaml_file]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        # 删除临时文件
        try:
            os.unlink(yaml_file)
        except:
            pass

        if result.returncode == 0:
            return (
                f"✅ 成功创建 pod！\n"
                f"Pod 名称: {pod_name}\n"
                f"命名空间: {namespace}\n"
                f"镜像: {image}\n\n"
                f"输出:\n{result.stdout}\n\n"
                f"提示：使用 k8s_get_pod_status 查看状态"
            )
        else:
            return (
                f"❌ 创建 pod 失败！\n"
                f"命令: {' '.join(cmd)}\n"
                f"错误信息:\n{result.stderr}"
            )

    except Exception as e:
        logger.error(f"创建 pod 时发生异常: {str(e)}")
        return f"❌ 创建 pod 时发生异常: {str(e)}"


@tool
def k8s_get_pod_status(
    namespace: str,
    pod_name: str = None,
    label_selector: str = None
) -> str:
    """
    查看 pod 状态

    Args:
        namespace: K8S 命名空间
        pod_name: pod 名称（可选）
        label_selector: 标签选择器（可选，例如：app=llama-factory-test）

    Returns:
        pod 状态信息

    Example:
        k8s_get_pod_status(namespace="llama-test", pod_name="llama-factory-test")
    """
    try:
        cmd = ["kubectl", "get", "pods", "-n", namespace]

        if pod_name:
            cmd.append(pod_name)
        elif label_selector:
            cmd.extend(["-l", label_selector])

        cmd.extend(["-o", "wide"])

        logger.info(f"查看 pod 状态: namespace={namespace}, pod={pod_name}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return (
                f"📊 Pod 状态信息\n\n"
                f"{result.stdout}"
            )
        else:
            return (
                f"❌ 获取 pod 状态失败！\n"
                f"错误信息:\n{result.stderr}"
            )

    except Exception as e:
        logger.error(f"获取 pod 状态时发生异常: {str(e)}")
        return f"❌ 获取 pod 状态时发生异常: {str(e)}"


@tool
def k8s_get_pod_logs(
    namespace: str,
    pod_name: str,
    container_name: str = None,
    tail_lines: int = 100,
    follow: bool = False
) -> str:
    """
    查看 pod 日志

    Args:
        namespace: K8S 命名空间
        pod_name: pod 名称
        container_name: 容器名称（可选）
        tail_lines: 显示最后 N 行日志，默认 100
        follow: 是否持续跟踪日志（仅支持非流式调用时使用）

    Returns:
        pod 日志内容

    Example:
        k8s_get_pod_logs(namespace="llama-test", pod_name="llama-factory-test", tail_lines=200)
    """
    try:
        cmd = ["kubectl", "logs", "-n", namespace, pod_name]

        if container_name:
            cmd.extend(["-c", container_name])

        if tail_lines:
            cmd.extend(["--tail", str(tail_lines)])

        logger.info(f"查看 pod 日志: {pod_name}, lines: {tail_lines}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            logs = result.stdout
            if not logs:
                return f"⚠️  Pod {pod_name} 暂无日志输出"
            return (
                f"📝 Pod 日志 (最近 {tail_lines} 行)\n\n"
                f"{'='*80}\n"
                f"{logs}\n"
                f"{'='*80}"
            )
        else:
            return (
                f"❌ 获取 pod 日志失败！\n"
                f"错误信息:\n{result.stderr}"
            )

    except subprocess.TimeoutExpired:
        return f"⚠️  获取日志超时，pod 可能正在启动中"
    except Exception as e:
        logger.error(f"获取 pod 日志时发生异常: {str(e)}")
        return f"❌ 获取 pod 日志时发生异常: {str(e)}"


@tool
def k8s_delete_pod(
    namespace: str,
    pod_name: str,
    force: bool = False
) -> str:
    """
    删除 pod

    Args:
        namespace: K8S 命名空间
        pod_name: pod 名称
        force: 是否强制删除

    Returns:
        删除操作的结果

    Example:
        k8s_delete_pod(namespace="llama-test", pod_name="llama-factory-test", force=True)
    """
    try:
        cmd = ["kubectl", "delete", "pod", "-n", namespace, pod_name]

        if force:
            cmd.append("--force")
            cmd.append("--grace-period=0")

        logger.info(f"删除 pod: {pod_name}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return f"✅ 成功删除 pod: {pod_name}"
        else:
            return (
                f"❌ 删除 pod 失败！\n"
                f"错误信息:\n{result.stderr}"
            )

    except Exception as e:
        logger.error(f"删除 pod 时发生异常: {str(e)}")
        return f"❌ 删除 pod 时发生异常: {str(e)}"


@tool
def k8s_wait_for_pod_ready(
    namespace: str,
    pod_name: str,
    timeout: int = 300,
    interval: int = 10
) -> str:
    """
    等待 pod 就绪

    Args:
        namespace: K8S 命名空间
        pod_name: pod 名称
        timeout: 超时时间（秒），默认 300
        interval: 检查间隔（秒），默认 10

    Returns:
        等待结果

    Example:
        k8s_wait_for_pod_ready(namespace="llama-test", pod_name="llama-factory-test", timeout=600)
    """
    try:
        logger.info(f"等待 pod 就绪: {pod_name}, timeout: {timeout}s")

        elapsed = 0
        while elapsed < timeout:
            # 检查 pod 状态
            result = subprocess.run(
                ["kubectl", "get", "pod", "-n", namespace, pod_name, "-o", "jsonpath={.status.phase}"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                phase = result.stdout.strip()

                if phase == "Running":
                    # 检查是否就绪
                    ready_result = subprocess.run(
                        ["kubectl", "get", "pod", "-n", namespace, pod_name, "-o", "jsonpath={.status.conditions[?(@.type=='Ready')].status}"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if ready_result.returncode == 0 and "True" in ready_result.stdout:
                        return f"✅ Pod {pod_name} 已就绪！"
                    elif ready_result.returncode == 0 and "False" in ready_result.stdout:
                        # 检查容器状态
                        state_result = subprocess.run(
                            ["kubectl", "get", "pod", "-n", namespace, pod_name, "-o", "jsonpath={.status.containerStatuses[0].state.waiting.reason}"],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )
                        wait_reason = state_result.stdout.strip() if state_result.returncode == 0 else "未知"
                        return f"⚠️  Pod 正在启动，等待原因: {wait_reason}"
                elif phase == "Failed" or phase == "Error":
                    return f"❌ Pod 启动失败！状态: {phase}"
                else:
                    # Pending, ContainerCreating, etc.
                    pass
            else:
                return f"❌ 无法获取 pod 状态: {result.stderr}"

            time.sleep(interval)
            elapsed += interval

        return f"⏱️  等待 pod 就绪超时（{timeout}秒），请检查 pod 状态和日志"

    except Exception as e:
        logger.error(f"等待 pod 就绪时发生异常: {str(e)}")
        return f"❌ 等待 pod 就绪时发生异常: {str(e)}"


@tool
def k8s_exec_command(
    namespace: str,
    pod_name: str,
    command: str,
    container_name: str = None
) -> str:
    """
    在 pod 中执行命令

    Args:
        namespace: K8S 命名空间
        pod_name: pod 名称
        command: 要执行的命令（字符串形式）
        container_name: 容器名称（可选）

    Returns:
        命令执行结果

    Example:
        k8s_exec_command(namespace="llama-test", pod_name="llama-factory-test", command="python -c 'import torch; print(torch.__version__)'")
    """
    try:
        cmd = ["kubectl", "exec", "-n", namespace, pod_name]

        if container_name:
            cmd.extend(["-c", container_name])

        cmd.extend(["--", "sh", "-c", command])

        logger.info(f"在 pod 中执行命令: {command}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        output = ""
        if result.stdout:
            output += f"标准输出:\n{result.stdout}\n"
        if result.stderr:
            output += f"标准错误:\n{result.stderr}"

        if result.returncode == 0:
            return f"✅ 命令执行成功\n\n{output}"
        else:
            return f"❌ 命令执行失败（返回码: {result.returncode}）\n\n{output}"

    except subprocess.TimeoutExpired:
        return f"⏱️  命令执行超时"
    except Exception as e:
        logger.error(f"执行命令时发生异常: {str(e)}")
        return f"❌ 执行命令时发生异常: {str(e)}"
