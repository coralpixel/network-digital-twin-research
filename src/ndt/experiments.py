
from pathlib import Path

import pandas as pd

from ndt.topology import create_baseline_topology
from ndt.traffic import generate_traffic_matrix
from ndt.metrics import analyze_structure
from ndt.performance import analyze_performance
from ndt.attacks import (
    simulate_traffic_surge,
    simulate_targeted_flood,
)


def _evaluate_scenario(name, graph, traffic, failed_link=None):
    """Collect structural and performance metrics for one scenario."""
    structure = analyze_structure(graph)
    performance = analyze_performance(graph, traffic)

    finite_latencies = [
        value
        for value in performance["link_latency_ms"].values()
        if value != float("inf")
    ]

    return {
        "scenario": name,
        "failed_link": failed_link,
        "node_count": graph.number_of_nodes(),
        "link_count": graph.number_of_edges(),
        "components": structure["component_count"],
        "unreachable_pairs": structure["unreachable_pairs"],
        "maximum_utilization": performance["maximum_utilization"],
        "average_utilization": performance["average_utilization"],
        "maximum_link_latency_ms": (
            max(finite_latencies) if finite_latencies else float("inf")
        ),
        "overloaded_links": len(performance["overloaded_links"]),
        "unreachable_demands": performance["unreachable_demands"],
        "total_traffic_mbps": sum(traffic.values()),
    }


def run_full_experiment(seed=42):
    """
    Compare baseline, independent link failures, and synthetic attacks.
    All scenarios use the same initial traffic matrix.
    """
    baseline = create_baseline_topology()
    traffic = generate_traffic_matrix(baseline, seed=seed)
    results = []

    # 1. Baseline
    results.append(
        _evaluate_scenario("baseline", baseline, traffic)
    )

    # 2. Independent link failures
    for source, destination in sorted(
        (min(u, v), max(u, v)) for u, v in baseline.edges()
    ):
        simulated = baseline.copy()
        simulated.remove_edge(source, destination)

        results.append(
            _evaluate_scenario(
                "link_failure",
                simulated,
                traffic,
                failed_link=f"{source}-{destination}",
            )
        )

    # 3. Synthetic traffic surge on one node pair
    surge_traffic = simulate_traffic_surge(
        traffic,
        source="A",
        destination="F",
        multiplier=3.0,
    )
    results.append(
        _evaluate_scenario(
            "traffic_surge_A_F_x3",
            baseline,
            surge_traffic,
        )
    )

    # 4. Synthetic targeted flood-like demand toward node F
    flood_traffic = simulate_targeted_flood(
        traffic,
        target="F",
        multiplier=5.0,
    )
    results.append(
        _evaluate_scenario(
            "targeted_flood_F_x5",
            baseline,
            flood_traffic,
        )
    )

    return pd.DataFrame(results)


def export_full_experiment(
    output_path="results/tables/full_experiment_results.csv",
    seed=42,
):
    """Save full experiment results as a CSV file."""
    results = run_full_experiment(seed=seed)

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(destination, index=False)

    return results

    
def run_link_failure_experiment(seed=42):
    """Run baseline and individual link-failure experiments."""
    results = run_full_experiment(seed=seed)

    results = results[
        results["scenario"].isin(["baseline", "link_failure"])
    ].copy()

    results["nodes_removed"] = 0
    results["links_removed"] = (
        results["scenario"] == "link_failure"
    ).astype(int)

    columns = [
        "scenario",
        "failed_link",
        "nodes_removed",
        "links_removed",
        "components",
        "unreachable_pairs",
        "maximum_utilization",
        "average_utilization",
        "unreachable_demands",
    ]

    return results[columns].reset_index(drop=True)

