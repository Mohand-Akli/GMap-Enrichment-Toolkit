import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import re
import time

def scraper_emails_selenium_csv(nom_fichier):
    print(f"📂 Chargement du fichier : {nom_fichier}")
    
    # 1. Charger le fichier CSV
    try:
        df = pd.read_csv(nom_fichier)
    except FileNotFoundError:
        print(f"❌ Le fichier '{nom_fichier}' est introuvable. Vérifiez qu'il est dans le même dossier.")
        return

    # Vérifier que la colonne 'Restaurant_name' existe bien
    if 'Restaurant_name' not in df.columns:
        print("❌ La colonne 'Restaurant_name' est introuvable dans le CSV.")
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
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    motif_email = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    
    # LISTE NOIRE DES DOMAINES (Annuaires, réseaux sociaux, plateformes, portails publics)
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
    
    # LISTE NOIRE DES PRÉFIXES (Comptes génériques/techniques)
    prefixes_a_fuir = [
        'app@', 'redaction@', 'webmaster@', 'support@', 'privacy@', 
        'abuse@', 'noreply@', 'be@', 'admcommunale@', 'contactpunt'
    ]
    
    # FAUX EMAILS EXACTS À IGNORER (Templates et placeholders)
    emails_invalides_exacts = {
        'name@example.com', 'nc@nc.fr', 'example@example.com', 'email@example.com', 'test@test.com'
    }

    # 3. Boucle sur chaque restaurant du fichier
    for index, row in df.iterrows():
        nom_restaurant = row['Restaurant_name']
        
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
                        # On ignore le lien si son URL contient un domaine banni
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
                    
                    # 1. Ignorer les formats de fichiers d'images
                    if email_propre.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
                        continue
                    # 2. Ignorer les adresses modèles / bidons
                    if email_propre in emails_invalides_exacts:
                        continue
                    # 3. Ignorer les préfixes techniques
                    if any(email_propre.startswith(prefix) for prefix in prefixes_a_fuir):
                        continue
                    # 4. Ignorer les emails rattachés à des domaines tiers ou annuaires
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

        # 5. Sauvegarde immédiate dans le CSV
        df.to_csv(nom_fichier, index=False, encoding='utf-8')
        print("   💾 Fichier mis à jour avec succès.")
        
    driver.quit()
    print("\n🎉 Fin du scraping ! Toutes les données sont enregistrées dans votre fichier CSV.")

# --- LANCEMENT ---
if __name__ == "__main__":
    # Nom du fichier mis à jour selon votre demande
    nom_du_fichier = "guide-michelin-com-2026-07-12 (1) - Copie de Sheet1 (1).csv"
    scraper_emails_selenium_csv(nom_du_fichier)
