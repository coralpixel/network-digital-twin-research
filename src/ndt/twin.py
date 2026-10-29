
from copy import deepcopy

import networkx as nx


class NetworkDigitalTwin:
    """Maintain a baseline network and an isolated simulation copy."""

    def __init__(self, baseline: nx.Graph):
        if baseline.number_of_nodes() == 0:
            raise ValueError("Baseline network cannot be empty.")

        self._baseline = deepcopy(baseline)
        self._twin = deepcopy(self._baseline)

    @property
    def baseline(self) -> nx.Graph:
        """Return a copy of the original baseline network."""
        return deepcopy(self._baseline)

    @property
    def twin(self) -> nx.Graph:
        """Return a copy of the current simulated network."""
        return deepcopy(self._twin)

    def reset(self) -> None:
        """Restore the twin to its original baseline state."""
        self._twin = deepcopy(self._baseline)

    def remove_link(self, source: str, destination: str) -> None:
        """Remove a link from the simulated network only."""
        if not self._twin.has_edge(source, destination):
            raise ValueError(
                f"Link {source}-{destination} does not exist in the twin."
            )

        self._twin.remove_edge(source, destination)

    def remove_node(self, node: str) -> None:
        """Remove a node and its incident links from the simulated network."""
        if node not in self._twin:
            raise ValueError(f"Node {node} does not exist in the twin.")

        self._twin.remove_node(node)
