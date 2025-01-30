import hashlib
import requests
import json
from datetime import datetime
import pytz
import os
import shutil

class TimeStamper:
    def __init__(self, storage_path=None, blockchain_path=None, tsa_url=None, ethereum_node_url=None):
        self.storage_path = storage_path
        self.blockchain_path = blockchain_path
        self.tsa_url = tsa_url or "http://timestamp.digicert.com"
        self.ethereum_node_url = ethereum_node_url or "https://mainnet.infura.io/v3/YOUR-PROJECT-ID"
    
    def calculate_hash(self, file_path):
        """Calcule le hash SHA256 d'un fichier"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.digest()

    def timestamp_file(self, file_path, options):
        """Horodate un fichier avec les options spécifiées"""
        try:
            # Obtenir le timestamp actuel
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Obtenir le chemin et le nom du fichier
            directory = os.path.dirname(file_path)
            filename = os.path.basename(file_path)
            name, ext = os.path.splitext(filename)
            
            # Renommer le fichier si l'option est activée
            if options.get('rename', False):
                new_filename = f"{name}_{timestamp}{ext}"
                if self.storage_path:
                    new_path = os.path.join(self.storage_path, new_filename)
                else:
                    new_path = os.path.join(directory, new_filename)
                shutil.copy2(file_path, new_path)
                file_to_certify = new_path
            else:
                file_to_certify = file_path
            
            # Créer le certificat RFC3161 si l'option est activée
            if options.get('rfc3161', False):
                cert_data = self.get_rfc3161_timestamp(file_to_certify, options)
            
            # Stocker dans la blockchain si l'option est activée
            if options.get('blockchain', False):
                blockchain_data = self.store_in_blockchain(file_to_certify, options)
            
            return {
                'timestamp': timestamp,
                'original_file': file_path,
                'timestamped_file': file_to_certify if options.get('rename', False) else None,
                'rfc3161_cert': cert_data if options.get('rfc3161', False) else None,
                'blockchain_proof': blockchain_data if options.get('blockchain', False) else None
            }
            
        except Exception as e:
            raise Exception(f"Erreur lors de l'horodatage : {str(e)}")

    def get_rfc3161_timestamp(self, file_path, options={}):
        """Obtient un certificat d'horodatage RFC3161"""
        try:
            file_hash = self.calculate_hash(file_path)
            
            # Simuler l'obtention d'un certificat RFC3161
            # Dans une implémentation réelle, il faudrait faire une requête à un service TSA
            cert_data = {
                'timestamp': datetime.now(pytz.UTC).isoformat(),
                'hash': file_hash.hex(),
                'algorithm': 'SHA256',
                'tsa_url': self.tsa_url
            }
            
            # Utiliser le chemin de stockage spécifié
            if self.storage_path:
                cert_path = os.path.join(self.storage_path, f"{os.path.basename(file_path)}.tsr")
            else:
                cert_path = f"{file_path}.tsr"
                
            with open(cert_path, 'w') as f:
                json.dump(cert_data, f, indent=4)
            
            return cert_data
            
        except Exception as e:
            raise Exception(f"Erreur lors de l'horodatage RFC3161: {str(e)}")

    def store_in_blockchain(self, file_path, options={}):
        """Simule le stockage du hash du fichier dans la blockchain"""
        try:
            file_hash = self.calculate_hash(file_path)
            
            # Simuler le stockage dans la blockchain
            # Dans une implémentation réelle, il faudrait interagir avec un nœud Ethereum
            proof = {
                'timestamp': datetime.now(pytz.UTC).isoformat(),
                'file_hash': file_hash.hex(),
                'blockchain': 'ethereum',
                'network': 'mainnet'
            }
            
            # Utiliser le chemin de stockage spécifié
            if self.blockchain_path:
                proof_path = os.path.join(self.blockchain_path, f"{os.path.basename(file_path)}.blockchain")
            else:
                proof_path = f"{file_path}.blockchain"
                
            with open(proof_path, 'w') as f:
                json.dump(proof, f, indent=4)
            
            return proof
            
        except Exception as e:
            raise Exception(f"Erreur lors du stockage blockchain: {str(e)}")

    def verify_rfc3161(self, file_path, cert_path):
        """Vérifie un certificat d'horodatage RFC3161"""
        try:
            current_hash = self.calculate_hash(file_path).hex()
            
            with open(cert_path, 'r') as f:
                cert_data = json.load(f)
            
            return current_hash == cert_data['hash']
            
        except Exception as e:
            raise Exception(f"Erreur lors de la vérification RFC3161: {str(e)}")

    def verify_blockchain(self, file_path, proof_path):
        """Vérifie une preuve blockchain"""
        try:
            current_hash = self.calculate_hash(file_path).hex()
            
            with open(proof_path, 'r') as f:
                proof_data = json.load(f)
            
            return current_hash == proof_data['file_hash']
            
        except Exception as e:
            raise Exception(f"Erreur lors de la vérification blockchain: {str(e)}")
