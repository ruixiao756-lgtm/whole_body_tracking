from __future__ import annotations

import argparse
import csv
import math
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path


ANSI_ESCAPE_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
ITERATION_RE = re.compile(r"Learning iteration\s+(\d+)/(\d+)")
KV_RE = re.compile(r"^\s*([^:]+):\s*(-?\d+(?:\.\d+)?)\s*$")
KV_WITH_UNIT_RE = re.compile(r"^\s*([^:]+):\s*(-?\d+(?:\.\d+)?)([A-Za-z%/]+)\s*$")
COMPUTATION_RE = re.compile(r"Computation:\s*(\d+(?:\.\d+)?)\s+steps/s")

POSITIVE_METRICS = [
    "Mean reward",
    "Mean episode length",
    "Episode_Reward/motion_global_anchor_pos",
    "Episode_Reward/motion_global_anchor_ori",
    "Episode_Reward/motion_body_pos",
    "Episode_Reward/motion_body_ori",
    "Episode_Reward/motion_body_lin_vel",
    "Episode_Reward/motion_body_ang_vel",
    "Episode_Termination/time_out",
]

NEGATIVE_METRICS = [
    "Metrics/motion/error_anchor_pos",
    "Metrics/motion/error_anchor_rot",
    "Metrics/motion/error_anchor_lin_vel",
    "Metrics/motion/error_anchor_ang_vel",
    "Metrics/motion/error_body_pos",
    "Metrics/motion/error_body_rot",
    "Metrics/motion/error_body_lin_vel",
    "Metrics/motion/error_body_ang_vel",
    "Metrics/motion/error_joint_pos",
    "Metrics/motion/error_joint_vel",
    "Episode_Termination/anchor_pos",
    "Episode_Termination/anchor_ori",
    "Episode_Termination/ee_body_pos",
    "Mean value_function loss",
]

DEFAULT_HIGHLIGHT_RULES = [
    ("Mean reward", "max"),
    ("Mean episode length", "max"),
    ("Episode_Reward/motion_global_anchor_pos", "max"),
    ("Episode_Reward/motion_global_anchor_ori", "max"),
    ("Metrics/motion/error_anchor_rot", "min"),
    ("Metrics/motion/error_anchor_lin_vel", "min"),
    ("Metrics/motion/error_anchor_ang_vel", "min"),
]

SUMMARY_COLUMNS = [
    "iteration",
    "total_timesteps",
    "composite_score",
    "Mean reward",
    "Mean episode length",
    "Episode_Reward/motion_global_anchor_pos",
    "Episode_Reward/motion_global_anchor_ori",
    "Episode_Reward/motion_body_pos",
    "Episode_Reward/motion_body_ori",
    "Metrics/motion/error_anchor_pos",
    "Metrics/motion/error_anchor_rot",
    "Metrics/motion/error_anchor_lin_vel",
    "Metrics/motion/error_anchor_ang_vel",
    "Metrics/motion/error_body_pos",
    "Metrics/motion/error_body_rot",
    "Metrics/motion/error_joint_pos",
    "Metrics/motion/error_joint_vel",
    "Computation/steps_per_s",
    "Iteration time",
]


@dataclass
class IterationBlock:
    iteration: int
    total_iterations: int
    raw_lines: list[str] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)
    text_fields: dict[str, str] = field(default_factory=dict)
    composite_score: float | None = None

    def get(self, key: str) -> float | None:
        return self.metrics.get(key)


def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE_RE.sub("", text)


def parse_log(log_path: Path) -> list[IterationBlock]:
    lines = log_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    blocks: list[IterationBlock] = []
    current: IterationBlock | None = None

    for raw_line in lines:
        line = strip_ansi(raw_line.rstrip("\n"))
        match = ITERATION_RE.search(line)
        if match:
            if current is not None:
                blocks.append(current)
            current = IterationBlock(
                iteration=int(match.group(1)),
                total_iterations=int(match.group(2)),
                raw_lines=[line],
            )
            continue

        if current is None:
            continue

        current.raw_lines.append(line)
        parse_metric_line(current, line)

    if current is not None:
        blocks.append(current)

    return blocks


