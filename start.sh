#!/bin/bash
# =============================================================================
# Asset Dashboard Quick Start Script
# 资产看板快速启动脚本
# =============================================================================

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 打印带颜色的信息
info() { echo -e "${BLUE}ℹ${NC}  $1"; }
success() { echo -e "${GREEN}✓${NC}  $1"; }
warning() { echo -e "${YELLOW}⚠${NC}  $1"; }
error() { echo -e "${RED}✗${NC}  $1"; }

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

OS=$(detect_os)

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║        📊 Asset Dashboard - Quick Start                  ║"
echo "║        资产配置看板 - 快速启动                             ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo

# 检查 Python 版本
info "检查运行环境..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    success "Python 3 已安装 ($PYTHON_VERSION)"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    if [[ $PYTHON_VERSION == 3.* ]]; then
        success "Python 已安装 ($PYTHON_VERSION)"
        PYTHON_CMD="python"
    else
        error "需要 Python 3.7+，当前版本: $PYTHON_VERSION"
        exit 1
    fi
else
    error "未找到 Python，请先安装 Python 3.7+"
    echo "  macOS:   brew install python3"
    echo "  Ubuntu:  sudo apt install python3"
    echo "  Windows: https://www.python.org/downloads/"
    exit 1
fi

# 检查数据源配置
if [ -f "config.js" ]; then
    DATA_DIR=$(grep "dataDir" config.js | sed -E 's/.*dataDir[^"]*"([^"]+)".*/\1/')
    info "当前数据源: $DATA_DIR"
else
    warning "未找到 config.js，将使用演示数据"
    DATA_DIR="demo_data"
fi

# 检查数据目录
if [ ! -d "$DATA_DIR" ]; then
    error "数据目录 '$DATA_DIR' 不存在"
    echo
    echo "初次使用？请运行:"
    echo "  ./scripts/setup_data.sh"
    exit 1
fi

# 验证关键 JSON 文件
info "验证数据文件..."
JSON_FILES=("target.json" "history.json")
ALL_VALID=true

for file in "${JSON_FILES[@]}"; do
    if [ -f "$DATA_DIR/$file" ]; then
        if $PYTHON_CMD -c "import json; json.load(open('$DATA_DIR/$file'))" 2>/dev/null; then
            success "$file 格式正确"
        else
            error "$file 格式错误（JSON 语法问题）"
            ALL_VALID=false
        fi
    else
        warning "$file 不存在（使用默认配置）"
    fi
done

if [ "$ALL_VALID" = false ]; then
    error "部分数据文件有问题，请修复后重试"
    exit 1
fi

echo
echo "═══════════════════════════════════════════════════════════"
echo

# 选择端口
PORT=8765
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    warning "端口 $PORT 已被占用，尝试其他端口..."
    PORT=8766
fi

# 获取本机 IP（用于局域网访问）
LOCAL_IP=""
if [ "$OS" = "macos" ]; then
    LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || echo "")
elif [ "$OS" = "linux" ]; then
    LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "")
fi

# 启动服务器
info "启动本地服务器..."
echo

echo "  🌐 本地访问:"
echo "     http://localhost:$PORT"
echo "     http://127.0.0.1:$PORT"
echo

if [ -n "$LOCAL_IP" ]; then
    echo "  📱 局域网访问（手机/iPad）:"
    echo "     http://$LOCAL_IP:$PORT"
    echo
fi

echo "  💡 使用提示:"
echo "     • 按 Ctrl+C 停止服务"
echo "     • 修改数据后刷新浏览器即可"
echo "     • 右上角可切换深色/浅色主题"
echo "     • 点击 '隐藏金额' 可截图分享"
echo

echo "═══════════════════════════════════════════════════════════"
echo

# 尝试自动打开浏览器
sleep 1
if [ "$1" != "--no-open" ]; then
    info "正在打开浏览器..."
    if [ "$OS" = "macos" ]; then
        open "http://localhost:$PORT" 2>/dev/null || true
    elif [ "$OS" = "linux" ]; then
        xdg-open "http://localhost:$PORT" 2>/dev/null || true
    elif [ "$OS" = "windows" ]; then
        start "http://localhost:$PORT" 2>/dev/null || true
    fi
fi

echo
success "服务器运行中..."
echo

# 启动 HTTP 服务器
$PYTHON_CMD -m http.server $PORT --bind 0.0.0.0
