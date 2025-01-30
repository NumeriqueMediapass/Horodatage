# Horodatage - Application d'Horodatage de Documents v1.0.0

Une application moderne et sécurisée pour horodater vos documents avec certification RFC3161 et blockchain.

Développée pour la [CC Sud-Avesnois](https://cc-sudavesnois.fr)

## Fonctionnalités

- ✨ Interface utilisateur moderne et intuitive
- 📝 Renommage automatique des fichiers avec horodatage
- 🔐 Certification RFC3161 (par défaut)
- ⛓️ Stockage des preuves sur la blockchain (optionnel)
- 🔍 Vérification des documents horodatés
- 📊 Tableau de bord avec statistiques en temps réel
- 📋 Journal des opérations détaillé
- 🔄 Système de mise à jour automatique
- 📁 Gestion personnalisée du stockage
- 🎨 Design épuré avec thème personnalisé

## Installation

1. Téléchargez la dernière version :
   - Rendez-vous sur la [page des releases](lien-vers-releases)
   - Téléchargez `Horodatage.exe`

2. Installation :
   - Exécutez `Horodatage.exe`
   - L'application créera automatiquement ses dossiers de travail

3. Mise à jour :
   - L'application vérifie automatiquement les mises à jour au démarrage
   - Suivez les instructions à l'écran pour installer les mises à jour

## Utilisation

1. Pour horodater des documents :
   - Cliquez sur "Ajouter des fichiers"
   - Sélectionnez un ou plusieurs fichiers
   - Choisissez vos options d'horodatage :
     - Renommage automatique (activé par défaut)
     - Certification RFC3161 (activé par défaut)
     - Stockage blockchain (optionnel)
   - Cliquez sur "Horodater"

2. Pour vérifier un document :
   - Cliquez sur "Vérifier un document"
   - Sélectionnez le document à vérifier
   - Sélectionnez le certificat (.tsr) ou la preuve blockchain (.blockchain)
   - Les résultats de vérification s'afficheront dans la fenêtre

3. Gestion du stockage :
   - Cliquez sur "Parcourir" dans les paramètres
   - Sélectionnez le dossier de stockage souhaité
   - Les fichiers seront organisés automatiquement :
     - `/str` : Certificats RFC3161
     - `/blockchain` : Preuves blockchain

## Structure des fichiers

- `main.py` : Point d'entrée de l'application
- `timestamper.py` : Logique d'horodatage (RFC3161 et blockchain)
- `theme.py` : Configuration du thème moderne
- `updater.py` : Système de mise à jour automatique
- `version.py` : Gestion des versions
- `assets/` : Dossier contenant le logo
- `requirements.txt` : Dépendances Python

## Sécurité

- Les fichiers originaux ne sont jamais modifiés
- Utilisation de certificats RFC3161 standard
- Stockage sécurisé des preuves blockchain
- Vérification cryptographique des documents
- Mises à jour sécurisées via HTTPS

## Dépendances principales

- Python 3.10+
- tkinter : Interface graphique
- python-tsp : Protocole RFC3161
- web3 : Interaction blockchain
- cryptography : Fonctions cryptographiques
- Pillow : Gestion des images
- requests : Mises à jour automatiques

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer des améliorations
- Soumettre des pull requests

## Licence

Ce projet est sous licence [insérer licence]
