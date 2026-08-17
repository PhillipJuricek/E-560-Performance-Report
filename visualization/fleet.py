import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from config import (
    EXCHANGERS,
    EXCHANGER_COLORS
)

def fleet_rntp_plot(df):

    fig, ax = plt.subplots(
        figsize=(18,6)
    )


    for x in EXCHANGERS:

        rntp_online = (
            df[f"RNTP_{x}"]
            .where(
                df[f"{x}_Online"]
            )
        )


        rntp_smoothed = (
            rntp_online
            .set_axis(df["datetime"])
            .rolling(
                "1D",
                min_periods=1
            )
            .mean()
        )


        ax.plot(

            df["datetime"],

            rntp_smoothed.values,

            color=EXCHANGER_COLORS[x],

            linewidth=1.3,

            alpha=0.85,

            label=x
        )


    ax.axhline(
        1.0,
        linestyle="--",
        color="black",
        linewidth=1,
        alpha=0.7,
        label="Fleet Median"
    )


    ax.set_xlabel(
        "Date",
        fontsize=12
    )

    ax.set_ylabel(
        "Relative Normalized Thermal Performance",
        fontsize=12
    )


    ax.set_title(
        "Heat Exchanger Fleet Thermal Performance — RNTP (Online Only)",
        fontsize=15,
        fontweight="bold",
        loc="left"
    )


    ax.set_ylim(
        -1,
        15
    )


    ax.xaxis.set_major_locator(
        mdates.DayLocator(interval=7)
    )

    ax.xaxis.set_major_formatter(
        mdates.DateFormatter("%d %b")
    )


    ax.tick_params(
        axis="x",
        rotation=30
    )


    ax.legend(
        loc="upper right",
        frameon=False,
        ncol=7,
        fontsize=10
    )


    ax.grid(
        alpha=0.3
    )


    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


    fig.tight_layout()


    return fig

def fleet_rri_plot(df):

    fig, ax = plt.subplots(
        figsize=(18,6)
    )


    for x in EXCHANGERS:

        rri_online = (
            df[f"{x}_RRI"]
            .where(
                df[f"{x}_Online"]
            )
        )


        ax.plot(

            df["datetime"],

            rri_online,

            color=EXCHANGER_COLORS[x],

            linewidth=1.3,

            alpha=0.85,

            label=x
        )


    ax.axhline(
        1.0,
        linestyle="--",
        color="black",
        linewidth=1,
        alpha=0.7,
        label="Fleet Median"
    )


    ax.set_xlabel(
        "Date",
        fontsize=12
    )


    ax.set_ylabel(
        "Relative Restriction Index",
        fontsize=12
    )


    ax.set_title(
        "Heat Exchanger Fleet Hydraulic/Restrictive Performance — RRI (Online Only)",
        fontsize=15,
        fontweight="bold",
        loc="left"
    )


    ax.xaxis.set_major_locator(
        mdates.DayLocator(interval=7)
    )

    ax.xaxis.set_major_formatter(
        mdates.DateFormatter("%d %b")
    )


    ax.tick_params(
        axis="x",
        rotation=30
    )


    ax.legend(
        loc="upper right",
        frameon=False,
        ncol=7,
        fontsize=10
    )


    ax.grid(
        alpha=0.3
    )


    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


    fig.tight_layout()


    return fig
