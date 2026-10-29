
import pandas as pd
import pytest

from ndt.stats import (
    summarize_repeated_experiments,
    run_repeated_experiments,
)


@pytest.fixture
def repeated_results():
    rows = []
    for seed, utilization, latency in [
        (1, 0.4, 10.0),
        (2, 0.5, 12.0),
        (3, 0.6, 14.0),
    ]:
        rows.append({
            "seed": seed,
            "scenario": "baseline",
            "maximum_utilization": utilization,
            "maximum_link_latency_ms": latency,
        })

    return pd.DataFrame(rows)


def test_summary_calculates_mean_and_std(repeated_results):
    summary = summarize_repeated_experiments(
        repeated_results,
        metrics=[
            "maximum_utilization",
            "maximum_link_latency_ms",
        ],
    )

    utilization = summary[
        summary["metric"] == "maximum_utilization"
    ].iloc[0]

    assert utilization["n"] == 3
    assert utilization["mean"] == pytest.approx(0.5)
    assert utilization["std"] == pytest.approx(0.1)


def test_confidence_interval_contains_mean(repeated_results):
    summary = summarize_repeated_experiments(
        repeated_results,
        metrics=["maximum_utilization"],
    )

    row = summary.iloc[0]
    assert row["ci95_lower"] < row["mean"]
    assert row["ci95_upper"] > row["mean"]



def test_duplicate_scenario_seed_is_rejected(repeated_results):
    duplicate = pd.concat(
        [repeated_results, repeated_results.iloc[[0]]],
        ignore_index=True,
    )

    with pytest.raises(
        ValueError,
        match="Each scenario configuration",
    ):
        summarize_repeated_experiments(
            duplicate,
            metrics=["maximum_utilization"],
        )



def test_empty_seed_list_is_rejected():
    with pytest.raises(ValueError, match="At least one seed"):
        run_repeated_experiments(seeds=[])
