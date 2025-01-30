"""
Module de gestion des mises à jour de l'application.

Ce module fournit les fonctionnalités pour :
- Vérifier la disponibilité des mises à jour
- Télécharger les nouvelles versions
- Installer les mises à jour automatiquement
- Gérer les dialogues de mise à jour
"""

import requests
import json
import os
import sys
import tempfile
import subprocess
from tkinter import messagebox
from version import VERSION, compare_versions


class Updater:
    """Gère les mises à jour automatiques de l'application."""
    
    def __init__(self):
        """Initialise le gestionnaire de mises à jour."""
        self.version_url = (
            "https://raw.githubusercontent.com/NumeriqueMediapass/"
            "Horodatage/main/version.json"
        )
        self.current_version = VERSION

    def check_for_updates(self):
        """Vérifie si une mise à jour est disponible.
        
        Returns:
            dict: Informations sur la mise à jour disponible ou None si erreur.
        """
        try:
            response = requests.get(self.version_url, timeout=5)
            response.raise_for_status()
            
            if response.status_code == 200:
                version_info = response.json()
                latest_version = version_info['version']
                
                if compare_versions(self.current_version, latest_version):
                    return {
                        'update_available': True,
                        'version': latest_version,
                        'changes': version_info.get('changes', []),
                        'download_url': version_info.get('download_url', ''),
                        'required': version_info.get('required', False)
                    }
            return {'update_available': False}
            
        except Exception as e:
            print(f"Erreur lors de la vérification des mises à jour : {str(e)}")
            return {'update_available': False}

    def download_update(self, download_url):
        """Télécharge la nouvelle version de l'application.
        
        Args:
            download_url (str): URL de téléchargement de la mise à jour.
            
        Returns:
            str: Chemin vers le fichier téléchargé ou None si erreur.
        """
        try:
            # Créer un fichier temporaire avec l'extension .exe
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix='.exe',
                prefix='horodatage_update_'
            ) as tmp:
                # Télécharger avec une barre de progression
                response = requests.get(download_url, stream=True)
                response.raise_for_status()
                
                # Écrire le fichier par morceaux
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        tmp.write(chunk)
                
                return tmp.name
                
        except Exception as e:
            print(f"Erreur lors du téléchargement : {str(e)}")
            return None

    def install_update(self, file_path):
        """Installe la nouvelle version de l'application.
        
        Args:
            file_path (str): Chemin vers le fichier d'installation.
            
        Returns:
            bool: True si l'installation réussit, False sinon.
        """
        try:
            if not os.path.exists(file_path):
                return False

            if sys.platform == 'win32':
                # Lancer le nouvel exécutable
                subprocess.Popen([file_path])
                # Quitter l'application actuelle
                sys.exit(0)
                
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'installation : {str(e)}")
            return False

    def update_available_dialog(self, version_info):
        """Affiche une boîte de dialogue pour la mise à jour.
        
        Args:
            version_info (dict): Informations sur la mise à jour.
            
        Returns:
            bool: True si l'utilisateur accepte la mise à jour, False sinon.
        """
        # Préparer le message
        changes = "\n".join(
            f"• {change}" for change in version_info.get('changes', [])
        )
        
        message = (
            f"Une nouvelle version {version_info['version']} est disponible !\n\n"
            f"Changements :\n{changes}\n\n"
            "Voulez-vous installer cette mise à jour ?"
        )

        # Si la mise à jour est obligatoire
        if version_info.get('required', False):
            messagebox.showwarning(
                "Mise à jour requise",
                "Cette mise à jour est obligatoire pour continuer à utiliser "
                "l'application.\n\nL'installation va commencer..."
            )
            return True

        # Sinon, demander confirmation
        return messagebox.askyesno(
            "Mise à jour disponible",
            message,
            icon=messagebox.INFO
        )
