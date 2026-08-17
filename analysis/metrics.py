import numpy as np
import pandas as pd

from config import (
    EXCHANGERS,
    ROLLING_WINDOW,
    MIN_FLOW,
    STATE_DEADBAND
)

def estimate_flows(df):

    # -----------------------------------------
    # Calculate total available pump flow
    # -----------------------------------------

    pump_columns = [
        "FIT_550A1_Flow Rate",
        "FIT_550B1_Flow Rate",
        "FIT_550C1_Flow Rate"
    ]

    df["Total_Pump_Flow"] = (
        df[pump_columns]
        .fillna(0)
        .sum(axis=1)
    )


    # -----------------------------------------
    # Initialize exchanger flow dataframe
    # -----------------------------------------

    flow_df = pd.DataFrame(
        np.nan,
        index=df.index,
        columns=[
            f"{x}_Flow"
            for x in EXCHANGERS
        ]
    )


    # -----------------------------------------
    # Estimate exchanger flows
    # -----------------------------------------

    for idx, row in df.iterrows():

        online = [
            x
            for x in EXCHANGERS
            if row[f"{x}_Online"]
        ]


        # No exchangers running
        if len(online) == 0:
            continue


        measured = []
        missing = []


        for x in online:

            flow = row[f"FIT_560{x}1_Flow Rate"]


            if pd.notna(flow) and flow > 0:
                measured.append(x)

            else:
                missing.append(x)



        # -----------------------------------------
        # Case 1:
        # All online exchangers have flow readings
        # -----------------------------------------

        if len(missing) == 0:

            for x in measured:

                flow_df.loc[
                    idx,
                    f"{x}_Flow"
                ] = row[f"FIT_560{x}1_Flow Rate"]



        # -----------------------------------------
        # Case 2:
        # Some exchangers need estimated flow
        # -----------------------------------------

        else:

            measured_sum = sum(
                row[f"FIT_560{x}1_Flow Rate"]
                for x in measured
            )


            remaining_flow = max(
                row["Total_Pump_Flow"] - measured_sum,
                0
            )


            # Keep measured flows

            for x in measured:

                flow_df.loc[
                    idx,
                    f"{x}_Flow"
                ] = row[f"FIT_560{x}1_Flow Rate"]



            # Split remaining flow evenly

            if len(missing) > 0:

                estimated_flow = (
                    remaining_flow / len(missing)
                )

                for x in missing:

                    flow_df.loc[
                        idx,
                        f"{x}_Flow"
                    ] = estimated_flow



    # -----------------------------------------
    # Merge back once
    # -----------------------------------------

    df = pd.concat(
        [
            df,
            flow_df
        ],
        axis=1
    )

    df = df.copy()
    return df

def calculate_temperature_metrics(df):


    for x in EXCHANGERS:


        # Temperature difference

        df[f"TIT_Delta_{x}"] = (
            df[f"TIT_560{x}1"]
            -
            df[f"TIT_560{x}2"]
        )


        # State

        df[f"{x}_State"] = np.where(
            ~df[f"{x}_Online"],
            "OFF",

            np.where(
                df[f"TIT_Delta_{x}"] > STATE_DEADBAND,
                "PRIMARY",

                np.where(
                    df[f"TIT_Delta_{x}"] < -STATE_DEADBAND,
                    "REVERSED",
                    "UNKNOWN"
                )
            )
        )


        df[f"Abs_Delta_{x}"] = (
            df[f"TIT_Delta_{x}"].abs()
        )


        # Rolling delta inside cycle

        df[f"TIT_Delta_{x}_Rolling"] = (
            df.groupby(
                f"{x}_OperatingCycle"
            )[f"TIT_Delta_{x}"]
            .transform(
                lambda s:
                s.rolling(
                    ROLLING_WINDOW,
                    min_periods=1
                )
                .mean()
            )
        )


        # HTI

        df[f"HTI_{x}"] = np.where(

            df[f"{x}_Online"],

            df[f"TIT_Delta_{x}_Rolling"].abs()
            *
            df[f"{x}_Flow"],

            0.0
        )



        # Determine driving force

        inlet = df[f"TIT_560{x}2"].copy()


        reversed_mask = (
            df[f"{x}_State"]
            ==
            "REVERSED"
        )


        inlet.loc[reversed_mask] = (
            df.loc[
                reversed_mask,
                f"TIT_560{x}1"
            ]
        )


        ATD = (
            df["TIT_5603"]
            -
            inlet
        )


        valid = (
            df[f"{x}_Online"]
            &
            ATD.notna()
            &
            (ATD > 0)
        )


        df[f"NHTI_{x}"] = np.nan


        df.loc[valid, f"NHTI_{x}"] = (
            df.loc[valid, f"HTI_{x}"]
            /
            ATD[valid]
        )

    df = df.copy()
    return df

def calculate_relative_thermal_performance(df):


    nhti_columns = [
        f"NHTI_{x}"
        for x in EXCHANGERS
    ]


    fleet_median = (
        df[nhti_columns]
        .median(axis=1)
    )


    for x in EXCHANGERS:

        df[f"RNTP_{x}"] = (
            df[f"NHTI_{x}"]
            /
            fleet_median
        )

    df = df.copy()
    return df

def calculate_restriction_metrics(df):


    for x in EXCHANGERS:


        df[f"{x}_Flow_Rolling"] = (
            df.groupby(
                f"{x}_OperatingCycle"
            )[f"{x}_Flow"]
            .transform(
                lambda s:
                s.rolling(
                    ROLLING_WINDOW,
                    min_periods=6
                )
                .mean()
            )
        )


        valve = (
            df[f"FIC_560{x}1_Data_Control Output"]
            /
            100
        )


        valid = (
            df[f"{x}_Online"]
            &
            (df[f"{x}_Flow_Rolling"] > MIN_FLOW)
        )


        df[f"{x}_RI"] = np.nan


        df.loc[
            valid,
            f"{x}_RI"
        ] = (
            valve[valid]
            /
            df.loc[
                valid,
                f"{x}_Flow_Rolling"
            ]
        )


    ri_columns = [
        f"{x}_RI"
        for x in EXCHANGERS
    ]


    fleet_median = (
        df[ri_columns]
        .median(axis=1)
    )


    for x in EXCHANGERS:

        df[f"{x}_RRI"] = (
            df[f"{x}_RI"]
            /
            fleet_median
        )

    df = df.copy()
    return df

def calculate_metrics(df):

    df = estimate_flows(df)

    df = calculate_temperature_metrics(df)

    df = calculate_relative_thermal_performance(df)

    df = calculate_restriction_metrics(df)

    return df

