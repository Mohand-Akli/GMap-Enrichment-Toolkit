import subprocess
import pandas as pd
import glob
import os

def selectionner_mode():
    """Menu interactif pour choisir les villes à scraper ou traiter."""
    print("\n--- Menu du Pipeline de Scraping ---")
    print("[1] Lancer l'extraction automatisée pour toutes les villes de la liste")
    print("[2] Fusionner des fichiers existants (depuis le dossier data/)")
    
    choix = input("\nEntrez votre choix (1 ou 2) : ").strip()
    return choix

def lancer_extraction_villes():
    villes = ["Charleroi", "Liège", "Namur", "Mons", "La Louvière", "Tournai", "Verviers", "Mouscron", "Bruxelles"]

    print("\n🚀 Lancement des extractions séquentielles automatisées...")

    for ville in villes:
        # On range les fichiers temporaires de chaque ville proprement dans data/
        fichier = f"data/halal_{ville.replace(' ', '_')}_parallele.csv"
        # On appelle ton main.py situé dans src/
        commande = ["python3", "src/main.py", "-s", f"Restaurant halal {ville}", "-t", "300", "-o", fichier]
        
        print(f"\n---> Démarrage de l'extraction pour : {ville}")
        subprocess.run(commande)

def fusionner_fichiers():
    print("\n--- Début de la fusion des fichiers ---")
    
    # 1. Lister tous les fichiers générés dans data/
    fichiers_csv = glob.glob("data/halal_*_parallele.csv")
    dataframes = []

    if not fichiers_csv:
        print("❌ Aucun fichier de données individuelles trouvé dans le dossier data/.")
        return

    # 2. Lire chaque fichier et l'ajouter à la liste
    for fichier in fichiers_csv:
        try:
            df = pd.read_csv(fichier)
            dataframes.append(df)
            print(f"-> Chargement de {fichier} ({len(df)} lignes)")
        except Exception as e:
            print(f"⚠️ Erreur avec le fichier {fichier} : {e}")

    # 3. Fusion et nettoyage
    if dataframes:
        fusion_df = pd.concat(dataframes, ignore_index=True)
        total_brut = len(fusion_df)
        
        # Suppression des doublons basés sur le nom et l'adresse
        if 'name' in fusion_df.columns and 'address' in fusion_df.columns:
            fusion_df = fusion_df.drop_duplicates(subset=['name', 'address'])
        else:
            fusion_df = fusion_df.drop_duplicates()
            
        total_net = len(fusion_df)
        
        # 4. Sauvegarde du fichier maître dans le dossier data/
        fichier_final = "data/restaurants_halal_base_complete.csv"
        fusion_df.to_csv(fichier_final, index=False)
        
        print("\n✅ Fusion terminée avec succès !")
        print(f"Restaurants trouvés avant nettoyage : {total_brut}")
        print(f"Restaurants uniques après nettoyage : {total_net}")
        print(f"Fichier final sauvegardé sous : {fichier_final}")
    else:
        print("⚠️ Aucun contenu valide n'a pu être fusionné.")

# --- LANCEMENT DU PIPELINE ---
if __name__ == "__main__":
    # Assurez-vous que le dossier data existe
    os.makedirs("data", exist_ok=True)
    
    mode = selectionner_mode()
    
    if mode == "1":
        lancer_extraction_villes()
        fusionner_fichiers()
    elif mode == "2":
        fusionner_fichiers()
    else:
        print("❌ Choix invalide. Relancez le script.")