def parse_metric_line(block: IterationBlock, line: str) -> None:
    computation_match = COMPUTATION_RE.search(line)
    if computation_match:
        block.metrics["Computation/steps_per_s"] = float(computation_match.group(1))
        block.text_fields["Computation"] = line.strip()
        return

    numeric_match = KV_RE.match(line)
    if numeric_match:
        key = numeric_match.group(1).strip()
        block.metrics[key] = float(numeric_match.group(2))
        return

    unit_match = KV_WITH_UNIT_RE.match(line)
    if unit_match:
        key = unit_match.group(1).strip()
        block.metrics[key] = float(unit_match.group(2))
        block.text_fields[key] = f"{unit_match.group(2)}{unit_match.group(3)}"
        return

    if ":" in line:
        key, value = line.split(":", 1)
        block.text_fields[key.strip()] = value.strip()


def compute_composite_scores(blocks: list[IterationBlock]) -> None:
    metric_ranges: dict[str, tuple[float, float]] = {}

    for metric in POSITIVE_METRICS + NEGATIVE_METRICS:
        values = [block.metrics[metric] for block in blocks if metric in block.metrics]
        if values:
            metric_ranges[metric] = (min(values), max(values))

    for block in blocks:
        score_parts: list[float] = []

        for metric in POSITIVE_METRICS:
            value = block.metrics.get(metric)
            bounds = metric_ranges.get(metric)
            if value is None or bounds is None:
                continue
            score = normalize(value, bounds[0], bounds[1])
            if score is not None:
                score_parts.append(score)

        for metric in NEGATIVE_METRICS:
            value = block.metrics.get(metric)
            bounds = metric_ranges.get(metric)
            if value is None or bounds is None:
                continue
            score = normalize(value, bounds[0], bounds[1])
            if score is not None:
                score_parts.append(1.0 - score)

        if score_parts:
            block.composite_score = sum(score_parts) / len(score_parts)


