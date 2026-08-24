import subprocess
import pandas as pd
import glob
import os

villes = ["Charleroi", "Liège", "Namur", "Mons", "La Louvière", "Tournai", "Verviers", "Mouscron", "Bruxelles"]

print("Lancement des extractions séquentielles automatisées...")

for ville in villes:
    fichier = f"halal_{ville.replace(' ', '_')}_parallele.csv"
    commande = ["python3", "main.py", "-s", f"Restaurant halal {ville}", "-t", "300", "-o", fichier]
    
    print(f"\n---> Démarrage de l'extraction pour : {ville}")
    # run() lance la commande et attend qu'elle se termine avant de passer à la suivante
    subprocess.run(commande)

print("\n--- Toutes les extractions sont terminées ! Début de la fusion ---")
# ... (le reste de ton code de fusion reste identique)

# 1. Lister tous les fichiers générés par l'extraction
fichiers_csv = glob.glob("halal_*_parallele.csv")
dataframes = []

# 2. Lire chaque fichier et l'ajouter à la liste
for fichier in fichiers_csv:
    try:
        df = pd.read_csv(fichier)
        dataframes.append(df)
        print(f"-> Chargement de {fichier} ({len(df)} lignes)")
    except Exception as e:
        print(f"Erreur avec le fichier {fichier} : {e}")

# 3. Fusion et nettoyage
if dataframes:
    # On colle tous les tableaux bout à bout
    fusion_df = pd.concat(dataframes, ignore_index=True)
    total_brut = len(fusion_df)
    
    # On supprime les doublons basés sur le nom et l'adresse
    if 'name' in fusion_df.columns and 'address' in fusion_df.columns:
        fusion_df = fusion_df.drop_duplicates(subset=['name', 'address'])
    else:
        fusion_df = fusion_df.drop_duplicates()
        
    total_net = len(fusion_df)
    
    # 4. Sauvegarde du fichier maître
    fichier_final = "restaurants_halal_base_complete.csv"
    fusion_df.to_csv(fichier_final, index=False)
    
    print("\n✅ Fusion terminée avec succès !")
    print(f"Restaurants trouvés avant nettoyage : {total_brut}")
    print(f"Restaurants uniques après nettoyage : {total_net}")
    print(f"Fichier final sauvegardé sous : {fichier_final}")
    
    # Optionnel : Dé-commente les deux lignes ci-dessous si tu veux que 
    # le script supprime automatiquement les fichiers individuels des villes à la fin.
    # for f in fichiers_csv:
    #     os.remove(f)
else:
    print("Aucun fichier n'a été trouvé pour la fusion.")
