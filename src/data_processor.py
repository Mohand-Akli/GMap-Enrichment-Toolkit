import os
import glob
import pandas as pd
import subprocess
import urllib.parse

def selectionner_fichier():
    """Menu interactif pour choisir le fichier CSV à traiter."""
    fichiers = glob.glob("data/*.csv") + glob.glob("*.csv")
    fichiers = list(set(fichiers))
    
    if not fichiers:
        print("❌ Aucun fichier .csv trouvé dans le projet.")
        exit()
        
    print("\n--- Fichiers CSV disponibles pour le tri ---")
    for i, fichier in enumerate(fichiers):
        print(f"[{i + 1}] {fichier}")
        
    while True:
        choix = input("\nEntrez le numéro du fichier à trier : ")
        if choix.isdigit() and 1 <= int(choix) <= len(fichiers):
            fichier_choisi = fichiers[int(choix) - 1]
            break
        print("⚠️ Choix invalide. Entrez un numéro valide.")
        
    base_name, ext = os.path.splitext(fichier_choisi)
    fichier_sortie = f"{base_name}_trie_manuel{ext}"
    return fichier_choisi, fichier_sortie

def nettoyer_interactivement():
    entree, sortie = selectionner_fichier()
    
    print(f"\n📂 Chargement de {entree}...")
    try:
        df = pd.read_csv(entree)
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier : {e}")
        return

    if os.path.exists(sortie):
        reprendre = input(f"Un fichier de sauvegarde trié existe déjà ({sortie}). Veux-tu reprendre le tri ? (o/n) : ").strip().lower()
        if reprendre == 'o':
            df_sortie = pd.read_csv(sortie)
            print(f"✅ Reprise du tri (déjà {len(df_sortie)} lignes traitées).")
        else:
            df_sortie = pd.DataFrame(columns=df.columns)
    else:
        df_sortie = pd.DataFrame(columns=df.columns)

    print("\n" + "="*50)
    print(" 🛠️ TRI INTERACTIF AVEC OUVERTURE GOOGLE MAPS")
    print(" 🌐 Le navigateur va s'ouvrir sur chaque restaurant.")
    print(" Commandes : [g]arder | [s]upprimer | [q]uitter")
    print("="*50 + "\n")

    for index, row in df.iterrows():
        nom = row.get('name', row.get('Restaurant_name', 'Inconnu'))
        adresse = row.get('address', row.get('adress', 'Adresse inconnue'))
        
        print(f"\n--- Ligne {index + 1} / {len(df)} ---")
        print(f"🍽️ Nom     : {nom}")
        print(f"📍 Adresse : {adresse}")
        if 'phone_number' in row and pd.notna(row['phone_number']):
            print(f"📞 Tél     : {row['phone_number']}")
        if 'website' in row and pd.notna(row['website']):
            print(f"🌐 Site    : {row['website']}")
            
        # 🌐 Ouverture automatique de Google Maps sur Mac pour ce restaurant précis
        query = f"{nom} {adresse}"
        url_maps = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(query)}"
        subprocess.run(["open", url_maps])
        
        choix = input("\n👉 Garder ce restaurant ? (g = garder / s = supprimer / q = quitter) : ").strip().lower()
        
        if choix == 'g':
            df_sortie = pd.concat([df_sortie, pd.DataFrame([row])], ignore_index=True)
            print("  ✅ [Conservé]")
        elif choix == 's':
            print("  ❌ [Supprimé]")
        elif choix == 'q':
            print("\n💾 Sauvegarde intermédiaire et fermeture...")
            break
        else:
            df_sortie = pd.concat([df_sortie, pd.DataFrame([row])], ignore_index=True)
            print("  ✅ [Conservé par défaut]")
            
        df_sortie.to_csv(sortie, index=False, encoding='utf-8')

    print(f"\n🎉 Tri terminé ! Fichier propre enregistré sous : {sortie}")
    print(f"📊 Total de restaurants gardés : {len(df_sortie)} sur {len(df)} examinés.")

if __name__ == "__main__":
    nettoyer_interactivement()
