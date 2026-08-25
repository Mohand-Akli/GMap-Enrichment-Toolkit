import requests
from bs4 import BeautifulSoup
import re
from googlesearch import search
import time

def chercher_emails_restaurant(nom_restaurant, nb_resultats=3):
    print(f"\n🔍 Recherche de contacts pour : {nom_restaurant}")
    
    # Expression régulière pour détecter une adresse e-mail
    motif_email = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    emails_trouves = set() # Utilisation d'un 'set' pour éviter les doublons
    
    # 1. Rechercher le restaurant sur Google pour obtenir les premiers liens
    requete = f"{nom_restaurant} restaurant contact officiel"
    
    try:
        # Récupère les X premiers résultats de recherche
        resultats_recherche = list(search(requete, num=nb_resultats, stop=nb_resultats, pause=2.0))
    except Exception as e:
        print(f"❌ Erreur lors de la recherche Google : {e}")
        return []

    if not resultats_recherche:
        print("Aucun site trouvé pour ce restaurant.")
        return []

    # 2. Visiter chaque lien pour y extraire les e-mails
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for url in resultats_recherche:
        print(f"  🌐 Analyse de : {url}")
        
        # Ignorer les annuaires ou réseaux sociaux qui faussent souvent les résultats
        if any(domaine in url for domaine in ['facebook.com', 'tripadvisor', 'yelp', 'instagram', 'deliveroo', 'ubereats', 'takeaway']):
            print("     -> Site ignoré (Réseau social ou annuaire).")
            continue

        try:
            # Télécharger la page web avec un délai d'attente maximum de 5 secondes
            reponse = requests.get(url, headers=headers, timeout=5)
            
            # Si la page s'est bien chargée
            if reponse.status_code == 200:
                soup = BeautifulSoup(reponse.text, 'html.parser')
                texte_page = soup.text
                
                # Chercher les e-mails dans le texte de la page
                emails_sur_page = re.findall(motif_email, texte_page)
                
                for email in emails_sur_page:
                    # Petit filtre pour ignorer les faux e-mails liés aux images ou au code (ex: exemple@2x.png)
                    if not email.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                        emails_trouves.add(email.lower())
            else:
                print(f"     -> Code d'erreur {reponse.status_code} lors de l'accès au site.")
                
        except requests.exceptions.RequestException as e:
            print(f"     -> Impossible d'accéder à la page (Timeout ou sécurité).")

        # Petite pause pour ne pas surcharger les serveurs
        time.sleep(1)

    # 3. Afficher le résultat final
    if emails_trouves:
        print(f"✅ E-mails trouvés pour {nom_restaurant} :")
        for email in emails_trouves:
            print(f"   - {email}")
    else:
        print(f"❌ Aucun e-mail pertinent trouvé pour {nom_restaurant}.")
        
    return list(emails_trouves)


# --- EXEMPLE D'UTILISATION ---
if __name__ == "__main__":
    # Vous pouvez remplacer cette liste par les noms de votre fichier CSV
    restaurants_a_chercher = [
        "La Seigneurie Verviers",
        "Chamas Tacos Liège",
        "Waffle Factory Tournai"
    ]
    
    for resto in restaurants_a_chercher:
        chercher_emails_restaurant(resto)
        print("-" * 40)
