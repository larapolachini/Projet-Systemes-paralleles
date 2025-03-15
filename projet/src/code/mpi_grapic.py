import pandas as pd
import matplotlib.pyplot as plt
import os

# Répertoire de fichiers
base_dir = "/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Tableau"
#base_dir = "/home/larapolachini/Projet-Systemes-paralleles/projet/src/Tableau"

# Fichiers (ajuster si les noms sont différents)
arquivos = {
    "seq": os.path.join(base_dir, "resultats_mpi_4"),
    2: os.path.join(base_dir, "resultats_temps_MPI_4_threads_2.csv"),
    4: os.path.join(base_dir, "resultats_temps_MPI_4_threads_4.csv"),
    8: os.path.join(base_dir, "resultats_temps_MPI_4_threads_8.csv")
}

# 1. Temps de référence séquentiel
df_seq = pd.read_csv(arquivos["seq"], sep=';', engine='python')

# Prenons la moyenne du temps séquentiel total
tempo_seq_medio = df_seq["Temps_total(ms)"].mean()
print(f"Temps séquentiel moyen: {tempo_seq_medio:.3f} ms")

# 2. Calculer l'accélération pour chaque configuration parallèle
threads = []
speedups = []

for n_threads, filepath in arquivos.items():
    if n_threads == "seq":
        continue

    df_paralelo = pd.read_csv(filepath, sep=';', engine='python')
    tempo_paralelo_medio = df_paralelo["Temps_total(ms)"].mean()

    speedup = tempo_seq_medio / tempo_paralelo_medio

    print(f"{n_threads} threads -> Temps moyen parallèle: {tempo_paralelo_medio:.3f} ms | Speedup: {speedup:.2f}")

    threads.append(n_threads)
    speedups.append(speedup)

# 3. Plot Speedup x Threads
plt.figure(figsize=(8, 6))
plt.plot(threads, speedups, marker='o', linestyle='-', label='Speedup obtenue')

plt.xlabel('Nombre de threads')
plt.ylabel('Speedup')
plt.title('Speedup x Nombre de threads (OMP avec MPI 4)')
plt.grid(True)
plt.legend()
plt.xticks(threads)
plt.show()
