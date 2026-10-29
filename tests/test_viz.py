
import pandas as pd
import pytest

from ndt.viz import create_impact_table


def test_impact_table_has_percentage_columns():
    results = pd.DataFrame([
        {
            "scenario": "baseline",
            "maximum_utilization": 0.4,
            "average_utilization": 0.2,
            "maximum_link_latency_ms": 10.0,
            "total_traffic_mbps": 100.0,
        },
        {
            "scenario": "traffic_surge",
            "maximum_utilization": 0.6,
            "average_utilization": 0.3,
            "maximum_link_latency_ms": 15.0,
            "total_traffic_mbps": 120.0,
        },
    ])

    impact = create_impact_table(results)

    assert "maximum_utilization_change_percent" in impact.columns
    assert "maximum_link_latency_ms_change_percent" in impact.columns


def test_baseline_percentage_changes_are_zero():
    results = pd.DataFrame([
        {
            "scenario": "baseline",
            "maximum_utilization": 0.4,
            "average_utilization": 0.2,
            "maximum_link_latency_ms": 10.0,
            "total_traffic_mbps": 100.0,
        },
    ])

    impact = create_impact_table(results)

    assert impact.iloc[0]["maximum_utilization_change_percent"] == 0
    assert impact.iloc[0]["maximum_link_latency_ms_change_percent"] == 0


def test_surge_percentage_change_is_correct():
    results = pd.DataFrame([
        {
            "scenario": "baseline",
            "maximum_utilization": 0.4,
            "average_utilization": 0.2,
            "maximum_link_latency_ms": 10.0,
            "total_traffic_mbps": 100.0,
        },
        {
            "scenario": "surge",
            "maximum_utilization": 0.6,
            "average_utilization": 0.3,
            "maximum_link_latency_ms": 15.0,
            "total_traffic_mbps": 120.0,
        },
    ])

    impact = create_impact_table(results)
    surge = impact[impact["scenario"] == "surge"].iloc[0]

    assert surge["maximum_utilization_change_percent"] == pytest.approx(50.0)
    assert surge["maximum_link_latency_ms_change_percent"] == pytest.approx(50.0)
    assert surge["total_traffic_mbps_change_percent"] == pytest.approx(20.0)


def test_missing_baseline_is_rejected():
    results = pd.DataFrame([
        {
            "scenario": "surge",
            "maximum_utilization": 0.6,
            "average_utilization": 0.3,
            "maximum_link_latency_ms": 15.0,
            "total_traffic_mbps": 120.0,
        },
    ])

    with pytest.raises(ValueError):
        create_impact_table(results)
