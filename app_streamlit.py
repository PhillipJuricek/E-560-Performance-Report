import io

import streamlit as st

from config import EXCHANGERS, MIN_ONLINE_STREAK_DAYS
from analysis.preprocessing import (
    preprocess_data,
    load_process_data,
    load_event_data,
)
from analysis.metrics import calculate_metrics
from analysis.rankings import build_rankings
from analysis.cycle_analysis import build_cycle_comparison
from visualization.fleet import fleet_rntp_plot, fleet_rri_plot
from visualization.fwko import fwko_constraint_plot
from visualization.cycle_plots import plot_cycle_comparison
from methodology import METHODOLOGY_SECTIONS, render_methodology_section

st.set_page_config(
    page_title="E-560 M-Exchanger Performance Report",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_data(show_spinner=False)
def run_analysis(process_bytes, event_bytes):
    df = load_process_data(io.BytesIO(process_bytes))
    events = load_event_data(io.BytesIO(event_bytes))

    df = preprocess_data(df, events)
    df = calculate_metrics(df)
    rankings = build_rankings(df)
    cycles = build_cycle_comparison(df)
    return df, rankings, cycles


st.title("E-560 M-Exchanger Performance Report")
st.caption("by Phillip Juricek")

# ---------------------------------------------------------------------------
# Data Input
# ---------------------------------------------------------------------------
st.header("Data Input")

st.markdown(
    "Upload the two source files below to generate the report. "
    "Drag and drop the files into the boxes, or browse for them "
    "on your machine."
)

st.info(
    "**Choosing a SCADA pull timeframe:** pull **~180 days** if you want to "
    "best see an exchanger's current cycle vs. previous cycle comparison — this "
    "gives enough history to reliably capture a full previous cycle. Pull a "
    "**28–90 day** window instead if you're only interested in current "
    "fleet performance (RNHTI/RRI) — a shorter window keeps the fleet-wide "
    "plots focused on recent, relevant operating conditions."
)

col_process, col_event = st.columns(2)

with col_process:
    process_file = st.file_uploader(
        "SCADA Process Data (CSV)",
        type=["csv"],
        help=(
            "The first file to input is a CSV dataset pulled from SCADA "
            "on the South Battery section, named E-560X "
            "(e.g. E-560-180-Aug3.CSV)."
        ),
    )
    st.caption(
        "First file: the CSV dataset pulled from SCADA on the "
        "South Battery section (E-560X)."
    )

with col_event:
    event_file = st.file_uploader(
        "Event Logbook Data (XLSX)",
        type=["xlsx"],
        help=(
            "The second file is the operator's native cleaning log "
            "(e.g. `2026 - E560 & 5611 Cleaning Log July 26.xlsx`)."
        ),
    )
    st.caption(
        "Second file: the operator's cleaning log from the E560 sheet."
    )

if process_file is not None and event_file is not None:
    st.caption(f"Loaded: `{process_file.name}` • `{event_file.name}`")

    with st.spinner("Loading and analyzing exchanger data..."):
        df, rankings, cycles = run_analysis(
            process_file.getvalue(),
            event_file.getvalue(),
        )

    st.success("Analysis complete.")

    # -----------------------------------------------------------------------
    # Fleet Wide Performance — RNTP on top, RRI below
    # -----------------------------------------------------------------------
    st.header("Fleet Wide Performance")
    st.pyplot(fleet_rntp_plot(df))
    st.pyplot(fleet_rri_plot(df))
    st.pyplot(fwko_constraint_plot(df))

    # -----------------------------------------------------------------------
    # Cycle Comparison
    # -----------------------------------------------------------------------
    st.header("Exchanger Cycle Comparison")

    exchanger = st.selectbox(
        "Select Exchanger",
        EXCHANGERS,
        index=0,
    )
    st.pyplot(
        plot_cycle_comparison(
            df,
            cycles,
            exchanger,
        )
    )

    # -----------------------------------------------------------------------
    # Worst Exchanger Metrics — below the cycle plot
    # -----------------------------------------------------------------------
    st.subheader("Worst Exchanger Metrics")

    thermal_worst = rankings["thermal"]["worst"]
    hydraulic_worst = rankings["hydraulic"]["worst"]

    thermal_excluded = [
        r["exchanger"]
        for r in rankings["thermal"]["ranking"]
        if not r["eligible"]
    ]
    hydraulic_excluded = [
        r["exchanger"]
        for r in rankings["hydraulic"]["ranking"]
        if not r["eligible"]
    ]

    col_thermal, col_hydraulic = st.columns(2)
    with col_thermal:
        if thermal_worst is not None:
            st.metric(
                label="Worst Thermal Performer (RNTP)",
                value=f"Exchanger {thermal_worst['exchanger']}",
                delta=f"{thermal_worst['RNTP']:.3f} RNTP",
                delta_color="off",
            )
        else:
            st.metric(
                label="Worst Thermal Performer (RNTP)",
                value="No eligible exchangers",
                delta_color="off",
            )
    with col_hydraulic:
        if hydraulic_worst is not None:
            st.metric(
                label="Worst Hydraulic Performer (RRI)",
                value=f"Exchanger {hydraulic_worst['exchanger']}",
                delta=f"{hydraulic_worst['RRI']:.3f} RRI",
                delta_color="off",
            )
        else:
            st.metric(
                label="Worst Hydraulic Performer (RRI)",
                value="No eligible exchangers",
                delta_color="off",
            )

    if thermal_excluded:
        st.caption(
            f"Excluded from thermal ranking (offline or online < "
            f"{MIN_ONLINE_STREAK_DAYS} consecutive days): "
            f"{', '.join(thermal_excluded)}"
        )
    if hydraulic_excluded:
        st.caption(
            f"Excluded from hydraulic ranking (offline or online < "
            f"{MIN_ONLINE_STREAK_DAYS} consecutive days): "
            f"{', '.join(hydraulic_excluded)}"
        )

else:
    st.info(
        "Please upload both files to display the report. "
        "You need the SCADA CSV **and** the logbook event file."
    )

# ---------------------------------------------------------------------------
# Methodology — always rendered at the bottom, even before files are uploaded
# ---------------------------------------------------------------------------
st.header("Methodology")

for section in METHODOLOGY_SECTIONS:
    render_methodology_section(section)

