#!/bin/bash
# =============================================================================
# Setup Data Directory - 初始化数据目录
# =============================================================================

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { echo -e "${BLUE}ℹ${NC}  $1"; }
success() { echo -e "${GREEN}✓${NC}  $1"; }
warning() { echo -e "${YELLOW}⚠${NC}  $1"; }

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║          📦 初始化数据目录                                 ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo

# 检查 data/ 是否已存在
if [ -d "data" ] && [ -f "data/history.json" ]; then
    warning "检测到现有数据目录"
    echo
    read -p "是否覆盖？这会删除所有现有数据！(yes/NO): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        info "已取消，保留现有数据"
        exit 0
    fi
    echo
    info "备份现有数据到 data.backup..."
    cp -r data data.backup.$(date +%Y%m%d_%H%M%S)
    success "备份完成"
fi

# 创建目录结构
info "创建数据目录结构..."
mkdir -p data/transactions/yearly
mkdir -p data/_backups
success "目录创建完成"

# 复制演示数据作为模板
info "复制演示数据作为模板..."
cp demo_data/target.json data/
cp demo_data/history.json data/
cp demo_data/recurring.json data/
cp demo_data/liabilities.json data/
cp demo_data/policies.json data/
cp demo_data/categories.json data/
cp demo_data/income_events.json data/
cp demo_data/risks.json data/
cp -r demo_data/transactions/* data/transactions/
success "数据文件复制完成"

# 创建 config.js
info "创建配置文件..."
cat > config.js << 'EOF'
// =============================================================
// 资产配置看板 · 全局配置
// =============================================================
window.AFD_CONFIG = {
  // 数据目录：'data' 为真实数据，'demo_data' 为演示数据
  dataDir: "data"
};
EOF
success "config.js 创建完成"

echo
echo "═══════════════════════════════════════════════════════════"
echo
success "初始化完成！"
echo
echo "  📝 下一步："
echo "     1. 编辑 data/target.json（调整你的目标配置）"
echo "     2. 编辑 data/history.json（填写真实持仓）"
echo "     3. 运行 ./start.sh 启动看板"
echo
warning "重要：请将 demo_data 中的所有金额改为你的真实数据！"
echo
echo "  💡 提示："
echo "     • 所有 data/ 文件不会被 Git 追踪（已忽略）"
echo "     • 建议使用 iCloud/OneDrive 同步 data/ 目录"
echo "     • 每次修改前运行: python3 scripts/backup_data.py"
echo
