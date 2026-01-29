# GMR运动重定向结果训练指南

## 📋 概述

本指南介绍如何将GMR重定向输出的pkl文件用于IsaacLab的whole_body_tracking训练。

## 🔄 数据流程

```
GMR pkl文件 → CSV文件(已有) → NPZ文件 → WandB Registry → IsaacLab训练
```

## ✅ 前置检查

### 1. GMR输出格式确认

GMR的pkl文件包含以下字段:
- `fps`: 帧率 (float)
- `root_pos`: 根位置 (N, 3)
- `root_rot`: 根旋转 (N, 4) - 四元数
- `dof_pos`: 关节位置 (N, 29) - G1机器人29个自由度
- `local_body_pos`: 局部体位置 (None或数据)
- `link_body_list`: 链接体列表 (None或列表)

### 2. CSV文件格式

GMR已经生成了所需的CSV文件(`pkl_files/csv/`目录),格式符合Unitree数据集规范:
- 每行一帧
- 包含36个字段(根位置3+根旋转4+关节位置29)
- 逗号分隔,科学计数法表示

## 📝 操作步骤

### 步骤1: 准备WandB账户

```bash
# 登录WandB
wandb login

# 创建Registry集合(在WandB网页端操作)
# 1. 访问 https://wandb.ai/
# 2. 进入 Core → Registry
# 3. 创建新集合,名称: "Motions", 类型: "All Types"
```

### 步骤2: 批量转换CSV到NPZ并上传

```bash
# 激活whole_body_tracking环境
cd /home/abc/whole_body_tracking
conda activate isaaclab  # 或你的IsaacLab环境名

# 使用提供的批量转换脚本
cd /home/abc/GMR
python programs/batch_csv_to_npz.py
```

### 步骤3: 验证上传结果

```bash
# 测试回放某个动作
cd /home/abc/whole_body_tracking
python scripts/replay_npz.py --registry_name=你的组织名-org/wandb-registry-motions/stand_g1
```

### 步骤4: 开始训练

```bash
# 训练单个动作
cd /home/abc/whole_body_tracking
python scripts/rsl_rl/train.py \
    --task=G1-Flat \
    --registry_name=你的组织名-org/wandb-registry-motions/stand_g1 \
    --num_envs=4096 \
    --max_iterations=1000 \
    --logger=wandb \
    --log_project_name=GMR-MotionTracking

# 使用提供的批量训练脚本
cd /home/abc/GMR
python programs/batch_train_motions.py
```

## 🛠️ 提供的辅助脚本

### 1. `programs/batch_csv_to_npz.py`
批量将GMR的CSV文件转换为NPZ并上传到WandB

### 2. `programs/batch_train_motions.py`
批量训练多个动作的脚本

### 3. `programs/check_wandb_registry.py`
检查WandB Registry中的动作列表

## ⚙️ 关键参数说明

### csv_to_npz.py参数
- `--input_file`: CSV文件路径
- `--input_fps`: 输入帧率(GMR默认30)
- `--frame_range`: 帧范围,可选(如: 100 500)
- `--output_name`: 输出名称(会作为WandB Registry的artifact名)
- `--output_fps`: 输出帧率(默认50,IsaacLab使用)
- `--headless`: 无头模式,不显示UI

### train.py参数
- `--task`: 任务名称(如: G1-Flat, G1-Rough)
- `--registry_name`: WandB Registry路径(格式: 组织/集合/动作名)
- `--num_envs`: 并行环境数(默认4096)
- `--max_iterations`: 训练迭代次数
- `--logger`: 日志工具(wandb/tensorboard)
- `--log_project_name`: WandB项目名

## 📊 推荐训练配置

### 硬件要求
- GPU: RTX 3090及以上(24GB显存)
- CPU: 16核以上
- RAM: 32GB以上

### 训练参数建议

| 动作类型 | num_envs | max_iterations | 预计时间 |
|---------|----------|----------------|---------|
| Stand   | 4096     | 500            | ~1小时  |
| Walk    | 4096     | 1000           | ~2小时  |
| Turn    | 4096     | 1000           | ~2小时  |
| Crouch  | 4096     | 1500           | ~3小时  |
| Dance   | 8192     | 2000           | ~5小时  |

## 🔍 故障排查

### 问题1: 找不到WandB Registry
```bash
# 检查registry名称格式
# 正确格式: <your-username>-org/wandb-registry-motions/<motion-name>:latest
# 或: <your-username>-org/wandb-registry-motions/<motion-name>:v0
```

### 问题2: CSV转NPZ失败
```bash
# 检查CSV格式
python -c "import pandas as pd; df = pd.read_csv('pkl_files/csv/stand_g1.csv', header=None); print(df.shape)"
# 应该输出: (N, 36) 其中N是帧数
```

### 问题3: 训练过程中GPU内存不足
```bash
# 减少并行环境数
--num_envs=2048  # 从4096降到2048
```

### 问题4: 动作质量不佳
- 检查CSV数据质量(使用GMR评估工具)
- 增加训练迭代次数
- 调整奖励函数权重(在IsaacLab任务配置中)

## 📁 文件结构

```
GMR/
├── pkl_files/
│   ├── walk_amass.pkl
│   ├── turn_amass.pkl
│   ├── ...
│   └── csv/
│       ├── stand_g1.csv  ✓ 已有
│       ├── walk_amass.csv  (需生成)
│       └── ...
├── programs/
│   ├── batch_csv_to_npz.py  (新建)
│   ├── batch_train_motions.py  (新建)
│   └── check_wandb_registry.py  (新建)
└── docs/
    └── whole_body_tracking训练指南.md  (本文档)

whole_body_tracking/
├── scripts/
│   ├── csv_to_npz.py  (使用此脚本)
│   ├── replay_npz.py
│   └── rsl_rl/
│       └── train.py  (训练脚本)
└── motions/
    └── *.npz  (转换后的文件,临时)
```

## 🎯 最佳实践

1. **数据准备阶段**
   - 先用小数据集(100-200帧)测试流程
   - 确认动作质量后再处理完整数据

2. **训练阶段**
   - 从简单动作(stand)开始
   - 逐步增加到复杂动作(dance)
   - 使用WandB监控训练曲线

3. **评估阶段**
   - 使用replay脚本可视化效果
   - 对比GMR评估结果和训练结果

## 📞 相关文档

- GMR项目说明: [CLAUDE.md](../CLAUDE.md)
- IsaacLab文档: https://isaac-sim.github.io/IsaacLab
- WandB文档: https://docs.wandb.ai/
- BeyondMimic论文: https://arxiv.org/abs/2508.08241

## 更新日志

- 2026-01-29: 初始版本,支持GMR重定向结果的训练流程
