
def simulate_traffic_surge(
    traffic_matrix,
    source,
    destination,
    multiplier=3.0,
):
    """
    Increase the demand between two nodes.

    This changes only the synthetic traffic matrix.
    It does not generate real network traffic.
    """
    if multiplier < 1.0:
        raise ValueError("Multiplier must be at least 1.0.")

    if source == destination:
        raise ValueError("Source and destination must differ.")

    key = (source, destination)
    reverse_key = (destination, source)

    if key in traffic_matrix:
        selected_key = key
    elif reverse_key in traffic_matrix:
        selected_key = reverse_key
    else:
        raise ValueError("The source-destination demand does not exist.")

    modified = traffic_matrix.copy()
    modified[selected_key] *= multiplier

    return modified


def simulate_targeted_flood(
    traffic_matrix,
    target,
    multiplier=5.0,
):
    """
    Increase all existing traffic demands involving a target node.

    This is an abstract, synthetic flood-like scenario.
    """
    if multiplier < 1.0:
        raise ValueError("Multiplier must be at least 1.0.")

    modified = traffic_matrix.copy()
    matched = 0

    for (source, destination), demand in traffic_matrix.items():
        if source == target or destination == target:
            modified[(source, destination)] = demand * multiplier
            matched += 1

    if matched == 0:
        raise ValueError("No traffic demands involve the target node.")

    return modified
