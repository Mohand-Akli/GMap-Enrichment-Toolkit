import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import urllib.parse
import time

# 1. Charger le fichier CSV
# (Assure-toi que ce nom correspond exactement au fichier dans ton dossier)
nom_fichier = "mon-resto-halal-com-complete-list - Numéro de téléphone et email.csv" 
df = pd.read_csv(nom_fichier)

# Créer la colonne "site web" si elle n'existe pas déjà
if 'site web' not in df.columns:
    df['site web'] = ""

# 2. Configurer Selenium
options = webdriver.ChromeOptions()
options.add_argument('--lang=fr')
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 4)       # Attente principale pour charger la page
short_wait = WebDriverWait(driver, 2) # Attente courte pour le deuxième élément

# 3. Parcourir chaque restaurant
for index, row in df.iterrows():
    resto_name = str(row['Restaurant_name'])
    address = str(row['adress'])
    
    print(f"\nRecherche en cours : {resto_name}...")
    
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
        # On cible le lien (balise 'a') qui contient l'attribut d'autorité ou le tooltip du site web
        xpath_website = "//a[contains(@data-item-id, 'authority') or contains(@data-tooltip, 'site Web') or contains(@data-tooltip, 'Site Web')]"
        website_element = short_wait.until(EC.presence_of_element_located((By.XPATH, xpath_website)))
        
        # Le lien réel est stocké dans l'attribut 'href'
        site_url = website_element.get_attribute("href") 
        df.at[index, 'site web'] = site_url
        print(f"  🌐 Site : {site_url}")
    except TimeoutException:
        df.at[index, 'site web'] = "Non trouvé"
        print("  🌐 Site : Non trouvé")
        
    # Petite pause pour éviter le blocage par Google
    time.sleep(2)

# 4. Sauvegarder dans un nouveau fichier
fichier_sortie = "mon-resto-halal-com_numeros_et_sites.csv"
df.to_csv(fichier_sortie, index=False)

driver.quit()
print(f"\n🎉 Terminé ! Le fichier mis à jour est sauvegardé sous : {fichier_sortie}")
