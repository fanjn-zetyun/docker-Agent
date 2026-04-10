#!/usr/bin/env python3
"""
Git Bundle 推送脚本
使用 bundle 文件推送代码到 GitHub
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path


def run_command(cmd, cwd=None, check=True):
    """执行 shell 命令"""
    print(f"执行: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=cwd,
        check=check,
        capture_output=True,
        text=True
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr and result.returncode != 0:
        print(f"错误: {result.stderr}", file=sys.stderr)
    return result


def push_bundle(bundle_file, remote_url):
    """推送 bundle 到远程仓库"""

    print("=" * 60)
    print("📦 Git Bundle 推送工具")
    print("=" * 60)
    print()

    # 检查 bundle 文件
    bundle_path = Path(bundle_file)
    if not bundle_path.exists():
        print(f"❌ Bundle 文件不存在: {bundle_file}")
        sys.exit(1)

    print(f"✅ 找到 bundle 文件: {bundle_file}")
    print(f"📏 文件大小: {bundle_path.stat().st_size / 1024:.2f} KB")
    print()

    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 创建临时目录: {temp_dir}")
        print()

        repo_dir = os.path.join(temp_dir, "repo")

        # 1. 克隆远程仓库
        print("1️⃣  克隆远程仓库...")
        run_command(["git", "clone", remote_url, repo_dir])
        print("✅ 克隆完成")
        print()

        # 2. 拉取 bundle
        print("2️⃣  拉取 bundle 文件...")
        run_command([
            "git", "pull",
            str(bundle_path.absolute()),
            "dev"
        ], cwd=repo_dir)
        print("✅ 拉取完成")
        print()

        # 3. 推送到远程
        print("3️⃣  推送到 GitHub...")
        run_command(["git", "push", "origin", "dev"], cwd=repo_dir)
        print("✅ 推送完成")
        print()

    print("=" * 60)
    print("🎉 推送成功！")
    print("=" * 60)
    print()
    print("📖 访问代码仓库:")
    print("   https://github.com/fanjn-zetyun/docker-Agent")
    print()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="使用 bundle 文件推送代码到 GitHub"
    )
    parser.add_argument(
        "bundle",
        nargs="?",
        default="docker-agent.bundle",
        help="Bundle 文件路径（默认: docker-agent.bundle）"
    )
    parser.add_argument(
        "--url",
        default="git@github.com:fanjn-zetyun/docker-Agent.git",
        help="远程仓库 URL"
    )

    args = parser.parse_args()

    push_bundle(args.bundle, args.url)


if __name__ == "__main__":
    main()
