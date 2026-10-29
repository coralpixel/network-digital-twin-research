
from ndt.experiments import run_link_failure_experiment


def test_experiment_includes_baseline_and_all_link_failures():
    results = run_link_failure_experiment()

    # One baseline scenario plus one scenario per baseline link.
    assert len(results) == 8
    assert results.iloc[0]["scenario"] == "baseline"
    assert (results["scenario"] == "link_failure").sum() == 7


def test_baseline_has_no_unreachable_demands():
    results = run_link_failure_experiment()

    baseline = results.iloc[0]

    assert baseline["unreachable_demands"] == 0
    assert baseline["components"] == 1


def test_each_link_failure_removes_one_link():
    results = run_link_failure_experiment()

    failures = results[results["scenario"] == "link_failure"]

    assert (failures["links_removed"] == 1).all()
    assert (failures["nodes_removed"] == 0).all()


def test_experiment_is_reproducible():
    first = run_link_failure_experiment(seed=42)
    second = run_link_failure_experiment(seed=42)

    assert first.equals(second)


def test_results_contain_performance_metrics():
    results = run_link_failure_experiment()

    assert "maximum_utilization" in results.columns
    assert "average_utilization" in results.columns
    assert "unreachable_demands" in results.columns
