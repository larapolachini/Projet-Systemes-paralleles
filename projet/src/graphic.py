import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

# === CONFIGURAÇÕES ===
PASTA_CSV = '.'  # Diretório onde estão os CSVs
PADRAO_ARQUIVO = 'resultats_temps_*_threads.csv'

# === LISTAR E LER OS ARQUIVOS ===
arquivos_csv = glob.glob(os.path.join(PASTA_CSV, PADRAO_ARQUIVO))

if not arquivos_csv:
    print("Nenhum arquivo CSV encontrado!")
    exit()

print(f"{len(arquivos_csv)} arquivos encontrados:\n")
for arq in arquivos_csv:
    print(f" - {arq}")

# === LER OS TEMPOS MÉDIOS TOTAIS DE CADA CSV ===
tempos_por_threads = {}

for arquivo in arquivos_csv:
    # Extrair número de threads do nome do arquivo
    nome_arquivo = os.path.basename(arquivo)
    partes = nome_arquivo.split('_')
    num_threads = int(partes[2])  # resultats_temps_<N>_threads.csv -> N

    # Ler CSV
    df = pd.read_csv(arquivo, sep=';', decimal='.', engine='python')

    # Calcular média do tempo total por iteração
    tempo_medio_total = df['Temps_total(ms)'].mean()

    tempos_por_threads[num_threads] = tempo_medio_total

# === ORDENAR PELO NÚMERO DE THREADS ===
threads_ordenadas = sorted(tempos_por_threads.keys())
tempos_ordenados = [tempos_por_threads[t] for t in threads_ordenadas]

# === CALCULAR SPEEDUP ===
tempo_sequencial = tempos_por_threads[1]  # Tempo com 1 thread é a base
speedup = [tempo_sequencial / t for t in tempos_ordenados]

# === PLOTAR O GRÁFICO DE SPEEDUP ===
plt.figure(figsize=(10, 6))
plt.plot(threads_ordenadas, speedup, marker='o', linestyle='-', color='green', label='Speedup')
plt.plot(threads_ordenadas, threads_ordenadas, linestyle='--', color='gray', label='Speedup ideal (linear)')

plt.title('Gráfico de Speedup')
plt.xlabel('Número de Threads')
plt.ylabel('Speedup')
plt.grid(True)
plt.legend()
plt.ylim(0,1.5)

plt.savefig('speedup_graph.png')
plt.show()

# === MOSTRAR VALORES NO TERMINAL ===
print("\nSpeedup calculado:")
for threads, s in zip(threads_ordenadas, speedup):
    print(f"Threads: {threads} - Speedup: {s:.2f}")
