import subprocess
import time

villes = ["Charleroi", "Liège", "Namur", "Mons", "La Louvière", "Tournai", "Verviers", "Mouscron", "Bruxelles"]
processus = []

print("Lancement des extractions en parallèle...")

for ville in villes:
    fichier = f"halal_{ville.replace(' ', '_')}_parallele.csv"
    commande = ["python3", "main.py", "-s", f"Restaurant halal {ville}", "-t", "300", "-o", fichier]
    
    # Popen lance la commande en arrière-plan sans bloquer la suite du script
    p = subprocess.Popen(commande)
    processus.append(p)
    
    # Petite pause de 2 secondes entre chaque lancement pour ne pas surcharger le processeur d'un coup
    time.sleep(2) 

# Le script maître attend que tous les sous-processus aient terminé leur travail
for p in processus:
    p.wait()

print("Toutes les extractions sont terminées !")
