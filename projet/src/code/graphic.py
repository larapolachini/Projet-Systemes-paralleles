import pandas as pd
import matplotlib.pyplot as plt
import glob

# Procura por todos os arquivos CSV que começam com "resultats_temps"
csv_files = glob.glob("/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Tableau/resultats_temps*.csv")

if not csv_files:
    print("Nenhum arquivo CSV encontrado.")
else:
    for file in csv_files:
        # Lê o CSV usando ";" como delimitador
        df = pd.read_csv(file, sep=";")
        # Remove espaços extras nos nomes das colunas
        df.columns = [col.strip() for col in df.columns]
        
        # Define o eixo X: utiliza "TimeStep" se existir, senão, utiliza "Iteration"
        x_column = "TimeStep" if "TimeStep" in df.columns else "Iteration"

        # Remove os dados do iterador 0 (primeira linha) ANTES de qualquer processamento
        df = df.iloc[1:].reset_index(drop=True)
        
        # Multiplica os valores de tempo por 100
        df['Temps_avancement(ms)'] = df['Temps_avancement(ms)'] * 100
        df['Temps_affichage(ms)']  = df['Temps_affichage(ms)'] * 100
        df['Temps_total(ms)']      = df['Temps_total(ms)'] * 100

        # Calcula a média móvel (rolling) com janela de 10, após remover o primeiro iterador
        df['Avancement_Rolling'] = df['Temps_avancement(ms)'].rolling(window=10, center=True, min_periods=1).mean()
        df['Affichage_Rolling']  = df['Temps_affichage(ms)'].rolling(window=10, center=True, min_periods=1).mean()
        df['Total_Rolling']      = df['Temps_total(ms)'].rolling(window=10, center=True, min_periods=1).mean()
        
        # Cria a figura com tamanho maior e boa resolução
        
        # Plota apenas as curvas suavizadas
        plt.plot(df[x_column], df['Avancement_Rolling'], linewidth=2, color='blue', 
                 label='Avancement (ms) [suavizado]')
        plt.plot(df[x_column], df['Affichage_Rolling'], linewidth=2, color='orange', 
                 label='Affichage (ms) [suavizado]')
        plt.plot(df[x_column], df['Total_Rolling'], linewidth=2, color='green', 
                 label='Total (ms) [suavizado]')
        
        plt.xlabel(x_column)
        plt.ylabel("Tempo (ms) x 100 (média móvel)")
        plt.title(f"Suavização dos Tempos (x100) - {file}")
        plt.legend()
        plt.grid(True)
        
        # Define o limite do eixo y fixo (exemplo: 0 a 1200)
        plt.ylim(0,600)
        
        # Salva e exibe o gráfico
        output_file = file.replace(".csv", "_rolling_no_first.png")
        import os
        folder = "/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Imagens"
        if not os.path.exists(folder):
            os.makedirs(folder)
        plt.savefig(os.path.join(folder, "_rolling_no_first.png"))
        plt.show() 
