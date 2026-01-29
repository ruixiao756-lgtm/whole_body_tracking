#!/usr/bin/env python3
"""
批量将GMR的CSV文件转换为NPZ格式并上传到WandB Registry

用法:
    python batch_csv_to_npz.py --wandb-org your-org-name [--headless]
    
示例:
    python batch_csv_to_npz.py --wandb-org ruixiao756-lgtm --headless --input-fps 30 --output-fps 50
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Dict
import glob

# 项目路径
WHOLE_BODY_TRACKING_ROOT = Path(__file__).parent.parent.parent
GMR_ROOT = Path("/home/abc/GMR")
PKL_CSV_DIR = GMR_ROOT / "pkl_files" / "csv"
CSV_TO_NPZ_SCRIPT = WHOLE_BODY_TRACKING_ROOT / "scripts" / "csv_to_npz.py"

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_info(msg: str):
    print(f"{Colors.BLUE}[INFO]{Colors.END} {msg}")

def print_success(msg: str):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.END} {msg}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}[WARNING]{Colors.END} {msg}")

def print_error(msg: str):
    print(f"{Colors.RED}[ERROR]{Colors.END} {msg}")

def find_csv_files() -> List[Path]:
    """查找所有CSV文件"""
    csv_files = list(PKL_CSV_DIR.glob("*.csv"))
    return sorted(csv_files)

def get_motion_name(csv_file: Path) -> str:
    """从CSV文件名提取动作名"""
    return csv_file.stem  # 去掉.csv后缀

def check_csv_format(csv_file: Path) -> bool:
    """检查CSV格式是否正确"""
    try:
        with open(csv_file, 'r') as f:
            first_line = f.readline().strip()
            values = first_line.split(',')
            if len(values) != 36:
                print_error(f"{csv_file.name}: 列数错误,期望36列,实际{len(values)}列")
                return False
        return True
    except Exception as e:
        print_error(f"{csv_file.name}: 读取失败 - {e}")
        return False

def convert_csv_to_npz(
    csv_file: Path,
    motion_name: str,
    input_fps: int = 30,
    output_fps: int = 50,
    headless: bool = False,
    wandb_org: str = None
) -> bool:
    """
    转换单个CSV文件到NPZ并上传到WandB
    
    Returns:
        bool: 是否成功
    """
    print_info(f"处理: {csv_file.name} → {motion_name}")
    
    # 构建命令
    cmd = [
        sys.executable,  # Python解释器
        str(CSV_TO_NPZ_SCRIPT),
        "--input_file", str(csv_file),
        "--input_fps", str(input_fps),
        "--output_name", motion_name,
        "--output_fps", str(output_fps),
    ]
    
    if headless:
        cmd.append("--headless")
    
    # 设置环境变量(可选,用于WandB配置)
    env = os.environ.copy()
    if wandb_org:
        env["WANDB_ENTITY"] = wandb_org
    
    print_info(f"执行命令: {' '.join(cmd)}")
    
    try:
        # 执行转换脚本
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=600  # 10分钟超时
        )
        
        if result.returncode == 0:
            print_success(f"✓ {motion_name} 转换成功")
            # 打印关键输出
            if "Motion saved to wandb registry" in result.stdout:
                print_success(f"  已上传到WandB Registry")
            return True
        else:
            print_error(f"✗ {motion_name} 转换失败")
            print_error(f"  错误输出: {result.stderr[-500:]}")  # 只打印最后500字符
            return False
            
    except subprocess.TimeoutExpired:
        print_error(f"✗ {motion_name} 转换超时(>10分钟)")
        return False
    except Exception as e:
        print_error(f"✗ {motion_name} 转换异常: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="批量将GMR的CSV文件转换为NPZ并上传到WandB"
    )
    parser.add_argument(
        "--wandb-org",
        type=str,
        required=True,
        help="WandB组织名(如: ruixiao756-lgtm)"
    )
    parser.add_argument(
        "--input-fps",
        type=int,
        default=30,
        help="输入CSV的帧率(GMR默认30)"
    )
    parser.add_argument(
        "--output-fps",
        type=int,
        default=50,
        help="输出NPZ的帧率(IsaacLab默认50)"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="无头模式,不显示UI"
    )
    parser.add_argument(
        "--filter",
        type=str,
        default="*",
        help="过滤CSV文件名(支持通配符,如: 'walk*' 或 'stand*')"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅列出将要处理的文件,不实际执行"
    )
    
    args = parser.parse_args()
    
    # 检查目录
    if not PKL_CSV_DIR.exists():
        print_error(f"CSV目录不存在: {PKL_CSV_DIR}")
        sys.exit(1)
    
    if not CSV_TO_NPZ_SCRIPT.exists():
        print_error(f"转换脚本不存在: {CSV_TO_NPZ_SCRIPT}")
        print_error(f"请确保whole_body_tracking已正确安装")
        sys.exit(1)
    
    # 查找CSV文件
    print_info("=" * 60)
    print_info(f"搜索CSV文件: {PKL_CSV_DIR}")
    
    all_csv_files = find_csv_files()
    if not all_csv_files:
        print_warning("未找到任何CSV文件")
        sys.exit(0)
    
    # 应用过滤器
    if args.filter != "*":
        import fnmatch
        filtered_files = [f for f in all_csv_files if fnmatch.fnmatch(f.name, f"{args.filter}.csv")]
        print_info(f"过滤器 '{args.filter}': {len(all_csv_files)} → {len(filtered_files)} 文件")
        csv_files = filtered_files
    else:
        csv_files = all_csv_files
    
    if not csv_files:
        print_warning("过滤后没有文件需要处理")
        sys.exit(0)
    
    print_info(f"找到 {len(csv_files)} 个CSV文件:")
    for csv_file in csv_files:
        motion_name = get_motion_name(csv_file)
        print(f"  - {csv_file.name:30s} → {motion_name}")
    
    if args.dry_run:
        print_info("=" * 60)
        print_warning("Dry-run模式,不执行转换")
        sys.exit(0)
    
    # 确认执行
    print_info("=" * 60)
    print_warning("开始转换(按Ctrl+C取消)...")
    print_info(f"WandB组织: {args.wandb_org}")
    print_info(f"输入帧率: {args.input_fps} FPS")
    print_info(f"输出帧率: {args.output_fps} FPS")
    print_info(f"无头模式: {'是' if args.headless else '否'}")
    print_info("=" * 60)
    
    # 批量转换
    success_count = 0
    failed_files = []
    
    for i, csv_file in enumerate(csv_files, 1):
        print_info(f"\n[{i}/{len(csv_files)}] 处理: {csv_file.name}")
        
        # 检查格式
        if not check_csv_format(csv_file):
            failed_files.append((csv_file.name, "格式错误"))
            continue
        
        # 转换
        motion_name = get_motion_name(csv_file)
        success = convert_csv_to_npz(
            csv_file=csv_file,
            motion_name=motion_name,
            input_fps=args.input_fps,
            output_fps=args.output_fps,
            headless=args.headless,
            wandb_org=args.wandb_org
        )
        
        if success:
            success_count += 1
        else:
            failed_files.append((csv_file.name, "转换失败"))
    
    # 总结
    print_info("\n" + "=" * 60)
    print_info("批量转换完成!")
    print_success(f"成功: {success_count}/{len(csv_files)}")
    
    if failed_files:
        print_error(f"失败: {len(failed_files)}/{len(csv_files)}")
        print_error("失败文件列表:")
        for filename, reason in failed_files:
            print(f"  - {filename:30s} ({reason})")
    
    # 打印WandB Registry访问信息
    if success_count > 0:
        print_info("\n" + "=" * 60)
        print_success("上传到WandB Registry成功!")
        print_info(f"访问: https://wandb.ai/{args.wandb_org}/registry/model")
        print_info(f"Registry路径格式: {args.wandb_org}-org/wandb-registry-motions/<motion_name>:latest")
        print_info("\n验证上传(示例):")
        if csv_files:
            example_motion = get_motion_name(csv_files[0])
            print(f"  cd /home/abc/whole_body_tracking")
            print(f"  python scripts/replay_npz.py --registry_name={args.wandb_org}-org/wandb-registry-motions/{example_motion}")
    
    print_info("=" * 60)

if __name__ == "__main__":
    main()
