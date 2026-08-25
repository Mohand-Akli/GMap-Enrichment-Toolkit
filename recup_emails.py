import requests
from bs4 import BeautifulSoup
import re
from duckduckgo_search import DDGS
import time

def chercher_emails_restaurant(nom_restaurant, nb_resultats=3):
    print(f"\n🔍 Recherche de contacts pour : {nom_restaurant}")
    
    # Expression régulière pour l'e-mail
    motif_email = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    emails_trouves = set()
    
    requete = f"{nom_restaurant} restaurant officiel contact"
    resultats_recherche = []
    
    # 1. Recherche via DuckDuckGo
    try:
        with DDGS() as ddgs:
            # Récupère les résultats sous forme de dictionnaire et extrait les liens (href)
            resultats = list(ddgs.text(requete, max_results=nb_resultats))
            resultats_recherche = [res['href'] for res in resultats]
    except Exception as e:
        print(f"❌ Erreur lors de la recherche DuckDuckGo : {e}")
        return []

    if not resultats_recherche:
        print("Aucun site trouvé pour ce restaurant.")
        return []

    # 2. Visiter chaque lien
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    for url in resultats_recherche:
        print(f"  🌐 Analyse de : {url}")
        
        # Ignorer les annuaires ou réseaux sociaux
        domaines_ignores = ['facebook.com', 'tripadvisor', 'yelp', 'instagram', 'deliveroo', 'ubereats', 'takeaway', 'resto.be', 'foursquare']
        if any(domaine in url for domaine in domaines_ignores):
            print("     -> Site ignoré (Réseau social ou annuaire).")
            continue

        try:
            # Téléchargement de la page
            reponse = requests.get(url, headers=headers, timeout=5)
            
            if reponse.status_code == 200:
                soup = BeautifulSoup(reponse.text, 'html.parser')
                texte_page = soup.text
                
                # Chercher les e-mails
                emails_sur_page = re.findall(motif_email, texte_page)
                
                for email in emails_sur_page:
                    if not email.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                        emails_trouves.add(email.lower())
            else:
                print(f"     -> Code d'erreur {reponse.status_code} lors de l'accès au site.")
                
        except requests.exceptions.RequestException:
            print(f"     -> Impossible d'accéder à la page (Timeout ou sécurité).")

        time.sleep(1)

    # 3. Résultat final
    if emails_trouves:
        print(f"✅ E-mails trouvés pour {nom_restaurant} :")
        for email in emails_trouves:
            print(f"   - {email}")
    else:
        print(f"❌ Aucun e-mail pertinent trouvé pour {nom_restaurant}.")
        
    return list(emails_trouves)

# --- EXEMPLE D'UTILISATION ---
if __name__ == "__main__":
    restaurants_a_chercher = [
        "La Seigneurie Verviers",
        "Chamas Tacos Liège",
        "Waffle Factory Tournai"
    ]
    
    for resto in restaurants_a_chercher:
        chercher_emails_restaurant(resto)
        print("-" * 40)
