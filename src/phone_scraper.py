import os
import glob
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import urllib.parse
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
    if base_name.endswith("_enrichi_maps"):
        fichier_sortie = fichier_choisi
    else:
        fichier_sortie = f"{base_name}_enrichi_maps{ext}"
        
    return fichier_choisi, fichier_sortie

def scraper_infos_maps_csv(fichier_entree, fichier_sortie):
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

    # S'assurer que les colonnes de destination existent
    if 'phone number' not in df.columns:
        df['phone number'] = ""
    if 'site web' not in df.columns:
        df['site web'] = ""

    # 2. Configurer Selenium
    print("🚀 Lancement de Chrome...")
    options = webdriver.ChromeOptions()
    options.add_argument('--lang=fr')
    driver = webdriver.Chrome(options=options)
    
    wait = WebDriverWait(driver, 4)        
    short_wait = WebDriverWait(driver, 2) 

    # 3. Parcourir chaque restaurant
    try:
        for index, row in df.iterrows():
            # Sécurité : vérifier les noms de colonnes (ajuste si ton CSV utilise d'autres noms)
            col_name = 'Restaurant_name' if 'Restaurant_name' in df.columns else 'name'
            col_address = 'adress' if 'adress' in df.columns else 'address'
            
            resto_name = str(row.get(col_name, ''))
            address = str(row.get(col_address, ''))
            
            # Reprise : sauter si on a déjà traité cette ligne (on vérifie le téléphone)
            if pd.notna(row.get('phone number')) and str(row.get('phone number')).strip() != "":
                print(f"\n⏭️ [IGNORÉ] {resto_name} a déjà été traité.")
                continue
            
            print(f"\n📍 Recherche en cours : {resto_name}...")
            
            # Créer l'URL de recherche Google Maps
            query = f"{resto_name} {address}"
            url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(query)}"
            driver.get(url)
            
            # Gérer le bouton d'acceptation des cookies lors du premier tour
            if index == 0:
                try:
                    cookie_btn = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Tout accepter') or contains(., 'Accept all')]"))
                    )
                    cookie_btn.click()
                    time.sleep(1)
                except TimeoutException:
                    pass

            # --- RECHERCHE DU NUMÉRO DE TÉLÉPHONE ---
            try:
                xpath_phone = "//button[contains(@data-tooltip, 'numéro de téléphone') or contains(@data-item-id, 'phone:tel:')]//div[contains(@class, 'fontBodyMedium')]"
                phone_element = wait.until(EC.presence_of_element_located((By.XPATH, xpath_phone)))
                phone_number = phone_element.text
                df.at[index, 'phone number'] = phone_number 
                print(f"  📞 Tél  : {phone_number}")
            except TimeoutException:
                df.at[index, 'phone number'] = "Non trouvé"
                print("  ❌ Tél  : Non trouvé")
                
            # --- RECHERCHE DU SITE WEB ---
            try:
                xpath_website = "//a[contains(@data-item-id, 'authority') or contains(@data-tooltip, 'site Web') or contains(@data-tooltip, 'Site Web')]"
                website_element = short_wait.until(EC.presence_of_element_located((By.XPATH, xpath_website)))
                site_url = website_element.get_attribute("href") 
                df.at[index, 'site web'] = site_url 
                print(f"  🌐 Site : {site_url}")
            except TimeoutException:
                df.at[index, 'site web'] = "Non trouvé"
                print("  🌐 Site : Non trouvé")
                
            # Sauvegarde en temps réel
            df.to_csv(fichier_sortie, index=False, encoding='utf-8')
            print("  💾 Sauvegardé.")
            
            # Petite pause pour éviter le blocage par Google
            time.sleep(2)
            
    finally:
        driver.quit()
        print(f"\n🎉 Terminé ! Le fichier mis à jour est sauvegardé sous : {fichier_sortie}")

# --- LANCEMENT ---
if __name__ == "__main__":
    entree, sortie = selectionner_fichier()
    scraper_infos_maps_csv(entree, sortie)
