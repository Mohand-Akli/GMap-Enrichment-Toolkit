import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import time

def chercher_emails_restaurant(nom_restaurant, nb_resultats=3):
    print(f"\n🔍 Recherche de contacts pour : {nom_restaurant}")
    
    motif_email = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    emails_trouves = set()
    resultats_recherche = []
    
    # 1. Recherche directe sur la version HTML de DuckDuckGo
    requete = f"{nom_restaurant} restaurant officiel contact"
    url_recherche = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(requete)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    
    try:
        # On envoie la requête de recherche
        reponse = requests.get(url_recherche, headers=headers, timeout=10)
        
        if reponse.status_code == 200:
            soup = BeautifulSoup(reponse.text, 'html.parser')
            
            # Extraction des liens des résultats de recherche
            for a in soup.find_all('a', class_='result__url'):
                href = a.get('href')
                if href:
                    # DuckDuckGo obfusque parfois les liens avec "uddg="
                    if 'uddg=' in href:
                        url_reelle = urllib.parse.unquote(href.split('uddg=')[1].split('&')[0])
                    else:
                        url_reelle = href
                        
                    # On ne garde pas les liens internes à DuckDuckGo
                    if url_reelle.startswith('http'):
                        resultats_recherche.append(url_reelle)
                        
                if len(resultats_recherche) >= nb_resultats:
                    break
        else:
            print(f"❌ Erreur d'accès à DuckDuckGo (Code: {reponse.status_code})")
            return []
            
    except Exception as e:
        print(f"❌ Erreur lors de la recherche : {e}")
        return []

    if not resultats_recherche:
        print("Aucun site trouvé pour ce restaurant.")
        return []

    # 2. Visiter chaque lien trouvé
    for url in resultats_recherche:
        print(f"  🌐 Analyse de : {url}")
        
        # Ignorer les annuaires ou réseaux sociaux
        domaines_ignores = ['facebook.com', 'tripadvisor', 'yelp', 'instagram', 'deliveroo', 'ubereats', 'takeaway', 'resto.be', 'foursquare', 'pagesjaunes', 'just-eat']
        if any(domaine in url for domaine in domaines_ignores):
            print("     -> Site ignoré (Réseau social ou annuaire).")
            continue

        try:
            # Téléchargement de la page du restaurant
            reponse = requests.get(url, headers=headers, timeout=5)
            
            if reponse.status_code == 200:
                soup = BeautifulSoup(reponse.text, 'html.parser')
                texte_page = soup.text
                
                # Chercher les e-mails
                emails_sur_page = re.findall(motif_email, texte_page)
                
                for email in emails_sur_page:
                    if not email.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
                        emails_trouves.add(email.lower())
            else:
                print(f"     -> Code d'erreur {reponse.status_code}.")
                
        except requests.exceptions.RequestException:
            print(f"     -> Impossible d'accéder à la page (Timeout ou sécurité).")

        # Petite pause pour respecter les serveurs
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
