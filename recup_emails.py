from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import re
import time

def google_top3_selenium(liste_restaurants):
    print("🚀 Lancement du navigateur Chrome (Ne fermez pas la fenêtre qui va s'ouvrir)...")
    
    # 1. Configuration du vrai navigateur
    options = Options()
    # On ajoute des options pour essayer de masquer le fait que c'est un robot
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Installation automatique et lancement de Chrome
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    motif_email = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    domaines_a_fuir = ['facebook.com', 'tripadvisor', 'yelp', 'instagram', 'uber', 'deliveroo', 'takeaway', 'foursquare', 'pagesjaunes', 'tiktok']

    for nom_restaurant in liste_restaurants:
        print(f"\n🔍 [GOOGLE] Recherche pour : {nom_restaurant}")
        
        # 2. Chercher sur Google
        requete = f"{nom_restaurant} restaurant officiel contact"
        driver.get(f"https://www.google.com/search?q={requete}")
        
        # On attend 3 secondes pour laisser la page charger 
        # (Si Google affiche le bouton "Tout accepter" pour les cookies, vous aurez le temps de cliquer manuellement dessus la première fois)
        time.sleep(3) 
        
        # 3. Prendre les 3 premiers résultats
        liens_trouves = []
        try:
            # On cherche tous les liens dans la zone de recherche Google
            elements_liens = driver.find_elements(By.CSS_SELECTOR, "#search a")
            for element in elements_liens:
                href = element.get_attribute("href")
                
                # Filtrer les liens pour ne garder que les bons
                if href and href.startswith("http") and "google.com" not in href:
                    if "translate.goog" not in href and "webcache" not in href:
                        if not any(domaine in href.lower() for domaine in domaines_a_fuir):
                            if href not in liens_trouves:
                                liens_trouves.append(href)
                            # On s'arrête à 3 liens
                            if len(liens_trouves) >= 3:
                                break
        except Exception:
            print("❌ Erreur lors de la lecture de la page Google.")
            
        if not liens_trouves:
            print("⚠️ Google n'a renvoyé aucun lien (Ou vous devez remplir un Captcha à l'écran).")
            continue
            
        # 4. Visiter les 3 liens et extraire les e-mails
        emails_finaux = set()
        for url in liens_trouves:
            print(f"  🌐 Visite de : {url}")
            try:
                driver.get(url)
                time.sleep(3) # Pause pour laisser le site web du restaurant charger
                
                # Extraire tout le texte de la page
                texte_page = driver.find_element(By.TAG_NAME, "body").text
                emails_sur_page = re.findall(motif_email, texte_page)
                
                for email in emails_sur_page:
                    email_propre = email.lower()
                    if not email_propre.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
                        emails_finaux.add(email_propre)
            except Exception:
                print(f"     -> ❌ Impossible de charger ce site.")

        # 5. Affichage des résultats
        if emails_finaux:
            print(f"✅ E-mails trouvés pour {nom_restaurant} :")
            for e in emails_finaux:
                print(f"   - {e}")
        else:
            print(f"❌ Aucun e-mail trouvé sur ces 3 pages.")
            
        print("-" * 50)
        
    # On ferme le navigateur à la fin du script
    driver.quit()

# --- LANCEMENT ---
if __name__ == "__main__":
    liste_restaurants = [
        "La Seigneurie Verviers",
        "Chamas Tacos Liège",
        "Waffle Factory Tournai"
    ]
    
    google_top3_selenium(liste_restaurants)
