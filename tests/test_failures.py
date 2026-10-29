
import pytest

from ndt.topology import create_baseline_topology
from ndt.twin import NetworkDigitalTwin
from ndt.failures import (
    simulate_link_failure,
    simulate_multiple_link_failures,
    simulate_node_failure,
)


def make_twin():
    return NetworkDigitalTwin(create_baseline_topology())


def test_single_link_failure():
    twin = make_twin()

    simulate_link_failure(twin, "B", "C")

    assert not twin.twin.has_edge("B", "C")
    assert twin.baseline.has_edge("B", "C")


def test_multiple_link_failures():
    twin = make_twin()

    simulate_multiple_link_failures(
        twin,
        [("B", "C"), ("E", "F")],
    )

    assert not twin.twin.has_edge("B", "C")
    assert not twin.twin.has_edge("E", "F")
    assert twin.baseline.number_of_edges() == 7


def test_invalid_multiple_failure_is_atomic():
    twin = make_twin()

    with pytest.raises(ValueError):
        simulate_multiple_link_failures(
            twin,
            [("B", "C"), ("A", "F")],
        )

    # No link should have been removed.
    assert twin.twin.has_edge("B", "C")
    assert twin.twin.number_of_edges() == 7


def test_node_failure():
    twin = make_twin()

    simulate_node_failure(twin, "C")

    assert "C" not in twin.twin
    assert "C" in twin.baseline
