import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from numpy.polynomial.polynomial import Polynomial

# Chemin du dossier de fichiers
base_dir = "/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Tableau"
#base_dir = "/home/larapolachini/Projet-Systemes-paralleles/projet/src/Tableau"

# Fichiers avec résultats
files = {
    "Sequencial": f"{base_dir}/results_mpi_1",
    "2 Threads": f"{base_dir}/resultats_temps_MPI_1_threads_2.csv",
    "4 Threads": f"{base_dir}/resultats_temps_MPI_1_threads_4.csv",
    "8 Threads": f"{base_dir}/resultats_temps_MPI_1_threads_8.csv"
}

# Fonction permettant de tracer le temps total par itération avec ajustement polynomial (degré 2)
def plot_tempo_iteracao(df, titulo):
    # Données et temps d'itération
    iterations = df["Iteration"]
    tempos_totais = df["Temps_total(ms)"]

    # Ajustement d'un polynôme de degré 2
    ajuste_poly = Polynomial.fit(iterations, tempos_totais, deg=2).convert()
    coefs = ajuste_poly.coef
    p = np.poly1d(coefs[::-1])  # Inverser les coefficients pour np.poly1d

    # Générer des points pour la courbe d'ajustement
    x_fit = np.linspace(iterations.min(), iterations.max(), 500)
    y_fit = p(x_fit)

    # Tracé du graphique
    plt.figure(figsize=(8, 6))
    plt.scatter(iterations, tempos_totais, color='blue', alpha=0.5, label="Dados Reais")
    plt.plot(x_fit, y_fit, color='red', linestyle='--', label="Ajuste Polinomial (grau 2)")
    
    plt.title(f"Tempo Total por Iteração - {titulo}")
    plt.xlabel("Iteração")
    plt.ylabel("Tempo Total (ms)")
    plt.legend()
    plt.ylim(0,4)
    plt.grid(True)
    plt.show()

# Charger les données et générer les graphiques
for titulo, filepath in files.items():
    # Lire le CSV (séparateur ";")
    df = pd.read_csv(filepath, sep=';', engine='python')
    
    # Générer le graphique avec ajustement polynomial
    plot_tempo_iteracao(df, titulo)


# Chemin du dossier de fichiers
base_dir = "/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Tableau"

# Fichiers avec résultats
files = {
    "Sequencial": f"{base_dir}/resultats_temps_MPI_1_seq",
    "2 Threads": f"{base_dir}/resultats_temps_MPI_1_threads_2.csv",
    "4 Threads": f"{base_dir}/resultats_temps_MPI_1_threads_4.csv",
    "8 Threads": f"{base_dir}/resultats_temps_MPI_1_threads_8.csv"
}

# Différentes couleurs pour chaque ligne du graphique
colors = {
    "Sequencial": "blue",
    "2 Threads": "green",
    "4 Threads": "orange",
    "8 Threads": "red"
}

# Figure unique avec tous les ajustements polynomiaux
plt.figure(figsize=(10, 7))

# Boucle pour traiter chaque ensemble de données
for titulo, filepath in files.items():
    # Lire le CSV (séparateur ";")
    df = pd.read_csv(filepath, sep=';', engine='python')

    # Données d'itération et temps total
    iterations = df["Iteration"]
    tempos_totais = df["Temps_total(ms)"]

    # Ajustement d'un polynôme de degré 2
    ajuste_poly = Polynomial.fit(iterations, tempos_totais, deg=2).convert()
    coefs = ajuste_poly.coef
    p = np.poly1d(coefs[::-1])

    # Générer des points pour la courbe
    x_fit = np.linspace(iterations.min(), iterations.max(), 500)
    y_fit = p(x_fit)

    # Tracé de la courbe d'ajustement
    plt.plot(x_fit, y_fit, linestyle='--', color=colors[titulo], label=f"{titulo} (ajuste grau 2)")

# Configuration du graphique
plt.title("Comparação: Tempo Total por Iteração com Ajuste Polinomial")
plt.xlabel("Iteração")
plt.ylabel("Tempo Total (ms)")
plt.legend()
plt.ylim(0,4)
plt.grid(True)
plt.show()
