import requests
from bs4 import BeautifulSoup
import re
import time
from googlesearch import search

def google_top3_emails(nom_restaurant):
    print(f"\n🔍 [GOOGLE] Recherche pour : {nom_restaurant}")
    
    requete = f"{nom_restaurant} restaurant officiel contact"
    liens_trouves = []
    
    # 1. ÉTAPE : Chercher sur Google et prendre les 3 premiers résultats
    try:
        # On demande à Google les résultats, avec une pause de 3 secondes pour éviter le blocage
        resultats_bruts = search(requete, num_results=3, lang="fr", sleep_interval=3)
        # On s'assure de ne garder strictement que les 3 premiers
        liens_trouves = list(resultats_bruts)[:3] 
    except Exception as e:
        print(f"❌ Erreur lors de la recherche Google : {e}")
        return
        
    if not liens_trouves:
        print("⚠️ Google n'a renvoyé aucun résultat. (Votre IP est probablement bloquée par Google).")
        return
        
    # 2. ÉTAPE : Visiter ces 3 liens
    motif_email = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    emails_finaux = set()
    
    # Faux navigateur pour tromper la sécurité des sites
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # On ignore les annuaires qui vont polluer les résultats avec de faux e-mails
    domaines_a_fuir = ['facebook.com', 'tripadvisor', 'yelp', 'instagram', 'uber', 'deliveroo', 'takeaway', 'foursquare']

    for url in liens_trouves:
        print(f"  🌐 Visite de : {url}")
        
        if any(domaine in url.lower() for domaine in domaines_a_fuir):
            print("     -> ⏭️ Annuaire ou réseau social ignoré.")
            continue
            
        try:
            # On se connecte au site
            reponse = requests.get(url, headers=headers, timeout=10)
            if reponse.status_code == 200:
                soup = BeautifulSoup(reponse.text, 'html.parser')
                # 3. ÉTAPE : Extraire les adresses mails
                emails_sur_page = re.findall(motif_email, soup.text)
                
                for email in emails_sur_page:
                    email_propre = email.lower()
                    # On retire les faux e-mails (images)
                    if not email_propre.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
                        emails_finaux.add(email_propre)
            else:
                print(f"     -> ❌ Accès refusé par le site (Code {reponse.status_code})")
        except Exception:
            print(f"     -> ❌ Impossible d'accéder au site (Timeout).")
            
        # Pause obligatoire pour ne pas se faire bloquer par les sites
        time.sleep(2) 
        
    # Bilan final
    if emails_finaux:
        print(f"✅ E-mails trouvés pour {nom_restaurant} :")
        for e in emails_finaux:
            print(f"   - {e}")
    else:
        print(f"❌ Aucun e-mail trouvé sur ces 3 pages.")

# --- LANCEMENT ---
if __name__ == "__main__":
    liste_restaurants = [
        "La Seigneurie Verviers",
        "Chamas Tacos Liège",
        "Waffle Factory Tournai"
    ]
    
    for resto in liste_restaurants:
        google_top3_emails(resto)
        print("-" * 50)
