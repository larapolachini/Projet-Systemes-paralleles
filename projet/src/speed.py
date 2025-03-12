import pandas as pd
import matplotlib.pyplot as plt

# Tu mets ici les résultats de tes tests
resultats = {
    1: "simulation_results.txt",
    2: "simulation_2threads.txt",
    4: "simulation_4threads.txt",
    8: "simulation_8threads.txt",
}

def lire_resultats(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()

    data_lines = []
    for line in lines:
        if line.strip() and line[0].isdigit():
            data_lines.append(line.strip().split())

    df = pd.DataFrame(data_lines, columns=["TimeStep", "UpdateTime (ms)", "DisplayTime (ms)", "TotalTime (ms)"])
    df["UpdateTime (ms)"] = df["UpdateTime (ms)"].astype(float)
    df["TotalTime (ms)"] = df["TotalTime (ms)"].astype(float)
    return df

# Sauvegarde des moyennes
moyennes_total = {}
moyennes_update = {}

for threads, filepath in resultats.items():
    df = lire_resultats(filepath)
    
    # Moyenne sur tous les time steps
    moy_total = df["TotalTime (ms)"].mean()
    moy_update = df["UpdateTime (ms)"].mean()
    
    moyennes_total[threads] = moy_total
    moyennes_update[threads] = moy_update

# Temps séquentiels pour normalisation (1 thread)
T1_total = moyennes_total[1]
T1_update = moyennes_update[1]

# Calcul speedup
speedup_total = {p: T1_total / t for p, t in moyennes_total.items()}
speedup_update = {p: T1_update / t for p, t in moyennes_update.items()}

# Affichage des speedups dans le terminal
print("\n# Threads\tSpeedup Total\tSpeedup Update")
for p in resultats.keys():
    print(f"{p}\t\t{speedup_total[p]:.2f}x\t\t{speedup_update[p]:.2f}x")

# ============================
# COURBE 1 : Speedup Total
# ============================
plt.figure(figsize=(10, 5))
plt.plot(speedup_total.keys(), speedup_total.values(), marker='o', label='Speedup Global')
plt.plot(speedup_update.keys(), speedup_update.values(), marker='s', label='Speedup Update')

plt.title("Accélération en fonction du nombre de threads")
plt.xlabel("Nombre de Threads")
plt.ylabel("Speedup (x)")
plt.legend()
plt.grid(True)

plt.savefig("speedup_threads.png")
plt.show()
