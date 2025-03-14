import pandas as pd
import matplotlib.pyplot as plt
import glob
import re
import numpy as np
from scipy.signal import savgol_filter

csv_files = glob.glob("/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Tableau/resultats_temps*.csv")
if not csv_files:
    print("Aucun fichier CSV trouvé.")
    exit()

dataframes = {}
for file in csv_files:
    match = re.search(r"_(\d+)_threads", file)
    threads = int(match.group(1)) if match else 1
    df = pd.read_csv(file, sep=";")
    df.columns = [col.strip() for col in df.columns]
    df = df.reset_index(drop=True)
    dataframes[threads] = df

sample_df = list(dataframes.values())[0]
x_column = "Iteration" if "Iteration" in sample_df.columns else "TimeStep"
min_length = min(len(df) for df in dataframes.values())

window_length = 31
polyorder = 3

fig, axs = plt.subplots(2, 1)
for threads, df in sorted(dataframes.items()):
    x = df[x_column].iloc[:min_length].reset_index(drop=True).astype(float)
    total_series = df["Temps_total(ms)"].iloc[:min_length].reset_index(drop=True).astype(float)
    avancement_series = df["Temps_avancement(ms)"].iloc[:min_length].reset_index(drop=True).astype(float)
    total_smoothed = savgol_filter(total_series, window_length=window_length, polyorder=polyorder)
    avancement_smoothed = savgol_filter(avancement_series, window_length=window_length, polyorder=polyorder)
    axs[0].plot(x, total_smoothed, label=f'{threads} thread(s)')
    axs[1].plot(x, avancement_smoothed, label=f'{threads} thread(s)')

axs[0].set_xlabel(x_column)
axs[0].set_ylabel("Tempo Total (ms)")
axs[0].set_title("Tempo Total (ms) vs " + x_column + " (suavizado com Savitzky–Golay)")
axs[0].legend()
axs[0].set_ylim(0, 10)
axs[0].grid(True)

axs[1].set_xlabel(x_column)
axs[1].set_ylabel("Tempo de Avancement (ms)")
axs[1].set_title("Tempo de Avancement (ms) vs " + x_column + " (suavizado com Savitzky–Golay)")
axs[1].legend()
axs[1].grid(True)

plt.tight_layout()

import os
folder = "/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Imagens"
if not os.path.exists(folder):
    os.makedirs(folder)
plt.savefig(os.path.join(folder, "comparison_total_avancement_savgol.png"))

plt.show()
