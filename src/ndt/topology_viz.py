
import matplotlib.pyplot as plt
import networkx as nx


def draw_network_topology(
    graph,
    failed_link=None,
    output_path=None,
):
    """
    Draw the network topology.

    failed_link: optional tuple, for example ("B", "C").
    The supplied graph should already represent the scenario.
    """
    positions = {
        "A": (0, 1),
        "B": (1, 2),
        "C": (2, 2),
        "D": (0, 0),
        "E": (1, 0),
        "F": (2, 1),
    }

    fig, ax = plt.subplots(figsize=(8, 5))

    nx.draw_networkx_nodes(
        graph,
        positions,
        node_size=1200,
        ax=ax,
    )

    nx.draw_networkx_labels(
        graph,
        positions,
        font_size=12,
        font_weight="bold",
        ax=ax,
    )

    normal_edges = [
        (u, v)
        for u, v in graph.edges()
        if failed_link is None
        or {u, v} != set(failed_link)
    ]

    nx.draw_networkx_edges(
        graph,
        positions,
        edgelist=normal_edges,
        width=2,
        ax=ax,
    )

    edge_labels = {
        (u, v): f"{data.get('capacity_mbps', '?')} Mbps"
        for u, v, data in graph.edges(data=True)
    }

    nx.draw_networkx_edge_labels(
        graph,
        positions,
        edge_labels=edge_labels,
        font_size=8,
        ax=ax,
    )

    ax.set_title("Network Digital Twin Topology")
    ax.axis("off")
    fig.tight_layout()

    if output_path is not None:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")

    return fig
