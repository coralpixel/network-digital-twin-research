
from ndt.twin import NetworkDigitalTwin


def simulate_link_failure(
    twin: NetworkDigitalTwin,
    source: str,
    destination: str,
) -> None:
    """Simulate a single link failure in the digital twin."""
    twin.remove_link(source, destination)


def simulate_multiple_link_failures(
    twin: NetworkDigitalTwin,
    links: list[tuple[str, str]],
) -> None:
    """Simulate multiple link failures in the digital twin."""
    # Validate every link before changing the twin.
    graph = twin.twin

    for source, destination in links:
        if not graph.has_edge(source, destination):
            raise ValueError(
                f"Link {source}-{destination} does not exist in the twin."
            )

    for source, destination in links:
        twin.remove_link(source, destination)


def simulate_node_failure(
    twin: NetworkDigitalTwin,
    node: str,
) -> None:
    """Simulate a node failure in the digital twin."""
    twin.remove_node(node)
