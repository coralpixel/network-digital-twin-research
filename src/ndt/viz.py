

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def load_experiment_results(
    csv_path="results/tables/full_experiment_results.csv",
):
    """Load experiment results from CSV."""
    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Results file not found: {path}. "
            "Run the full experiment first."
        )

    return pd.read_csv(path)


def _scenario_labels(results):
    """Create concise labels for plots."""
    labels = []

    for _, row in results.iterrows():
        scenario = row["scenario"]
        failed_link = row.get("failed_link")

        if scenario == "baseline":
            label = "Baseline"
        elif scenario == "link_failure":
            label = f"Fail {failed_link}"
        elif scenario == "traffic_surge_A_F_x3":
            label = "Traffic surge"
        elif scenario == "targeted_flood_F_x5":
            label = "Targeted flood"
        else:
            label = str(scenario)

        labels.append(label)

    return labels


def plot_maximum_utilization(
    results,
    output_path="results/figures/maximum_utilization.png",
):
    """Plot maximum utilization with values and capacity threshold."""
    from pathlib import Path
    import matplotlib.pyplot as plt

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    labels = _scenario_labels(results)
    values = results["maximum_utilization"] * 100

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(range(len(labels)), values)

    ax.axhline(
        100,
        linestyle="--",
        label="Link capacity (100%)",
    )

    ax.bar_label(
        bars,
        labels=[f"{value:.1f}%" for value in values],
        padding=3,
        fontsize=8,
    )

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_ylabel("Maximum link utilization (%)")
    ax.set_xlabel("Scenario")
    ax.set_title("Maximum Link Utilization Across Scenarios")
    ax.legend()
    ax.set_ylim(0, max(110, float(values.max()) * 1.15))
    fig.tight_layout()
    fig.savefig(str(output.resolve()), dpi=300, bbox_inches="tight")
    plt.close(fig)

    return output


def plot_maximum_latency(
    results,
    output_path="results/figures/maximum_latency.png",
):
    """Plot maximum modeled link latency with values above bars."""
    from pathlib import Path
    import matplotlib.pyplot as plt

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    labels = _scenario_labels(results)
    values = results["maximum_link_latency_ms"]

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(range(len(labels)), values)

    ax.bar_label(
        bars,
        labels=[f"{value:.1f}" for value in values],
        padding=3,
        fontsize=8,
    )

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_ylabel("Maximum modeled link latency (ms)")
    ax.set_xlabel("Scenario")
    ax.set_title("Modeled Link Latency Across Scenarios")
    ax.set_ylim(0, float(values.max()) * 1.15)
    fig.tight_layout()
    fig.savefig(str(output.resolve()), dpi=300, bbox_inches="tight")
    plt.close(fig)

    return output



def create_impact_table(results):
    """Calculate percentage changes relative to baseline."""
    baseline_rows = results[results["scenario"] == "baseline"]

    if baseline_rows.empty:
        raise ValueError("Results must contain a baseline scenario.")

    baseline = baseline_rows.iloc[0]
    output = results.copy()

    for column in [
        "maximum_utilization",
        "average_utilization",
        "maximum_link_latency_ms",
        "total_traffic_mbps",
    ]:
        baseline_value = baseline[column]

        if pd.isna(baseline_value) or baseline_value == 0:
            output[f"{column}_change_percent"] = float("nan")
        else:
            output[f"{column}_change_percent"] = (
                (output[column] - baseline_value)
                / abs(baseline_value)
            ) * 100

    return output


