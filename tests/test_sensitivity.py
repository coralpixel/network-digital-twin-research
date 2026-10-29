
import pytest

from ndt.sensitivity import (
    run_traffic_sensitivity,
    summarize_traffic_sensitivity,
)


def test_sensitivity_generates_expected_rows():
    results = run_traffic_sensitivity(
        seeds=[42, 43],
        surge_multipliers=[1.0, 2.0],
        flood_multipliers=[1.0, 2.0],
    )

    # Per seed: 1 baseline + 2 surge + 2 flood scenarios.
    assert len(results) == 10
    assert set(results["scenario"]) == {
        "baseline",
        "traffic_surge",
        "targeted_flood",
    }


def test_sensitivity_rejects_invalid_multiplier():
    with pytest.raises(ValueError, match="at least 1.0"):
        run_traffic_sensitivity(
            seeds=[42],
            surge_multipliers=[0.5],
            flood_multipliers=[1.0],
        )



def test_summary_contains_expected_statistics():
    results = run_traffic_sensitivity(
        seeds=[42, 43],
        surge_multipliers=[2.0],
        flood_multipliers=[2.0],
    )

    summary = summarize_traffic_sensitivity(results)

    assert "mean_finite" in summary.columns
    assert "std_finite" in summary.columns
    assert "ci95_lower_finite" in summary.columns
    assert "ci95_upper_finite" in summary.columns
    assert "n_total" in summary.columns
    assert "n_finite" in summary.columns
    assert "n_infinite" in summary.columns

