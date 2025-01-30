# Guide de Mise à Jour - Horodatage

Ce document explique comment mettre à jour l'application Horodatage et générer un nouvel exécutable.

## Prérequis

1. Python 3.10 ou supérieur installé
2. Les dépendances du projet installées :
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

## Configuration du Système de Mise à Jour

Le système de mise à jour automatique est en place mais nécessite une configuration :

1. Configuration du dépôt GitHub :
   - Créez un dépôt GitHub pour héberger les mises à jour
   - Le dépôt doit être public pour permettre l'accès au fichier version.json

2. Configuration de version.json :
   ```json
   {
       "version": "1.1.0",
       "changes": [
           "Liste des changements",
           "Un changement par ligne"
       ],
       "download_url": "URL_VERS_EXECUTABLE"
   }
   ```

3. Mise en place des releases :
   - Créez une release GitHub pour chaque version
   - Uploadez l'exécutable dans la release
   - Mettez à jour l'URL dans version.json

4. Test du système :
   - Vérifiez que version.json est accessible
   - Testez le téléchargement depuis l'URL
   - Validez le processus complet de mise à jour

### Notes Importantes

- L'URL dans version.json doit pointer vers un fichier .exe
- Le fichier version.json doit être à la racine du dépôt
- Les versions doivent suivre le format x.x.x
- L'URL de téléchargement doit être une URL directe

## Procédure de Mise à Jour de l'Exécutable

### 1. Sauvegarde

1. Faites une copie de l'exécutable actuel :
   - Renommez `Horodatage.exe` en `Horodatage_old.exe`
   - Gardez-le dans un dossier de sauvegarde

2. Sauvegardez les données importantes :
   - Dossier `Horodatage` contenant les certificats
   - Fichiers de configuration personnalisés

### 2. Installation de la Nouvelle Version

1. Téléchargez le nouvel exécutable depuis GitHub :
   - Allez sur la page des releases
   - Téléchargez la dernière version de `Horodatage.exe`

2. Installation :
   - Fermez l'ancienne version si elle est en cours d'exécution
   - Placez le nouvel exécutable à l'emplacement souhaité
   - Copiez le dossier `Horodatage` sauvegardé à côté du nouvel exécutable

3. Premier lancement :
   - Double-cliquez sur le nouvel exécutable
   - Vérifiez que la version affichée est la bonne
   - Testez que vos anciens certificats sont toujours accessibles

### 3. En Cas de Problème

1. Si la nouvelle version ne fonctionne pas :
   - Fermez l'application
   - Restaurez `Horodatage_old.exe`
   - Renommez-le en `Horodatage.exe`
   - Signalez le problème sur GitHub

2. Problèmes courants :
   - Erreur au démarrage : Vérifiez que tous les fichiers sont au bon endroit
   - Certificats manquants : Vérifiez le dossier `Horodatage`
   - Erreur de mise à jour : Vérifiez votre connexion internet

## Étapes de Mise à Jour

### 1. Modification du Code Source

- Modifiez les fichiers source selon vos besoins :
  - `main.py` : Programme principal
  - `theme.py` : Thème et styles
  - `timestamper.py` : Logique d'horodatage
  - `updater.py` : Système de mise à jour automatique
  - `version.py` : Gestion des versions

### 2. Mise à Jour des Versions

Lorsque vous changez la version de l'application, mettez à jour les fichiers suivants :

1. Dans `version.py` :
   ```python
   VERSION = "x.x.x"  # Modifiez la version ici
   ```

2. Dans `version.json` sur GitHub :
   ```json
   {
       "version": "x.x.x",
       "changes": "- Liste des changements",
       "download_url": "URL de téléchargement"
   }
   ```

3. Dans `file_version_info.txt` :
   ```python
   VSVersionInfo(
     ffi=FixedFileInfo(
       filevers=(x, x, x, 0),  # Exemple : (1, 0, 1, 0)
       prodvers=(x, x, x, 0),  # Doit correspondre à filevers
       ...
     ),
     kids=[
       StringFileInfo(
         [
         StringTable(
           u'040904B0',
           [
           ...
           StringStruct(u'FileVersion', u'x.x.x'),    # Exemple : '1.0.1'
           StringStruct(u'ProductVersion', u'x.x.x'),  # Même version
           ...
   ```

