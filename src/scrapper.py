import subprocess
import sys
import os

def afficher_menu():
    print("\n========================================")
    print("       GESTIONNAIRE DE SCRAPING         ")
    print("========================================")
    print("[1] Pipeline global (Extraction villes + Fusion) - main.py")
    print("[2] Nettoyage et tri interactif des données - data_processor.py")
    print("[3] Scraping des e-mails - email_scraper.py")
    print("[4] Extraction Google Maps / Détails des lieux - gmaps_scrapper.py")
    print("[5] Récupération des numéros de téléphone - phone_scraper.py")
    print("[6] Recherche des numéros de TVA - vat_finder.py")
    print("[0] Quitter")
    print("========================================")

def executer_script(chemin_script):
    if not os.path.exists(chemin_script):
        print(f"\n❌ Erreur : Le fichier '{chemin_script}' est introuvable.")
        return
    
    print(f"\n🚀 Lancement de {chemin_script}...\n")
    try:
        subprocess.run([sys.executable, chemin_script])
    except Exception as e:
        print(f"\n❌ Une erreur est survenue lors de l'exécution : {e}")

def main():
    os.makedirs("data", exist_ok=True)
    
    while True:
        afficher_menu()
        choix = input("\nChoisissez le numéro du programme à lancer : ").strip()
        
        if choix == "1":
            executer_script("src/main.py")
        elif choix == "2":
            executer_script("src/data_processor.py")
        elif choix == "3":
            executer_script("src/email_scraper.py")
        elif choix == "4":
            executer_script("src/gmaps_scrapper.py")
        elif choix == "5":
            executer_script("src/phone_scraper.py")
        elif choix == "6":
            executer_script("src/vat_finder.py")
        elif choix == "0":
            print("\nFermeture du gestionnaire. À bientôt !")
            break
        else:
            print("\n⚠️ Choix invalide. Veuillez entrer un chiffre entre 0 et 6.")

if __name__ == "__main__":
    main()
