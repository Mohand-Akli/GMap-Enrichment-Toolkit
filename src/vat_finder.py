import os
import glob
import pandas as pd
import re
import time
from ddgs import DDGS

def selectionner_fichier():
    """Génère un menu interactif pour choisir le fichier CSV à traiter."""
    fichiers = glob.glob("data/*.csv") + glob.glob("*.csv")
    fichiers = list(set(fichiers))
    
    if not fichiers:
        print("❌ Aucun fichier .csv trouvé dans le projet (dossier data/ ou racine).")
        exit()
        
    print("\n--- Fichiers CSV disponibles ---")
    for i, fichier in enumerate(fichiers):
        print(f"[{i + 1}] {fichier}")
        
    while True:
        choix = input("\nEntrez le numéro du fichier à traiter : ")
        if choix.isdigit() and 1 <= int(choix) <= len(fichiers):
            fichier_choisi = fichiers[int(choix) - 1]
            break
        print("⚠️ Choix invalide. Entrez un numéro correspondant à la liste.")
        
    # Génère le nom du fichier de sortie
    base_name, ext = os.path.splitext(fichier_choisi)
    if base_name.endswith("_avec_tva"):
        fichier_sortie = fichier_choisi
    else:
        fichier_sortie = f"{base_name}_avec_tva{ext}"
        
    return fichier_choisi, fichier_sortie

def chercher_numeros_tva(fichier_entree, fichier_sortie):
    print(f"\n📂 Initialisation...")
    
    # 1. Charger le fichier CSV avec système de reprise
    if os.path.exists(fichier_sortie):
        df = pd.read_csv(fichier_sortie)
        print(f"✅ Reprise du fichier de sortie existant : {fichier_sortie}")
    else:
        try:
            df = pd.read_csv(fichier_entree)
            print(f"✅ Chargement de la source et création de : {fichier_sortie}")
        except FileNotFoundError:
            print(f"❌ Le fichier '{fichier_entree}' est introuvable.")
            return

    # Ajouter la colonne tva si elle n'existe pas
    if 'tva' not in df.columns:
        df['tva'] = ""
    
    df['tva'] = df['tva'].astype(object)

    print(f"Début de l'analyse pour {len(df)} restaurants...")

    # 2. Utilisation sécurisée de DuckDuckGo
    with DDGS() as ddgs:
        for index, row in df.iterrows():
            nom = row.get('name', '')
            adresse = row.get('address', '')
            
            # Sécurité : Si une TVA a déjà été trouvée, on passe au suivant
            if pd.notna(row.get('tva')) and str(row.get('tva')).strip() != "" and str(row.get('tva')) != "Non trouvé":
                print(f"\n⏭️ [IGNORÉ] {nom} a déjà une TVA enregistrée.")
                continue

            # On évite de traiter les lignes sans nom
            if pd.isna(nom) or str(nom).strip() == "":
                continue
                
            requete = f'"{nom}" "{adresse}" tva entreprise belgique'
            print(f"\n🔍 Recherche pour : {nom}")
            
            try:
                results = list(ddgs.text(requete, max_results=2))
                tva_trouvee = False
                
                for r in results:
                    texte_complet = r.get('title', '') + " " + r.get('body', '')
                    
                    # Expression régulière pour détecter un numéro de TVA belge (BE + chiffres)
                    match_tva = re.search(r'\b(BE\s?0?[0-9]{9})\b', texte_complet, re.IGNORECASE)
                    if match_tva:
                        tva_propre = match_tva.group(1).upper().replace(" ", "")
                        df.at[index, 'tva'] = tva_propre
                        print(f"   ✅ [TROUVÉ] -> {tva_propre}")
                        tva_trouvee = True
                        break
                
                if not tva_trouvee:
                    df.at[index, 'tva'] = "Non trouvé"
                    print(f"   ❌ [Non trouvé]")
                        
            except Exception as e:
                print(f"   ⚠️ [Erreur réseau/limite] : {e}")
                time.sleep(5) # Pause de sécurité si le serveur bloque temporairement
                
            # Sauvegarde en temps réel à chaque itération
            df.to_csv(fichier_sortie, index=False, encoding='utf-8')
            
            # Courte pause pour respecter les limites du moteur de recherche
            time.sleep(2)

    print(f"\n✅ Terminé ! Fichier final sauvegardé sous : {fichier_sortie}")

# --- LANCEMENT ---
if __name__ == "__main__":
    entree, sortie = selectionner_fichier()
    chercher_numeros_tva(entree, sortie)
