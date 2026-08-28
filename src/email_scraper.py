import os
import glob
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from ddgs import DDGS
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURATION ---
motif_email = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'

# On réduit la liste noire pour scanner plus de liens
domaines_a_fuir = [
    'tripadvisor', 'yelp', 'uber', 'deliveroo', 'takeaway', 'just-eat', 'thefork'
]

prefixes_a_fuir = ['app@', 'redaction@', 'webmaster@', 'support@', 'privacy@', 'abuse@', 'noreply@']
emails_invalides = {'name@example.com', 'email@example.com', 'test@test.com', 'contact@restaurant.com'}

def selectionner_fichier():
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

def nettoyer_emails(liste_emails):
    """Filtre les faux e-mails et les extensions d'images."""
    propres = set()
    for email in liste_emails:
        email_clean = email.lower().rstrip('.').strip()
        if email_clean.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.wixpress.com')):
            continue
        if email_clean in emails_invalides:
            continue
        if any(email_clean.startswith(prefix) for prefix in prefixes_a_fuir):
            continue
        propres.add(email_clean)
    return propres

def extraire_emails_de_url(url, timeout=5):
    """Télécharge une page web et extrait les emails du code HTML."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        reponse = requests.get(url, headers=headers, timeout=timeout, verify=False)
        reponse.raise_for_status()
        
        soup = BeautifulSoup(reponse.text, 'html.parser')
        emails_trouves = set()
        
        # 1. Chercher dans les liens mailto
        for a in soup.find_all('a', href=True):
            if a['href'].startswith('mailto:'):
                emails_trouves.add(a['href'].replace('mailto:', '').split('?')[0].strip())
                
        # 2. Chercher dans le texte global
        emails_trouves.update(re.findall(motif_email, soup.get_text(separator=' ')))
        
        return nettoyer_emails(emails_trouves)
    except Exception:
        return set()

def traiter_restaurant(nom_restaurant, adresse, site_web):
    emails_finaux = set()
    
    # ÉTAPE 1 : Si on a déjà un site web dans le CSV, on le scrape en priorité !
    if pd.notna(site_web) and str(site_web).startswith('http'):
        emails_finaux.update(extraire_emails_de_url(site_web))
        
    # ÉTAPE 2 : Recherche sur DuckDuckGo (avec l'adresse pour être précis)
    if not emails_finaux:
        adresse_str = str(adresse) if pd.notna(adresse) else ""
        requete = f'"{nom_restaurant}" {adresse_str} email contact'
        
        try:
            with DDGS() as ddgs:
                resultats = list(ddgs.text(requete, max_results=5))
                liens_visites = 0
                
                for res in resultats:
                    # Chercher l'email DIRECTEMENT dans la description de la recherche
                    texte_snippet = res.get('body', '') + " " + res.get('title', '')
                    emails_snippet = re.findall(motif_email, texte_snippet)
                    emails_finaux.update(nettoyer_emails(emails_snippet))
                    
                    # Si on n'a toujours rien, on visite le lien (max 2 liens)
                    url = res.get('href', '')
                    if not emails_finaux and liens_visites < 2:
                        if not any(d in url.lower() for d in domaines_a_fuir) and 'facebook.com' not in url.lower() and 'instagram.com' not in url.lower():
                            emails_finaux.update(extraire_emails_de_url(url))
                            liens_visites += 1
        except Exception:
            pass
            
    return nom_restaurant, emails_finaux

def scraper_emails_rapide(fichier_entree, fichier_sortie):
    print(f"\n📂 Initialisation...")
    df = pd.read_csv(fichier_sortie) if os.path.exists(fichier_sortie) else pd.read_csv(fichier_entree)

    # Sécurité pour les colonnes
    if 'name' not in df.columns:
        print(f"❌ Erreur : Colonne 'name' introuvable.")
        print(f"👉 Colonnes détectées dans ton fichier : {list(df.columns)}")
        return

    # S'assurer que les colonnes address et website existent (même vides) pour éviter les crashs
    if 'address' not in df.columns: df['address'] = ""
    if 'website' not in df.columns: df['website'] = ""
    if 'mail' not in df.columns: df['mail'] = ""
    
    df['mail'] = df['mail'].astype(object)
    index_a_traiter = df[df['mail'].isna() | (df['mail'] == "")].index.tolist()
    
    if not index_a_traiter:
        print("✅ Tous les restaurants ont déjà un e-mail.")
        return
        
    print(f"🚀 Démarrage du scraping agressif pour {len(index_a_traiter)} restaurants...")

    with ThreadPoolExecutor(max_workers=10) as executor:
        # On passe le nom, l'adresse et le site web à la fonction
        futures = {
            executor.submit(
                traiter_restaurant, 
                df.at[idx, 'name'], 
                df.at[idx, 'address'], 
                df.at[idx, 'website']
            ): idx for idx in index_a_traiter
        }
        
        for future in as_completed(futures):
            idx = futures[future]
            nom, emails = future.result()
            
            if emails:
                emails_str = ", ".join(emails)
                df.at[idx, 'mail'] = emails_str
                print(f"✅ {nom} : {emails_str}")
            else:
                print(f"❌ {nom} : Aucun e-mail")
                
            df.to_csv(fichier_sortie, index=False, encoding='utf-8')

    print(f"\n🎉 Fin du scraping ! Fichier mis à jour : {fichier_sortie}")

if __name__ == "__main__":
    entree, sortie = selectionner_fichier()
    scraper_emails_rapide(entree, sortie)
