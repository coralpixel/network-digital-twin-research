
import pytest

from ndt.topology import create_baseline_topology
from ndt.traffic import generate_traffic_matrix
from ndt.performance import (
    analyze_performance,
    calculate_link_loads,
    calculate_link_utilization,
    calculate_link_latency,
    estimate_packet_loss,
)


def test_link_loads_are_non_negative():
    graph = create_baseline_topology()
    traffic = generate_traffic_matrix(graph, seed=42)

    loads = calculate_link_loads(graph, traffic)

    assert loads
    assert all(load >= 0 for load in loads.values())


def test_utilization_is_non_negative():
    graph = create_baseline_topology()
    traffic = generate_traffic_matrix(graph, seed=42)
    loads = calculate_link_loads(graph, traffic)

    utilization = calculate_link_utilization(graph, loads)

    assert all(value >= 0 for value in utilization.values())


def test_zero_load_has_propagation_latency():
    graph = create_baseline_topology()
    loads = {tuple(sorted(edge)): 0.0 for edge in graph.edges()}

    latency = calculate_link_latency(graph, loads)

    for u, v, data in graph.edges(data=True):
        assert latency[tuple(sorted((u, v)))] == pytest.approx(
            data["delay_ms"]
        )


def test_packet_loss_is_between_zero_and_one():
    graph = create_baseline_topology()
    traffic = generate_traffic_matrix(graph, seed=42)
    loads = calculate_link_loads(graph, traffic)

    losses = estimate_packet_loss(graph, loads)

    assert all(0.0 <= loss <= 1.0 for loss in losses.values())


def test_performance_analysis_returns_expected_fields():
    graph = create_baseline_topology()
    traffic = generate_traffic_matrix(graph, seed=42)

    result = analyze_performance(graph, traffic)

    assert "link_loads_mbps" in result
    assert "link_utilization" in result
    assert "link_latency_ms" in result
    assert "estimated_packet_loss" in result
    assert "maximum_utilization" in result
    assert "unreachable_demands" in result
    assert result["unreachable_demands"] == 0


def test_disconnected_demand_is_counted():
    graph = create_baseline_topology()
    graph.remove_edge("A", "B")
    graph.remove_edge("A", "D")

    traffic = {("A", "F"): 10.0}

    result = analyze_performance(graph, traffic)

    assert result["unreachable_demands"] == 1
