import re

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

EVENT_COL_RE = re.compile(r"^([A-F])_(Clean|Rebuild|Fail_External|Fail_Internal)$")

FWKO_CONSTRAINT = 50.0

def fwko_constraint_plot(df):

    # Work on a copy so we never mutate the shared, cached dataframe.
    d = df.copy()
    d["datetime"] = pd.to_datetime(d["datetime"])
    d = d.sort_values("datetime").set_index("datetime")

    # ------------------------------------------------------------------
    # 2-day rolling averages (full window, then slice for the recent view)
    # ------------------------------------------------------------------
    d["FWKO_Temp_2d"] = d["TT_207B"].rolling("2D").mean()

    # ---- Find the most recent maintenance event across all exchangers ----
    event_cols = [c for c in d.columns if EVENT_COL_RE.match(c)]

    events = []
    for col in event_cols:
        m = EVENT_COL_RE.match(col)
        ex = m.group(1)
        ev_type = m.group(2)
        hit_dates = d.index[d[col] == True]
        for hit_date in hit_dates:
            events.append((hit_date, ex, ev_type))

    events_df = pd.DataFrame(
        events,
        columns=["date", "exchanger", "event"],
    ).sort_values("date")

    last_event = events_df.iloc[-1] if not events_df.empty else None

    # ---- Timeline starts at the last maintenance event ----
    if last_event is not None:
        cutoff = min(last_event["date"], d.index.max())
    else:
        cutoff = d.index.max() - pd.Timedelta(days=14)

    df_recent = d[d.index >= cutoff].copy()

    # 2-day rolling average of boiler header temp
    df_recent["TIT_5603_2d"] = df_recent["TIT_5603"].rolling("2D").mean()

    # ------------------------------------------------------------------
    # Color scheme — semantic, not decorative:
    #   blue  = FWKO (cold/process side)
    #   red   = Boiler (hot/heat-source side)
    #   gray  = anything that's a reference/annotation, not a measured series
    # Diverging colorbrewer RdBu pair — stays distinguishable under
    # red-green colorblindness, unlike a red/green scheme would.
    # ------------------------------------------------------------------
    COLOR_FWKO = "#2166AC"      # deep blue
    COLOR_BOILER = "#B2182B"    # deep red
    COLOR_REFERENCE = "#6E6E6E" # neutral gray — constraint line + event marker
    COLOR_VIOLATION = "#B2182B" # violation shading reuses boiler-adjacent red family, but very low alpha so it stays a background cue, not a competing series

    fig, ax = plt.subplots(figsize=(14, 5))

    # FWKO — 2-day rolling average (headline series only)
    ax.plot(
        df_recent.index,
        df_recent["FWKO_Temp_2d"],
        color=COLOR_FWKO,
        linewidth=2.5,
        solid_capstyle="round",
        label="FWKO Temp (2-Day Avg)",
    )

    # Constraint line — neutral, since it's a threshold reference, not data
    ax.axhline(
        FWKO_CONSTRAINT,
        color=COLOR_REFERENCE,
        linestyle="--",
        linewidth=1.5,
        alpha=0.8,
        label=f"Constraint ({FWKO_CONSTRAINT:.0f}°C)",
    )

    # Shade violations of the constraint
    ax.fill_between(
        df_recent.index,
        df_recent["FWKO_Temp_2d"],
        FWKO_CONSTRAINT,
        where=(df_recent["FWKO_Temp_2d"] < FWKO_CONSTRAINT),
        color=COLOR_VIOLATION,
        alpha=0.10,
        interpolate=True,
    )

    # ---- Mark the last maintenance event, labeled in the legend ----
    if last_event is not None:
        ev_label = (
            f"{last_event['exchanger']} "
            f"{last_event['event'].replace('_', ' ')} "
            f"({last_event['date']:%b %d})"
        )
        ax.axvline(
            last_event["date"],
            color=COLOR_REFERENCE,
            linestyle=":",
            linewidth=1.5,
            alpha=0.8,
            label=ev_label,
            zorder=1,
        )

    # ---- Boiler header temp — 2-day rolling average (headline series only) ----
    ax2 = ax.twinx()
    ax2.plot(
        df_recent.index,
        df_recent["TIT_5603_2d"],
        color=COLOR_BOILER,
        linewidth=2.5,
        solid_capstyle="round",
        label="Boiler Inlet Header Temp (2-Day Avg)",
    )
    ax2.set_ylabel("Boiler Inlet Header Temp (°C)", fontsize=10.5, color=COLOR_BOILER)
    ax2.tick_params(
        axis="y",
        labelsize=9.5,
        labelcolor=COLOR_BOILER,
        color="#cccccc",
    )
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_color("#cccccc")
    ax2.spines["left"].set_visible(False)

    # ---- Styling (primary axis) ----
    ax.set_title(
        "FWKO Temperature vs. Boiler Temperature",
        fontsize=14,
        fontweight="bold",
        loc="left",
    )
    ax.set_title(
        "Since last maintenance event",
        fontsize=10,
        color="#666666",
        loc="right",
    )
    ax.set_ylabel("FWKO Temperature (°C)", fontsize=10.5, color=COLOR_FWKO)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#cccccc")
    ax.spines["bottom"].set_color("#cccccc")
    ax.grid(alpha=0.3, linewidth=0.6)
    ax.tick_params(axis="y", labelsize=9.5, labelcolor=COLOR_FWKO, color="#cccccc")
    ax.tick_params(axis="x", labelsize=9.5, color="#cccccc")

    # Day-level ticks (span is dynamic, so thin out ticks if the window is long)
    span_days = (df_recent.index.max() - df_recent.index.min()).days
    locator_interval = max(1, span_days // 14)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=locator_interval))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

    ax.margins(x=0.01)

    # ---- Combined legend (primary + secondary axis handles) ----
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(
        lines1 + lines2,
        labels1 + labels2,
        frameon=False,
        fontsize=9.5,
        loc="upper left",
        bbox_to_anchor=(0, 1.02),
    )

    fig.tight_layout(rect=[0, 0, 1, 0.93])

    return fig
