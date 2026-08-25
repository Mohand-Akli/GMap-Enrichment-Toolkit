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
    
    # 1. Recherche via Yahoo (beaucoup plus tolérant pour les scripts)
    requete = f"{nom_restaurant} restaurant officiel contact"
    url_recherche = f"https://fr.search.yahoo.com/search?p={urllib.parse.quote(requete)}"
    
    # On simule un navigateur très standard
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        reponse = requests.get(url_recherche, headers=headers, timeout=10)
        
        if reponse.status_code == 200:
            soup = BeautifulSoup(reponse.text, 'html.parser')
            
            # Extraire les liens de la page Yahoo
            for a in soup.find_all('a', href=True):
                href = a['href']
                
                # Filtrer les liens internes de Yahoo et les pubs
                if href.startswith('http') and 'yahoo.com' not in href and 'yahoo.net' not in href:
                    
                    # Yahoo cache souvent le vrai lien derrière le paramètre 'RU='
                    if 'RU=' in href:
                        try:
                            # On découpe l'URL pour récupérer la vraie adresse
                            url_reelle = urllib.parse.unquote(href.split('RU=')[1].split('/RK=')[0])
                        except:
                            url_reelle = href
                    else:
                        url_reelle = href
                        
                    # Ajouter à la liste sans créer de doublons
                    if url_reelle not in resultats_recherche:
                        resultats_recherche.append(url_reelle)
                        
                # On s'arrête quand on a le nombre de résultats souhaité
                if len(resultats_recherche) >= nb_resultats:
                    break
        else:
            print(f"❌ Erreur d'accès à Yahoo (Code: {reponse.status_code})")
            return []
            
    except Exception as e:
        print(f"❌ Erreur lors de la recherche : {e}")
        return []

    if not resultats_recherche:
        print("Aucun site trouvé pour ce restaurant.")
        return []

    # 2. Visiter chaque lien trouvé
    domaines_ignores = ['facebook.com', 'tripadvisor.com', 'tripadvisor.be', 'yelp', 'instagram.com', 'deliveroo.be', 'ubereats.com', 'takeaway.com', 'resto.be', 'foursquare.com', 'pagesjaunes', 'just-eat', 'tiktok.com', 'youtube.com']
    
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
                
                # Extraire les adresses e-mail de la page
                emails_sur_page = re.findall(motif_email, texte_page)
                
                for email in emails_sur_page:
                    # On ignore les faux e-mails liés à des images
                    if not email.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
                        emails_trouves.add(email.lower())
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
