import os
import glob
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import re
import time

def selectionner_fichier():
    """Génère un menu interactif pour choisir le fichier CSV à traiter."""
    fichiers = glob.glob("data/*.csv") + glob.glob("*.csv")
    fichiers = list(set(fichiers))
    
    if not fichiers:
        print("❌ Aucun fichier .csv trouvé dans le projet (dossier data/ ou racine).")
        exit()
        
    print("\n--- Fichiers CSV disponibles ---")
    for i, fichier in enumerate(fichiers):
        print(f"[{i + 1}] {fichier}")
        
    while True:
        choix = input("\nEntrez le numéro du fichier à traiter : ")
        if choix.isdigit() and 1 <= int(choix) <= len(fichiers):
            fichier_choisi = fichiers[int(choix) - 1]
            break
        print("⚠️ Choix invalide. Entrez un numéro correspondant à la liste.")
        
    # Génère le nom du fichier de sortie
    base_name, ext = os.path.splitext(fichier_choisi)
    if base_name.endswith("_avec_emails"):
        fichier_sortie = fichier_choisi
    else:
        fichier_sortie = f"{base_name}_avec_emails{ext}"
        
    return fichier_choisi, fichier_sortie

def scraper_emails_selenium_csv(fichier_entree, fichier_sortie):
    print(f"\n📂 Initialisation...")
    
    # 1. Charger le fichier CSV avec système de reprise
    if os.path.exists(fichier_sortie):
        df = pd.read_csv(fichier_sortie)
        print(f"✅ Reprise du fichier de sortie existant : {fichier_sortie}")
    else:
        try:
            df = pd.read_csv(fichier_entree)
            print(f"✅ Chargement de la source et création de : {fichier_sortie}")
        except FileNotFoundError:
            print(f"❌ Le fichier '{fichier_entree}' est introuvable.")
            return

    # Vérifier que la colonne 'name' existe bien
    if 'name' not in df.columns:
        print("❌ La colonne 'name' est introuvable dans le CSV.")
        return

    # Utiliser la colonne 'mail' pour stocker les résultats
    if 'mail' not in df.columns:
        df['mail'] = ""
        
    df['mail'] = df['mail'].astype(object)

    # 2. Configuration de Chrome (Selenium)
    print("🚀 Lancement de Chrome...")
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    motif_email = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    
    # LISTE NOIRE DES DOMAINES
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
    
    # LISTE NOIRE DES PRÉFIXES
    prefixes_a_fuir = [
        'app@', 'redaction@', 'webmaster@', 'support@', 'privacy@', 
        'abuse@', 'noreply@', 'be@', 'admcommunale@', 'contactpunt'
    ]
    
    # FAUX EMAILS EXACTS
    emails_invalides_exacts = {
        'name@example.com', 'nc@nc.fr', 'example@example.com', 'email@example.com', 'test@test.com'
    }

    # 3. Boucle sur chaque restaurant du fichier
    for index, row in df.iterrows():
        nom_restaurant = row['name']
        
        # Sécurité : Si un e-mail a déjà été scrappé, on passe au suivant
        if pd.notna(row.get('mail')) and str(row.get('mail')).strip() != "":
            print(f"\n⏭️ [IGNORÉ] {nom_restaurant} a déjà un e-mail enregistré.")
            continue

        print(f"\n🔍 [GOOGLE] Recherche pour : {nom_restaurant}")
        requete = f"{nom_restaurant} restaurant officiel contact"
        driver.get(f"https://www.google.com/search?q={requete}")
        
        time.sleep(3) 

        liens_trouves = []
        try:
            elements_liens = driver.find_elements(By.CSS_SELECTOR, "#search a")
            for element in elements_liens:
                href = element.get_attribute("href")
                if href and href.startswith("http") and "google.com" not in href:
                    if "translate.goog" not in href and "webcache" not in href:
                        if not any(domaine in href.lower() for domaine in domaines_a_fuir):
                            if href not in liens_trouves:
                                liens_trouves.append(href)
                            if len(liens_trouves) >= 3:
                                break
        except Exception:
            print("   ❌ Erreur lors de la lecture des résultats Google.")

        if not liens_trouves:
            print("   ⚠️ Google n'a renvoyé aucun lien exploitable.")
            continue

        emails_finaux = set()
        for url in liens_trouves:
            print(f"  🌐 Visite de : {url}")
            try:
                driver.get(url)
                time.sleep(3)
                texte_page = driver.find_element(By.TAG_NAME, "body").text
                emails_sur_page = re.findall(motif_email, texte_page)
                
                for email in emails_sur_page:
                    email_propre = email.lower().rstrip('.')
                    
                    if email_propre.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
                        continue
                    if email_propre in emails_invalides_exacts:
                        continue
                    if any(email_propre.startswith(prefix) for prefix in prefixes_a_fuir):
                        continue
                    if any(domaine in email_propre for domaine in domaines_a_fuir):
                        continue
                        
                    emails_finaux.add(email_propre)
                    
            except Exception:
                print(f"     -> ❌ Impossible de charger ce site.")

        # 4. Enregistrement des résultats
        if emails_finaux:
            emails_str = ", ".join(emails_finaux)
            df.at[index, 'mail'] = emails_str
            print(f"   ✅ E-mail(s) trouvé(s) : {emails_str}")
        else:
            print(f"   ❌ Aucun e-mail valide trouvé sur ces pages.")

        # 5. Sauvegarde dans le NOUVEAU fichier CSV
        df.to_csv(fichier_sortie, index=False, encoding='utf-8')
        print(f"   💾 Données sauvegardées dans {fichier_sortie}.")
        
    driver.quit()
    print(f"\n🎉 Fin du scraping ! Toutes les données sont enregistrées dans {fichier_sortie}.")

# --- LANCEMENT ---
if __name__ == "__main__":
    entree, sortie = selectionner_fichier()
    scraper_emails_selenium_csv(entree, sortie)
