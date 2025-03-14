import pandas as pd
import matplotlib.pyplot as plt
import os

# Diretório dos arquivos
base_dir = "/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Tableau"

# Arquivos (ajuste se os nomes forem diferentes)
arquivos = {
    "seq": os.path.join(base_dir, "resultats_temps_MPI_4_seq"),
    2: os.path.join(base_dir, "resultats_temps_MPI_4_threads_2.csv"),
    4: os.path.join(base_dir, "resultats_temps_MPI_4_threads_4.csv"),
    8: os.path.join(base_dir, "resultats_temps_MPI_4_threads_8.csv")
}

# 1. Tempo de referência do sequencial
df_seq = pd.read_csv(arquivos["seq"], sep=';', engine='python')

# Vamos pegar a média do tempo total sequencial
tempo_seq_medio = df_seq["Temps_total(ms)"].mean()
print(f"Tempo sequencial médio: {tempo_seq_medio:.3f} ms")

# 2. Calcular speedup para cada configuração paralela
threads = []
speedups = []

for n_threads, filepath in arquivos.items():
    if n_threads == "seq":
        continue

    df_paralelo = pd.read_csv(filepath, sep=';', engine='python')
    tempo_paralelo_medio = df_paralelo["Temps_total(ms)"].mean()

    speedup = tempo_seq_medio / tempo_paralelo_medio

    print(f"{n_threads} threads -> Tempo médio paralelo: {tempo_paralelo_medio:.3f} ms | Speedup: {speedup:.2f}")

    threads.append(n_threads)
    speedups.append(speedup)

# 3. Plotando Speedup x Threads
plt.figure(figsize=(8, 6))
plt.plot(threads, speedups, marker='o', linestyle='-', label='Speedup obtido')

plt.xlabel('Número de Threads')
plt.ylabel('Speedup')
plt.title('Speedup x Número de Threads (OMP com MPI 4)')
plt.grid(True)
plt.legend()
plt.xticks(threads)
plt.show()