def export_impact_table(
    results,
    output_path="results/tables/impact_comparison.csv",
):
    """Save percentage-change analysis to CSV."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    impact = create_impact_table(results)
    impact.to_csv(output, index=False)

    return impact


def plot_sensitivity_utilization(
    csv_path="results/tables/traffic_sensitivity_runs.csv",
    output_path="results/figures/sensitivity_utilization.png",
):
    """Plot mean maximum link utilization by traffic multiplier."""
    from pathlib import Path

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    results = pd.read_csv(csv_path)
    results = results[
        results["scenario"].isin(["traffic_surge", "targeted_flood"])
    ]

    summary = (
        results.groupby(["scenario", "multiplier"])["maximum_utilization"]
        .mean()
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(9, 5))

    for scenario, group in summary.groupby("scenario"):
        group = group.sort_values("multiplier")
        ax.plot(
            group["multiplier"],
            group["maximum_utilization"] * 100,
            marker="o",
            label=scenario.replace("_", " ").title(),
        )

    ax.axhline(100, linestyle="--", label="Link capacity (100%)")
    ax.set_xlabel("Traffic multiplier")
    ax.set_ylabel("Mean maximum link utilization (%)")
    ax.set_title("Traffic Intensity vs. Maximum Link Utilization")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return output


def plot_sensitivity_latency(
    csv_path="results/tables/traffic_sensitivity_runs.csv",
    output_path="results/figures/sensitivity_latency.png",
):
    """Plot finite mean latency and mark scenarios with infinite latency."""
    from pathlib import Path

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    results = pd.read_csv(csv_path)
    results = results[
        results["scenario"].isin(["traffic_surge", "targeted_flood"])
    ]

    grouped = results.groupby(["scenario", "multiplier"])
    summary = grouped["maximum_link_latency_ms"].agg(
        total="count",
        finite=lambda values: values[
            values.map(lambda value: pd.notna(value) and value != float("inf"))
        ].count(),
        infinite=lambda values: (values == float("inf")).sum(),
        mean_finite=lambda values: values[
            values.map(lambda value: pd.notna(value) and value != float("inf"))
        ].mean(),
    ).reset_index()

    fig, ax = plt.subplots(figsize=(9, 5))

    for scenario, group in summary.groupby("scenario"):
        group = group.sort_values("multiplier")
        finite = group["mean_finite"].notna()

        ax.plot(
            group.loc[finite, "multiplier"],
            group.loc[finite, "mean_finite"],
            marker="o",
            label=scenario.replace("_", " ").title(),
        )

        # Mark multipliers where every observation has infinite latency.
        all_infinite = group["infinite"] == group["total"]
        if all_infinite.any():
            ax.scatter(
                group.loc[all_infinite, "multiplier"],
                [0] * int(all_infinite.sum()),
                marker="x",
                s=80,
                label=f"{scenario.replace('_', ' ').title()}: all runs infinite",
            )

    ax.set_xlabel("Traffic multiplier")
    ax.set_ylabel("Mean finite maximum link latency (ms)")
    ax.set_title("Traffic Intensity vs. Modeled Link Latency")
    ax.text(
        0.02,
        0.97,
        "× at zero indicates all runs had infinite latency; "
        "it does not mean zero latency.",
        transform=ax.transAxes,
        va="top",
        fontsize=8,
    )
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return output


def plot_sensitivity_overload_frequency(
    csv_path="results/tables/traffic_sensitivity_runs.csv",
    output_path="results/figures/sensitivity_overload_frequency.png",
):
    """Plot the percentage of seeds with at least one overloaded link."""
    from pathlib import Path

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    results = pd.read_csv(csv_path)
    results = results[
        results["scenario"].isin(["traffic_surge", "targeted_flood"])
    ]

    results["has_overload"] = results["overloaded_links"] > 0

    summary = (
        results.groupby(["scenario", "multiplier"])["has_overload"]
        .mean()
        .mul(100)
        .reset_index(name="overload_frequency_percent")
    )

    fig, ax = plt.subplots(figsize=(9, 5))

    for scenario, group in summary.groupby("scenario"):
        group = group.sort_values("multiplier")
        ax.plot(
            group["multiplier"],
            group["overload_frequency_percent"],
            marker="o",
            label=scenario.replace("_", " ").title(),
        )

    ax.set_xlabel("Traffic multiplier")
    ax.set_ylabel("Runs with at least one overloaded link (%)")
    ax.set_ylim(-5, 105)
    ax.set_title("Traffic Intensity vs. Overload Frequency")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return output
