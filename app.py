import matplotlib.pyplot as plt

from config import EXCHANGERS

from analysis.preprocessing import preprocess_data
from analysis.metrics import calculate_metrics
from analysis.rankings import build_rankings
from analysis.cycle_analysis import build_cycle_comparison

from visualization.fleet import fleet_rntp_plot, fleet_rri_plot
from visualization.cycle_plots import plot_cycle_comparison



def run_analysis():

    print("Loading and preprocessing data...")

    df = preprocess_data()


    print("Calculating exchanger metrics...")

    df = calculate_metrics(
        df
    )


    print("Building exchanger rankings...")

    rankings = build_rankings(
        df
    )


    print("Building cycle comparisons...")

    cycles = build_cycle_comparison(
        df
    )


    return {

        "data": df,

        "rankings": rankings,

        "cycles": cycles

    }



if __name__ == "__main__":


    results = run_analysis()


    print("\n==============================")
    print("THERMAL PERFORMANCE")
    print("==============================")

    print(
        results["rankings"]["thermal"]
    )


    print("\n==============================")
    print("HYDRAULIC PERFORMANCE")
    print("==============================")

    print(
        results["rankings"]["hydraulic"]
    )



    print("\nGenerating RNTP plot...")

    fig = fleet_rntp_plot(
        results["data"]
    )

    plt.show()



    print("\nGenerating RRI plot...")

    fig = fleet_rri_plot(
        results["data"]
    )

    plt.show()



    print("\nGenerating cycle plots...")


    for exchanger in EXCHANGERS:

        print(
            f"Generating exchanger {exchanger}"
        )

        fig = plot_cycle_comparison(results["data"], 
            results["cycles"],
            exchanger
        )

        plt.show()
