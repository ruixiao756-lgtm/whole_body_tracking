# GMR训练工具集

将GMR运动重定向结果用于whole_body_tracking强化学习训练的完整工具链。

## 📁 目录结构

```
whole_body_tracking/
├── scripts/
│   ├── csv_to_npz.py           # IsaacLab原生转换脚本
│   ├── replay_npz.py           # IsaacLab原生回放脚本
│   ├── gmr_training/           # GMR训练工具集 (新增)
│   │   ├── batch_csv_to_npz.py       # 批量CSV→NPZ转换
│   │   ├── batch_train_motions.py    # 批量训练脚本
│   │   ├── check_wandb_registry.py   # Registry检查工具
│   │   └── example_workflow.sh       # 示例流程脚本
│   └── rsl_rl/
│       └── train.py            # 训练脚本
└── docs/
    └── gmr_training/           # GMR训练文档 (新增)
        ├── 训练快速开始.md       # ⭐ 5分钟快速指南
        ├── 训练方案总览.md        # 完整方案说明
        ├── whole_body_tracking训练指南.md
        ├── WandB配置指南.md
        ├── README_TRAINING.md    # 主文档
        └── TRAINING_COMPLETED.md # 完成总结
```

## 🚀 快速开始

### 方式1: 使用示例脚本 (推荐新手)

```bash
cd /home/abc/whole_body_tracking
bash scripts/gmr_training/example_workflow.sh your-wandb-username
```

### 方式2: 分步执行

```bash
cd /home/abc/whole_body_tracking

# 1. 转换CSV到NPZ并上传WandB
python scripts/gmr_training/batch_csv_to_npz.py \
    --wandb-org your-username \
    --headless

# 2. 检查Registry
python scripts/gmr_training/check_wandb_registry.py \
    --wandb-org your-username

# 3. 批量训练
python scripts/gmr_training/batch_train_motions.py \
    --wandb-org your-username
```

## 📚 文档

- **快速开始**: [docs/gmr_training/训练快速开始.md](../../docs/gmr_training/训练快速开始.md)
- **完整教程**: [docs/gmr_training/训练方案总览.md](../../docs/gmr_training/训练方案总览.md)
- **WandB配置**: [docs/gmr_training/WandB配置指南.md](../../docs/gmr_training/WandB配置指南.md)

## 🛠️ 工具说明

### batch_csv_to_npz.py
批量将GMR的CSV文件转换为NPZ格式并上传到WandB Registry

**功能**:
- 自动扫描 `/home/abc/GMR/pkl_files/csv/` 目录
- CSV格式验证(36列检查)
- 批量转换并上传
- 支持通配符过滤

**示例**:
```bash
# 转换所有动作
python scripts/gmr_training/batch_csv_to_npz.py --wandb-org USER --headless

# 只转换特定动作
python scripts/gmr_training/batch_csv_to_npz.py --wandb-org USER --filter "walk*" --headless

# 测试模式(不实际执行)
python scripts/gmr_training/batch_csv_to_npz.py --wandb-org USER --dry-run
```

### batch_train_motions.py
批量训练多个GMR重定向动作

**功能**:
- 7个动作的预设配置
- 自动时间估算
- 失败后继续选项
- WandB日志集成

**示例**:
```bash
# 训练所有动作
python scripts/gmr_training/batch_train_motions.py --wandb-org USER

# 训练特定动作
python scripts/gmr_training/batch_train_motions.py \
    --wandb-org USER \
    --motions stand_g1 walk_amass

# 自定义参数
python scripts/gmr_training/batch_train_motions.py \
    --wandb-org USER \
    --motions walk_amass \
    --max-iterations 2000 \
    --num-envs 8192
```

### check_wandb_registry.py
检查WandB Registry中已上传的动作

**示例**:
```bash
python scripts/gmr_training/check_wandb_registry.py --wandb-org USER
```

## 🎯 数据流程

```
GMR重定向结果
(/home/abc/GMR/pkl_files/)
    ↓
CSV文件 (已生成)
    ↓
batch_csv_to_npz.py → NPZ文件 + WandB上传
    ↓
check_wandb_registry.py → 验证上传
    ↓
batch_train_motions.py → IsaacLab训练
    ↓
WandB可视化 + IsaacLab回放
```

## ⚙️ 默认配置

| 动作 | 并行环境 | 迭代次数 | 预计时间 |
|------|----------|---------|---------|
| stand_g1 | 4096 | 500 | ~1小时 |
| walk_amass | 4096 | 1000 | ~2小时 |
| turn_amass | 4096 | 1000 | ~2小时 |
| crouch_amass | 4096 | 1500 | ~3小时 |
| sway_amass | 4096 | 1000 | ~2小时 |
| swing_amass | 4096 | 1000 | ~2小时 |
| dance2_* | 8192 | 2000 | ~5小时 |

## 🔧 常见问题

### Q: GMR的CSV文件在哪里?
A: `/home/abc/GMR/pkl_files/csv/` 目录。工具会自动读取这个路径。

### Q: 训练结果保存在哪里?
A: 
- Checkpoint: `whole_body_tracking/logs/rsl_rl/`
- WandB在线: `https://wandb.ai/your-username/GMR-MotionTracking`

### Q: GPU内存不足怎么办?
A: 减少并行环境数: `--num-envs=2048` (或更低到1024)

### Q: 如何添加新动作?
A: 
1. GMR生成新的CSV文件到 `/home/abc/GMR/pkl_files/csv/`
2. 运行 `batch_csv_to_npz.py` 转换新动作
3. 运行 `batch_train_motions.py --motions new_motion` 训练

## 📞 获取帮助

- 阅读文档: `docs/gmr_training/训练快速开始.md`
- 查看脚本帮助: `python scripts/gmr_training/*.py --help`
- GMR项目文档: `/home/abc/GMR/CLAUDE.md`

## ✅ 前置条件

开始前确认:
- [ ] WandB已登录: `wandb login`
- [ ] WandB Registry已创建(Motions集合)
- [ ] GMR已生成CSV文件
- [ ] IsaacLab环境已激活

---

**位置**: `/home/abc/whole_body_tracking/scripts/gmr_training/`  
**创建日期**: 2026-01-29  
**用途**: GMR运动重定向结果的批量训练工具集
