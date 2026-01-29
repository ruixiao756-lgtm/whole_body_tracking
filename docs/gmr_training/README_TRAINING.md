# GMR → IsaacLab训练工具包

将GMR运动重定向结果用于IsaacLab强化学习训练的完整工具链。

## 📦 已完成准备

✅ **GMR输出**: pkl文件和CSV文件已生成  
✅ **转换脚本**: CSV→NPZ批量转换工具  
✅ **训练脚本**: 批量训练自动化  
✅ **WandB集成**: 自动上传Registry  
✅ **文档**: 完整使用指南  

## 🚀 快速开始(5分钟)

### 1. 登录WandB并创建Registry

```bash
# 登录
wandb login

# 创建Registry集合(浏览器操作)
# 访问 https://wandb.ai/ → Core → Registry → New Collection
# Name: Motions, Type: All Types
```

### 2. 转换并上传动作

```bash
cd /home/abc/GMR

# 转换所有CSV到NPZ并上传WandB
python programs/batch_csv_to_npz.py --wandb-org your-username --headless

# 示例: python programs/batch_csv_to_npz.py --wandb-org ruixiao756-lgtm --headless
```

### 3. 开始训练

```bash
# 训练所有动作
python programs/batch_train_motions.py --wandb-org your-username

# 训练特定动作
python programs/batch_train_motions.py --wandb-org your-username --motions stand_g1 walk_amass
```

### 4. 查看结果

访问: `https://wandb.ai/your-username/GMR-MotionTracking`

## 📚 完整文档

| 文档 | 说明 |
|------|------|
| [训练快速开始.md](docs/训练快速开始.md) | ⭐ 5分钟快速指南 |
| [训练方案总览.md](docs/训练方案总览.md) | 完整方案说明 |
| [whole_body_tracking训练指南.md](docs/whole_body_tracking训练指南.md) | 详细教程 |
| [WandB配置指南.md](docs/WandB配置指南.md) | WandB设置 |

## 🛠️ 工具脚本

### 核心脚本

| 脚本 | 功能 | 用法 |
|------|------|------|
| `batch_csv_to_npz.py` | CSV→NPZ转换 | `python programs/batch_csv_to_npz.py --wandb-org USER` |
| `batch_train_motions.py` | 批量训练 | `python programs/batch_train_motions.py --wandb-org USER` |
| `check_wandb_registry.py` | 检查Registry | `python programs/check_wandb_registry.py --wandb-org USER` |
| `example_workflow.sh` | 示例流程 | `bash example_workflow.sh USER` |

### 使用示例

```bash
# 1. 转换单个动作(测试)
python programs/batch_csv_to_npz.py --wandb-org your-username --filter "stand*" --headless

# 2. 转换所有动作
python programs/batch_csv_to_npz.py --wandb-org your-username --headless

# 3. 检查上传结果
python programs/check_wandb_registry.py --wandb-org your-username

# 4. 训练单个动作
python programs/batch_train_motions.py --wandb-org your-username --motions stand_g1

# 5. 训练所有动作
python programs/batch_train_motions.py --wandb-org your-username

# 6. 完整示例流程
bash example_workflow.sh your-username
```

## 📁 项目结构

```
GMR/
├── pkl_files/
│   ├── *.pkl                    # GMR重定向结果
│   └── csv/
│       ├── stand_g1.csv         # ✓ 已生成
│       └── *.csv                # 其他动作CSV
│
├── programs/                    # 🔧 训练工具
│   ├── batch_csv_to_npz.py     # CSV→NPZ批量转换
│   ├── batch_train_motions.py  # 批量训练
│   ├── check_wandb_registry.py # Registry检查
│   └── ...                      # 其他工具
│
├── docs/                        # 📖 文档
│   ├── 训练快速开始.md          # ⭐ 快速指南
│   ├── 训练方案总览.md          # 完整方案
│   ├── whole_body_tracking训练指南.md
│   └── WandB配置指南.md
│
├── example_workflow.sh          # 🚀 示例流程
└── README_TRAINING.md           # 本文档
```

