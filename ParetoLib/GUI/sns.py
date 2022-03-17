import csv
import seaborn as sns
import numpy as np
import pandas as pd

# Leer fichero en CSV

sns.set_theme(style="darkgrid")
muestra_1= [1, 2]
muestra_2= [2, 3]

signal_np = np.array([muestra_1, muestra_2], np.int32)
signal_df = pd.DataFrame(signal_np, columns=["timepoint", "signal"])

# Plot the responses for different events and regions
sns.lineplot(x="timepoint", y="signal",
             data=signal_np)
             
             
# Plot the responses for different events and regions
sns.lineplot(x="timepoint", y="signal",
             data=signal_df)