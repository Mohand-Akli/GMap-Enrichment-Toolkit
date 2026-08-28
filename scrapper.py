import subprocess
import sys
import os

# Codes couleurs ANSI pour le terminal
class Color:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

def afficher_menu():
    print("\n" + Color.CYAN + "========================================" + Color.RESET)
    print(Color.BOLD + Color.HEADER + "       🚀 GESTIONNAIRE DE SCRAPING        " + Color.RESET)
    print(Color.CYAN + "========================================" + Color.RESET)
    print(f" {Color.YELLOW}[1]{Color.RESET} Pipeline global (Extraction villes + Fusion) {Color.BLUE}[main.py]{Color.RESET}")
    print(f" {Color.YELLOW}[2]{Color.RESET} Nettoyage et tri interactif des données {Color.BLUE}[data_processor.py]{Color.RESET}")
    print(f" {Color.YELLOW}[3]{Color.RESET} Scraping des e-mails {Color.BLUE}[email_scraper.py]{Color.RESET}")
    print(f" {Color.YELLOW}[4]{Color.RESET} Extraction Google Maps / Détails {Color.BLUE}[gmaps_scrapper.py]{Color.RESET}")
    print(f" {Color.YELLOW}[5]{Color.RESET} Récupération des numéros de téléphone {Color.BLUE}[phone_scraper.py]{Color.RESET}")
    print(f" {Color.YELLOW}[6]{Color.RESET} Recherche des numéros de TVA {Color.BLUE}[vat_finder.py]{Color.RESET}")
    print(f" {Color.RED}[0]{Color.RESET} Quitter")
    print(Color.CYAN + "========================================" + Color.RESET)

def executer_script(chemin_script):
    if not os.path.exists(chemin_script):
        print(f"\n{Color.RED}❌ Erreur : Le fichier '{chemin_script}' est introuvable.{Color.RESET}")
        return
    
    # On cible explicitement le python situé dans le dossier venv de ton projet
    python_venv = os.path.join(os.getcwd(), "venv", "bin", "python")
    if not os.path.exists(python_venv):
        python_venv = sys.executable  # Solution de repli si le venv n'est pas trouvé

    print(f"\n{Color.GREEN}🚀 Lancement de {chemin_script}...{Color.RESET}\n")
    try:
        subprocess.run([python_venv, chemin_script])
    except Exception as e:
        print(f"\n{Color.RED}❌ Une erreur est survenue lors de l'exécution : {e}{Color.RESET}")
        
def main():
    os.makedirs("data", exist_ok=True)
    
    while True:
        afficher_menu()
        choix = input(f"\n{Color.BOLD}Choisissez le numéro du programme à lancer : {Color.RESET}").strip()
        
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
            print(f"\n{Color.GREEN}✨ Fermeture du gestionnaire. À bientôt !{Color.RESET}\n")
            break
        else:
            print(f"\n{Color.YELLOW}⚠️ Choix invalide. Veuillez entrer un chiffre entre 0 et 6.{Color.RESET}")

if __name__ == "__main__":
    main()
