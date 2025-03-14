import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from numpy.polynomial.polynomial import Polynomial

# Caminho da pasta dos arquivos
base_dir = "/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Tableau"

# Arquivos com os resultados
files = {
    "Sequencial": f"{base_dir}/resultats_temps_MPI_1_seq",
    "2 Threads": f"{base_dir}/resultats_temps_MPI_1_threads_2.csv",
    "4 Threads": f"{base_dir}/resultats_temps_MPI_1_threads_4.csv",
    "8 Threads": f"{base_dir}/resultats_temps_MPI_1_threads_8.csv"
}

# Função para plotar tempo total por iteração com ajuste polinomial (grau 2)
def plot_tempo_iteracao(df, titulo):
    # Dados das iterações e tempos
    iterations = df["Iteration"]
    tempos_totais = df["Temps_total(ms)"]

    # Ajuste polinomial de grau 2
    ajuste_poly = Polynomial.fit(iterations, tempos_totais, deg=2).convert()
    coefs = ajuste_poly.coef
    p = np.poly1d(coefs[::-1])  # Inverter os coeficientes para np.poly1d

    # Gera pontos para a curva de ajuste
    x_fit = np.linspace(iterations.min(), iterations.max(), 500)
    y_fit = p(x_fit)

    # Plot do gráfico
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

# Carrega os dados e gera os gráficos
for titulo, filepath in files.items():
    # Lê o CSV (separador ";")
    df = pd.read_csv(filepath, sep=';', engine='python')
    
    # Gera o gráfico com ajuste polinomial
    plot_tempo_iteracao(df, titulo)


# Caminho da pasta dos arquivos
base_dir = "/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Tableau"

# Arquivos com os resultados
files = {
    "Sequencial": f"{base_dir}/resultats_temps_MPI_1_seq",
    "2 Threads": f"{base_dir}/resultats_temps_MPI_1_threads_2.csv",
    "4 Threads": f"{base_dir}/resultats_temps_MPI_1_threads_4.csv",
    "8 Threads": f"{base_dir}/resultats_temps_MPI_1_threads_8.csv"
}

# Cores diferentes para cada linha no gráfico
colors = {
    "Sequencial": "blue",
    "2 Threads": "green",
    "4 Threads": "orange",
    "8 Threads": "red"
}

# Figura única com todos os ajustes polinomiais
plt.figure(figsize=(10, 7))

# Loop para processar cada conjunto de dados
for titulo, filepath in files.items():
    # Lê o CSV (separador ";")
    df = pd.read_csv(filepath, sep=';', engine='python')

    # Dados de iteração e tempo total
    iterations = df["Iteration"]
    tempos_totais = df["Temps_total(ms)"]

    # Ajuste polinomial de grau 2
    ajuste_poly = Polynomial.fit(iterations, tempos_totais, deg=2).convert()
    coefs = ajuste_poly.coef
    p = np.poly1d(coefs[::-1])

    # Gera pontos para a curva
    x_fit = np.linspace(iterations.min(), iterations.max(), 500)
    y_fit = p(x_fit)

    # Plot da curva de ajuste
    plt.plot(x_fit, y_fit, linestyle='--', color=colors[titulo], label=f"{titulo} (ajuste grau 2)")

# Configuração do gráfico
plt.title("Comparação: Tempo Total por Iteração com Ajuste Polinomial")
plt.xlabel("Iteração")
plt.ylabel("Tempo Total (ms)")
plt.legend()
plt.ylim(0,4)
plt.grid(True)
plt.show()
