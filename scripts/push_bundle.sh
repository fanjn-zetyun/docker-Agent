#!/bin/bash

# ============================================================
# Git Bundle 推送脚本
# 使用 bundle 文件推送代码到 GitHub
# ============================================================

set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 检查参数
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    cat << EOF
Git Bundle 推送脚本

用法:
    $0 [bundle_file]

参数:
    bundle_file    Bundle 文件路径（默认: docker-agent.bundle）

说明:
    此脚本会将 bundle 文件中的提交推送到 GitHub 远程仓库

示例:
    # 使用默认 bundle 文件
    $0

    # 指定 bundle 文件
    $0 /path/to/docker-agent.bundle

EOF
    exit 0
fi

# Bundle 文件路径
BUNDLE_FILE="${1:-docker-agent.bundle}"

# 检查 bundle 文件是否存在
if [ ! -f "$BUNDLE_FILE" ]; then
    print_error "Bundle 文件不存在: $BUNDLE_FILE"
    exit 1
fi

print_info "找到 bundle 文件: $BUNDLE_FILE"

# 临时目录
TEMP_DIR=$(mktemp -d)
print_info "创建临时目录: $TEMP_DIR"

# 清理函数
cleanup() {
    print_info "清理临时目录..."
    rm -rf "$TEMP_DIR"
}

trap cleanup EXIT

# 克隆远程仓库到临时目录
print_info "克隆远程仓库..."
cd "$TEMP_DIR"
git clone git@github.com:fanjn-zetyun/docker-Agent.git repo
cd repo

# 拉取 bundle
print_info "拉取 bundle 文件..."
git pull "$BUNDLE_FILE" dev

# 推送到远程
print_info "推送到 GitHub..."
git push origin dev

print_info "✅ 推送成功！"
print_info "访问 https://github.com/fanjn-zetyun/docker-Agent 查看代码"
