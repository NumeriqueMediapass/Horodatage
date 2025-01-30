import requests
import json
import os
import sys
import tempfile
import subprocess
from tkinter import messagebox
from version import VERSION, compare_versions

class Updater:
    def __init__(self):
        # URL du fichier JSON contenant les informations de version
        # À remplacer par l'URL de votre dépôt GitHub
        self.version_url = "https://raw.githubusercontent.com/votre-repo/Horodatage/main/version.json"
        self.download_url = "https://github.com/votre-repo/Horodatage/releases/download/"
        self.current_version = VERSION

    def check_for_updates(self):
        """Vérifie si une mise à jour est disponible"""
        try:
            response = requests.get(self.version_url, timeout=5)
            if response.status_code == 200:
                version_info = response.json()
                latest_version = version_info['version']
                
                if compare_versions(self.current_version, latest_version):
                    return {
                        'update_available': True,
                        'version': latest_version,
                        'changes': version_info.get('changes', ''),
                        'download_url': version_info.get('download_url', '')
                    }
            
            return {'update_available': False}
            
        except Exception as e:
            print(f"Erreur lors de la vérification des mises à jour : {str(e)}")
            return {'update_available': False}

    def download_update(self, download_url):
        """Télécharge la mise à jour"""
        try:
            response = requests.get(download_url, stream=True)
            if response.status_code == 200:
                # Créer un dossier temporaire pour la mise à jour
                with tempfile.NamedTemporaryFile(delete=False, suffix='.exe') as temp_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            temp_file.write(chunk)
                    return temp_file.name
            return None
        except Exception as e:
            print(f"Erreur lors du téléchargement : {str(e)}")
            return None

    def install_update(self, update_file):
        """Installe la mise à jour"""
        try:
            # Créer un script batch pour remplacer l'exécutable
            batch_path = os.path.join(tempfile.gettempdir(), 'update.bat')
            current_exe = sys.executable
            
            with open(batch_path, 'w') as batch:
                batch.write('@echo off\n')
                batch.write('timeout /t 2 /nobreak > nul\n')  # Attendre que l'application se ferme
                batch.write(f'copy /Y "{update_file}" "{current_exe}"\n')
                batch.write(f'start "" "{current_exe}"\n')
                batch.write(f'del "%~f0"\n')  # Auto-suppression du batch
            
            # Lancer le script batch et fermer l'application
            subprocess.Popen(['cmd', '/c', batch_path], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'installation : {str(e)}")
            return False

    def propose_update(self):
        """Vérifie et propose la mise à jour à l'utilisateur"""
        update_info = self.check_for_updates()
        
        if update_info['update_available']:
            message = f"Une nouvelle version ({update_info['version']}) est disponible !\n\n"
            if update_info['changes']:
                message += f"Changements :\n{update_info['changes']}\n\n"
            message += "Voulez-vous mettre à jour l'application ?"
            
            if messagebox.askyesno("Mise à jour disponible", message):
                # Télécharger la mise à jour
                update_file = self.download_update(update_info['download_url'])
                if update_file:
                    # Installer la mise à jour
                    if self.install_update(update_file):
                        messagebox.showinfo(
                            "Mise à jour",
                            "La mise à jour va être installée. L'application va redémarrer."
                        )
                        sys.exit(0)
                    else:
                        messagebox.showerror(
                            "Erreur",
                            "Impossible d'installer la mise à jour."
                        )
                else:
                    messagebox.showerror(
                        "Erreur",
                        "Impossible de télécharger la mise à jour."
                    )
