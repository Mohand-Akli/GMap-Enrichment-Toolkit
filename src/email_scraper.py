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

# On réduit la liste noire pour scanner plus de liens (on bloque surtout les gros annuaires inutiles)
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
    fichier_sortie = fichier_choisi if base_name.endswith("_avec_emails") else f"{base_name
