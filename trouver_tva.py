import pandas as pd
import re
import time
from duckduckgo_search import DDGS

# 1. Charger ton fichier fusionné de restaurants
fichier_entree = "restaurants_halal_base_complete.csv"
print(f"Chargement de {fichier_entree}...")
df = pd.read_csv(fichier_entree)

# Ajouter des colonnes vides si elles n'existent pas
if 'tva' not in df.columns:
    df['tva'] = "Non trouvé"
if 'contact_potentiel' not in df.columns:
    df['contact_potentiel'] = "Non trouvé"

print("Début de la recherche des numéros de TVA...")

# 2. Utilisation de DuckDuckGo en arrière-plan pour trouver les infos légales
with DDGS() as ddgs:
    for index, row in df.iterrows():
        nom = row.get('name', '')
        adresse = row.get('address', '')
        
        # On cible explicitement la Belgique et les termes légaux
        requete = f'"{nom}" "{adresse}" tva entreprise belgique'
        
        try:
            # On récupère les 2 premiers résultats web
            results = list(ddgs.text(requete, max_results=2))
            
            for r in results:
                texte_complet = r.get('title', '') + " " + r.get('body', '')
                
                # Expression régulière pour détecter un numéro de TVA belge (BE + 10 chiffres)
                match_tva = re.search(r'\b(BE\s?0?[0-9]{9})\b', texte_complet, re.IGNORECASE)
                if match_tva:
                    tva_propre = match_tva.group(1).upper().replace(" ", "")
                    df.at[index, 'tva'] = tva_propre
                    print(f"[TROUVÉ] {nom} -> TVA: {tva_propre}")
                    break
                    
        except Exception as e:
            # En cas de mini-coupure réseau, on continue
            pass
            
        # Courte pause pour ne pas saturer le moteur de recherche
        time.sleep(1)

# 3. Sauvegarde du fichier enrichi
fichier_sortie = "restaurants_halal_avec_tva.csv"
df.to_csv(fichier_sortie, index=False)
print(f"\n✅ Terminé ! Fichier sauvegardé sous : {fichier_sortie}")
