import os
import glob
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def selectionner_fichier():
    # Liste tous les fichiers CSV dans le dossier data/ (nouvelle structure) et à la racine
    fichiers = glob.glob("data/*.csv") + glob.glob("*.csv")
    fichiers = list(set(fichiers)) # Supprime les éventuels doublons
    
    if not fichiers:
        print("Aucun fichier .csv trouvé dans le projet.")
        exit()
        
    print("\n--- Fichiers CSV disponibles ---")
    for i, fichier in enumerate(fichiers):
        print(f"[{i + 1}] {fichier}")
        
    while True:
        choix = input("\nEntrez le numéro du fichier à traiter : ")
        if choix.isdigit() and 1 <= int(choix) <= len(fichiers):
            fichier_choisi = fichiers[int(choix) - 1]
            break
        print("Choix invalide. Entrez un numéro correspondant à la liste.")
        
    # Génère automatiquement le nom du fichier de sortie
    base_name, ext = os.path.splitext(fichier_choisi)
    
    # Si l'utilisateur sélectionne un fichier qui a déjà "_trie" dans le nom
    if base_name.endswith("_trie"):
        fichier_sortie = fichier_choisi
    else:
        fichier_sortie = f"{base_name}_trie{ext}"
        
    return fichier_choisi, fichier_sortie

# Assignation dynamique des noms de fichiers
input_csv, output_csv = selectionner_fichier()

# Charger le fichier CSV (reprise automatique si le fichier trié existe déjà)
if os.path.exists(output_csv):
    df = pd.read_csv(output_csv)
    print(f"\nReprise du fichier trié existant ({len(df)} restaurants restants).")
else:
    df = pd.read_csv(input_csv)
    print(f"\nChargement initial de {len(df)} restaurants depuis {input_csv}.")

# Configuration de Selenium Chrome
chrome_options = Options()
# ... [Le reste de ton code original à partir d'ici] ...
