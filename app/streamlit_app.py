
import networkx as nx
from ndt.topology import create_baseline_topology
from ndt.topology_viz import draw_network_topology
import matplotlib.pyplot as plt

from pathlib import Path
import sys

import pandas as pd
import streamlit as st

# Allow the app to import the project package from src/.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

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
