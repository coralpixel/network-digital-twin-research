
import pandas as pd
import pytest

from ndt.impact import calculate_impact_table


@pytest.fixture
def sample_results():
    return pd.DataFrame([
        {
            "scenario": "baseline",
            "maximum_utilization": 0.4,
            "average_utilization": 0.2,
            "maximum_link_latency_ms": 10.0,
            "total_traffic_mbps": 100.0,
        },
        {
            "scenario": "test_scenario",
            "maximum_utilization": 0.6,
            "average_utilization": 0.3,
            "maximum_link_latency_ms": 15.0,
            "total_traffic_mbps": 120.0,
        },
    ])


def test_baseline_changes_are_zero(sample_results):
    impact = calculate_impact_table(sample_results)
    baseline = impact[impact["scenario"] == "baseline"].iloc[0]

    assert baseline["maximum_utilization_change_percent"] == pytest.approx(0)
    assert baseline["maximum_link_latency_ms_change_percent"] == pytest.approx(0)


def test_relative_and_percentage_point_changes(sample_results):
    impact = calculate_impact_table(sample_results)
    scenario = impact[impact["scenario"] == "test_scenario"].iloc[0]

    assert scenario["maximum_utilization_change_percent"] == pytest.approx(50)
    assert scenario["maximum_utilization_change_percentage_points"] == pytest.approx(20)
    assert scenario["maximum_link_latency_ms_change_percent"] == pytest.approx(50)
    assert scenario["total_traffic_mbps_change_percent"] == pytest.approx(20)


def test_missing_baseline_raises_error(sample_results):
    non_baseline = sample_results[
        sample_results["scenario"] != "baseline"
    ]

    with pytest.raises(ValueError, match="exactly one baseline"):
        calculate_impact_table(non_baseline)


def test_duplicate_baseline_raises_error(sample_results):
    duplicate = pd.concat(
        [sample_results, sample_results.iloc[[0]]],
        ignore_index=True,
    )

    with pytest.raises(ValueError, match="exactly one baseline"):
        calculate_impact_table(duplicate)
