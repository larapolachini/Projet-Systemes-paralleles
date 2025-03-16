import pandas as pd
import matplotlib.pyplot as plt
import re

# Função para extrair informações MPI/OMP dos nomes dos arquivos
def extract_mpi_omp(filename):
    pattern = r"results_mpi_(\d+)_omp_(\d+).csv"
    match = re.search(pattern, filename)
    if match:
        mpi = int(match.group(1))
        omp = int(match.group(2))
        return mpi, omp
    return None, None

# Função para ler o CSV ignorando o cabeçalho inicial e pegando só os TimeSteps
def read_simulation_data(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Encontrar a linha onde começam os dados (a que contém "TimeStep")
    for idx, line in enumerate(lines):
        if line.strip().startswith("TimeStep"):
            start_idx = idx
            break

    # Lê a partir desta linha
    df = pd.read_csv(file_path, sep=";", skiprows=start_idx)
    return df

# Lista de arquivos CSV - substitua com o caminho correto se necessário
all_files = [
    "/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Tableau/Tableau_Part3/results_mpi_1_omp_1.csv",
    "/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Tableau/Tableau_Part3/results_mpi_1_omp_2.csv",
    "/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Tableau/Tableau_Part3/results_mpi_1_omp_4.csv",
    "/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Tableau/Tableau_Part3/results_mpi_1_omp_8.csv",
    "/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Tableau/Tableau_Part3/results_mpi_2_omp_1.csv",
    "/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Tableau/Tableau_Part3/results_mpi_2_omp_2.csv",
    "/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Tableau/Tableau_Part3/results_mpi_2_omp_4.csv",
    "/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Tableau/Tableau_Part3/results_mpi_2_omp_8.csv",
    "/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Tableau/Tableau_Part3/results_mpi_4_omp_1.csv",
    "/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Tableau/Tableau_Part3/results_mpi_4_omp_2.csv",
    "/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Tableau/Tableau_Part3/results_mpi_4_omp_4.csv",
    "/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Tableau/Tableau_Part3/results_mpi_4_omp_8.csv",
]

# Lista para armazenar os resultados resumidos
results = []

# Processa cada arquivo
for file in all_files:
    mpi, omp = extract_mpi_omp(file)
    if mpi is None or omp is None:
        print(f"Arquivo com nome inesperado: {file}")
        continue

    df = read_simulation_data(file)

    # Cálculo das médias de tempo de avancement e tempo total
    avg_avancement = df['Temps_avancement(ms)'].mean()
    avg_total = df['Temps_total(ms)'].mean()

    results.append({
        'mpi': mpi,
        'omp': omp,
        'threads_totais': mpi * omp,
        'temps_avancement_ms': avg_avancement,
        'temps_total_ms': avg_total
    })

# Criar o DataFrame com os dados de resultados
df_results = pd.DataFrame(results)

# Ordenar por número de threads para organização
df_results.sort_values(by='threads_totais', inplace=True)

# Definir referência (MPI=1, OMP=1) para calcular a aceleração
ref_row = df_results[(df_results['mpi'] == 1) & (df_results['omp'] == 1)].iloc[0]
ref_total = ref_row['temps_total_ms']
ref_avancement = ref_row['temps_avancement_ms']

# Cálculo das acelerações
df_results['acceleration_globale'] = ref_total / df_results['temps_total_ms']
df_results['acceleration_avancement'] = ref_avancement / df_results['temps_avancement_ms']

# Mostrar o DataFrame com os dados finais
print("\nResultados com acelerações:")
print(df_results)

# =====================================================
# GRÁFICO 1: Accélération (Globale e Avancement) X Threads Totais
# =====================================================
plt.figure(figsize=(10, 6))
plt.plot(df_results['threads_totais'], df_results['acceleration_globale'],
         marker='o', label='Accélération Globale')
plt.plot(df_results['threads_totais'], df_results['acceleration_avancement'],
         marker='s', label="Accélération d'Avancement")

plt.xlabel('Nombre total de Threads (MPI * OMP)')
plt.ylabel('Accélération')
plt.title("Accélération Globale et d'Avancement en fonction des Threads Totaux")
plt.legend()
plt.grid(True)
plt.xticks(df_results['threads_totais'])

plt.show()

# =====================================================
# GRÁFICOS 2, 3, 4: Accélération X Threads OMP para cada MPI (1, 2, 4)
# =====================================================
mpi_values = [1, 2, 4]

for mpi in mpi_values:
    subset = df_results[df_results['mpi'] == mpi].sort_values(by='omp')
    
    plt.figure(figsize=(8, 5))
    
    plt.plot(subset['omp'], subset['acceleration_globale'],
             marker='o', label='Accélération Globale')
    
    plt.plot(subset['omp'], subset['acceleration_avancement'],
             marker='s', label="Accélération d'Avancement")
    
    plt.xlabel('Nombre de Threads OpenMP (OMP)')
    plt.ylabel('Accélération')
    plt.title(f"Accélération en fonction des Threads OMP (MPI={mpi})")
    plt.legend()
    plt.grid(True)
    plt.xticks(subset['omp'])
    
    plt.show()

# =====================================================
# GRÁFICOS 5 a 12: Detalhes dos TimeSteps de cada CSV
# =====================================================
def plot_per_file(file_path):
    mpi, omp = extract_mpi_omp(file_path)
    if mpi is None or omp is None:
        print(f"Arquivo {file_path} com nome inesperado!")
        return

    df = read_simulation_data(file_path)

    plt.figure(figsize=(10, 6))
    plt.plot(df['TimeStep'], df['Temps_avancement(ms)'], label='Temps Avancement (ms)', marker='o')
    plt.plot(df['TimeStep'], df['Temps_affichage(ms)'], label='Temps Affichage (ms)', marker='s')
    plt.plot(df['TimeStep'], df['Temps_total(ms)'], label='Temps Total (ms)', marker='^')

    plt.xlabel('TimeStep')
    plt.ylabel('Temps (ms)')
    plt.title(f'Temps de Simulation - MPI={mpi}, OMP={omp} (Threads Totais={mpi * omp})')
    plt.legend()
    plt.grid(True)
    plt.show()

# Loop para gerar os gráficos de TimeSteps
for file in all_files:
    plot_per_file(file)
