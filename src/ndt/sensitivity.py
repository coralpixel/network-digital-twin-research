
from pathlib import Path

import pandas as pd

from ndt.attacks import (
    simulate_targeted_flood,
    simulate_traffic_surge,
)
from ndt.performance import analyze_performance
from ndt.topology import create_baseline_topology
from ndt.traffic import generate_traffic_matrix


def run_traffic_sensitivity(
    seeds=range(30, 60),
    surge_multipliers=(1.0, 1.5, 2.0, 3.0, 4.0),
    flood_multipliers=(1.0, 2.0, 3.0, 4.0, 5.0),
    surge_pair=("A", "F"),
    flood_target="F",
):
    """
    Evaluate synthetic traffic intensity across multiple random seeds.

    Each multiplier is applied to a fresh baseline traffic matrix.
    This is an analytical simulation, not real network traffic.
    """
    seeds = list(seeds)
    surge_multipliers = list(surge_multipliers)
    flood_multipliers = list(flood_multipliers)

    if not seeds:
        raise ValueError("At least one seed is required.")

    if len(set(seeds)) != len(seeds):
        raise ValueError("Seeds must be unique.")

    all_multipliers = surge_multipliers + flood_multipliers

    if any(multiplier < 1.0 for multiplier in all_multipliers):
        raise ValueError("All multipliers must be at least 1.0.")

    graph = create_baseline_topology()
    rows = []

    for seed in seeds:
        # Generate a fresh baseline traffic matrix for this seed.
        traffic = generate_traffic_matrix(graph, seed=seed)

        scenarios = [
            ("baseline", 1.0, traffic),
        ]

        # Traffic surge scenarios.
        for multiplier in surge_multipliers:
            modified = simulate_traffic_surge(
                traffic,
                source=surge_pair[0],
                destination=surge_pair[1],
                multiplier=multiplier,
            )

            scenarios.append(
                ("traffic_surge", multiplier, modified)
            )

        # Targeted flood-like scenarios.
        for multiplier in flood_multipliers:
            modified = simulate_targeted_flood(
                traffic,
                target=flood_target,
                multiplier=multiplier,
            )

            scenarios.append(
                ("targeted_flood", multiplier, modified)
            )

        # Evaluate every scenario using the existing performance model.
        for scenario, multiplier, matrix in scenarios:
            metrics = analyze_performance(graph, matrix)

            rows.append({
                "seed": seed,
                "scenario": scenario,
                "multiplier": multiplier,
                "maximum_utilization": metrics["maximum_utilization"],
                "average_utilization": metrics["average_utilization"],
                "maximum_link_latency_ms": max(
                    metrics["link_latency_ms"].values(),
                    default=0.0,
                ),
                "overloaded_links": len(
                    metrics["overloaded_links"]
                ),
                "unreachable_demands": metrics["unreachable_demands"],
                "total_traffic_mbps": sum(matrix.values()),
            })

    return pd.DataFrame(rows)



def summarize_traffic_sensitivity(
    results: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize sensitivity results while handling infinite latency."""
    required = {
        "seed",
        "scenario",
        "multiplier",
        "maximum_utilization",
        "average_utilization",
        "maximum_link_latency_ms",
        "overloaded_links",
        "unreachable_demands",
        "total_traffic_mbps",
    }

    missing = sorted(required - set(results.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if results.empty:
        raise ValueError("Results must not be empty.")

    if results.duplicated(["seed", "scenario", "multiplier"]).any():
        raise ValueError(
            "Each seed, scenario, and multiplier combination must be unique."
        )

    metric_columns = [
        "maximum_utilization",
        "average_utilization",
        "maximum_link_latency_ms",
        "overloaded_links",
        "unreachable_demands",
        "total_traffic_mbps",
    ]

    rows = []

    for (scenario, multiplier), group in results.groupby(
        ["scenario", "multiplier"],
        sort=True,
    ):
        for metric in metric_columns:
            values = pd.to_numeric(
                group[metric],
                errors="raise",
            ).dropna().astype(float)

            # Keep the original infinite values in the raw CSV.
            infinite_count = int(values.eq(float("inf")).sum())
            finite_values = values[values.map(lambda x: __import__("math").isfinite(x))]

            n_total = len(values)
            n_finite = len(finite_values)
            mean = finite_values.mean() if n_finite else float("nan")
            std = (
                finite_values.std(ddof=1)
                if n_finite >= 2
                else float("nan")
            )

            if n_finite >= 2:
                from scipy.stats import t

                critical_value = t.ppf(0.975, df=n_finite - 1)
                margin = critical_value * std / (n_finite ** 0.5)
                ci_lower = mean - margin
                ci_upper = mean + margin
            else:
                ci_lower = float("nan")
                ci_upper = float("nan")

            rows.append({
                "scenario": scenario,
                "multiplier": multiplier,
                "metric": metric,
                "n_total": n_total,
                "n_finite": n_finite,
                "n_infinite": infinite_count,
                "mean_finite": mean,
                "std_finite": std,
                "ci95_lower_finite": ci_lower,
                "ci95_upper_finite": ci_upper,
            })

    return pd.DataFrame(rows)



def export_traffic_sensitivity(
    results: pd.DataFrame,
    output_dir="results/tables",
) -> pd.DataFrame:
    """Export raw sensitivity results and statistical summaries."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    summary = summarize_traffic_sensitivity(results)

    results.to_csv(
        output / "traffic_sensitivity_runs.csv",
        index=False,
    )

    summary.to_csv(
        output / "traffic_sensitivity_summary.csv",
        index=False,
    )

    return summary
