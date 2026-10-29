
import networkx as nx
import pytest

from ndt.topology import create_baseline_topology
from ndt.twin import NetworkDigitalTwin


def test_twin_starts_as_baseline():
    baseline = create_baseline_topology()
    twin = NetworkDigitalTwin(baseline)

    assert twin.twin.number_of_nodes() == 6
    assert twin.twin.number_of_edges() == 7


def test_removing_link_does_not_change_baseline():
    twin = NetworkDigitalTwin(create_baseline_topology())

    twin.remove_link("B", "C")

    assert twin.baseline.has_edge("B", "C")
    assert not twin.twin.has_edge("B", "C")


def test_reset_restores_baseline():
    twin = NetworkDigitalTwin(create_baseline_topology())

    twin.remove_link("B", "C")
    twin.reset()

    assert twin.twin.number_of_nodes() == 6
    assert twin.twin.number_of_edges() == 7
    assert twin.twin.has_edge("B", "C")


def test_removing_node_does_not_change_baseline():
    twin = NetworkDigitalTwin(create_baseline_topology())

    twin.remove_node("C")

    assert "C" in twin.baseline
    assert "C" not in twin.twin


def test_invalid_link_raises_error():
    twin = NetworkDigitalTwin(create_baseline_topology())

    with pytest.raises(ValueError):
        twin.remove_link("A", "F")


def test_empty_baseline_is_rejected():
    with pytest.raises(ValueError):
        NetworkDigitalTwin(nx.Graph())
