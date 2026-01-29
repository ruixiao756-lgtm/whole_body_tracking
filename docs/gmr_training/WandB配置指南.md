# WandB配置快速参考

## 1. 初始化WandB账户

### 登录WandB
```bash
wandb login
# 输入你的API key (从 https://wandb.ai/authorize 获取)
```

### 创建Registry集合

1. 访问 https://wandb.ai/
2. 点击左侧菜单 **Core** → **Registry**
3. 点击 **New Collection**
4. 填写信息:
   - **Name**: Motions
   - **Type**: All Types (或选择 dataset)
   - **Description**: GMR motion retargeting results
5. 点击 **Create**

## 2. 获取你的组织名

- 查看URL: `https://wandb.ai/<your-username>/...`
- 组织名格式: `<your-username>-org`
- 例如: 用户名是 `ruixiao756-lgtm`, 则组织名是 `ruixiao756-lgtm-org`

## 3. WandB Registry路径格式

```
<org-name>-org/wandb-registry-<collection-name>/<artifact-name>:<version>
```

示例:
```
ruixiao756-lgtm-org/wandb-registry-motions/stand_g1:latest
ruixiao756-lgtm-org/wandb-registry-motions/walk_amass:v0
```

## 4. 环境变量配置(可选)

```bash
# 设置默认组织
export WANDB_ENTITY=your-username

# 设置默认项目
export WANDB_PROJECT=GMR-MotionTracking

# 离线模式(仅本地保存)
export WANDB_MODE=offline
```

## 5. 快速检查

```bash
# 检查是否已登录
python -c "import wandb; api = wandb.Api(); print('✓ WandB已登录')"

# 列出Registry中的动作
cd /home/abc/GMR
python programs/check_wandb_registry.py --wandb-org your-username
```

## 6. 常见问题

### Q: Registry集合名称必须是"Motions"吗?
A: 不是,可以自定义。但如果修改,需要在`batch_csv_to_npz.py`中修改`REGISTRY`变量。

### Q: 可以使用多个Registry集合吗?
A: 可以。比如创建"Motions-Simple"和"Motions-Complex"分别存放简单和复杂动作。

### Q: WandB免费版有存储限制吗?
A: 免费版有100GB存储限制。每个NPZ文件约几MB,足够存储数百个动作。

### Q: 训练时必须使用WandB吗?
A: 不是。可以使用`--logger=tensorboard`或不使用logger。但WandB提供更好的可视化和实验管理。

## 7. 相关文档

- WandB官方文档: https://docs.wandb.ai/
- Registry文档: https://docs.wandb.ai/guides/registry
- API参考: https://docs.wandb.ai/ref/python/
