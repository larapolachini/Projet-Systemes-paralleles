import re
import pandas as pd
import matplotlib.pyplot as plt

# Função para ler um arquivo de resultados
def ler_resultados(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()

    data_lines = []
    pattern = re.compile(r'^\d+')  # Captura linhas que começam com um número
    for line in lines:
        if pattern.match(line):
            data_lines.append(line.strip().split())

    if not data_lines:
        print(f"Nenhum dado encontrado em {filepath}")
        return pd.DataFrame(columns=["TimeStep", "UpdateTime (ms)", "DisplayTime (ms)", "TotalTime (ms)"])

    df = pd.DataFrame(data_lines, columns=["TimeStep", "UpdateTime (ms)", "DisplayTime (ms)", "TotalTime (ms)"])

    # Converte colunas numéricas de string para float/int
    df["TimeStep"] = df["TimeStep"].astype(int)
    df["UpdateTime (ms)"] = df["UpdateTime (ms)"].astype(float)
    df["TotalTime (ms)"] = df["TotalTime (ms)"].astype(float)

    return df

# Arquivos de simulação para diferentes números de threads
arquivos = {
    "1 Thread": "simulation_1threads.txt",
    "2 Threads": "simulation_2threads.txt",
    "4 Threads": "simulation_4threads.txt",
    "8 Threads": "simulation_8threads.txt"
}

# Lê todos os DataFrames
dataframes = {label: ler_resultados(path) for label, path in arquivos.items()}

# Verifica o conteúdo lido (opcional)
for label, df in dataframes.items():
    print(f"\nArquivo: {label}")
    print(df.head())

# ===============================
# Gráficos separados para cada config
# ===============================
for label, df in dataframes.items():
    # Gera nome para o arquivo (para salvar)
    thread_label = label.replace(" ", "_").lower()  # Exemplo: '1_thread'

    # --- Gráfico de Update Time ---
    plt.figure(figsize=(12, 6))
    plt.plot(df["TimeStep"], df["UpdateTime (ms)"], marker='o')
    plt.title(f"Update Time por TimeStep - {label}")
    plt.xlabel("TimeStep")
    plt.ylabel("Update Time (ms)")
    plt.grid(True)
    plt.savefig(f"update_time_{thread_label}.png")
    plt.show()

    # --- Gráfico de Total Time ---
    plt.figure(figsize=(12, 6))
    plt.plot(df["TimeStep"], df["TotalTime (ms)"], marker='o', color='orange')
    plt.title(f"Total Time por TimeStep - {label}")
    plt.xlabel("TimeStep")
    plt.ylabel("Total Time (ms)")
    plt.grid(True)
    plt.savefig(f"total_time_{thread_label}.png")
    plt.show()

    print(f"Gráficos gerados para {label}: update_time_{thread_label}.png e total_time_{thread_label}.png")

print("Todos os gráficos foram gerados!")