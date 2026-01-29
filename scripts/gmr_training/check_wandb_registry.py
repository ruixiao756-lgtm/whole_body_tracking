#!/usr/bin/env python3
"""
检查WandB Registry中已上传的动作

用法:
    python check_wandb_registry.py --wandb-org your-org-name
    
示例:
    python check_wandb_registry.py --wandb-org ruixiao756-lgtm
"""

import argparse
import sys
from pathlib import Path

try:
    import wandb
except ImportError:
    print("错误: 未安装wandb库")
    print("安装命令: pip install wandb")
    sys.exit(1)

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'

def print_info(msg: str):
    print(f"{Colors.BLUE}[INFO]{Colors.END} {msg}")

def print_success(msg: str):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.END} {msg}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}[WARNING]{Colors.END} {msg}")

def print_error(msg: str):
    print(f"{Colors.RED}[ERROR]{Colors.END} {msg}")

def print_title(msg: str):
    print(f"\n{Colors.CYAN}{'=' * 70}")
    print(f"{msg}")
    print(f"{'=' * 70}{Colors.END}\n")

def list_registry_motions(wandb_org: str, registry_name: str = "motions"):
    """列出WandB Registry中的所有动作"""
    
    print_title(f"WandB Registry - {wandb_org}")
    
    try:
        # 初始化API
        api = wandb.Api()
        
        # 获取registry集合
        collection_path = f"{wandb_org}-org/wandb-registry-{registry_name}"
        print_info(f"查询集合: {collection_path}")
        
        # 列出所有artifacts
        print_info("获取artifacts列表...")
        
        artifacts = api.artifacts(
            type_name=registry_name,
            name=f"{collection_path}/*"
        )
        
        artifact_list = list(artifacts)
        
        if not artifact_list:
            print_warning(f"未找到任何动作")
            print_info(f"\n请确保:")
            print(f"  1. WandB组织名正确: {wandb_org}")
            print(f"  2. Registry集合已创建: {registry_name}")
            print(f"  3. 已上传至少一个动作")
            return
        
        print_success(f"找到 {len(artifact_list)} 个动作\n")
        
        # 打印表头
        print(f"{'序号':<5} {'动作名':<35} {'版本':<10} {'大小':<10} {'创建时间'}")
        print("-" * 90)
        
        # 打印每个动作信息
        for i, artifact in enumerate(artifact_list, 1):
            # 提取动作名(去掉路径前缀)
            motion_name = artifact.name.split("/")[-1].split(":")[0]
            version = artifact.version
            
            # 获取大小(KB)
            size_bytes = artifact.size
            size_kb = size_bytes / 1024 if size_bytes else 0
            size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
            
            # 创建时间
            created_at = artifact.created_at[:19] if artifact.created_at else "未知"
            
            print(f"{i:<5} {motion_name:<35} {version:<10} {size_str:<10} {created_at}")
        
        # 打印使用示例
        if artifact_list:
            example_motion = artifact_list[0].name.split("/")[-1].split(":")[0]
            
            print_title("使用示例")
            
            print_info("1. 回放动作(验证上传成功):")
            print(f"   cd /home/abc/whole_body_tracking")
            print(f"   python scripts/replay_npz.py \\")
            print(f"       --registry_name={wandb_org}-org/wandb-registry-{registry_name}/{example_motion}:latest")
            
            print_info("\n2. 训练动作:")
            print(f"   cd /home/abc/whole_body_tracking")
            print(f"   python scripts/rsl_rl/train.py \\")
            print(f"       --task=G1-Flat \\")
            print(f"       --registry_name={wandb_org}-org/wandb-registry-{registry_name}/{example_motion}:latest \\")
            print(f"       --num_envs=4096 \\")
            print(f"       --max_iterations=1000 \\")
            print(f"       --logger=wandb \\")
            print(f"       --log_project_name=GMR-MotionTracking")
            
            print_info("\n3. 批量训练所有动作:")
            print(f"   cd /home/abc/GMR")
            print(f"   python programs/batch_train_motions.py --wandb-org {wandb_org}")
        
    except wandb.errors.CommError as e:
        print_error(f"WandB API错误: {e}")
        print_warning("请确保:")
        print("  1. 已登录WandB: wandb login")
        print("  2. 网络连接正常")
        print("  3. 组织名正确")
    except Exception as e:
        print_error(f"发生错误: {e}")
        import traceback
        traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(
        description="检查WandB Registry中已上传的动作"
    )
    parser.add_argument(
        "--wandb-org",
        type=str,
        required=True,
        help="WandB组织名(如: ruixiao756-lgtm)"
    )
    parser.add_argument(
        "--registry-name",
        type=str,
        default="motions",
        help="Registry集合名称(默认: motions)"
    )
    
    args = parser.parse_args()
    
    # 检查是否已登录
    try:
        api = wandb.Api()
        print_success("WandB已登录")
    except Exception as e:
        print_error("未登录WandB")
        print_info("请先执行: wandb login")
        sys.exit(1)
    
    # 列出Registry中的动作
    list_registry_motions(args.wandb_org, args.registry_name)

if __name__ == "__main__":
    main()