def estimate_min_metric_count(blocks: list[IterationBlock]) -> int:
    metric_counts = sorted(len(block.metrics) for block in blocks)
    if not metric_counts:
        return 0
    median_count = metric_counts[len(metric_counts) // 2]
    return max(8, int(median_count * 0.6))


def normalize(value: float, minimum: float, maximum: float) -> float | None:
    if math.isclose(maximum, minimum):
        return None
    return (value - minimum) / (maximum - minimum)


def add_reason(reasons: dict[int, list[str]], block: IterationBlock, reason: str) -> None:
    if reason not in reasons[block.iteration]:
        reasons[block.iteration].append(reason)


def select_highlights(
    blocks: list[IterationBlock],
    target_count: int,
    evenly_spaced_count: int,
    change_count: int,
) -> tuple[list[IterationBlock], dict[int, list[str]]]:
    reasons: dict[int, list[str]] = defaultdict(list)
    by_iteration = {block.iteration: block for block in blocks}
    min_metric_count = estimate_min_metric_count(blocks)
    eligible_blocks = [block for block in blocks if len(block.metrics) >= min_metric_count]
    if len(eligible_blocks) < 3:
        eligible_blocks = blocks

    first_block = blocks[0]
    last_block = blocks[-1]
    add_reason(reasons, first_block, "start")
    add_reason(reasons, last_block, "end")

    required_iterations: list[int] = []
    push_unique(required_iterations, first_block.iteration)
    push_unique(required_iterations, last_block.iteration)

    scored_blocks = [block for block in eligible_blocks if block.composite_score is not None]
    if scored_blocks:
        best_composite = max(scored_blocks, key=lambda block: block.composite_score or float("-inf"))
        add_reason(reasons, best_composite, "best composite score")

    for metric, direction in DEFAULT_HIGHLIGHT_RULES:
        candidates = [block for block in eligible_blocks if metric in block.metrics]
        if not candidates:
            continue
        if direction == "max":
            selected = max(candidates, key=lambda block: block.metrics[metric])
            add_reason(reasons, selected, f"best {metric}")
        else:
            selected = min(candidates, key=lambda block: block.metrics[metric])
            add_reason(reasons, selected, f"best {metric} (lowest)")

    if change_count > 0 and len(scored_blocks) >= 2:
        deltas: list[tuple[float, IterationBlock, str]] = []
        previous = scored_blocks[0]
        for current in scored_blocks[1:]:
            if previous.composite_score is None or current.composite_score is None:
                previous = current
                continue
            delta = current.composite_score - previous.composite_score
            label = f"composite jump {delta:+.3f} vs iter {previous.iteration}"
            deltas.append((abs(delta), current, label))
            previous = current

        for _, block, label in sorted(deltas, key=lambda item: item[0], reverse=True)[:change_count]:
            add_reason(reasons, block, label)

    evenly_spaced_blocks = choose_evenly_spaced_blocks(eligible_blocks, evenly_spaced_count)
    for index, block in enumerate(evenly_spaced_blocks):
        progress = 0.0 if len(evenly_spaced_blocks) == 1 else index / (len(evenly_spaced_blocks) - 1)
        add_reason(reasons, block, f"timeline {progress:.0%}")
        push_unique(required_iterations, block.iteration)

    ordered_iterations = prioritize_iterations(blocks, reasons)
    selected_iterations = list(required_iterations)
    for iteration in ordered_iterations:
        if len(selected_iterations) >= target_count:
            break
        push_unique(selected_iterations, iteration)

    selected_blocks = [by_iteration[iteration] for iteration in sorted(selected_iterations)]
    selected_reasons = {block.iteration: reasons[block.iteration] for block in selected_blocks}
    return selected_blocks, selected_reasons


def choose_evenly_spaced_indices(total: int, count: int) -> list[int]:
    if total <= 0 or count <= 0:
        return []
    if count >= total:
        return list(range(total))
    if count == 1:
        return [0]

    indices = set()
    for rank in range(count):
        index = round(rank * (total - 1) / (count - 1))
        indices.add(index)
    return sorted(indices)


def choose_evenly_spaced_blocks(blocks: list[IterationBlock], count: int) -> list[IterationBlock]:
    indices = choose_evenly_spaced_indices(len(blocks), count)
    return [blocks[index] for index in indices]


def push_unique(values: list[int], value: int) -> None:
    if value not in values:
        values.append(value)


def prioritize_iterations(blocks: list[IterationBlock], reasons: dict[int, list[str]]) -> list[int]:
    order_map = {block.iteration: idx for idx, block in enumerate(blocks)}

    def priority(iteration: int) -> tuple[int, int, int]:
        reason_list = reasons[iteration]
        hard_priority = 0
        if "start" in reason_list or "end" in reason_list:
            hard_priority = 3
        elif any(reason.startswith("best ") for reason in reason_list) or "best composite score" in reason_list:
            hard_priority = 2
        elif any(reason.startswith("composite jump") for reason in reason_list):
            hard_priority = 1
        return (-hard_priority, -len(reason_list), order_map[iteration])

    return sorted(reasons.keys(), key=priority)


def write_outputs(
    log_path: Path,
    selected_blocks: list[IterationBlock],
    reasons: dict[int, list[str]],
    output_prefix: Path,
) -> tuple[Path, Path, Path]:
    csv_path = output_prefix.with_suffix(".csv")
    markdown_path = output_prefix.with_suffix(".md")
    log_excerpt_path = output_prefix.with_suffix(".log")

    write_csv(csv_path, selected_blocks, reasons)
    write_markdown(markdown_path, log_path, selected_blocks, reasons)
    write_log_excerpt(log_excerpt_path, selected_blocks, reasons)
    return csv_path, markdown_path, log_excerpt_path


def write_csv(csv_path: Path, blocks: list[IterationBlock], reasons: dict[int, list[str]]) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=SUMMARY_COLUMNS + ["reasons"])
        writer.writeheader()
        for block in blocks:
            row = build_summary_row(block)
            row["reasons"] = "; ".join(reasons[block.iteration])
            writer.writerow(row)