## 🎯 训练配置

### 已配置的动作

| 动作 | 并行环境 | 迭代次数 | 预计时间 |
|------|----------|---------|---------|
| stand_g1 | 4096 | 500 | ~1小时 |
| walk_amass | 4096 | 1000 | ~2小时 |
| turn_amass | 4096 | 1000 | ~2小时 |
| crouch_amass | 4096 | 1500 | ~3小时 |
| sway_amass | 4096 | 1000 | ~2小时 |
| swing_amass | 4096 | 1000 | ~2小时 |
| dance2_subject2_unitree_g1 | 8192 | 2000 | ~5小时 |

### 自定义参数

```bash
# 修改训练次数
python programs/batch_train_motions.py \
    --wandb-org your-username \
    --motions walk_amass \
    --max-iterations 2000

# 修改并行环境数(GPU显存不足时)
python programs/batch_train_motions.py \
    --wandb-org your-username \
    --num-envs 2048
```

## 🔍 故障排查

### 常见问题

1. **找不到CSV文件**
   ```bash
   ls /home/abc/GMR/pkl_files/csv/
   # 应该看到至少有 stand_g1.csv
   ```

2. **WandB未登录**
   ```bash
   wandb login
   # 或重新登录: wandb login --relogin
   ```

3. **GPU内存不足**
   ```bash
   # 减少并行环境数
   --num-envs=2048  # 或 1024
   ```

4. **Registry找不到动作**
   ```bash
   # 检查Registry中的动作
   python programs/check_wandb_registry.py --wandb-org your-username
   ```

详细故障排查请查看[训练方案总览.md](docs/训练方案总览.md)。

## 📊 工作流程

```
1. GMR重定向           → pkl + csv 文件
2. batch_csv_to_npz   → NPZ文件 + WandB上传
3. check_registry     → 验证上传
4. batch_train        → IsaacLab训练
5. WandB可视化        → 查看训练结果
6. IsaacLab回放        → 验证效果
7. MuJoCo仿真         → 稳定性测试
8. 真机部署(返校后)    → 实际应用
```

## 🎓 学习路径

### 新手(第一次使用)
1. 阅读 [训练快速开始.md](docs/训练快速开始.md)
2. 运行 `bash example_workflow.sh your-username`
3. 训练第一个动作(stand_g1)
4. 查看WandB训练曲线

### 进阶使用
1. 阅读 [训练方案总览.md](docs/训练方案总览.md)
2. 批量训练所有动作
3. 调整训练参数优化效果
4. 在IsaacLab中回放验证

### 高级定制
1. 修改 `MOTION_CONFIGS` 添加新动作
2. 调整IsaacLab任务配置
3. 实现多动作联合训练
4. 准备真机部署

## 📞 获取帮助

- 📖 查看 [docs/](docs/) 目录中的详细文档
- 🔧 运行 `python programs/*.py --help` 查看脚本帮助
- 📝 参考 [GMR/CLAUDE.md](CLAUDE.md) 了解项目背景
- 🌐 访问 [IsaacLab文档](https://isaac-sim.github.io/IsaacLab)

## ✅ 检查清单

开始前确认:
- [ ] GMR已生成CSV文件
- [ ] WandB已登录(`wandb login`)
- [ ] WandB Registry已创建(Motions集合)
- [ ] IsaacLab环境已安装
- [ ] whole_body_tracking已安装

训练中检查:
- [ ] WandB显示训练曲线
- [ ] GPU使用率正常
- [ ] 无内存错误
- [ ] Checkpoint正常保存

训练后验证:
- [ ] WandB报告完整
- [ ] IsaacLab回放正常
- [ ] MuJoCo仿真稳定
- [ ] 准备真机部署

---

**创建日期**: 2026-01-29  
**适用于**: 毕业设计 - 仿人机器人运动重定向  
**相关项目**: GMR, whole_body_tracking, IsaacLab

**快速开始**: `bash example_workflow.sh your-wandb-username`
