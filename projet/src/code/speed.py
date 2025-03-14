import pandas as pd
import matplotlib.pyplot as plt
import glob
import re
import numpy as np

# Rechercher tous les fichiers CSV commençant par « resultats_temps »
csv_files = glob.glob("/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Tableau/resultats_temps*.csv")

if not csv_files:
    print("Nenhum arquivo CSV encontrado.")
    exit()

# Identifiez le fichier de référence (nous supposons qu'il s'agit de "resultats_temps.csv")
baseline_filename = "/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Tableau/resultats_temps.csv"
if baseline_filename not in csv_files:
    print("Arquivo baseline não encontrado (resultats_temps.csv)")
    exit()

# Charger la ligne de base (1 thread)
baseline_df = pd.read_csv(baseline_filename, sep=";")
baseline_df.columns = [col.strip() for col in baseline_df.columns]

# Choisissez l'axe des x : s'il existe, "Iteration" l'utilise ; sinon "TimeStep"
x_column = "Iteration" if "Iteration" in baseline_df.columns else "TimeStep"
baseline_df = baseline_df.reset_index(drop=True)
baseline_total = baseline_df["Temps_total(ms)"]

# Stocker les dataframes dans un dictionnaire : threads -> dataframe
dataframes = {1: baseline_df}

# Chargez les fichiers restants et extrayez le nombre de threads à partir du nom
for file in csv_files:
    if file == baseline_filename:
        continue
    match = re.search(r"_(\d+)_threads", file)
    if match:
        threads = int(match.group(1))
    else:
        continue
    df = pd.read_csv(file, sep=";")
    df.columns = [col.strip() for col in df.columns]
    df = df.reset_index(drop=True)
    dataframes[threads] = df

# Calculer l'accélération par itération pour chaque nombre de threads
speedups = {}
for threads, df in dataframes.items():
    # Aligner la série en utilisant le plus petit nombre d'itérations
    n = min(len(baseline_total), len(df["Temps_total(ms)"]))
    # Calculer l'accélération pour les itérations courantes
    speedup_series = baseline_total.iloc[:n].reset_index(drop=True) / \
                     df["Temps_total(ms)"].iloc[:n].reset_index(drop=True)
    # Lisser la série avec une moyenne mobile avec une fenêtre de 10 itérations
    speedup_smoothed = speedup_series.rolling(window=10, center=True, min_periods=1).mean()
    speedups[threads] = speedup_smoothed

# GRAPHIQUE 1 : Accélération par rapport à l'itération/pas de temps ajusté à un polynôme (degré 3) pour chaque nombre de threads
degree = 3  # degré du polynôme à ajuster
for threads, s in sorted(speedups.items()):
    n = len(s)
    # Alignez les données à l'aide de l'axe des x de base et convertissez-les en un tableau numérique
    x = baseline_df[x_column].iloc[:n].reset_index(drop=True).values.astype(float)
    y = s.values.astype(float)
    # Ajuster un polynôme de degré "degré" aux données
    coeffs = np.polyfit(x, y, deg=degree)
    poly_fn = np.poly1d(coeffs)
    # Générer des points pour tracer la courbe polynomiale lisse
    x_fit = np.linspace(x.min(), x.max(), 500)
    y_fit = poly_fn(x_fit)
    plt.plot(x_fit, y_fit, linewidth=2, label=f'{threads} thread(s) (ajuste polinomial)')

plt.xlabel(x_column)
plt.ylabel("Speedup (baseline / tempo)")
plt.title("Speedup por Iteração/Timestep (Ajuste Polinomial) para cada Quantidade de Threads")
plt.legend()
plt.grid(True)
import os
folder = "/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Imagens"
if not os.path.exists(folder):
    os.makedirs(folder)
plt.savefig(os.path.join(folder, "SpeedupxTimeStep"))
plt.show() 

# GRAPHIQUE 2 : Accélération moyenne en fonction du nombre de threads (aucun ajustement, car il s'agit d'une valeur unique par thread)
avg_speedups = {threads: np.mean(s) for threads, s in speedups.items()}
threads_list = sorted(avg_speedups.keys())
avg_values = [avg_speedups[t] for t in threads_list]

plt.figure(figsize=(10, 6), dpi=150)
plt.plot(threads_list, avg_values, marker='o', linestyle='-', label='Speedup Médio')
plt.xlabel("Número de Threads")
plt.ylabel("Speedup Médio")
plt.title("Speedup Médio versus Número de Threads")
plt.xticks(threads_list)
plt.legend()
plt.grid(True)
import os
folder = "/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Imagens"
if not os.path.exists(folder):
    os.makedirs(folder)
plt.savefig(os.path.join(folder, "_rolling_no_first.png"))
plt.show() 