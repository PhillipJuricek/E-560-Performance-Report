import pandas as pd

from config import (
    EXCHANGERS,
    LOOKBACK_DAYS,
    MIN_ONLINE_STREAK_DAYS,
)


def calculate_7_day_average(df, column, online_column=None):
    """
    Calculate average value over the most recent LOOKBACK_DAYS.

    If online_column is given, only rows where the exchanger is online
    are included in the average.
    """
    cutoff = (
        df["datetime"].max()
        -
        pd.Timedelta(days=LOOKBACK_DAYS)
    )

    recent = df[df["datetime"] >= cutoff]

    if online_column is not None:
        recent = recent[recent[online_column]]

    return recent[column].mean()


def online_coverage(df, online_column):
    """
    Fraction of samples within the lookback window where the exchanger
    is online. Reported for context; not used for eligibility.
    """
    cutoff = (
        df["datetime"].max()
        -
        pd.Timedelta(days=LOOKBACK_DAYS)
    )

    recent = df[df["datetime"] >= cutoff]

    if len(recent) == 0:
        return 0.0

    return float(recent[online_column].mean())


def online_at_end(df, online_column):
    """
    True when the exchanger is online at the last sample (report time).
    It is pointless to rank an exchanger that is not currently in service.
    """
    return bool(df[online_column].iloc[-1])


def fleet_offline_mask(df):
    """
    Boolean series marking samples where NO exchanger is online at once.
    These are treated as plant emergencies / shutdowns rather than a real
    offline period for any single exchanger, so they do not reset streaks.
    """
    return ~df[[f"{x}_Online" for x in EXCHANGERS]].any(axis=1)


def online_streak_days(df, online_column, fleet_offline):
    """
    Days of continuous online operation ending at the last sample.

    A genuine offline break resets the streak, but a fleet-wide outage
    (every exchanger down simultaneously) is treated as still-online, so
    a plant emergency / shutdown does not penalize an otherwise healthy
    exchanger.
    """
    streak_online = df[online_column] | fleet_offline

    times = df["datetime"]

    last_break = times[~streak_online].max()

    if pd.isna(last_break):
        # Never genuinely offline: the streak spans the whole dataset
        span = times.max() - times.min()
    else:
        span = times.max() - last_break

    return span.total_seconds() / 86400


def thermal_ranking(df):
    """
    Rank exchangers based on Relative Normalized Thermal Performance.

    Higher RNTP = better thermal performance.

    An exchanger is eligible only when it is online at the report time,
    has been online continuously for more than MIN_ONLINE_STREAK_DAYS days
    (fleet-wide outages exempt), and has valid RNTP data.
    """
    fleet_offline = fleet_offline_mask(df)

    results = []

    for x in EXCHANGERS:

        online_column = f"{x}_Online"

        avg_rntp = calculate_7_day_average(
            df,
            f"RNTP_{x}",
            online_column,
        )

        coverage = online_coverage(df, online_column)

        online_now = online_at_end(df, online_column)

        streak_days = online_streak_days(
            df,
            online_column,
            fleet_offline,
        )

        eligible = (
            online_now
            and streak_days > MIN_ONLINE_STREAK_DAYS
            and avg_rntp is not None
            and not pd.isna(avg_rntp)
        )

        results.append({
            "exchanger": x,
            "RNTP": float(round(avg_rntp, 3)) if eligible else None,
            "eligible": bool(eligible),
            "online_now": online_now,
            "online_streak_days": round(streak_days, 2),
            "online_coverage": round(coverage, 3),
        })

    ranked = sorted(
        [r for r in results if r["eligible"]],
        key=lambda r: r["RNTP"],
    )

    return {
        "worst": ranked[0] if ranked else None,
        "best": ranked[-1] if ranked else None,
        "ranked": ranked,
        "ranking": results,
    }


def hydraulic_ranking(df):
    """
    Rank exchangers based on Relative Restriction Index.

    Higher RRI = worse hydraulic restriction.

    An exchanger is eligible only when it is online at the report time,
    has been online continuously for more than MIN_ONLINE_STREAK_DAYS days
    (fleet-wide outages exempt), and has valid RRI data.
    """
    fleet_offline = fleet_offline_mask(df)

    results = []

    for x in EXCHANGERS:

        online_column = f"{x}_Online"

        avg_rri = calculate_7_day_average(
            df,
            f"{x}_RRI",
            online_column,
        )

        coverage = online_coverage(df, online_column)

        online_now = online_at_end(df, online_column)

        streak_days = online_streak_days(
            df,
            online_column,
            fleet_offline,
        )

        eligible = (
            online_now
            and streak_days > MIN_ONLINE_STREAK_DAYS
            and avg_rri is not None
            and not pd.isna(avg_rri)
        )

        results.append({
            "exchanger": x,
            "RRI": float(round(avg_rri, 3)) if eligible else None,
            "eligible": bool(eligible),
            "online_now": online_now,
            "online_streak_days": round(streak_days, 2),
            "online_coverage": round(coverage, 3),
        })

    ranked = sorted(
        [r for r in results if r["eligible"]],
        key=lambda r: r["RRI"],
    )

    return {
        "worst": ranked[-1] if ranked else None,
        "best": ranked[0] if ranked else None,
        "ranked": ranked,
        "ranking": results,
    }


def build_rankings(df):
    return {
        "thermal": thermal_ranking(df),
        "hydraulic": hydraulic_ranking(df),
    }
