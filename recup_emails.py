import pandas as pd
import re
import requests
import urllib3

# Désactiver les avertissements de sécurité SSL pour les sites un peu anciens
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 1. Charger ton fichier de restaurants
fichier_entree = "restaurants_halal_wallonie_bruxelles_complet.csv"
print(f"Chargement de {fichier_entree}...")
df = pd.read_csv(fichier_entree)

# Créer une colonne email si elle n'existe pas
if 'email' not in df.columns:
    df['email'] = ""

def trouver_email_sur_site(url):
    if pd.isna(url) or not isinstance(url, str) or len(url.strip()) == 0:
        return "Pas de site web"
    
    # S'assurer que l'URL commence bien par https://
    if not url.startswith('http'):
        url = 'https://' + url
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        # On télécharge la page d'accueil (timeout court de 4 secondes pour aller vite)
        response = requests.get(url, headers=headers, timeout=4, verify=False)
        if response.status_code == 200:
            # Recherche de tous les motifs d'e-mails dans le code source de la page
            emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', response.text))
            
            # Filtrer les faux positifs (images, scripts, domaines techniques)
            exclus = ['.png', '.jpg', '.gif', '.svg', 'sentry', 'wix', 'example', 'domain', 'wordpress', 'elementor', 'your-email']
            emails_propres = [e for e in emails if not any(x in e.lower() for x in exclus)]
            
            if emails_propres:
                return ", ".join(emails_propres)
    except Exception:
        pass
        
    return "Non trouvé"

print("Début de l'analyse des sites web...")
total_trouves = 0

for idx, row in df.iterrows():
    site = row.get('website')
    nom = row.get('name')
    
    if pd.notna(site) and str(site).strip() != "":
        email = trouver_email_sur_site(site)
        if email != "Non trouvé" and email != "Pas de site web":
            total_trouves += 1
            print(f"[TROUVÉ] {nom} ({site}) -> {email}")
            df.at[idx, 'email'] = email
        else:
            df.at[idx, 'email'] = email
    else:
        df.at[idx, 'email'] = "Pas de site web"

# 2. Sauvegarder le fichier enrichi
fichier_sortie = "restaurants_halal_avec_emails.csv"
df.to_csv(fichier_sortie, index=False)
print(f"\n--- Terminé ! ---")
print(f"E-mails trouvés sur les sites web : {total_trouves}")
print(f"Résultats sauvegardés dans : {fichier_sortie}")
