import requests
from bs4 import BeautifulSoup
import re
import time
from googlesearch import search

def chercher_emails_restaurant(nom_restaurant, nb_resultats=3):
    print(f"\n🔍 Recherche de contacts pour : {nom_restaurant}")
    
    motif_email = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    emails_trouves = set()
    resultats_recherche = []
    
    requete = f"{nom_restaurant} restaurant officiel contact"
    
    # 1. Recherche Google
    try:
        # num_results est le bon paramètre pour la version actuelle de googlesearch-python
        resultats_recherche = list(search(requete, num_results=nb_resultats, lang="fr", sleep_interval=2))
    except Exception as e:
        print(f"❌ Erreur lors de la recherche Google : {e}")
        return []

    if not resultats_recherche:
        print("Aucun site trouvé pour ce restaurant.")
        return []

    # 2. Visiter chaque lien trouvé
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Liste des sites à ignorer pour ne pas fausser les e-mails
    domaines_ignores = ['facebook.com', 'tripadvisor', 'yelp', 'instagram', 'deliveroo', 'ubereats', 'takeaway', 'resto.be', 'foursquare', 'pagesjaunes', 'just-eat', 'tiktok', 'youtube', 'coca-cola']
    
    for url in resultats_recherche:
        print(f"  🌐 Analyse de : {url}")
        
        if any(domaine in url for domaine in domaines_ignores):
            print("     -> Site ignoré (Réseau social ou annuaire).")
            continue

        try:
            # Téléchargement de la page du restaurant
            reponse = requests.get(url, headers=headers, timeout=7)
            
            if reponse.status_code == 200:
                soup = BeautifulSoup(reponse.text, 'html.parser')
                texte_page = soup.text
                
                # Extraire les adresses e-mail
                emails_sur_page = re.findall(motif_email, texte_page)
                
                for email in emails_sur_page:
                    email_propre = email.lower()
                    # Ignorer les e-mails qui sont en fait des noms d'images ou liés à des technologies web
                    if not email_propre.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.js', '.css', 'sentry.io')):
                        emails_trouves.add(email_propre)
            else:
                print(f"     -> Code d'erreur {reponse.status_code}.")
                
        except requests.exceptions.RequestException:
            print(f"     -> Impossible d'accéder à la page (Timeout ou sécurité).")

        # Petite pause pour ne pas surcharger les serveurs
        time.sleep(1)

    # 3. Affichage du résultat final
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
