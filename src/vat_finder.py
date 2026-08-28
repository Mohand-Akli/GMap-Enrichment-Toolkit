import pandas as pd
import re
import time
from ddgs import DDGS

# 1. Charger ton fichier de restaurants
fichier_entree = "restaurants_halal_base_complete.csv"
print(f"Chargement de {fichier_entree}...")
df = pd.read_csv(fichier_entree)

# Ajouter les colonnes si elles n'existent pas
if 'tva' not in df.columns:
    df['tva'] = "Non trouvé"

print(f"Début de l'analyse pour {len(df)} restaurants...")

# 2. Utilisation sécurisée de DuckDuckGo
with DDGS() as ddgs:
    for index, row in df.iterrows():
        nom = row.get('name', '')
        adresse = row.get('address', '')
        
        # On évite de traiter les lignes vides
        if pd.isna(nom) or str(nom).strip() == "":
            continue
            
        requete = f'"{nom}" "{adresse}" tva entreprise belgique'
        
        try:
            results = list(ddgs.text(requete, max_results=2))
            
            for r in results:
                texte_complet = r.get('title', '') + " " + r.get('body', '')
                
                # Expression régulière pour détecter un numéro de TVA belge (BE + 10 chiffres)
                match_tva = re.search(r'\b(BE\s?0?[0-9]{9})\b', texte_complet, re.IGNORECASE)
                if match_tva:
                    tva_propre = match_tva.group(1).upper().replace(" ", "")
                    df.at[index, 'tva'] = tva_propre
                    print(f"[{index+1}/{len(df)}] [TROUVÉ] {nom} -> {tva_propre}")
                    break
            else:
                print(f"[{index+1}/{len(df)}] [Non trouvé] {nom}")
                
        except Exception as e:
            # Si le web tousse, on affiche l'alerte mais on NE CRASH PAS
            print(f"[{index+1}/{len(df)}] [Erreur réseau/limite] {nom} : {e}")
            time.sleep(5) # Petite pause de sécurité si le serveur râle
            
        # Sauvegarde automatique intermédiaire toutes les 10 lignes
        if (index + 1) % 10 == 0:
            df.to_csv("restaurants_halal_avec_tva_sauvegarde.csv", index=False)
            
        # Courte pause pour respecter les limites du moteur de recherche
        time.sleep(2)

# 3. Sauvegarde finale propre
fichier_sortie = "restaurants_halal_avec_tva_final.csv"
df.to_csv(fichier_sortie, index=False)
print(f"\n✅ Terminé ! Fichier final sauvegardé sous : {fichier_sortie}")
