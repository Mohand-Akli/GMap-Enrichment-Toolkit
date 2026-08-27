import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Nom des fichiers
input_csv = "repertoire_restaurants_halal_wallonie (1).csv"
output_csv = "repertoire_restaurants_halal_wallonie_trie.csv"

# Charger le fichier CSV (si le fichier trié existe déjà, on reprend là où on s'était arrêté)
if os.path.exists(output_csv):
    df = pd.read_csv(output_csv)
    print(f"Reprise du fichier trié existant ({len(df)} restaurants restants).")
else:
    df = pd.read_csv(input_csv)
    print(f"Chargement de {len(df)} restaurants depuis {input_csv}.")

# Configuration de Selenium Chrome
chrome_options = Options()
# chrome_options.add_argument("--headless") # Décommente si tu ne veux pas voir la fenêtre s'ouvrir
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

print("\n--- Démarrage du tri interactif ---")
print("Pour chaque restaurant, la page Google Maps s'ouvrira.")
print("Commandes dans la console :")
print("  [g] ou [Entrée] : Garder le restaurant et passer au suivant")
print("  [s] ou [suppr]  : Supprimer définitivement le restaurant de la liste")
print("  [q]             : Quitter et sauvegarder la progression\n")

indices_to_drop = []

try:
    for idx, row in df.iterrows():
        name = row["name"]
        address = row.get("address", "")
        query = f"{name} {address}"
        
        print(f"\n[{idx + 1}/{len(df)}] Traitement en cours : {name} ({address})")
        
        # Ouvrir Google Maps avec la recherche du restaurant
        search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
        driver.get(search_url)
        
        # Demander l'action à l'utilisateur dans la console
        choix = input("Voulez-vous garder ce restaurant ? ([g]arder / [s]upprimer / [q]uitter) : ").strip().lower()
        
        if choix == 'q':
            print("Sauvegarde et arrêt du programme...")
            break
        elif choix in ['s', 'supprimer', 'suppr']:
            indices_to_drop.append(idx)
            print(f"-> '{name}' sera supprimé.")
        else:
            print(f"-> '{name}' conservé.")

finally:
    # Fermer le navigateur
    driver.quit()
    
    # Mettre à jour le DataFrame en retirant les lignes sélectionnées
    if indices_to_drop:
        df = df.drop(indices_to_drop)
        
    # Sauvegarder le résultat mis à jour
    df.to_csv(output_csv, index=False)
    print(f"\nSession terminée. Fichier sauvegardé sous : {output_csv}")
    print(f"Il reste {len(df)} restaurants dans la liste.")
