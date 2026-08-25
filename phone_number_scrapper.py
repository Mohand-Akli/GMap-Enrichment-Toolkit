import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import urllib.parse
import time

# 1. Charger le fichier CSV
nom_fichier = "mon-resto-halal-com-complete-list - Numéro de téléphone et email.csv"
df = pd.read_csv(nom_fichier)

# 2. Configurer Selenium
options = webdriver.ChromeOptions()
options.add_argument('--lang=fr') # Force la page en français pour cibler les éléments plus facilement
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 5) # Temps d'attente maximum de 5 secondes

# 3. Parcourir chaque restaurant
for index, row in df.iterrows():
    # Vérifier si la colonne "phone number" est déjà remplie pour gagner du temps
    if pd.notna(row['phone number']) and str(row['phone number']).strip() != "":
        continue
        
    resto_name = str(row['Restaurant_name'])
    address = str(row['adress'])
    
    # Créer l'URL de recherche Google Maps
    query = f"{resto_name} {address}"
    url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(query)}"
    driver.get(url)
    
    try:
        # Lors de la première recherche, gérer le bouton d'acceptation des cookies de Google
        if index == 0:
            try:
                cookie_btn = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Tout accepter') or contains(., 'Accept all')]"))
                )
                cookie_btn.click()
                time.sleep(1)
            except TimeoutException:
                pass # S'il n'y a pas de pop-up, on continue

        # Cibler l'élément contenant le numéro de téléphone. 
        # Google Maps utilise souvent un attribut data-tooltip spécifique ou data-item-id
        xpath_phone = "//button[contains(@data-tooltip, 'numéro de téléphone') or contains(@data-item-id, 'phone:tel:')]//div[contains(@class, 'fontBodyMedium')]"
        
        phone_element = wait.until(EC.presence_of_element_located((By.XPATH, xpath_phone)))
        phone_number = phone_element.text
        
        if phone_number:
            df.at[index, 'phone number'] = phone_number
            print(f"✅ Trouvé pour {resto_name} : {phone_number}")
            
    except TimeoutException:
        print(f"❌ Aucun numéro trouvé pour {resto_name}")
        df.at[index, 'phone number'] = "Non trouvé"
    except Exception as e:
        print(f"⚠️ Erreur avec {resto_name} : {e}")
        
    # Petite pause pour éviter que Google bloque l'IP pour requêtes abusives
    time.sleep(2)

# 4. Sauvegarder dans un nouveau fichier pour ne pas écraser l'original en cas de problème
fichier_sortie = "mon-resto-halal-com_numeros_maj.csv"
df.to_csv(fichier_sortie, index=False)

driver.quit()
print(f"\nTerminé ! Le fichier mis à jour est sauvegardé sous : {fichier_sortie}")
