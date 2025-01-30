"""
Script pour créer une nouvelle release de l'application.

Ce script :
1. Met à jour les fichiers de version
2. Crée l'exécutable
3. Prépare les fichiers pour la release
"""

import os
import json
import shutil
import subprocess
from version import VERSION

def update_version_files():
    """Met à jour les fichiers de version."""
    # Lire le fichier version.json actuel
    with open('version.json', 'r', encoding='utf-8') as f:
        version_data = json.load(f)
    
    # Mettre à jour l'URL de téléchargement
    version_data['download_url'] = (
        f"https://github.com/NumeriqueMediapass/Horodatage/releases/"
        f"download/v{VERSION}/Horodatage.exe"
    )
    
    # Sauvegarder les modifications
    with open('version.json', 'w', encoding='utf-8') as f:
        json.dump(version_data, f, indent=4, ensure_ascii=False)

def create_executable():
    """Crée l'exécutable avec PyInstaller."""
    # Nettoyer les anciens builds
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    # Créer le nouvel exécutable avec des options optimisées
    subprocess.run([
        'pyinstaller',
        '--clean',
        '--onefile',
        '--windowed',
        '--icon=assets/icon.ico',
        '--version-file=version_info.txt',
        '--add-data', 'assets;assets',
        '--name', 'Horodatage',
        '--uac-admin',  # Demander les droits admin
        '--noupx',      # Désactiver UPX pour réduire les faux positifs
        # Options pour réduire les faux positifs
        '--disable-windowed-traceback',
        '--collect-submodules=tkinter',
        '--collect-submodules=PIL',
        '--collect-data=certifi',
        # Exclure les modules inutiles
        '--exclude-module=_tkinter',
        '--exclude-module=tk',
        '--exclude-module=tcl',
        '--exclude-module=numpy',
        '--exclude-module=pandas',
        '--exclude-module=matplotlib',
        'main.py'
    ], check=True)

def prepare_release():
    """Prépare les fichiers pour la release."""
    # Créer le dossier de release
    release_dir = f'release_v{VERSION}'
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    os.makedirs(release_dir)
    
    # Copier les fichiers
    shutil.copy('dist/Horodatage.exe', release_dir)
    shutil.copy('README.md', release_dir)
    shutil.copy('version.json', release_dir)
    
    # Créer un fichier de vérification
    with open(os.path.join(release_dir, 'verification.txt'), 'w') as f:
        f.write(f"""Application Horodatage v{VERSION}
Éditeur : CC Sud-Avesnois
Site web : https://cc-sudavesnois.fr
SHA-256 : [À remplir après la génération]
""")
    
    print(f"\nRelease v{VERSION} préparée dans le dossier {release_dir}")
    print("\nÉtapes suivantes :")
    print("1. Créez une nouvelle release sur GitHub")
    print("2. Tag : v" + VERSION)
    print("3. Uploadez Horodatage.exe")
    print("4. Mettez à jour version.json sur GitHub")
    print("\nPour réduire les faux positifs antivirus :")
    print("1. Signez l'exécutable avec un certificat de signature de code")
    print("2. Soumettez l'exécutable à Microsoft pour analyse")
    print("3. Ajoutez le hash SHA-256 dans verification.txt")

if __name__ == '__main__':
    print(f"Création de la release v{VERSION}")
    
    print("\n1. Mise à jour des fichiers de version...")
    update_version_files()
    
    print("\n2. Création de l'exécutable...")
    create_executable()
    
    print("\n3. Préparation de la release...")
    prepare_release()
