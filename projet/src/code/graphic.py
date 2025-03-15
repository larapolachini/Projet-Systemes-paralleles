import pandas as pd
import matplotlib.pyplot as plt
import glob

# Rechercher tous les fichiers CSV commençant par "resultats_temps"
csv_files = glob.glob("/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Tableau/resultats_temps*.csv")
#csv_files = glob.glob("/home/larapolachini/Projet-Systemes-paralleles/projet/src/Tableau/resultats_temps*.csv")


if not csv_files:
    print("Aucun fichier CSV trouvé.")
else:
    for file in csv_files:
        # Lire CSV en utilisant ";" comme délimiteur
        df = pd.read_csv(file, sep=";")
        # Supprimer les espaces supplémentaires dans les noms de colonnes
        df.columns = [col.strip() for col in df.columns]
        
        # Définit l'axe X : utilise « TimeStep » s'il existe, sinon, utilise « Iteration »
        x_column = "TimeStep" if "TimeStep" in df.columns else "Iteration"

        # Supprimer les données de l'itérateur 0 (première ligne) AVANT tout traitement
        df = df.iloc[1:].reset_index(drop=True)
        
        # Multipliez les valeurs de temps par 100
        df['Temps_avancement(ms)'] = df['Temps_avancement(ms)'] * 100
        df['Temps_affichage(ms)']  = df['Temps_affichage(ms)'] * 100
        df['Temps_total(ms)']      = df['Temps_total(ms)'] * 100

        # Calculer la moyenne mobile (rolling) avec une fenêtre de 10, après avoir supprimé le premier itérateur
        df['Avancement_Rolling'] = df['Temps_avancement(ms)'].rolling(window=10, center=True, min_periods=1).mean()
        df['Affichage_Rolling']  = df['Temps_affichage(ms)'].rolling(window=10, center=True, min_periods=1).mean()
        df['Total_Rolling']      = df['Temps_total(ms)'].rolling(window=10, center=True, min_periods=1).mean()
        
        # Crée la figure avec une taille plus grande et une bonne résolution
        
        # Tracer uniquement les courbes lissées
        plt.plot(df[x_column], df['Avancement_Rolling'], linewidth=2, color='blue', 
                 label='Avancement (ms) [softened]')
        plt.plot(df[x_column], df['Affichage_Rolling'], linewidth=2, color='orange', 
                 label='Affichage (ms) [softened]')
        plt.plot(df[x_column], df['Total_Rolling'], linewidth=2, color='green', 
                 label='Total (ms) [softened]')
        
        plt.xlabel(x_column)
        plt.ylabel("Temps (ms) x 100 (moyenne mobile)")
        plt.title(f"Adoucissement des temps (x100) - {file}")
        plt.legend()
        plt.grid(True)
        
        # Définit la limite fixe de l'axe des y (exemple : 0 à 600)
        plt.ylim(0,600)
        
        # Enregistrer et afficher le graphique
        output_file = file.replace(".csv", "_rolling_no_first.png")
        import os
        folder = "/home/davy/Ensta/ProjetParallel/Projet-Systemes-paralleles/projet/src/Imagens"
        #folder = "/home/larapolachini/Projet-Systemes-paralleles/projet/src/Imagens"
        if not os.path.exists(folder):
            os.makedirs(folder)
        plt.savefig(os.path.join(folder, "_rolling_no_first.png"))
        plt.show() 
