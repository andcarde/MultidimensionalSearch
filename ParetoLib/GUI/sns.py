import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def plot_csv(csvfile):
    # Read CSV file
    names = ["Time", "Signal"]
    df_signal = pd.read_csv(csvfile, names=names)

    # Plot the responses for different events and regions
    sns.set_theme(style="darkgrid")
    fig = sns.lineplot(x="Time",
                       y="Signal",
                       data=df_signal)
    plt.show()


if __name__ == '__main__':
    csvfile = "../../Tests/Oracle/OracleSTLe/2D/stabilization/stabilization.csv"
    # csvfile = sys.argv[1]
    plot_csv(csvfile)
