"""
Module de synchronisation cloud.

Gère la synchronisation des certificats avec OneDrive et Google Drive.
"""

import os
import json
import threading
from datetime import datetime
from pathlib import Path
from O365 import Account
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


class CloudSync:
    """Gère la synchronisation avec les services cloud."""
    
    def __init__(self, config_file="cloud_config.json"):
        """Initialise le gestionnaire de synchronisation.
        
        Args:
            config_file: Chemin vers le fichier de configuration
        """
        self.config_file = config_file
        self.config = self._load_config()
        self.onedrive = None
        self.gdrive = None
        
    def _load_config(self):
        """Charge la configuration depuis le fichier."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {
            'onedrive': {
                'client_id': '',
                'client_secret': '',
                'enabled': False,
                'last_sync': None
            },
            'gdrive': {
                'client_id': '',
                'client_secret': '',
                'enabled': False,
                'last_sync': None
            },
            'auto_sync': False,
            'sync_interval': 3600  # 1 heure
        }
        
    def save_config(self):
        """Sauvegarde la configuration."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
            
    def setup_onedrive(self, client_id, client_secret):
        """Configure OneDrive.
        
        Args:
            client_id: ID client OAuth
            client_secret: Secret client OAuth
        """
        try:
            self.config['onedrive']['client_id'] = client_id
            self.config['onedrive']['client_secret'] = client_secret
            
            # Initialiser OneDrive
            account = Account((client_id, client_secret))
            if account.authenticate():
                self.onedrive = account.storage()
                self.config['onedrive']['enabled'] = True
                self.save_config()
                return True
        except Exception as e:
            print(f"Erreur OneDrive : {str(e)}")
            return False
            
    def setup_gdrive(self, client_id, client_secret):
        """Configure Google Drive.
        
        Args:
            client_id: ID client OAuth
            client_secret: Secret client OAuth
        """
        try:
            self.config['gdrive']['client_id'] = client_id
            self.config['gdrive']['client_secret'] = client_secret
            
            # Initialiser Google Drive
            gauth = GoogleAuth()
            gauth.credentials = {
                'client_id': client_id,
                'client_secret': client_secret
            }
            
            if gauth.Authorize():
                self.gdrive = GoogleDrive(gauth)
                self.config['gdrive']['enabled'] = True
                self.save_config()
                return True
        except Exception as e:
            print(f"Erreur Google Drive : {str(e)}")
            return False
            
    def sync_to_cloud(self, local_path, callback=None):
        """Synchronise les fichiers vers le cloud.
        
        Args:
            local_path: Chemin local des fichiers à synchroniser
            callback: Fonction de callback pour le progrès
        """
        def _sync():
            try:
                # Synchroniser avec OneDrive
                if self.config['onedrive']['enabled']:
                    self._sync_to_onedrive(local_path, callback)
                    
                # Synchroniser avec Google Drive
                if self.config['gdrive']['enabled']:
                    self._sync_to_gdrive(local_path, callback)
                    
                # Mettre à jour la date de dernière synchro
                now = datetime.now().isoformat()
                self.config['onedrive']['last_sync'] = now
                self.config['gdrive']['last_sync'] = now
                self.save_config()
                
                if callback:
                    callback("Synchronisation terminée")
                    
            except Exception as e:
                if callback:
                    callback(f"Erreur : {str(e)}")
                    
        # Lancer la synchro dans un thread
        thread = threading.Thread(target=_sync)
        thread.daemon = True
        thread.start()
        
    def _sync_to_onedrive(self, local_path, callback=None):
        """Synchronise vers OneDrive."""
        if not self.onedrive:
            return
            
        try:
            # Créer le dossier distant
            remote_folder = "Horodatage/Certificats"
            folder = self.onedrive.create_folder(remote_folder)
            
            # Parcourir les fichiers locaux
            for root, _, files in os.walk(local_path):
                for file in files:
                    if file.endswith(('.tsr', '.blockchain')):
                        local_file = os.path.join(root, file)
                        
                        if callback:
                            callback(f"Upload vers OneDrive : {file}")
                            
                        # Upload du fichier
                        folder.upload_file(local_file)
                        
        except Exception as e:
            print(f"Erreur OneDrive : {str(e)}")
            
    def _sync_to_gdrive(self, local_path, callback=None):
        """Synchronise vers Google Drive."""
        if not self.gdrive:
            return
            
        try:
            # Créer le dossier distant
            folder_name = "Horodatage/Certificats"
            folder = self._get_or_create_folder(folder_name)
            
            # Parcourir les fichiers locaux
            for root, _, files in os.walk(local_path):
                for file in files:
                    if file.endswith(('.tsr', '.blockchain')):
                        local_file = os.path.join(root, file)
                        
                        if callback:
                            callback(f"Upload vers Google Drive : {file}")
                            
                        # Upload du fichier
                        f = self.gdrive.CreateFile({
                            'title': file,
                            'parents': [{'id': folder['id']}]
                        })
                        f.SetContentFile(local_file)
                        f.Upload()
                        
        except Exception as e:
            print(f"Erreur Google Drive : {str(e)}")
            
    def _get_or_create_folder(self, folder_path):
        """Récupère ou crée un dossier sur Google Drive."""
        current_folder = {'id': 'root'}
        
        for folder_name in folder_path.split('/'):
            # Chercher le dossier
            file_list = self.gdrive.ListFile({
                'q': f"'{current_folder['id']}' in parents and "
                     f"title='{folder_name}' and "
                     "mimeType='application/vnd.google-apps.folder' and "
                     "trashed=false"
            }).GetList()
            
            if file_list:
                current_folder = file_list[0]
            else:
                # Créer le dossier
                folder = self.gdrive.CreateFile({
                    'title': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [{'id': current_folder['id']}]
                })
                folder.Upload()
                current_folder = folder
                
        return current_folder
