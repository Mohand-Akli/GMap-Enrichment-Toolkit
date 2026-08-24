import pandas as pd
import re
from duckduckgo_search import DDGS
import time

# 1. Charger ton fichier de restaurants existant
fichier_entree = "restaurants_halal_base_complete.csv"
print(f"Chargement de {fichier_entree}...")
df = pd.read_csv(fichier_entree)

# Initialisation des nouvelles colonnes si elles n'existent pas
df['tva_trouvee'] = ""
df['contact_info'] = ""

# 2. Parcourir chaque restaurant de la liste
with DDGS() as ddgs:
    for index, row in df.iterrows():
        nom = row.get('name', '')
        ville = row.get('address', '') # ou la ville si stockée séparément
        
        # Requête ciblée sur les entreprises belges
        requete = f"restaurant {nom} {ville} belgique tva entreprise"
        print(f"Recherche pour : {nom}...")
        
        try:
            # On interroge DuckDuckGo
            results = list(ddgs.text(requete, max_results=3))
            
            tva_trouvee = None
            email_trouve = None
            
            for r in results:
                texte_global = r.get('title', '') + " " + r.get('body', '')
                
                # Recherche d'un numéro de TVA belge (Format BE suivi de 0 ou 1 puis 9 chiffres)
                match_tva = re.search(r'\b(BE\s?0?[0-9]{9})\b', texte_global, re.IGNORECASE)
                if match_tva and not tva_trouvee:
                    tva_trouvee = match_tva.group(1).upper()
                
                # Recherche d'un e-mail dans les extraits de texte
                match_email = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', texte_global)
                if match_email and not email_trouve:
                    email_trouve = match_email.group(0)
            
            # Sauvegarde des trouvailles dans le tableau
            df.at[index, 'tva_trouvee'] = tva_trouvee if tva_trouvee else "Non trouvé"
            df.at[index, 'contact_info'] = email_trouve if email_trouve else "Non trouvé"
            
        except Exception as e:
            print(f"Erreur lors de la recherche pour {nom}: {e}")
            
        # Petite pause pour éviter d'se faire bloquer par le moteur de recherche
        time.sleep(2)

# 3. Exporter vers un nouveau fichier final enrichi
fichier_sortie = "restaurants_halal_totalement_enrichis.csv"
df.to_csv(fichier_sortie, index=False)
print(f"\nEnrichissement terminé ! Fichier sauvegardé sous : {fichier_sortie}")
