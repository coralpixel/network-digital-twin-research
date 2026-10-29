
from pathlib import Path

from ndt.topology import create_baseline_topology
from ndt.twin import NetworkDigitalTwin
from ndt.failures import simulate_link_failure
from ndt.metrics import compare_structures
from ndt.viz import plot_network_comparison


def main():
    results_dir = Path("results/figures")
    results_dir.mkdir(parents=True, exist_ok=True)

    baseline = create_baseline_topology()
    twin = NetworkDigitalTwin(baseline)

    # Simulate a link failure in the digital twin.
    failed_link = ("B", "C")
    simulate_link_failure(twin, *failed_link)

    simulated = twin.twin

    comparison = compare_structures(twin.baseline, simulated)

    print("\n=== STRUCTURAL IMPACT ANALYSIS ===")
    print("\nBaseline:")
    for metric, value in comparison["baseline"].items():
        print(f"  {metric}: {value}")

    print("\nSimulated:")
    for metric, value in comparison["simulated"].items():
        print(f"  {metric}: {value}")

    print("\nChanges:")
    for metric, value in comparison["changes"].items():
        print(f"  {metric}: {value}")

    plot_network_comparison(
        baseline=twin.baseline,
        simulated=simulated,
        failed_links=[failed_link],
        output_path=str(results_dir / "link_failure_comparison.png"),
    )


if __name__ == "__main__":
    main()
