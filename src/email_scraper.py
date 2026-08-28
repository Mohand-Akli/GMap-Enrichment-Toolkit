import os
import glob
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from ddgs import DDGS

# --- LISTES NOIRES (reprises de ta configuration) ---
domaines_a_fuir = [
    'facebook.com', 'tripadvisor', 'yelp', 'instagram', 'uber', 'deliveroo', 
    'takeaway', 'foursquare', 'pagesjaunes', 'tiktok', 'haliago', 'restoconnection', 
    'pagesdor', 'infobel', 'restaurantguru', 'data.gouv', 'just-eat', 'societe.com',
    'annuaire', 'waterlooplaza', 'lefigaro.fr', 'mappy.com', 'kompass.com', 
    'mon-resto-halal.com', 'thefork', 'eatbu.com', 'privateaser.com', 'marseille-tourisme',
    'latranchesurmer-tourisme', 'infiniment-charentes', 'zoekkinderopvang', 'helan.be',
    'service-public.gouv.fr', 'vdl.lu', 'sudinfo.be', 'companyweb.be', 'matablehalal',
    'visit.brussels', 'cotedazurfrance', 'visitvar', 'trouvetonresto', 'resto.be'
]

prefixes_a_fuir = [
    'app@', 'redaction@', 'webmaster@', 'support@', 'privacy@', 
    'abuse@', 'noreply@', 'be@', 'admcommunale@', 'contactpunt'
]

emails_invalides_exacts = {
    'name@example.com', 'nc@nc.fr', 'example@example.com', 'email@example.com', 'test@test.com'
}

motif_email = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'

def selectionner_fichier():
    """Identique à ta fonction d'origine pour choisir le CSV."""
    fichiers = glob.glob("data/*.csv") + glob.glob("*.csv")
    fichiers = list(set(fichiers))
    
    if not fichiers:
        print("❌ Aucun fichier .csv trouvé.")
        exit()
        
    print("\n--- Fichiers CSV disponibles ---")
    for i, fichier in enumerate(fichiers):
        print(f"[{i + 1}] {fichier}")
        
    while True:
        choix = input("\nEntrez le numéro du fichier à traiter : ")
        if choix.isdigit() and 1 <= int(choix) <= len(fichiers):
            fichier_choisi = fichiers[int(choix) - 1]
            break
        print("⚠️ Choix invalide.")
        
    base_name, ext = os.path.splitext(fichier_choisi)
    fichier_sortie = fichier_choisi if base_name.endswith("_avec_emails") else f"{base_name}_avec_emails{ext}"
    return fichier_choisi, fichier_sortie

def extraire_emails_de_url(url, timeout=5):
    """Télécharge la page via requests et extrait les emails."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    emails_trouves = set()
    try:
        reponse = requests.get(url, headers=headers, timeout=timeout, verify=False)
        reponse.raise_for_status()
        
        # BeautifulSoup pour extraire uniquement le texte visible ou les liens mailto:
        soup = BeautifulSoup(reponse.text, 'html.parser')
        
        # 1. Chercher dans les liens "mailto:" (très précis)
        for a_tag in soup.find_all('a', href=True):
            if a_tag['href'].startswith('mailto:'):
                emails_trouves.add(a_tag['href'].replace('mailto:', '').split('?')[0].strip())
        
        # 2. Chercher dans le texte global
        texte_page = soup.get_text(separator=' ')
        emails_sur_page = re.findall(motif_email, texte_page)
        emails_trouves.update(emails_sur_page)
        
        # Nettoyage et filtrage selon tes listes
        emails_propres = set()
        for email in emails_trouves:
            email_propre = email.lower().rstrip('.')
            if email_propre.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
                continue
            if email_propre in emails_invalides_exacts:
                continue
            if any(email_propre.startswith(prefix) for prefix in prefixes_a_fuir):
                continue
            if any(domaine in email_propre for domaine in domaines_a_fuir):
                continue
            emails_propres.add(email_propre)
            
        return emails_propres
    except Exception:
        return set()

def traiter_restaurant(nom_restaurant):
    """Recherche le resto sur DDG, visite les 3 premiers liens, et retourne les emails."""
    requete = f"{nom_restaurant} restaurant officiel contact"
    liens_a_visiter = []
    
    # Recherche via DuckDuckGo (sans navigateur)
    try:
        with DDGS() as ddgs:
            resultats = list(ddgs.text(requete, max_results=5))
            for res in resultats:
                url = res.get('href', '')
                if not any(domaine in url.lower() for domaine in domaines_a_fuir):
                    liens_a_visiter.append(url)
                    if len(liens_a_visiter) >= 3:
                        break
    except Exception:
        pass
        
    emails_finaux = set()
    for url in liens_a_visiter:
        emails = extraire_emails_de_url(url)
        emails_finaux.update(emails)
        
    return nom_restaurant, emails_finaux

def scraper_emails_rapide(fichier_entree, fichier_sortie):
    print(f"\n📂 Initialisation...")
    if os.path.exists(fichier_sortie):
        df = pd.read_csv(fichier_sortie)
    else:
        df = pd.read_csv(fichier_entree)

    # Vérification de sécurité adaptée à ton CSV
    if 'Restaurant_name' not in df.columns:
        print(f"❌ Erreur : La colonne 'Restaurant_name' est introuvable dans le CSV.")
        print(f"👉 Colonnes détectées dans ton fichier : {list(df.columns)}")
        return

    if 'mail' not in df.columns:
        df['mail'] = ""
    df['mail'] = df['mail'].astype(object)

    # Identifier les restaurants qui n'ont pas encore d'e-mail
    index_a_traiter = df[df['mail'].isna() | (df['mail'] == "")].index.tolist()
    
    if not index_a_traiter:
        print("✅ Tous les restaurants ont déjà un e-mail enregistré.")
        return
        
    print(f"🚀 Démarrage du scraping multi-thread pour {len(index_a_traiter)} restaurants...")

    # Exécution en parallèle (10 requêtes simultanées)
    with ThreadPoolExecutor(max_workers=10) as executor:
        # On utilise 'Restaurant_name' pour cibler la bonne colonne
        futures = {executor.submit(traiter_restaurant, df.at[idx, 'Restaurant_name']): idx for idx in index_a_traiter}
        
        for future in as_completed(futures):
            idx = futures[future]
            nom, emails = future.result()
            
            if emails:
                emails_str = ", ".join(emails)
                df.at[idx, 'mail'] = emails_str
                print(f"✅ {nom} : {emails_str}")
            else:
                print(f"❌ {nom} : Aucun e-mail")
                
            # Sauvegarde régulière
            df.to_csv(fichier_sortie, index=False, encoding='utf-8')

    print(f"\n🎉 Fin du scraping ! Fichier mis à jour : {fichier_sortie}")
    
if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    entree, sortie = selectionner_fichier()
    scraper_emails_rapide(entree, sortie)