def write_markdown(markdown_path: Path, log_path: Path, blocks: list[IterationBlock], reasons: dict[int, list[str]]) -> None:
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    header = [
        f"# Training Highlights for {log_path.name}",
        "",
        f"Selected {len(blocks)} representative iterations from the full log.",
        "",
        "| Iteration | Timesteps | Composite | Mean reward | Episode length | Anchor pos reward | Anchor ori reward | Anchor lin vel error | Anchor ang vel error | Reasons |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]

    rows = []
    for block in blocks:
        row = build_summary_row(block)
        rows.append(
            "| {iteration} | {timesteps} | {score} | {reward} | {length} | {anchor_pos_reward} | {anchor_ori_reward} | {anchor_lin_vel_error} | {anchor_ang_vel_error} | {reasons} |".format(
                iteration=row["iteration"],
                timesteps=format_cell(row["total_timesteps"]),
                score=format_cell(row["composite_score"]),
                reward=format_cell(row["Mean reward"]),
                length=format_cell(row["Mean episode length"]),
                anchor_pos_reward=format_cell(row["Episode_Reward/motion_global_anchor_pos"]),
                anchor_ori_reward=format_cell(row["Episode_Reward/motion_global_anchor_ori"]),
                anchor_lin_vel_error=format_cell(row["Metrics/motion/error_anchor_lin_vel"]),
                anchor_ang_vel_error=format_cell(row["Metrics/motion/error_anchor_ang_vel"]),
                reasons="; ".join(reasons[block.iteration]),
            )
        )

    markdown_path.write_text("\n".join(header + rows) + "\n", encoding="utf-8")


def write_log_excerpt(log_excerpt_path: Path, blocks: list[IterationBlock], reasons: dict[int, list[str]]) -> None:
    log_excerpt_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for index, block in enumerate(blocks):
        if index > 0:
            lines.extend(["", "=" * 80, ""])
        lines.append(f"# Iteration {block.iteration} | reasons: {'; '.join(reasons[block.iteration])}")
        lines.extend(block.raw_lines)
    log_excerpt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_summary_row(block: IterationBlock) -> dict[str, str | float | int | None]:
    row: dict[str, str | float | int | None] = {
        "iteration": block.iteration,
        "total_timesteps": as_int_if_possible(block.metrics.get("Total timesteps")),
        "composite_score": round(block.composite_score, 4) if block.composite_score is not None else None,
    }

    for column in SUMMARY_COLUMNS:
        if column in row:
            continue
        value = block.metrics.get(column)
        if value is None:
            row[column] = None
        else:
            row[column] = round(value, 4)

    return row


def as_int_if_possible(value: float | None) -> int | None:
    if value is None:
        return None
    if float(value).is_integer():
        return int(value)
    return int(round(value))


def format_cell(value: str | float | int | None) -> str:
    if value is None:
        return "-"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def default_output_prefix(log_path: Path) -> Path:
    return log_path.with_name(f"{log_path.stem}_highlights")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract representative iterations from long training logs.",
    )
    parser.add_argument("log_path", type=Path, help="Path to the training log file.")
    parser.add_argument(
        "--target-count",
        type=int,
        default=12,
        help="Maximum number of highlighted iterations to keep.",
    )
    parser.add_argument(
        "--evenly-spaced-count",
        type=int,
        default=5,
        help="How many timeline checkpoints to keep.",
    )
    parser.add_argument(
        "--change-count",
        type=int,
        default=3,
        help="How many large composite-score jumps to keep.",
    )
    parser.add_argument(
        "--output-prefix",
        type=Path,
        default=None,
        help="Output prefix for .csv, .md and .log files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    log_path: Path = args.log_path
    if not log_path.exists():
        raise FileNotFoundError(f"Log file not found: {log_path}")

    blocks = parse_log(log_path)
    if not blocks:
        raise ValueError("No training iterations were found in the log.")

    compute_composite_scores(blocks)
    selected_blocks, reasons = select_highlights(
        blocks=blocks,
        target_count=max(args.target_count, 2),
        evenly_spaced_count=max(args.evenly_spaced_count, 0),
        change_count=max(args.change_count, 0),
    )

    output_prefix = args.output_prefix or default_output_prefix(log_path)
    csv_path, markdown_path, log_excerpt_path = write_outputs(
        log_path=log_path,
        selected_blocks=selected_blocks,
        reasons=reasons,
        output_prefix=output_prefix,
    )

    print(f"Parsed iterations: {len(blocks)}")
    print(f"Selected highlights: {len(selected_blocks)}")
    print(f"CSV summary: {csv_path}")
    print(f"Markdown summary: {markdown_path}")
    print(f"Log excerpt: {log_excerpt_path}")


if __name__ == "__main__":
    main()