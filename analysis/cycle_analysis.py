import pandas as pd

from config import EXCHANGERS


def get_cycle_data(df, exchanger, cycle_number):
    """
    Extract RNTP history and operating duration
    for a specific exchanger cycle.
    """

    cycle_df = df[
        df[f"{exchanger}_OperatingCycle"] == cycle_number
    ].copy()

    if cycle_df.empty:
        return None


    return {

        "datetime":
            cycle_df["datetime"].tolist(),

        "RNTP":
            cycle_df[f"RNTP_{exchanger}"].tolist(),

        "days":
            float(
                cycle_df[f"{exchanger}_DaysInOperation"].max()
            )

    }



def build_cycle_comparison(df):
    """
    Build current vs previous cycle comparison
    for every exchanger.

    Current cycle:
        OperatingCycle == 1

    Previous cycle:
        OperatingCycle == 2
    """

    cycle_comparison = {}


    for x in EXCHANGERS:

        cycle_comparison[x] = {

            "current":
                get_cycle_data(
                    df,
                    x,
                    1
                ),

            "previous":
                get_cycle_data(
                    df,
                    x,
                    2
                )

        }


    return cycle_comparison
