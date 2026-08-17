import matplotlib.pyplot as plt

from config import EXCHANGER_COLORS


def _get_cycle_maintenance(df, exchanger, cycle):
    """
    Returns the maintenance event that immediately preceded an operating cycle.
    """
    cycle_col = f"{exchanger}_OperatingCycle"
    clean_col = f"{exchanger}_Clean"
    rebuild_col = f"{exchanger}_Rebuild"

    cycle_rows = df[df[cycle_col] == cycle]

    if cycle_rows.empty:
        return None

    start_idx = cycle_rows.index[0]

    prior = df.loc[:start_idx]

    clean_idx = prior.index[prior[clean_col]]
    rebuild_idx = prior.index[prior[rebuild_col]]

    last_clean = clean_idx.max() if len(clean_idx) else None
    last_rebuild = rebuild_idx.max() if len(rebuild_idx) else None

    if last_clean is None and last_rebuild is None:
        return None

    if last_rebuild is None:
        return "Clean"

    if last_clean is None:
        return "Rebuild"

    return "Clean" if last_clean > last_rebuild else "Rebuild"


def plot_cycle_comparison(df, cycle_data, exchanger):

    current = cycle_data[exchanger]["current"]
    previous = cycle_data[exchanger]["previous"]
    color = EXCHANGER_COLORS[exchanger]

    fig, ax = plt.subplots(figsize=(12, 5))

    def to_days(datetimes):
        t0 = datetimes.iloc[0] if hasattr(datetimes, "iloc") else datetimes[0]
        return [(t - t0).total_seconds() / 86400 for t in datetimes]

    # Maintenance events
    current_event = _get_cycle_maintenance(df, exchanger, 1)
    previous_event = _get_cycle_maintenance(df, exchanger, 2)

    current_label = f"Current Cycle ({current['days']:.1f} days)"
    if current_event:
        current_label += f" • After {current_event}"

    if previous is not None:
        previous_label = f"Previous Cycle ({previous['days']:.1f} days)"
        if previous_event:
            previous_label += f" • After {previous_event}"

    # --------------------------
    # Previous cycle
    # --------------------------
    if previous is not None and len(previous["datetime"]) > 0:

        previous_days = to_days(previous["datetime"])

        ax.plot(
            previous_days,
            previous["RNTP"],
            color=color,
            linewidth=2,
            linestyle="--",
            alpha=0.45,
            zorder=2,
            label=previous_label,
        )

    else:
        print(f"[{exchanger}] no previous cycle data")

    # --------------------------
    # Current cycle
    # --------------------------
    if current is not None and len(current["datetime"]) > 0:

        current_days = to_days(current["datetime"])

        ax.plot(
            current_days,
            current["RNTP"],
            color=color,
            linewidth=3,
            alpha=1.0,
            zorder=3,
            label=current_label,
        )

    else:
        print(f"[{exchanger}] no current cycle data")

    # --------------------------
    # Formatting
    # --------------------------
    ax.axhline(
        1.0,
        linestyle="--",
        color="black",
        linewidth=1,
        alpha=0.6,
        label="Fleet Median",
        zorder=1,
    )

    ax.set_xlabel("Days Since Maintenance")
    ax.set_ylabel("Relative Normalized Thermal Performance (RNTP)")
    ax.set_title(
        f"E-560 Exchanger {exchanger} — Current vs Previous Cycle",
        fontsize=14,
        fontweight="bold",
        loc="left",
    )

    ax.legend(frameon=False)
    ax.grid(alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()

    return fig
