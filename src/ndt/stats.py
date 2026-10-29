
from pathlib import Path
import math

import pandas as pd



DEFAULT_METRICS = [
    "maximum_utilization",
    "average_utilization",
    "maximum_link_latency_ms",
    "overloaded_links",
    "unreachable_demands",
    "total_traffic_mbps",
]


# Two-sided 95% Student-t critical values for degrees of freedom 1–30.
_T_CRITICAL_95 = [
    None,
    12.706, 4.303, 3.182, 2.776, 2.571, 2.447, 2.365, 2.306,
    2.262, 2.228, 2.201, 2.179, 2.160, 2.145, 2.131, 2.120,
    2.110, 2.101, 2.093, 2.086, 2.080, 2.074, 2.069, 2.064,
    2.060, 2.056, 2.052, 2.048, 2.045, 2.042,
]


def _critical_value_95(sample_size: int) -> float:
    """Return a two-sided 95% t critical value."""
    degrees_of_freedom = sample_size - 1

    if degrees_of_freedom < 1:
        return float("nan")
    if degrees_of_freedom <= 30:
        return _T_CRITICAL_95[degrees_of_freedom]

    # Large-sample normal approximation.
    return 1.96


def run_repeated_experiments(
    seeds=range(30, 60),
) -> pd.DataFrame:
    """Run the full experiment once per seed and combine all rows."""
    from ndt.experiments import run_full_experiment

    seeds = list(seeds)
    if not seeds:
        raise ValueError("At least one seed is required.")

    if len(set(seeds)) != len(seeds):
        raise ValueError("Seeds must be unique.")

    frames = []
    for seed in seeds:
        result = run_full_experiment(seed=seed).copy()
        result["seed"] = seed
        frames.append(result)

    return pd.concat(frames, ignore_index=True)




def summarize_repeated_experiments(
    results: pd.DataFrame,
    metrics=DEFAULT_METRICS,
) -> pd.DataFrame:
    """Summarize each scenario configuration across independent seeds."""
    required = {"scenario", "seed", *metrics}
    missing = sorted(required - set(results.columns))

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if results.empty:
        raise ValueError("Results must not be empty.")

    # Distinguish individual link-failure configurations.
    group_columns = ["scenario"]

    if "failed_link" in results.columns:
        group_columns.append("failed_link")

    # Reject duplicate results for the same configuration and seed.
    duplicate_columns = group_columns + ["seed"]

    if results.duplicated(duplicate_columns).any():
        raise ValueError(
            "Each scenario configuration must occur at most once per seed."
        )

    rows = []

    # Group by scenario and, where available, failed link.
    for group_key, group in results.groupby(
        group_columns,
        sort=False,
        dropna=False,
    ):
        if not isinstance(group_key, tuple):
            group_key = (group_key,)

        scenario_info = dict(zip(group_columns, group_key))

        for metric in metrics:
            values = pd.to_numeric(
                group[metric],
                errors="raise",
            ).dropna().astype(float)

            n = len(values)
            mean = values.mean() if n else float("nan")
            std = values.std(ddof=1) if n >= 2 else float("nan")

            if n >= 2:
                margin = (
                    _critical_value_95(n)
                    * std
                    / math.sqrt(n)
                )
                ci_lower = mean - margin
                ci_upper = mean + margin
            else:
                ci_lower = float("nan")
                ci_upper = float("nan")

            rows.append({
                **scenario_info,
                "metric": metric,
                "n": n,
                "mean": mean,
                "std": std,
                "ci95_lower": ci_lower,
                "ci95_upper": ci_upper,
            })

    return pd.DataFrame(rows)





def export_statistical_results(
    raw_results: pd.DataFrame,
    output_dir="results/tables",
) -> pd.DataFrame:
    """Export raw repeated runs and their statistical summary."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    summary = summarize_repeated_experiments(raw_results)

    raw_results.to_csv(
        output / "repeated_experiment_runs.csv", index=False
    )
    summary.to_csv(
        output / "statistical_summary.csv", index=False
    )

    return summary
