#!/bin/bash
# GMR → IsaacLab 训练示例脚本
# 用法: bash example_workflow.sh <your-wandb-username>

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查参数
if [ -z "$1" ]; then
    echo -e "${RED}错误: 请提供WandB用户名${NC}"
    echo "用法: bash $0 <your-wandb-username>"
    echo "示例: bash $0 ruixiao756-lgtm"
    exit 1
fi

WANDB_ORG=$1
GMR_ROOT="/home/abc/GMR"
WBT_ROOT="/home/abc/whole_body_tracking"
SCRIPT_DIR="$WBT_ROOT/scripts/gmr_training"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}GMR → IsaacLab 训练示例流程${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "WandB组织: ${GREEN}${WANDB_ORG}${NC}"
echo ""

# Step 1: 检查环境
echo -e "${YELLOW}[Step 1/5]${NC} 检查环境..."

if [ ! -d "$GMR_ROOT/pkl_files/csv" ]; then
    echo -e "${RED}错误: CSV目录不存在${NC}"
    exit 1
fi

if [ ! -f "$WBT_ROOT/scripts/csv_to_npz.py" ]; then
    echo -e "${RED}错误: whole_body_tracking未安装${NC}"
    exit 1
fi

CSV_COUNT=$(ls -1 "$GMR_ROOT/pkl_files/csv"/*.csv 2>/dev/null | wc -l)
echo -e "${GREEN}✓${NC} 找到 $CSV_COUNT 个CSV文件"

# Step 2: 测试WandB连接
echo -e "\n${YELLOW}[Step 2/5]${NC} 检查WandB连接..."

if ! python3 -c "import wandb; api = wandb.Api(); print('✓ WandB已登录')" 2>/dev/null; then
    echo -e "${RED}错误: WandB未登录${NC}"
    echo "请先执行: wandb login"
    exit 1
fi

# Step 3: 转换CSV到NPZ (仅转换一个示例)
echo -e "\n${YELLOW}[Step 3/5]${NC} 转换CSV到NPZ (示例: stand_g1)..."

read -p "是否执行转换? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd "$WBT_ROOT"
    python scripts/gmr_training/batch_csv_to_npz.py \
        --wandb-org "$WANDB_ORG" \
        --filter "stand*" \
        --headless
    
    echo -e "${GREEN}✓${NC} 转换完成"
else
    echo -e "${YELLOW}跳过转换${NC}"
fi

# Step 4: 检查Registry
echo -e "\n${YELLOW}[Step 4/5]${NC} 检查WandB Registry..."

cd "$WBT_ROOT"
python scripts/gmr_training/check_wandb_registry.py --wandb-org "$WANDB_ORG"

# Step 5: 训练示例
echo -e "\n${YELLOW}[Step 5/5]${NC} 训练示例..."

read -p "是否开始训练stand_g1? (约1小时) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd "$WBT_ROOT"
    python scripts/gmr_training/batch_train_motions.py \
        --wandb-org "$WANDB_ORG" \
        --motions stand_g1 \
        --max-iterations 500
    
    echo -e "${GREEN}✓${NC} 训练完成"
    echo -e "查看结果: ${BLUE}https://wandb.ai/$WANDB_ORG/GMR-MotionTracking${NC}"
else
    echo -e "${YELLOW}跳过训练${NC}"
fi

# 完成
echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}示例流程完成!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "下一步操作:"
echo -e "  1. 转换所有动作:"
echo -e "     ${BLUE}python scripts/gmr_training/batch_csv_to_npz.py --wandb-org $WANDB_ORG --headless${NC}"
echo ""
echo -e "  2. 批量训练:"
echo -e "     ${BLUE}python scripts/gmr_training/batch_train_motions.py --wandb-org $WANDB_ORG${NC}"
echo ""
echo -e "  3. 查看文档:"
echo -e "     ${BLUE}cat docs/gmr_training/训练快速开始.md${NC}"
echo ""
