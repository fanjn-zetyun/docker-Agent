#!/bin/bash

# ============================================================
# Docker Agent Web UI 启动脚本
# ============================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印信息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 检查依赖
check_dependencies() {
    print_info "检查依赖..."

    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 未安装"
        exit 1
    fi

    # 检查 uv
    if ! command -v uv &> /dev/null; then
        print_warning "uv 未安装，将使用 pip"
        USE_PIP=true
    else
        USE_PIP=false
    fi

    # 检查 streamlit
    if ! python3 -c "import streamlit" 2>/dev/null; then
        print_info "安装 streamlit..."
        if [ "$USE_PIP" = true ]; then
            pip3 install streamlit
        else
            uv pip install streamlit
        fi
    fi

    print_info "依赖检查完成"
}

# 启动 Web UI
start_web_ui() {
    print_info "启动 Docker Agent Web UI..."

    # 获取工作目录
    WORKSPACE_DIR="${COZE_WORKSPACE_PATH:-/workspace/projects}"
    cd "$WORKSPACE_DIR" || exit 1

    # 设置环境变量
    export API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
    export K8S_NAMESPACE="${K8S_NAMESPACE:-fjn}"

    print_info "工作目录: $WORKSPACE_DIR"
    print_info "API 地址: $API_BASE_URL"
    print_info "K8S 命名空间: $K8S_NAMESPACE"

    # 启动 Streamlit
    print_info "Web UI 即将在浏览器中打开..."
    streamlit run src/web_ui.py \
        --server.port 8501 \
        --server.address 0.0.0.0 \
        --server.headless true \
        --server.fileWatcherType poll \
        --browser.gatherUsageStats false
}

# 帮助信息
show_help() {
    cat << EOF
Docker Agent Web UI 启动脚本

用法:
    $0 [选项]

选项:
    -h, --help          显示帮助信息
    --check             仅检查依赖，不启动

环境变量:
    API_BASE_URL        Agent API 地址 (默认: http://localhost:8000)
    K8S_NAMESPACE       K8S 命名空间 (默认: fjn)
    COZE_WORKSPACE_PATH 工作目录 (默认: /workspace/projects)

示例:
    # 启动 Web UI
    $0

    # 自定义 API 地址
    API_BASE_URL=http://192.168.1.100:8000 $0

    # 指定命名空间
    K8S_NAMESPACE=production $0

EOF
}

# 主函数
main() {
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            --check)
                check_dependencies
                exit 0
                ;;
            *)
                print_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
        shift
    done

    # 检查依赖
    check_dependencies

    # 启动 Web UI
    start_web_ui
}

# 执行主函数
main "$@"
