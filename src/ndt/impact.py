
from pathlib import Path

import pandas as pd


RELATIVE_CHANGE_METRICS = [
    "maximum_utilization",
    "average_utilization",
    "maximum_link_latency_ms",
    "total_traffic_mbps",
]


def calculate_impact_table(results: pd.DataFrame) -> pd.DataFrame:
    """Calculate scenario changes relative to the baseline."""
    if "scenario" not in results.columns:
        raise ValueError("Results must contain a 'scenario' column.")

    baseline_rows = results[results["scenario"] == "baseline"]

    if len(baseline_rows) != 1:
        raise ValueError(
            "Results must contain exactly one baseline scenario."
        )

    missing = [
        column
        for column in RELATIVE_CHANGE_METRICS
        if column not in results.columns
    ]
    if missing:
        raise ValueError(f"Missing required metrics: {missing}")

    baseline = baseline_rows.iloc[0]
    impact = results.copy()

    for metric in RELATIVE_CHANGE_METRICS:
        values = pd.to_numeric(impact[metric], errors="raise")
        baseline_value = float(baseline[metric])

        if baseline_value == 0:
            impact[f"{metric}_change_percent"] = float("nan")
        else:
            impact[f"{metric}_change_percent"] = (
                (values - baseline_value)
                / abs(baseline_value)
                * 100.0
            )

    impact["maximum_utilization_change_percentage_points"] = (
        pd.to_numeric(impact["maximum_utilization"], errors="raise")
        - float(baseline["maximum_utilization"])
    ) * 100.0

    return impact


def save_impact_table(
    results: pd.DataFrame,
    output_path: str = "results/tables/impact_analysis.csv",
) -> pd.DataFrame:
    """Save baseline-relative impact analysis as a CSV file."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    impact = calculate_impact_table(results)
    impact.to_csv(output, index=False)

    return impact
