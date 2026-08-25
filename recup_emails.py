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

    # Vérifier que la colonne 'name' existe bien
    if 'name' not in df.columns:
        print("❌ La colonne 'name' est introuvable dans le CSV.")
        return

    # Créer une colonne pour stocker nos découvertes
    if 'email_scrappe' not in df.columns:
        df['email_scrappe'] = ""

    # 2. Configuration de Chrome (Selenium)
    print("🚀 Lancement de Chrome...")
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    motif_email = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    domaines_a_fuir = ['facebook.com', 'tripadvisor', 'yelp', 'instagram', 'uber', 'deliveroo', 'takeaway', 'foursquare', 'pagesjaunes', 'tiktok']

    # 3. Boucle sur chaque restaurant du fichier
    for index, row in df.iterrows():
        nom_restaurant = row['name']
        
        # Sécurité : Si un e-mail a déjà été scrappé, on passe au suivant
        if pd.notna(row.get('email_scrappe')) and str(row.get('email_scrappe')).strip() != "":
            print(f"\n⏭️ [IGNORÉ] {nom_restaurant} a déjà un e-mail enregistré.")
            continue

        print(f"\n🔍 [GOOGLE] Recherche pour : {nom_restaurant}")
        requete = f"{nom_restaurant} restaurant officiel contact"
        driver.get(f"https://www.google.com/search?q={requete}")
        
        # Pause : laissez le temps de charger (ou de cliquer sur "Accepter" les cookies la 1ère fois)
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
                            # On s'arrête aux 3 PREMIERS LIENS
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
                time.sleep(3) # On laisse le site charger
                texte_page = driver.find_element(By.TAG_NAME, "body").text
                emails_sur_page = re.findall(motif_email, texte_page)
                
                for email in emails_sur_page:
                    email_propre = email.lower()
                    if not email_propre.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
                        emails_finaux.add(email_propre)
            except Exception:
                print(f"     -> ❌ Impossible de charger ce site.")

        # 4. Enregistrement des résultats
        if emails_finaux:
            emails_str = ", ".join(emails_finaux)
            df.at[index, 'email_scrappe'] = emails_str
            print(f"   ✅ E-mail(s) trouvé(s) : {emails_str}")
        else:
            print(f"   ❌ Aucun e-mail trouvé sur ces 3 pages.")

        # 5. Sauvegarde immédiate dans le CSV
        df.to_csv(nom_fichier, index=False, encoding='utf-8')
        print("   💾 Fichier mis à jour avec succès.")
        
    # Fin de la boucle
    driver.quit()
    print("\n🎉 Fin du scraping ! Toutes les données sont enregistrées dans votre fichier CSV.")

# --- LANCEMENT ---
if __name__ == "__main__":
    # Nom du fichier (doit être dans le même dossier que le script Python)
    nom_du_fichier = "repertoire_restaurants_halal_wallonie.csv"
    scraper_emails_selenium_csv(nom_du_fichier)
