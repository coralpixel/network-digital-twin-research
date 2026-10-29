from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import altair as alt

from ndt.topology import create_baseline_topology
from ndt.topology_viz import draw_network_topology
from ndt.experiments import run_full_experiment

st.set_page_config(
    page_title="Network Digital Twin",
    page_icon="🌐",
    layout="wide",
)

st.title("Network Digital Twin")
st.subheader("Network Failure and Attack Impact Analysis")

st.write(
    "Explore how individual link failures and synthetic traffic scenarios "
    "affect network structure and modeled performance."
)

st.info(
    "This dashboard uses a simplified analytical model and synthetic traffic. "
    "It does not measure a live network or perform real attacks."
)

# Run the reproducible experiment.
@st.cache_data
def get_results(seed):
    return run_full_experiment(seed=seed)


with st.sidebar:
    st.header("Experiment settings")
    seed = st.number_input(
        "Traffic random seed",
        min_value=0,
        max_value=1000000,
        value=42,
        step=1,
    )

    st.caption("Changing the seed generates a different reproducible traffic matrix.")

results = get_results(int(seed))

scenario_options = results["scenario"].drop_duplicates().tolist()


st.header("Scenario analysis")

def scenario_label(row):
    scenario = row["scenario"]

    if scenario == "baseline":
        return "Baseline"

    if scenario == "link_failure":
        return f"Link failure: {row['failed_link']}"

    if scenario == "traffic_surge_A_F_x3":
        return "Traffic surge: A → F (3×)"

    if scenario == "targeted_flood_F_x5":
        return "Targeted flood: F (5×)"

    return scenario

results = results.copy()
results["scenario_label"] = results.apply(scenario_label, axis=1)

selected_label = st.selectbox(
    "Choose a scenario",
    results["scenario_label"].tolist(),
)

selected = results.loc[
    results["scenario_label"] == selected_label
].iloc[0]

baseline = results.loc[
    results["scenario"] == "baseline"
].iloc[0]


utilization = float(selected["maximum_utilization"]) * 100
baseline_utilization = float(baseline["maximum_utilization"]) * 100

latency = float(selected["maximum_link_latency_ms"])
baseline_latency = float(baseline["maximum_link_latency_ms"])

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Maximum utilization",
    f"{utilization:.2f}%",
    delta=f"{utilization - baseline_utilization:+.2f} percentage points",
)

col2.metric(
    "Maximum modeled link latency",
    f"{latency:.2f} ms",
    delta=f"{latency - baseline_latency:+.2f} ms",
)

col3.metric(
    "Overloaded links",
    int(selected["overloaded_links"]),
)

col4.metric(
    "Unreachable traffic demands",
    int(selected["unreachable_demands"]),
)

st.caption(
    "Utilization changes are shown in percentage points relative to baseline. "
    "Latency is an analytical estimate, not a real-network measurement."
)


st.divider()


st.divider()

st.header("Network topology")

topology = create_baseline_topology()
failed_link_value = selected["failed_link"]

if selected["scenario"] == "link_failure" and pd.notna(failed_link_value):
    node_a, node_b = failed_link_value.split("-")
    topology.remove_edge(node_a, node_b)

topology_figure = draw_network_topology(topology)
st.pyplot(topology_figure, width="stretch")
plt.close(topology_figure)



st.header("Compare all scenarios")

import altair as alt

chart_data = results[
    ["scenario", "failed_link", "maximum_utilization",
     "maximum_link_latency_ms"]
].copy()

chart_data["maximum_utilization_percent"] = (
    chart_data["maximum_utilization"] * 100
)

chart_data["display_label"] = chart_data.apply(
    lambda row: (
        "Baseline" if row["scenario"] == "baseline"
        else f"Fail {row['failed_link']}"
        if row["scenario"] == "link_failure"
        else "Traffic surge"
        if row["scenario"] == "traffic_surge_A_F_x3"
        else "Targeted flood"
        if row["scenario"] == "targeted_flood_F_x5"
        else row["scenario"]
    ),
    axis=1,
)

st.subheader("Maximum link utilization")

utilization_chart = (
    alt.Chart(chart_data)
    .mark_bar()
    .encode(
        x=alt.X(
            "display_label:N",
            title="Scenario",
            sort=None,
            axis=alt.Axis(labelAngle=-35),
        ),
        y=alt.Y(
            "maximum_utilization_percent:Q",
            title="Maximum link utilization (%)",
            scale=alt.Scale(
                domain=[
                    0,
                    max(
                        110,
                        float(chart_data["maximum_utilization_percent"].max())
                        * 1.15,
                    ),
                ]
            ),
        ),
        tooltip=[
            alt.Tooltip("display_label:N", title="Scenario"),
            alt.Tooltip(
                "maximum_utilization_percent:Q",
                title="Utilization (%)",
                format=".2f",
            ),
        ],
    )
    .properties(height=400)
)

capacity_line = (
    alt.Chart(pd.DataFrame({"capacity": [100]}))
    .mark_rule(strokeDash=[6, 4])
    .encode(y="capacity:Q")
)

st.altair_chart(
    utilization_chart + capacity_line,
    width="stretch",
)

st.subheader("Maximum modeled link latency")

