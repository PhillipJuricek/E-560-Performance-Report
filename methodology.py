"""
Skeleton content for the methodology section of the Streamlit report.

Each entry in METHODOLOGY_SECTIONS has a "title" and a "blocks" list. Each
block is one of:

    {"type": "text",    "value": "<markdown string>"}
    {"type": "formula", "value": "<latex string, no $ delimiters>"}
    {"type": "callout", "value": "<markdown string>"}   # plain-language takeaway

Rendering is handled by render_methodology_section() (see bottom of file),
which the app calls once per section. Extend this module to add/refine
explanations without touching the app layout.
"""

import streamlit as st

from config import (
    ROLLING_WINDOW,
    MIN_FLOW,
    STATE_DEADBAND,
    LOOKBACK_DAYS,
    MIN_ONLINE_STREAK_DAYS,
)

METHODOLOGY_SECTIONS = [
    {
        "title": "Overview",
        "blocks": [
            {
                "type": "text",
                "value": (
                    "This report evaluates the thermal and hydraulic performance of the "
                    "six E-560X main exchangers on the South Battery section. All metrics "
                    "are derived from two sources: a process dataset pulled from SCADA "
                    "(`E-560X` CSV) and an event log from the maintenance logbook "
                    "(Excel). "
                    "Performance is expressed in **relative** terms against the live "
                    "fleet median so that every exchanger is compared to its peers "
                    "under the same operating conditions."
                ),
            },
        ],
    },
    {
        "title": "1. Preprocessing & Data Cleaning",
        "blocks": [
            {
                "type": "text",
                "value": (
                    "- Process rows are loaded from the SCADA CSV and any rows with "
                    "empty process-variable values are dropped.\n"
                    "- A `datetime` column is built from the `Date` and `Time` columns "
                    "and the data is sorted chronologically.\n"
                    "- Column names are normalised (SCADA tag prefixes removed, "
                    "`-` replaced with `_`) so they map cleanly onto exchanger tags.\n"
                    "- Clean / Rebuild event dates from the logbook are merged onto "
                    "the process data as boolean columns per exchanger "
                    "(e.g. `A_Clean`, `A_Rebuild`)."
                ),
            },
        ],
    },
    {
        "title": "2. Online Determination",
        "blocks": [
            {
                "type": "text",
                "value": (
                    "An exchanger is considered **online** only when both of its "
                    "control valves are open:\n\n"
                    "- Flow control output `FIC_560X1 > 0`\n"
                    "- Temperature control output `TIC_560X2 > 0`\n\n"
                    "This avoids interpreting a flow reversal or a shutdown as a "
                    "performance change. All downstream metrics are evaluated on "
                    "online periods only."
                ),
            },
        ],
    },
    {
        "title": "3. Operating Cycle Determination",
        "blocks": [
            {
                "type": "text",
                "value": (
                    "A new operating **cycle** starts every time an exchanger "
                    "transitions from offline to online. Each continuous online period "
                    "is numbered from most recent to oldest (cycle `1` = current, "
                    "cycle `2` = previous).\n\n"
                    "- `OperatingCycle`: the cycle number for every timestamp.\n"
                    "- `CycleStart`: the start time of the current cycle.\n"
                    "- `DaysInOperation`: hours since the cycle start, in days.\n\n"
                    "Cycle data powers the current vs previous cycle comparison and "
                    "keeps rolling statistics from bleeding across maintenance "
                    "boundaries."
                ),
            },
        ],
    },
    {
        "title": "4. Flow Estimation",
        "blocks": [
            {
                "type": "text",
                "value": (
                    "Total pump flow is the sum of the three supply pumps "
                    "(`FIT_550A1`, `FIT_550B1`, `FIT_550C1`). Per-exchanger flow is "
                    "resolved as follows:\n\n"
                    "- If **all** online exchangers have a valid, positive flow reading "
                    "(`FIT_560X1`), the measured values are used directly.\n"
                    "- If **any** online exchanger is missing a reading, the unaccounted "
                    "flow (total pump flow minus the sum of measured flows) is split "
                    "evenly across the exchangers without a reading.\n\n"
                    "The estimated flow per exchanger is stored as `X_Flow`."
                ),
            },
        ],
    },
    {
        "title": "5. Performance Metrics",
        "blocks": [
            {
                "type": "text",
                "value": (
                    "The goal of these metrics is to quantify exchanger health while "
                    "minimizing the influence of changing process conditions. Since "
                    "all exchangers operate within the same process environment, "
                    "fleet-relative metrics are used wherever possible."
                ),
            },
            {
                "type": "text",
                "value": "**1. Delta T**",
            },
            {
                "type": "formula",
                "value": r"\Delta T = T_{outlet,\,emulsion} - T_{inlet,\,emulsion}",
            },
            {
                "type": "text",
                "value": (
                    "Temperature increase achieved by the exchanger. Sensor "
                    "direction is adjusted during flow reversals so ΔT stays "
                    "positive for a healthy, actively heating exchanger."
                ),
            },
            {
                "type": "text",
                "value": "**2. Heat Transfer Index (HTI)**",
            },
            {
                "type": "formula",
                "value": r"HTI = Flow_{emulsion} \times \Delta T",
            },
            {
                "type": "text",
                "value": (
                    "Represents the total heat delivered to the emulsion stream. "
                    "Useful for measuring exchanger contribution but influenced by "
                    "operating conditions."
                ),
            },
            {
                "type": "text",
                "value": "**3. Normalized Heat Transfer Index (NHTI)**",
            },
            {
                "type": "formula",
                "value": r"NHTI = \frac{Flow_{emulsion} \times \Delta T}{T_{glycol,\,supply} - T_{emulsion,\,inlet}}",
            },
            {
                "type": "text",
                "value": (
                    "Normalizes heat transfer performance against the available "
                    "temperature driving force from the glycol system."
                ),
            },
            {
                "type": "text",
                "value": "**4. Relative Normalized Heat Transfer Index (RNHTI)**",
            },
            {
                "type": "formula",
                "value": r"RNHTI = \frac{NHTI_{exchanger}}{Median(NHTI_{online\ fleet})}",
            },
            {
                "type": "text",
                "value": (
                    "Compares each exchanger against current fleet performance to "
                    "identify underperforming exchangers independent of process "
                    "conditions."
                ),
            },
            {
                "type": "text",
                "value": "**5. Hydraulic Restriction Index (RI)**",
            },
            {
                "type": "formula",
                "value": r"RI = \frac{FIC\ Output}{Flow}",
            },
            {
                "type": "text",
                "value": (
                    "Estimates the valve effort required to maintain exchanger "
                    "flow. Increasing values may indicate increased hydraulic "
                    "resistance due to fouling or plugging."
                ),
            },
            {
                "type": "text",
                "value": "**6. Relative Restriction Index (RRI)**",
            },
            {
                "type": "formula",
                "value": r"RRI = \frac{RI_{exchanger}}{Median(RI_{online\ fleet})}",
            },
            {
                "type": "text",
                "value": (
                    "Compares exchanger hydraulic performance against the "
                    "operating fleet."
                ),
            },
        ],
    },
    {
        "title": "6. Rankings (Worst / Best Performers)",
        "blocks": [
            {
                "type": "text",
                "value": (
                    "Rankings are based on the average of each metric over the "
                    "**last "
                    + f"{LOOKBACK_DAYS}"
                    + " days** while the exchanger is online:\n\n"
                    "- **Thermal**: ranked by average RNTP — highest is best, lowest "
                    "is the worst thermal performer.\n"
                    "- **Hydraulic**: ranked by average RRI — lowest is best, highest "
                    "is the worst hydraulic performer.\n\n"
                    "An exchanger only qualifies when it is **online at the report "
                    "time** and has been online **continuously for more than "
                    + f"{MIN_ONLINE_STREAK_DAYS} days"
                    + "** (ending at the report time). It is pointless to rank an "
                    "exchanger that is not currently in service, and a newly-started "
                    "exchanger does not yet have enough history. A simultaneous "
                    "fleet-wide outage (plant emergency / shutdown) does not reset "
                    "an exchanger's online streak.\n\n"
                    "These drive the 'Worst Exchanger Metrics' cards shown below the "
                    "cycle plots."
                ),
            },
        ],
    },
    {
        "title": "7. Cycle Comparison Plot",
        "blocks": [
            {
                "type": "text",
                "value": (
                    "For each exchanger the report overlays the **current cycle** "
                    "(cycle `1`) and, when available, the **previous cycle** "
                    "(cycle `2`) as RNTP vs days since the cycle began. The "
                    "maintenance event (Clean or Rebuild) that immediately preceded "
                    "each cycle is detected from the logbook and shown in the legend, "
                    "so you can see how performance decays between cleanings."
                ),
            },
        ],
    },
    {
        "title": "8. Configuration Values",
        "blocks": [
            {
                "type": "text",
                "value": (
                    f"- Rolling window: `{ROLLING_WINDOW}` hours\n"
                    f"- Minimum flow for restriction metric: `{MIN_FLOW} m³/day`\n"
                    f"- State classification deadband: `{STATE_DEADBAND} °C`\n"
                    f"- Ranking lookback: `{LOOKBACK_DAYS}` days\n"
                    f"- Minimum continuous online time to qualify for a ranking: "
                    f"`{MIN_ONLINE_STREAK_DAYS}` days (must also be online at the "
                    "report time; fleet-wide outages are exempt)\n\n"
                    "These parameters live in `config.py` and can be tuned without "
                    "changing the analysis code."
                ),
            },
        ],
    },
    {
        "title": "9. Contact",
        "blocks": [
            {
                "type": "callout",
                "value": (
                    "Questions, feedback, or suggestions about this report? "
                    "Reach out to **Phillip Juricek** — "
                    "'phlipjuricek@gmail.com` · [LinkedIn](https://www.linkedin.com/in/phillip-juricek-143a83302/)"
                ),
            },
        ],
    },
    {
        "title": "10. Source Code",
        "blocks": [
            {
                "type": "callout",
                "value": (
                    "Want to see how this analysis was built step by step? "
                    "The full **Google Colab notebook** is available on GitHub: "
                    "[View the Colab notebook](https://github.com/PhillipJuricek/E-560-Report-Methodology/blob/main/E_560_Performance_Report_Methodology.ipynb)"
                ),
            },
        ],
    },
]


def render_methodology_section(section: dict) -> None:
    """
    Render a single METHODOLOGY_SECTIONS entry to the Streamlit app.

    Call this once per section, e.g.:

        st.header("Methodology")
        for section in METHODOLOGY_SECTIONS:
            render_methodology_section(section)
    """
    st.subheader(section["title"])
    for block in section["blocks"]:
        if block["type"] == "text":
            st.markdown(block["value"])
        elif block["type"] == "formula":
            st.latex(block["value"])
        elif block["type"] == "callout":
            st.info(block["value"])
        else:
            raise ValueError(f"Unknown block type: {block['type']!r}")
