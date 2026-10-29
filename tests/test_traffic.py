
import pytest

from ndt.topology import create_baseline_topology
from ndt.traffic import generate_traffic_matrix


def test_traffic_matrix_contains_all_unordered_pairs():
    graph = create_baseline_topology()
    traffic = generate_traffic_matrix(graph, seed=42)

    assert len(traffic) == 15


def test_traffic_is_reproducible():
    graph = create_baseline_topology()

    first = generate_traffic_matrix(graph, seed=42)
    second = generate_traffic_matrix(graph, seed=42)

    assert first == second


def test_demands_are_within_bounds():
    graph = create_baseline_topology()
    traffic = generate_traffic_matrix(graph, seed=42)

    assert all(2.0 <= demand <= 15.0 for demand in traffic.values())


def test_invalid_demand_bounds_are_rejected():
    graph = create_baseline_topology()

    with pytest.raises(ValueError):
        generate_traffic_matrix(
            graph,
            min_demand_mbps=20,
            max_demand_mbps=10,
        )
