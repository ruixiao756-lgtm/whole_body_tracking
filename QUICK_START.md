# 🚀 GMR训练快速指南 - 新位置版本

## ✅ 文件已迁移到whole_body_tracking

所有GMR训练工具现在位于: `/home/abc/whole_body_tracking/scripts/gmr_training/`

## 🎯 5分钟开始训练

### 方式1: 一键运行 (最简单) ⭐

```bash
cd /home/abc/whole_body_tracking
bash scripts/gmr_training/example_workflow.sh your-wandb-username
```

### 方式2: 分步执行 (推荐理解流程)

```bash
cd /home/abc/whole_body_tracking

# Step 1: 转换CSV到NPZ并上传WandB
python scripts/gmr_training/batch_csv_to_npz.py \
    --wandb-org your-username \
    --headless

# Step 2: 检查上传结果
python scripts/gmr_training/check_wandb_registry.py \
    --wandb-org your-username

# Step 3: 开始训练
python scripts/gmr_training/batch_train_motions.py \
    --wandb-org your-username
```

## 📚 文档位置

所有文档现在在: `/home/abc/whole_body_tracking/docs/gmr_training/`

- **快速开始**: `docs/gmr_training/训练快速开始.md` ⭐
- **完整教程**: `docs/gmr_training/训练方案总览.md`
- **WandB配置**: `docs/gmr_training/WandB配置指南.md`
- **文档索引**: `docs/gmr_training/README.md`

## 🔧 常用命令

### 转换特定动作
```bash
cd /home/abc/whole_body_tracking
python scripts/gmr_training/batch_csv_to_npz.py \
    --wandb-org USER \
    --filter "stand*" \
    --headless
```

### 训练特定动作
```bash
python scripts/gmr_training/batch_train_motions.py \
    --wandb-org USER \
    --motions stand_g1 walk_amass
```

### 自定义训练参数
```bash
python scripts/gmr_training/batch_train_motions.py \
    --wandb-org USER \
    --motions walk_amass \
    --max-iterations 2000 \
    --num-envs 8192
```

### 测试模式(不实际执行)
```bash
python scripts/gmr_training/batch_csv_to_npz.py \
    --wandb-org USER \
    --dry-run
```

## 📁 目录结构

```
whole_body_tracking/
├── scripts/gmr_training/      # 训练脚本
│   ├── batch_csv_to_npz.py
│   ├── batch_train_motions.py
│   ├── check_wandb_registry.py
│   ├── example_workflow.sh
│   └── README.md
│
├── docs/gmr_training/         # 训练文档
│   ├── 训练快速开始.md ⭐
│   ├── 训练方案总览.md
│   └── ...
│
├── GMR_TRAINING_INTEGRATION.md  # 集成说明
└── MIGRATION_COMPLETE.md        # 迁移完成总结
```

## 💡 重要提示

### ✅ 使用新位置
```bash
# ✅ 正确 (新位置)
cd /home/abc/whole_body_tracking
python scripts/gmr_training/batch_csv_to_npz.py ...
```

### ❌ 不要使用旧位置
```bash
# ❌ 已废弃 (旧位置保留作为备份)
cd /home/abc/GMR
python programs/batch_csv_to_npz.py ...
```

## 🎓 学习路径

1. **首次使用**: 运行 `example_workflow.sh`
2. **理解流程**: 阅读 `docs/gmr_training/训练快速开始.md`
3. **深入学习**: 阅读 `docs/gmr_training/训练方案总览.md`
4. **自定义配置**: 修改训练参数进行优化

## 📞 获取帮助

```bash
# 查看脚本帮助
python scripts/gmr_training/batch_csv_to_npz.py --help
python scripts/gmr_training/batch_train_motions.py --help

# 查看文档
cat docs/gmr_training/训练快速开始.md
cat GMR_TRAINING_INTEGRATION.md
```

---

**重要**: 所有文件已迁移到whole_body_tracking,请使用新路径!
