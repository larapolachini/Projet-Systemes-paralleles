import pandas as pd
import matplotlib.pyplot as plt
import glob
import re
import numpy as np

# Procura por todos os arquivos CSV que começam com "resultats_temps"
csv_files = glob.glob("/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Tableau/resultats_temps*.csv")

if not csv_files:
    print("Nenhum arquivo CSV encontrado.")
    exit()

# Identifica o arquivo baseline (supomos que seja "resultats_temps.csv")
baseline_filename = "/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Tableau/resultats_temps.csv"
if baseline_filename not in csv_files:
    print("Arquivo baseline não encontrado (resultats_temps.csv)")
    exit()

# Carrega o baseline (1 thread)
baseline_df = pd.read_csv(baseline_filename, sep=";")
baseline_df.columns = [col.strip() for col in baseline_df.columns]
# Escolhe o eixo x: se existir "Iteration" usa; caso contrário, "TimeStep"
x_column = "Iteration" if "Iteration" in baseline_df.columns else "TimeStep"
baseline_df = baseline_df.reset_index(drop=True)
baseline_total = baseline_df["Temps_total(ms)"]

# Armazena os dataframes num dicionário: threads -> dataframe
dataframes = {1: baseline_df}

# Carrega os demais arquivos e extrai o número de threads a partir do nome
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

# Calcula o speedup por iteração para cada quantidade de thread
speedups = {}
for threads, df in dataframes.items():
    # Alinha as séries usando o menor número de iterações
    n = min(len(baseline_total), len(df["Temps_total(ms)"]))
    # Calcula o speedup para as iterações em comum
    speedup_series = baseline_total.iloc[:n].reset_index(drop=True) / \
                     df["Temps_total(ms)"].iloc[:n].reset_index(drop=True)
    # Suaviza a série com média móvel (rolling average) com janela de 10 iterações
    speedup_smoothed = speedup_series.rolling(window=10, center=True, min_periods=1).mean()
    speedups[threads] = speedup_smoothed

# GRÁFICO 1: Speedup versus iteração/timestep ajustado a um polinômio (grau 3) para cada quantidade de thread
degree = 3  # grau do polinômio para ajuste
for threads, s in sorted(speedups.items()):
    n = len(s)
    # Alinha os dados usando o eixo x do baseline e converte para array numérico
    x = baseline_df[x_column].iloc[:n].reset_index(drop=True).values.astype(float)
    y = s.values.astype(float)
    # Ajusta um polinômio de grau "degree" aos dados
    coeffs = np.polyfit(x, y, deg=degree)
    poly_fn = np.poly1d(coeffs)
    # Gera pontos para plotar a curva polinomial suave
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

# GRÁFICO 2: Speedup médio versus número de threads (sem ajuste, pois é um único valor por thread)
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