latency_chart = (
    alt.Chart(chart_data)
    .mark_bar()
    .encode(
        x=alt.X(
            "display_label:N",
            title="Scenario",
            sort=None,
            axis=alt.Axis(labelAngle=-35),
        ),
        y=alt.Y(
            "maximum_link_latency_ms:Q",
            title="Maximum modeled link latency (ms)",
            scale=alt.Scale(zero=True),
        ),
        tooltip=[
            alt.Tooltip("display_label:N", title="Scenario"),
            alt.Tooltip(
                "maximum_link_latency_ms:Q",
                title="Latency (ms)",
                format=".2f",
            ),
        ],
    )
    .properties(height=400)
)

st.altair_chart(latency_chart, width="stretch")

st.header("Experiment results")

display_results = results.drop(columns=["scenario_label"], errors="ignore")

st.dataframe(
    display_results.round(4),
    width="stretch",
    hide_index=True,
)

st.download_button(
    label="Download experiment results (CSV)",
    data=results.to_csv(index=False).encode("utf-8"),
    file_name="full_experiment_results.csv",
    mime="text/csv",
)


st.divider()
st.header("Research Analysis")

st.write(
    "Statistical and sensitivity analysis across repeated synthetic "
    "traffic experiments. Results are produced by an analytical model, "
    "not measurements from a live network."
)

# Load statistical results if the experiment files exist.
tables_dir = PROJECT_ROOT / "results" / "tables"
figures_dir = PROJECT_ROOT / "results" / "figures"

stats_path = tables_dir / "statistical_summary.csv"
sensitivity_path = tables_dir / "traffic_sensitivity_runs.csv"
sensitivity_summary_path = tables_dir / "traffic_sensitivity_summary.csv"

if stats_path.exists():
    stats_df = pd.read_csv(stats_path)

    st.subheader("Repeated experiment statistical summary")
    st.dataframe(stats_df.round(4), width="stretch", hide_index=True)

    st.download_button(
        "Download statistical summary (CSV)",
        data=stats_df.to_csv(index=False).encode("utf-8"),
        file_name="statistical_summary.csv",
        mime="text/csv",
    )
else:
    st.warning(
        "Statistical summary not found. Run the repeated experiments "
        "to generate statistical_summary.csv."
    )

if sensitivity_path.exists():
    sensitivity_df = pd.read_csv(sensitivity_path)

    st.subheader("Traffic sensitivity analysis")

    sensitivity_scenarios = sensitivity_df[
        sensitivity_df["scenario"].isin(
            ["traffic_surge", "targeted_flood"]
        )
    ].copy()

    utilization_summary = (
        sensitivity_scenarios.groupby(
            ["scenario", "multiplier"], as_index=False
        )["maximum_utilization"]
        .mean()
    )
    utilization_summary["maximum_utilization_percent"] = (
        utilization_summary["maximum_utilization"] * 100
    )

    utilization_plot = (
        alt.Chart(utilization_summary)
        .mark_line(point=True)
        .encode(
            x=alt.X("multiplier:Q", title="Traffic multiplier"),
            y=alt.Y(
                "maximum_utilization_percent:Q",
                title="Mean maximum utilization (%)",
            ),
            color=alt.Color("scenario:N", title="Scenario"),
            tooltip=[
                "scenario",
                "multiplier",
                alt.Tooltip(
                    "maximum_utilization_percent:Q",
                    title="Mean utilization (%)",
                    format=".2f",
                ),
            ],
        )
        .properties(height=350)
    )

    capacity_rule = (
        alt.Chart(pd.DataFrame({"capacity": [100]}))
        .mark_rule(strokeDash=[6, 4])
        .encode(y="capacity:Q")
    )

    st.altair_chart(
        utilization_plot + capacity_rule,
        width="stretch",
    )

    # Report infinite latency observations without treating them as zero.
    latency_summary = (
        sensitivity_scenarios.groupby(
            ["scenario", "multiplier"]
        )["maximum_link_latency_ms"]
        .agg(
            total_runs="count",
            finite_runs=lambda values: (
                values.notna() & (values != float("inf"))
            ).sum(),
            infinite_runs=lambda values: (values == float("inf")).sum(),
        )
        .reset_index()
    )

    latency_summary["infinite_run_percent"] = (
        latency_summary["infinite_runs"]
        / latency_summary["total_runs"]
        * 100
    )

    st.subheader("Latency validity and overload indicators")
    st.caption(
        "Infinite latency is retained as a model outcome when a link "
        "reaches or exceeds its capacity. It is not interpreted as zero."
    )
    st.dataframe(
        latency_summary.round(3),
        width="stretch",
        hide_index=True,
    )

    st.download_button(
        "Download sensitivity runs (CSV)",
        data=sensitivity_df.to_csv(index=False).encode("utf-8"),
        file_name="traffic_sensitivity_runs.csv",
        mime="text/csv",
    )

    if sensitivity_summary_path.exists():
        sensitivity_summary_df = pd.read_csv(
            sensitivity_summary_path
        )

        st.download_button(
            "Download sensitivity summary (CSV)",
            data=sensitivity_summary_df.to_csv(
                index=False
            ).encode("utf-8"),
            file_name="traffic_sensitivity_summary.csv",
            mime="text/csv",
        )
else:
    st.warning(
        "Sensitivity results not found. Generate the traffic sensitivity "
        "CSV files before using this section."
    )