4. Dans `README.md` :
   ```markdown
   # Horodatage - Application d'Horodatage de Documents vx.x.x
   ```

### 3. Génération de l'Exécutable

1. Ouvrez un terminal dans le dossier du projet :
   ```bash
   cd chemin/vers/Horodatage
   ```

2. Lancez PyInstaller pour créer l'exécutable :
   ```bash
   pyinstaller --clean --onefile --windowed ^
               --icon=assets/icon.ico ^
               --add-data "assets;assets" ^
               --name Horodatage ^
               main.py
   ```

3. L'exécutable sera généré dans le dossier `dist`

### 4. Test de l'Application

1. Testez le nouvel exécutable dans `dist/Horodatage.exe`
2. Vérifiez que :
   - L'application démarre correctement
   - Le logo s'affiche
   - Toutes les fonctionnalités marchent
   - La nouvelle version est affichée
   - Les statistiques s'affichent correctement
   - Le système de mise à jour fonctionne
   - Le stockage personnalisé fonctionne

### 5. Publication de la Mise à Jour

1. Créez une nouvelle release sur GitHub :
   - Tag : vx.x.x
   - Titre : Version x.x.x
   - Description : Liste des changements
   - Fichiers : Horodatage.exe

2. Mettez à jour `version.json` sur GitHub avec :
   - La nouvelle version
   - L'URL de téléchargement de la release
   - La liste des changements

### 6. Documentation

1. Mettez à jour la documentation si nécessaire :
   - `README.md` : Instructions d'installation et d'utilisation
   - `MAJ.md` : Procédure de mise à jour
   - Commentaires dans le code

2. Ajoutez les changements importants dans un fichier `CHANGELOG.md`

### 7. Sauvegarde

1. Faites une sauvegarde du projet :
   - Code source
   - Exécutable
   - Documentation
   - Assets (images, icônes)

2. Créez une archive du projet complet

## Structure des Fichiers

```
Horodatage/
├── main.py              # Programme principal
├── theme.py            # Thème et styles
├── timestamper.py      # Logique d'horodatage
├── updater.py          # Système de mise à jour
├── version.py          # Gestion des versions
├── version.json        # Informations de version en ligne
├── requirements.txt    # Dépendances Python
├── horodatage.spec    # Configuration PyInstaller
├── file_version_info.txt # Informations de version Windows
├── README.md          # Documentation principale
├── MAJ.md            # Ce guide
├── assets/           # Ressources (logo, icône)
└── dist/             # Dossier contenant l'exécutable
    └── Horodatage.exe
```

## Résolution des Problèmes

1. Si l'exécutable ne se lance pas :
   - Vérifiez que toutes les dépendances sont installées
   - Relancez avec `pyinstaller --clean horodatage.spec`
   - Testez d'abord le code source avec `python main.py`

2. Si les assets ne sont pas inclus :
   - Vérifiez que le dossier `assets` existe
   - Vérifiez le chemin dans `horodatage.spec`

3. Si la version n'est pas mise à jour :
   - Vérifiez tous les fichiers mentionnés dans la section "Mise à Jour des Versions"
   - Utilisez toujours `--clean` avec PyInstaller

4. Si le système de mise à jour ne fonctionne pas :
   - Vérifiez que version.json est accessible sur GitHub
   - Vérifiez les URLs dans updater.py
   - Vérifiez la connexion internet

5. Si les statistiques ne s'affichent pas :
   - Vérifiez les widgets dans main.py
   - Vérifiez la mise à jour des compteurs

## Support

Pour toute question ou problème :
- Consultez la documentation sur [cc-sudavesnois.fr](https://cc-sudavesnois.fr)
- Contactez le support technique de la CC Sud-Avesnois
