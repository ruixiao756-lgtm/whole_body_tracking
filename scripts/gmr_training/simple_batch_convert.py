#!/usr/bin/env python3
"""
简化版批量CSV转NPZ脚本 - 直接上传到WandB项目而不需要Registry

用法:
    python simple_batch_convert.py
"""

import subprocess
import sys
from pathlib import Path

# 配置
CSV_DIR = Path("/home/abc/GMR/pkl_files/csv")
WANDB_PROJECT = "motion-retargeting"  # 直接使用项目
MOTIONS = [
    ("crouch_amass.csv", "crouch_amass"),
    ("stand_amass.csv", "stand_amass"),  
    ("sway_amass.csv", "sway_amass"),
    ("swing_amass.csv", "swing_amass"),
    ("turn_amass.csv", "turn_amass"),
    ("walk_amass.csv", "walk_amass"),
]

def convert_one(csv_file: str, output_name: str) -> bool:
    """转换一个CSV文件"""
    csv_path = CSV_DIR / csv_file
    
    cmd = [
        "python", "scripts/csv_to_npz.py",
        "--input_file", str(csv_path),
        "--input_fps", "30",
        "--output_name", output_name,
        "--output_fps", "50",
        "--headless",
    ]
    
    print(f"\n{'='*70}")
    print(f"转换: {csv_file} → {output_name}")
    print(f"{'='*70}")
    
    try:
        result = subprocess.run(
            cmd,
            check=True,
            timeout=600,  # 10分钟超时
            capture_output=False,  # 直接显示输出
        )
        print(f"✅ 成功: {output_name}")
        return True
    except subprocess.TimeoutExpired:
        print(f"❌ 超时: {output_name}")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ 失败: {output_name}")
        return False
    except KeyboardInterrupt:
        print(f"\n⚠️  用户中断")
        sys.exit(1)

def main():
    print(f"""
╔════════════════════════════════════════════════════════════════╗
║              批量CSV→NPZ转换并上传到WandB                        ║
╚════════════════════════════════════════════════════════════════╝

📁 CSV目录: {CSV_DIR}
📦 WandB项目: {WANDB_PROJECT}
📝 待转换: {len(MOTIONS)} 个动作

""")
    
    results = {}
    for i, (csv_file, output_name) in enumerate(MOTIONS, 1):
        print(f"\n[{i}/{len(MOTIONS)}] {output_name}")
        success = convert_one(csv_file, output_name)
        results[output_name] = success
    
    # 总结
    print(f"\n\n{'='*70}")
    print("转换完成总结")
    print(f"{'='*70}")
    
    success_count = sum(results.values())
    for name, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    print(f"\n成功: {success_count}/{len(MOTIONS)}")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
