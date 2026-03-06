import wandb
import pandas as pd
import argparse
import numpy as np

def fetch_wandb_logs(run_path, sample_size=None, sample_frac=None, output_file='training_log.csv'):
    """
    从wandb获取训练日志，支持抽样
    
    Args:
        run_path: wandb run的路径，格式: "entity/project/runs/run_id"
        sample_size: 抽样数量（固定数量，等间隔采样）
        sample_frac: 抽样比例（0-1之间，例如0.1表示10%，等间隔采样）
        output_file: 输出文件名
    """
    api = wandb.Api()
    run = api.run(run_path)
    
    # 获取历史数据
    history_df = pd.DataFrame(run.history())
    print(f"原始数据行数: {len(history_df)}")
    
    # 等间隔抽样处理（保持时间序列顺序，平均分布）
    if sample_size is not None:
        sample_size = min(sample_size, len(history_df))
        indices = np.linspace(0, len(history_df) - 1, sample_size, dtype=int)
        history_df = history_df.iloc[indices]
        print(f"抽样后行数 (固定数量): {len(history_df)}")
    elif sample_frac is not None:
        sample_size = max(1, int(len(history_df) * sample_frac))
        indices = np.linspace(0, len(history_df) - 1, sample_size, dtype=int)
        history_df = history_df.iloc[indices]
        print(f"抽样后行数 (比例: {sample_frac*100:.1f}%): {len(history_df)}")
    
    # 导出为CSV
    history_df.to_csv(output_file, index=False)
    print(f"已保存到: {output_file}")
    print(f"\n数据列数: {len(history_df.columns)}")
    print(f"数据行数: {len(history_df)}")
    
    return history_df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='从wandb提取训练日志')
    parser.add_argument('--run-id', type=str, 
                       default='/1755247252-harbin-institute-of-technology/walk_amass/runs/i4fsxy8t',
                       help='wandb run路径')
    parser.add_argument('--sample-size', type=int, default=None,
                       help='抽样数量（固定值）')
    parser.add_argument('--sample-frac', type=float, default=None,
                       help='抽样比例（0-1，如0.1表示10%）')
    parser.add_argument('--output', type=str, default='training_log.csv',
                       help='输出文件名')
    
    args = parser.parse_args()
    
    history_df = fetch_wandb_logs(
        run_path=args.run_id,
        sample_size=args.sample_size,
        sample_frac=args.sample_frac,
        output_file=args.output
    )
    print("\n数据预览:")
    print(history_df.head())