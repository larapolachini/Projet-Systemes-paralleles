import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

# === CONFIGURAÇÕES ===
# Pasta onde estão seus arquivos CSV
PASTA_CSV = '.'  # Mude para o caminho correto se estiver em outro lugar
PADRAO_ARQUIVO = 'resultats_temps_*_threads.csv'

# === LISTAR E LER OS ARQUIVOS ===
arquivos_csv = glob.glob(os.path.join(PASTA_CSV, PADRAO_ARQUIVO))

if not arquivos_csv:
    print("Nenhum arquivo CSV encontrado!")
    exit()

print(f"{len(arquivos_csv)} arquivos encontrados:\n")
for arq in arquivos_csv:
    print(f" - {arq}")

# === ANALISAR CADA CSV ===
for arquivo in arquivos_csv:
    # Extrair o número de threads do nome do arquivo (por exemplo: 8_threads.csv -> 8)
    nome_arquivo = os.path.basename(arquivo)
    partes = nome_arquivo.split('_')
    num_threads = partes[2]  # resultats_temps_<N>_threads.csv -> N

    print(f"\nAnalisando arquivo: {nome_arquivo} ({num_threads} threads)")

    # Ler CSV em um DataFrame
    df = pd.read_csv(arquivo, sep=';', decimal='.', engine='python')

    # === GRÁFICO 1: TEMPO DE AVANÇAMENTO POR ITERAÇÃO ===
    plt.figure(figsize=(10, 6))
    plt.plot(df['Iteration'], df['Temps_avancement(ms)'], marker='o', linestyle='-', label='Avancement (ms)')
    plt.title(f"Temps d'avancement par itération ({num_threads} threads)")
    plt.xlabel('Itération')
    plt.ylabel('Temps (ms)')
    plt.grid(True)
    plt.legend()
    plt.savefig(f'graph_avancement_{num_threads}_threads.png')
    plt.show()

    # === GRÁFICO 2: TEMPO TOTAL POR ITERAÇÃO ===
    plt.figure(figsize=(10, 6))
    plt.plot(df['Iteration'], df['Temps_total(ms)'], marker='s', linestyle='-', color='red', label='Temps Total (ms)')
    plt.title(f"Temps total par itération ({num_threads} threads)")
    plt.xlabel('Itération')
    plt.ylabel('Temps (ms)')
    plt.grid(True)
    plt.legend()
    plt.savefig(f'graph_total_{num_threads}_threads.png')
    plt.show()

    # === ESTATÍSTICAS RESUMIDAS ===
    print(f"  ➡️ Temps moyen d'avancement : {df['Temps_avancement(ms)'].mean():.3f} ms")
    print(f"  ➡️ Temps moyen d'affichage  : {df['Temps_affichage(ms)'].mean():.3f} ms")
    print(f"  ➡️ Temps moyen total        : {df['Temps_total(ms)'].mean():.3f} ms")

# === OPCIONAL: GRÁFICO COMPARATIVO ENTRE THREADS ===
# (se quiser, podemos juntar os tempos médios de todos para um gráfico só)
