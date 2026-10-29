
import pytest

from ndt.topology import create_baseline_topology
from ndt.traffic import generate_traffic_matrix
from ndt.attacks import (
    simulate_traffic_surge,
    simulate_targeted_flood,
)


def test_traffic_surge_increases_selected_demand():
    graph = create_baseline_topology()
    traffic = generate_traffic_matrix(graph, seed=42)

    modified = simulate_traffic_surge(
        traffic, "A", "B", multiplier=3.0
    )

    assert modified[("A", "B")] == pytest.approx(
        traffic[("A", "B")] * 3.0
    )


def test_traffic_surge_does_not_modify_original():
    graph = create_baseline_topology()
    traffic = generate_traffic_matrix(graph, seed=42)
    original = traffic.copy()

    simulate_traffic_surge(traffic, "A", "B")

    assert traffic == original


def test_traffic_surge_accepts_reverse_pair():
    traffic = {("A", "B"): 10.0}

    modified = simulate_traffic_surge(
        traffic, "B", "A", multiplier=2.0
    )

    assert modified[("A", "B")] == 20.0


def test_invalid_surge_multiplier_is_rejected():
    traffic = {("A", "B"): 10.0}

    with pytest.raises(ValueError):
        simulate_traffic_surge(
            traffic, "A", "B", multiplier=0.5
        )


def test_targeted_flood_increases_demands_to_target():
    graph = create_baseline_topology()
    traffic = generate_traffic_matrix(graph, seed=42)

    modified = simulate_targeted_flood(
        traffic, target="F", multiplier=5.0
    )

    for (source, destination), demand in traffic.items():
        if source == "F" or destination == "F":
            assert modified[(source, destination)] == pytest.approx(
                demand * 5.0
            )


def test_targeted_flood_preserves_other_demands():
    traffic = {
        ("A", "B"): 10.0,
        ("A", "F"): 4.0,
        ("B", "F"): 6.0,
    }

    modified = simulate_targeted_flood(
        traffic, target="F", multiplier=5.0
    )

    assert modified[("A", "B")] == 10.0


def test_invalid_flood_multiplier_is_rejected():
    traffic = {("A", "B"): 10.0}

    with pytest.raises(ValueError):
        simulate_targeted_flood(
            traffic, target="A", multiplier=0.5
        )


def test_unknown_target_is_rejected():
    traffic = {("A", "B"): 10.0}

    with pytest.raises(ValueError):
        simulate_targeted_flood(
            traffic, target="Z", multiplier=5.0
        )
