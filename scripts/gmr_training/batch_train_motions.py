#!/usr/bin/env python3
"""
批量训练GMR重定向的动作

用法:
    python batch_train_motions.py --wandb-org your-org-name [options]
    
示例:
    # 训练所有动作,每个1000次迭代
    python batch_train_motions.py --wandb-org ruixiao756-lgtm --max-iterations 1000
    
    # 只训练特定动作
    python batch_train_motions.py --wandb-org ruixiao756-lgtm --motions stand_g1 walk_amass
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Dict
import time
from datetime import datetime

# 项目路径
WHOLE_BODY_TRACKING_ROOT = Path(__file__).parent.parent.parent
TRAIN_SCRIPT = WHOLE_BODY_TRACKING_ROOT / "scripts" / "rsl_rl" / "train.py"
GMR_ROOT = Path("/home/abc/GMR")

# 训练配置(根据动作复杂度调整)
MOTION_CONFIGS = {
    "stand_g1": {
        "num_envs": 4096,
        "max_iterations": 500,
        "description": "站立动作"
    },
    "walk_amass": {
        "num_envs": 4096,
        "max_iterations": 1000,
        "description": "行走动作"
    },
    "turn_amass": {
        "num_envs": 4096,
        "max_iterations": 1000,
        "description": "转身动作"
    },
    "crouch_amass": {
        "num_envs": 4096,
        "max_iterations": 1500,
        "description": "蹲下动作"
    },
    "sway_amass": {
        "num_envs": 4096,
        "max_iterations": 1000,
        "description": "摇摆动作"
    },
    "swing_amass": {
        "num_envs": 4096,
        "max_iterations": 1000,
        "description": "摆动动作"
    },
    "dance2_subject2_unitree_g1": {
        "num_envs": 8192,
        "max_iterations": 2000,
        "description": "舞蹈动作(复杂)"
    }
}

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

def get_motion_config(motion_name: str, default_iterations: int = None) -> Dict:
    """获取动作配置"""
    if motion_name in MOTION_CONFIGS:
        config = MOTION_CONFIGS[motion_name].copy()
    else:
        # 使用默认配置
        config = {
            "num_envs": 4096,
            "max_iterations": default_iterations or 1000,
            "description": "未知动作"
        }
    return config

def train_motion(
    motion_name: str,
    wandb_org: str,
    task: str = "G1-Flat",
    num_envs: int = None,
    max_iterations: int = None,
    wandb_project: str = "GMR-MotionTracking",
    registry_alias: str = "latest",
    dry_run: bool = False
) -> bool:
    """
    训练单个动作
    
    Args:
        motion_name: 动作名称
        wandb_org: WandB组织名
        task: IsaacLab任务名
        num_envs: 并行环境数
        max_iterations: 训练迭代次数
        wandb_project: WandB项目名
        registry_alias: Registry版本别名
        dry_run: 仅打印命令,不执行
        
    Returns:
        bool: 是否成功
    """
    # 获取配置
    config = get_motion_config(motion_name, max_iterations)
    
    # 使用传入的参数覆盖配置
    if num_envs:
        config["num_envs"] = num_envs
    if max_iterations:
        config["max_iterations"] = max_iterations
    
    # 构建registry名称
    registry_name = f"{wandb_org}-org/wandb-registry-motions/{motion_name}:{registry_alias}"
    
    print_title(f"训练动作: {motion_name}")
    print_info(f"描述: {config['description']}")
    print_info(f"任务: {task}")
    print_info(f"并行环境: {config['num_envs']}")
    print_info(f"训练迭代: {config['max_iterations']}")
    print_info(f"Registry: {registry_name}")
    print_info(f"WandB项目: {wandb_project}")
    
    # 构建训练命令
    cmd = [
        sys.executable,
        str(TRAIN_SCRIPT),
        f"--task={task}",
        f"--registry_name={registry_name}",
        f"--num_envs={config['num_envs']}",
        f"--max_iterations={config['max_iterations']}",
        "--logger=wandb",
        f"--log_project_name={wandb_project}",
        "--headless",  # 无头模式
    ]
    
    print_info(f"\n命令:")
    print(f"  {' '.join(cmd)}\n")
    
    if dry_run:
        print_warning("Dry-run模式,跳过执行")
        return True
    
    # 记录开始时间
    start_time = time.time()
    
    try:
        # 执行训练
        print_info("开始训练...")
        result = subprocess.run(
            cmd,
            cwd=WHOLE_BODY_TRACKING_ROOT,
            capture_output=False,  # 实时显示输出
            text=True
        )
        
        # 计算耗时
        elapsed_time = time.time() - start_time
        elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        
        if result.returncode == 0:
            print_success(f"✓ {motion_name} 训练完成! 耗时: {elapsed_str}")
            return True
        else:
            print_error(f"✗ {motion_name} 训练失败! (退出码: {result.returncode})")
            return False
            
    except KeyboardInterrupt:
        print_warning(f"\n用户中断训练: {motion_name}")
        return False
    except Exception as e:
        print_error(f"✗ {motion_name} 训练异常: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="批量训练GMR重定向的动作",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
可训练的动作列表:
  - stand_g1               (站立, 500次迭代)
  - walk_amass             (行走, 1000次迭代)
  - turn_amass             (转身, 1000次迭代)
  - crouch_amass           (蹲下, 1500次迭代)
  - sway_amass             (摇摆, 1000次迭代)
  - swing_amass            (摆动, 1000次迭代)
  - dance2_subject2_unitree_g1  (舞蹈, 2000次迭代)

示例:
  # 训练所有动作
  python batch_train_motions.py --wandb-org ruixiao756-lgtm
  
  # 训练特定动作
  python batch_train_motions.py --wandb-org ruixiao756-lgtm --motions stand_g1 walk_amass
  
  # 自定义训练参数
  python batch_train_motions.py --wandb-org ruixiao756-lgtm --motions walk_amass \
      --num-envs 8192 --max-iterations 2000
        """
    )
    
    parser.add_argument(
        "--wandb-org",
        type=str,
        required=True,
        help="WandB组织名(如: ruixiao756-lgtm)"
    )
    parser.add_argument(
        "--motions",
        nargs="+",
        default=None,
        help="要训练的动作列表(默认训练所有)"
    )
    parser.add_argument(
        "--task",
        type=str,
        default="G1-Flat",
        help="IsaacLab任务名(默认: G1-Flat)"
    )
    parser.add_argument(
        "--num-envs",
        type=int,
        default=None,
        help="并行环境数(覆盖默认配置)"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="训练迭代次数(覆盖默认配置)"
    )
    parser.add_argument(
        "--wandb-project",
        type=str,
        default="GMR-MotionTracking",
        help="WandB项目名(默认: GMR-MotionTracking)"
    )
    parser.add_argument(
        "--registry-alias",
        type=str,
        default="latest",
        help="WandB Registry别名(默认: latest)"
    )
    parser.add_argument(
        "--continue-on-failure",
        action="store_true",
        help="某个动作失败后继续训练其他动作"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅显示将要执行的命令,不实际训练"
    )
    
    args = parser.parse_args()
    
    # 检查训练脚本
    if not TRAIN_SCRIPT.exists():
        print_error(f"训练脚本不存在: {TRAIN_SCRIPT}")
        print_error("请确保whole_body_tracking已正确安装")
        sys.exit(1)
    
    # 确定要训练的动作
    if args.motions:
        motions_to_train = args.motions
    else:
        motions_to_train = list(MOTION_CONFIGS.keys())
    
    print_title("批量训练GMR动作")
    print_info(f"WandB组织: {args.wandb_org}")
    print_info(f"WandB项目: {args.wandb_project}")
    print_info(f"任务: {args.task}")
    print_info(f"要训练的动作数量: {len(motions_to_train)}")
    
    for motion in motions_to_train:
        print(f"  - {motion}")
    
    if args.dry_run:
        print_warning("\nDry-run模式,不会实际训练")
    
    print("\n")
    
    # 批量训练
    success_count = 0
    failed_motions = []
    total_start_time = time.time()
    
    for i, motion_name in enumerate(motions_to_train, 1):
        print_info(f"\n进度: [{i}/{len(motions_to_train)}]")
        
        success = train_motion(
            motion_name=motion_name,
            wandb_org=args.wandb_org,
            task=args.task,
            num_envs=args.num_envs,
            max_iterations=args.max_iterations,
            wandb_project=args.wandb_project,
            registry_alias=args.registry_alias,
            dry_run=args.dry_run
        )
        
        if success:
            success_count += 1
        else:
            failed_motions.append(motion_name)
            if not args.continue_on_failure:
                print_error("\n训练失败,停止批处理(使用 --continue-on-failure 继续)")
                break
        
        # 动作之间短暂休息
        if i < len(motions_to_train) and not args.dry_run:
            print_info("等待5秒后继续下一个动作...")
            time.sleep(5)
    
    # 总结
    total_elapsed = time.time() - total_start_time
    total_elapsed_str = time.strftime("%H:%M:%S", time.gmtime(total_elapsed))
    
    print_title("批量训练完成!")
    print_success(f"成功: {success_count}/{len(motions_to_train)}")
    
    if failed_motions:
        print_error(f"失败: {len(failed_motions)}/{len(motions_to_train)}")
        print_error("失败动作列表:")
        for motion in failed_motions:
            print(f"  - {motion}")
    
    if not args.dry_run:
        print_info(f"\n总耗时: {total_elapsed_str}")
        print_info(f"\n查看训练结果: https://wandb.ai/{args.wandb_org}/{args.wandb_project}")
    
    print("")

if __name__ == "__main__":
    main()
