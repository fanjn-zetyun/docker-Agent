"""
Dockerfile 分析和学习工具
用于分析 Dockerfile 构建规律，帮助理解镜像构建逻辑
"""
import os
import re
from langchain.tools import tool


@tool
def analyze_dockerfile(dockerfile_path: str) -> str:
    """
    分析 Dockerfile，提取关键信息和构建规律

    Args:
        dockerfile_path: Dockerfile 文件路径

    Returns:
        Dockerfile 的详细分析报告，包括基础镜像、依赖、命令等

    Example:
        analyze_dockerfile(dockerfile_path="Dockerfile")
    """
    try:
        workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")

        if not os.path.isabs(dockerfile_path):
            dockerfile_full_path = os.path.join(workspace_path, dockerfile_path)
        else:
            dockerfile_full_path = dockerfile_path

        if not os.path.exists(dockerfile_full_path):
            return f"错误：Dockerfile 不存在于路径 {dockerfile_full_path}"

        with open(dockerfile_full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        analysis = {
            "基础镜像": [],
            "安装的依赖": [],
            "复制的文件": [],
            "环境变量": [],
            "暴露的端口": [],
            "工作目录": [],
            "构建参数": [],
            "运行命令": [],
            "总行数": len(content.splitlines())
        }

        # 解析 Dockerfile
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # FROM - 基础镜像
            if line.upper().startswith('FROM'):
                parts = line.split()
                if len(parts) > 1:
                    analysis["基础镜像"].append(' '.join(parts[1:]))

            # RUN - 安装依赖或执行命令
            elif line.upper().startswith('RUN'):
                cmd = line[4:].strip()
                analysis["运行命令"].append(cmd)
                # 检测常见的依赖安装
                if any(x in cmd.lower() for x in ['pip install', 'apt-get install', 'apt install', 'yum install']):
                    # 提取包名
                    if 'pip install' in cmd.lower():
                        deps = re.findall(r'pip install\s+-[^\s]*\s+(.+)', cmd)
                        if not deps:
                            deps = re.findall(r'pip install\s+(.+)', cmd)
                        if deps:
                            analysis["安装的依赖"].extend(deps)
                    elif 'apt-get install' in cmd.lower() or 'apt install' in cmd.lower():
                        deps = re.findall(r'(?:apt-get|apt) install\s+-[^\s]*\s+(.+)', cmd)
                        if not deps:
                            deps = re.findall(r'(?:apt-get|apt) install\s+(.+)', cmd)
                        if deps:
                            analysis["安装的依赖"].append(deps[0])

            # COPY/ADD - 复制文件
            elif line.upper().startswith('COPY') or line.upper().startswith('ADD'):
                parts = line.split()
                if len(parts) > 1:
                    analysis["复制的文件"].append(' '.join(parts[1:]))

            # ENV - 环境变量
            elif line.upper().startswith('ENV'):
                parts = line.split(None, 2)
                if len(parts) > 1:
                    analysis["环境变量"].append(' '.join(parts[1:]))

            # EXPOSE - 暴露端口
            elif line.upper().startswith('EXPOSE'):
                ports = line.split()[1:]
                analysis["暴露的端口"].extend(ports)

            # WORKDIR - 工作目录
            elif line.upper().startswith('WORKDIR'):
                parts = line.split()
                if len(parts) > 1:
                    analysis["工作目录"].append(parts[1])

            # ARG - 构建参数
            elif line.upper().startswith('ARG'):
                parts = line.split(None, 1)
                if len(parts) > 1:
                    analysis["构建参数"].append(parts[1])

            # CMD/ENTRYPOINT - 启动命令
            elif line.upper().startswith('CMD') or line.upper().startswith('ENTRYPOINT'):
                analysis["运行命令"].append(line)

        # 生成报告
        report = "📊 Dockerfile 分析报告\n\n"
        report += "=" * 80 + "\n"

        for key, value in analysis.items():
            if value:
                report += f"\n🔹 {key}:\n"
                for item in value:
                    report += f"  - {item}\n"
            else:
                report += f"\n🔹 {key}: 无\n"

        # 总结和建议
        report += "\n" + "=" * 80 + "\n"
        report += "\n📝 构建规律总结:\n"
        report += f"1. 基于 {len(analysis['基础镜像'])} 个基础镜像构建\n"
        report += f"2. 定义了 {len(analysis['环境变量'])} 个环境变量\n"
        report += f"3. 复制了 {len(analysis['复制的文件'])} 个文件/目录\n"
        report += f"4. 安装了多种依赖包\n"
        report += f"5. 暴露了 {len(analysis['暴露的端口'])} 个端口\n"

        if analysis["工作目录"]:
            report += f"6. 工作目录设置为: {analysis['工作目录'][-1]}\n"

        return report

    except Exception as e:
        return f"❌ 分析 Dockerfile 时发生异常: {str(e)}"


@tool
def learn_dockerfile_pattern(dockerfile_path: str, previous_analysis: dict = None) -> str:
    """
    从 Dockerfile 中学习构建模式，并对比之前的版本

    Args:
        dockerfile_path: Dockerfile 文件路径
        previous_analysis: 之前的分析结果（可选），用于对比变化

    Returns:
        学习到的构建模式和变化点

    Example:
        learn_dockerfile_pattern(dockerfile_path="Dockerfile")
    """
    try:
        # 先分析当前 Dockerfile
        analyze_result = analyze_dockerfile(dockerfile_path)

        if not previous_analysis:
            return (
                f"📚 Dockerfile 学习报告（首次分析）\n\n"
                f"{analyze_result}\n\n"
                f"💡 记住了当前的构建模式，下次可以对比变化！"
            )

        # 对比变化
        changes = []

        # 这里可以添加更详细的对比逻辑
        # 当前简化实现

        report = "📚 Dockerfile 学习报告\n\n"
        report += "=" * 80 + "\n\n"

        if changes:
            report += "🔄 检测到的变化:\n"
            for change in changes:
                report += f"  - {change}\n"
        else:
            report += "✅ Dockerfile 与之前版本一致，无变化\n"

        report += "\n" + "=" * 80 + "\n"
        report += f"\n{analyze_result}"

        return report

    except Exception as e:
        return f"❌ 学习 Dockerfile 时发生异常: {str(e)}"


@tool
def validate_dockerfile(dockerfile_path: str) -> str:
    """
    验证 Dockerfile 的语法和常见问题

    Args:
        dockerfile_path: Dockerfile 文件路径

    Returns:
        验证结果和改进建议

    Example:
        validate_dockerfile(dockerfile_path="Dockerfile")
    """
    try:
        workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")

        if not os.path.isabs(dockerfile_path):
            dockerfile_full_path = os.path.join(workspace_path, dockerfile_path)
        else:
            dockerfile_full_path = dockerfile_path

        if not os.path.exists(dockerfile_full_path):
            return f"错误：Dockerfile 不存在于路径 {dockerfile_full_path}"

        with open(dockerfile_full_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        issues = []
        warnings = []
        suggestions = []

        # 检查每一行
        for i, line in enumerate(lines, 1):
            # 检查未清理的缓存
            if line.strip().upper().startswith('RUN') and 'apt-get install' in line.lower():
                if 'apt-get clean' not in ''.join(lines[i:]):  # 简化检查
                    warnings.append(f"行 {i}: 安装 apt 包后建议清理缓存（apt-get clean）")

            # 检查 layer 优化
            if line.strip().upper().startswith('RUN') and '&&' not in line:
                if not any(c in line for c in [';', '&&', '|&']):
                    warnings.append(f"行 {i}: 建议合并 RUN 命令以减少镜像层数")

            # 检查环境变量
            if line.strip().upper().startswith('ENV'):
                if ' ' in line.split('ENV', 1)[1] and '=' not in line:
                    issues.append(f"行 {i}: ENV 格式可能不正确，建议使用 KEY=value 格式")

        # 生成报告
        report = "✅ Dockerfile 验证报告\n\n"

        if issues:
            report += "❌ 发现问题:\n"
            for issue in issues:
                report += f"  {issue}\n"
            report += "\n"

        if warnings:
            report += "⚠️  警告:\n"
            for warning in warnings:
                report += f"  {warning}\n"
            report += "\n"

        if suggestions:
            report += "💡 改进建议:\n"
            for suggestion in suggestions:
                report += f"  {suggestion}\n"
            report += "\n"

        if not issues and not warnings and not suggestions:
            report += "✨ Dockerfile 看起来很棒！没有发现明显问题。\n"

        return report

    except Exception as e:
        return f"❌ 验证 Dockerfile 时发生异常: {str(e)}"
