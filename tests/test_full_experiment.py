
from ndt.experiments import run_full_experiment


def test_full_experiment_contains_expected_scenarios():
    results = run_full_experiment()

    assert len(results) == 10
    assert results.iloc[0]["scenario"] == "baseline"
    assert (results["scenario"] == "link_failure").sum() == 7
    assert "traffic_surge_A_F_x3" in results["scenario"].values
    assert "targeted_flood_F_x5" in results["scenario"].values


def test_baseline_has_no_unreachable_demands():
    results = run_full_experiment()
    baseline = results.iloc[0]

    assert baseline["unreachable_demands"] == 0
    assert baseline["components"] == 1


def test_surge_increases_total_traffic():
    results = run_full_experiment()

    baseline = results.loc[
        results["scenario"] == "baseline"
    ].iloc[0]
    surge = results.loc[
        results["scenario"] == "traffic_surge_A_F_x3"
    ].iloc[0]

    assert surge["total_traffic_mbps"] > baseline["total_traffic_mbps"]


def test_flood_increases_total_traffic():
    results = run_full_experiment()

    baseline = results.loc[
        results["scenario"] == "baseline"
    ].iloc[0]
    flood = results.loc[
        results["scenario"] == "targeted_flood_F_x5"
    ].iloc[0]

    assert flood["total_traffic_mbps"] > baseline["total_traffic_mbps"]


def test_experiment_is_reproducible():
    first = run_full_experiment()
    second = run_full_experiment()

    assert first.equals(second)


def test_all_scenarios_have_performance_metrics():
    results = run_full_experiment()

    assert results["maximum_utilization"].notna().all()
    assert results["average_utilization"].notna().all()
    assert results["total_traffic_mbps"].notna().all()
