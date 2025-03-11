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
            # split() quebra por qualquer quantidade de espaços em branco
            data_lines.append(line.strip().split())

    # Verifica se tem dados lidos
    if not data_lines:
        print(f"Nenhum dado encontrado em {filepath}")
        return pd.DataFrame(columns=["TimeStep", "UpdateTime (ms)"])

    df = pd.DataFrame(data_lines, columns=["TimeStep", "UpdateTime (ms)", "DisplayTime (ms)", "TotalTime (ms)"])

    # Converte colunas numéricas de string para float
    df["TimeStep"] = df["TimeStep"].astype(int)
    df["UpdateTime (ms)"] = df["UpdateTime (ms)"].astype(float)

    return df

# Dicionário com os arquivos para comparação
arquivos = {
    "Sequencial": "simulation_results.txt",
    "Paralelo": "simulation_results2.txt"
}

# Lê todos os DataFrames
dataframes = {label: ler_resultados(path) for label, path in arquivos.items()}

# Verifica o conteúdo lido
for label, df in dataframes.items():
    print(f"Arquivo: {label}")
    print(df.head())  # Exibe as primeiras linhas para checar se foi lido corretamente

# ============================
# Gráfico ÚNICO: Update Time de ambos
# ============================
plt.figure(figsize=(12, 6))
for label, df in dataframes.items():
    plt.plot(df["TimeStep"], df["UpdateTime (ms)"], label=f"{label} - Update Time", marker='o')

plt.title("Comparação de Update Time (Sequencial x Paralelo)")
plt.xlabel("TimeStep")
plt.ylabel("Update Time (ms)")
plt.legend()
plt.grid(True)

# Defina limites de eixos conforme seus dados!
# Aqui estão desativados para garantir a exibição completa dos dados
# plt.ylim(0, 15)
# plt.xlim(0, 10)

plt.savefig("comparacao_update_time.png")
plt.show()

print("Gráfico de comparação do Update Time gerado e salvo como 'comparacao_update_time.png'")
