"""
Application d'horodatage de documents avec certification RFC3161 et blockchain.

Cette application permet de :
1. Horodater des documents avec certification RFC3161
2. Stocker des preuves sur la blockchain Ethereum
3. Vérifier l'authenticité des documents horodatés
4. Suivre les statistiques d'utilisation
5. Mettre à jour automatiquement l'application

Développé pour la CC Sud-Avesnois
"""

# Bibliothèques standard
import os
import sys
import json
from datetime import datetime

# Interface graphique
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Modules de l'application
from timestamper import TimeStamper
from theme import ModernTheme
from updater import Updater
from preview import DocumentPreview
from cloud_sync import CloudSync

class HorodatageApp:
    """Interface principale de l'application d'horodatage."""

    VERSION = "1.1.0"
    WEBSITE = "https://cc-sudavesnois.fr"

    def __init__(self, root):
        """Initialise l'application avec sa fenêtre principale.

        Args:
            root: La fenêtre principale Tkinter
        """
        self.root = root
        self.root.title(f"Horodatage de Documents v{self.VERSION}")
        self.root.state('zoomed')

        # Obtenir le chemin de base (fonctionne avec PyInstaller)
        if getattr(sys, 'frozen', False):
            self.base_path = sys._MEIPASS
        else:
            self.base_path = os.path.dirname(os.path.abspath(__file__))

        # Dossier de stockage par défaut
        self.storage_path = os.path.join(self.base_path, "Horodatage")
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)

        # Configuration de l'icône
        icon_path = os.path.join(self.base_path, "assets", "icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
            try:
                import ctypes
                app_id = f'ccsudavesnois.horodatage.v{self.VERSION}'
                ctypes.windll.shell32.\
                    SetCurrentProcessExplicitAppUserModelID(app_id)
            except Exception:
                pass

        # Initialisation du thème
        self.root.configure(bg=ModernTheme.BACKGROUND)
        ModernTheme.setup_theme()

        # Initialisation des nouveaux modules
        self.cloud_sync = CloudSync()
        
        # Configuration de l'interface
        self.setup_ui()
        
        # Vérifier les mises à jour
        self.check_updates()
        
        # Initialisation du TimeStamper
        self.timestamper = TimeStamper()

        # Variables pour la vérification
        self.document_path = None
        self.cert_path = None
        self.selected_files = []

        # Initialiser les statistiques
        self.stats = {
            'files_processed': 0,
            'certificates_created': 0,
            'blockchain_proofs': 0,
            'verifications_done': 0
        }

    def setup_ui(self):
        """Configure l'interface utilisateur."""
        # Création du menu
        self.create_menu()
        
        # Création des onglets
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Onglet Horodatage
        self.timestamp_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.timestamp_tab, text="Horodatage")
        self.create_timestamp_tab()
        
        # Onglet Vérification
        self.verify_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.verify_tab, text="Vérification")
        self.create_verify_tab()
        
        # Onglet Cloud
        self.cloud_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.cloud_tab, text="Cloud")
        self.create_cloud_tab()
        
    def create_timestamp_tab(self):
        """Crée l'interface de l'onglet Horodatage."""
        # Frame principale avec deux colonnes
        main_frame = ttk.Frame(self.timestamp_tab)
        main_frame.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Colonne gauche : sélection et options
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True)
        
        # Zone de sélection des fichiers
        files_frame = ttk.LabelFrame(
            left_frame,
            text="Fichiers à horodater"
        )
        files_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Liste des fichiers
        self.files_text = tk.Text(
            files_frame,
            height=10,
            wrap='none'
        )
        self.files_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Boutons
        buttons_frame = ttk.Frame(files_frame)
        buttons_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(
            buttons_frame,
            text="Sélectionner des fichiers",
            command=self.select_files,
            name='select_files_button'
        ).pack(side='left', padx=5)
        
        # Options d'horodatage
        options_frame = ttk.LabelFrame(
            left_frame,
            text="Options d'horodatage",
            name='options_frame'
        )
        options_frame.pack(fill='x', padx=5, pady=5)
        
        self.rfc3161_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Certification RFC3161",
            variable=self.rfc3161_var
        ).pack(padx=5, pady=2)
        
        self.blockchain_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Preuve Blockchain",
            variable=self.blockchain_var
        ).pack(padx=5, pady=2)
        
        # Bouton d'horodatage
        ttk.Button(
            left_frame,
            text="Horodater les fichiers",
            command=self.timestamp_files,
            style='Accent.TButton',
            name='timestamp_button'
        ).pack(fill='x', padx=5, pady=10)
        
        # Colonne droite : prévisualisation
        right_frame = ttk.LabelFrame(
            main_frame,
            text="Prévisualisation",
            name='preview_frame'
        )
        right_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        # Widget de prévisualisation
        self.preview = DocumentPreview(right_frame)
        self.preview.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Journal en bas
        log_frame = ttk.LabelFrame(self.timestamp_tab, text="Journal")
        log_frame.pack(fill='x', padx=10, pady=5)
        
        self.log_text = tk.Text(
            log_frame,
            height=5,
            wrap='word'
        )
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
    def create_verify_tab(self):
        """Crée l'interface de l'onglet Vérification."""
        # Frame principale de l'onglet
        main_frame = ttk.Frame(
            self.verify_tab,
            style="Modern.TFrame",
            padding=20
        )
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Zone de sélection du document
        doc_frame = ModernTheme.create_card_frame(main_frame)
        doc_frame.pack(fill="x", pady=(0, 20))

        doc_title = ttk.Label(
            doc_frame,
            text=" Document à vérifier",
            style="Modern.TLabel",
            font=("Segoe UI", 12, "bold")
        )
        doc_title.pack(anchor="w", padx=10, pady=10)

        # Bouton de sélection du document
        select_doc_btn = ttk.Button(
            doc_frame,
            text="Sélectionner le document",
            command=self.select_document,
            style="Accent.TButton"
        )
        select_doc_btn.pack(side="left", padx=10, pady=(0, 10))

        # Label pour le nom du document
        self.doc_label = ttk.Label(
            doc_frame,
            text="Aucun document sélectionné",
            style="Modern.TLabel"
        )
        self.doc_label.pack(side="left", padx=10, pady=(0, 10))

        # Zone de sélection du certificat
        cert_frame = ModernTheme.create_card_frame(main_frame)
        cert_frame.pack(fill="x", pady=(0, 20))

        cert_title = ttk.Label(
            cert_frame,
            text=" Certificat ou preuve",
            style="Modern.TLabel",
            font=("Segoe UI", 12, "bold")
        )
        cert_title.pack(anchor="w", padx=10, pady=10)

        # Bouton de sélection du certificat
        select_cert_btn = ttk.Button(
            cert_frame,
            text="Sélectionner le certificat",
            command=self.select_certificate,
            style="Accent.TButton"
        )
        select_cert_btn.pack(side="left", padx=10, pady=(0, 10))

        # Label pour le nom du certificat
        self.cert_label = ttk.Label(
            cert_frame,
            text="Aucun certificat sélectionné",
            style="Modern.TLabel"
        )
        self.cert_label.pack(side="left", padx=10, pady=(0, 10))

        # Bouton de vérification
        verify_btn = ttk.Button(
            main_frame,
            text="Vérifier le document",
            command=self.verify_document,
            style="Accent.TButton"
        )
        verify_btn.pack(anchor="center", pady=20)

        # Zone de résultats
        result_frame = ModernTheme.create_card_frame(main_frame)
        result_frame.pack(fill="both", expand=True)

        result_title = ttk.Label(
            result_frame,
            text=" Résultats de la vérification",
            style="Modern.TLabel",
            font=("Segoe UI", 12, "bold")
        )
        result_title.pack(anchor="w", padx=10, pady=10)

        # Zone de texte pour les résultats
        self.result_text = tk.Text(
            result_frame,
            height=10,
            bg=ModernTheme.CARD_BG,
            fg=ModernTheme.TEXT,
            font=("Consolas", 10)
        )
        self.result_text.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10)
        )

    def create_cloud_tab(self):
        """Crée l'interface de l'onglet Cloud."""
        # Frame principale
        main_frame = ttk.Frame(self.cloud_tab)
        main_frame.pack(expand=True, fill='both', padx=10, pady=5)
        
        # OneDrive
        onedrive_frame = ttk.LabelFrame(
            main_frame,
            text="Microsoft OneDrive",
            name='onedrive_frame'
        )
        onedrive_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(
            onedrive_frame,
            text="Client ID:"
        ).pack(padx=5, pady=2)
        
        self.onedrive_id = ttk.Entry(onedrive_frame)
        self.onedrive_id.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(
            onedrive_frame,
            text="Client Secret:"
        ).pack(padx=5, pady=2)
        
        self.onedrive_secret = ttk.Entry(
            onedrive_frame,
            show='*'
        )
        self.onedrive_secret.pack(fill='x', padx=5, pady=2)
        
        ttk.Button(
            onedrive_frame,
            text="Configurer OneDrive",
            command=self.setup_onedrive
        ).pack(padx=5, pady=5)
        
        # Google Drive
        gdrive_frame = ttk.LabelFrame(
            main_frame,
            text="Google Drive",
            name='gdrive_frame'
        )
        gdrive_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(
            gdrive_frame,
            text="Client ID:"
        ).pack(padx=5, pady=2)
        
        self.gdrive_id = ttk.Entry(gdrive_frame)
        self.gdrive_id.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(
            gdrive_frame,
            text="Client Secret:"
        ).pack(padx=5, pady=2)
        
        self.gdrive_secret = ttk.Entry(
            gdrive_frame,
            show='*'
        )
        self.gdrive_secret.pack(fill='x', padx=5, pady=2)
        
        ttk.Button(
            gdrive_frame,
            text="Configurer Google Drive",
            command=self.setup_gdrive
        ).pack(padx=5, pady=5)
        
        # Options de synchronisation
        sync_frame = ttk.LabelFrame(
            main_frame,
            text="Options de synchronisation",
            name='sync_options'
        )
        sync_frame.pack(fill='x', padx=5, pady=5)
        
        self.auto_sync_var = tk.BooleanVar(
            value=self.cloud_sync.config['auto_sync']
        )
        ttk.Checkbutton(
            sync_frame,
            text="Synchronisation automatique",
            variable=self.auto_sync_var,
            command=self.toggle_auto_sync
        ).pack(padx=5, pady=2)
        
        ttk.Label(
            sync_frame,
            text="Intervalle de synchronisation (minutes):"
        ).pack(padx=5, pady=2)
        
        self.sync_interval = ttk.Entry(
            sync_frame,
            width=10
        )
        self.sync_interval.insert(
            0,
            str(self.cloud_sync.config['sync_interval'] // 60)
        )
        self.sync_interval.pack(padx=5, pady=2)
        
        ttk.Button(
            sync_frame,
            text="Synchroniser maintenant",
            command=self.sync_now
        ).pack(padx=5, pady=5)
        
    def setup_onedrive(self):
        """Configure OneDrive."""
        client_id = self.onedrive_id.get()
        client_secret = self.onedrive_secret.get()
        
        if not client_id or not client_secret:
            messagebox.showwarning(
                "Configuration incomplète",
                "Veuillez entrer l'ID client et le secret client."
            )
            return
            
        if self.cloud_sync.setup_onedrive(client_id, client_secret):
            messagebox.showinfo(
                "Succès",
                "OneDrive configuré avec succès!"
            )
        else:
            messagebox.showerror(
                "Erreur",
                "Erreur lors de la configuration d'OneDrive."
            )
            
    def setup_gdrive(self):
        """Configure Google Drive."""
        client_id = self.gdrive_id.get()
        client_secret = self.gdrive_secret.get()
        
        if not client_id or not client_secret:
            messagebox.showwarning(
                "Configuration incomplète",
                "Veuillez entrer l'ID client et le secret client."
            )
            return
            
        if self.cloud_sync.setup_gdrive(client_id, client_secret):
            messagebox.showinfo(
                "Succès",
                "Google Drive configuré avec succès!"
            )
        else:
            messagebox.showerror(
                "Erreur",
                "Erreur lors de la configuration de Google Drive."
            )
            
    def toggle_auto_sync(self):
        """Active/désactive la synchronisation automatique."""
        self.cloud_sync.config['auto_sync'] = self.auto_sync_var.get()
        self.cloud_sync.save_config()
        
    def sync_now(self):
        """Lance une synchronisation manuelle."""
        def callback(message):
            self.log_message(message)
            
        self.cloud_sync.sync_to_cloud(
            self.storage_path,
            callback=callback
        )
        
    def select_files(self):
        """Ouvre une boîte de dialogue pour sélectionner des fichiers."""
        files = filedialog.askopenfilenames(
            title="Sélectionner les fichiers à horodater",
            filetypes=[
                ("Tous les fichiers", "*.*"),
                ("Documents PDF", "*.pdf"),
                ("Images", "*.png *.jpg *.jpeg")
            ]
        )
        
        if files:
            self.selected_files = list(files)
            self.update_file_list()
            
            # Prévisualiser le premier fichier
            if self.selected_files:
                self.preview.preview_file(self.selected_files[0])
                
    def update_file_list(self):
        """Met à jour l'affichage de la liste des fichiers."""
        self.files_text.delete(1.0, tk.END)
        for file in self.selected_files:
            self.files_text.insert(tk.END, f"• {os.path.basename(file)}\n")
            
    def timestamp_files(self):
        """Horodate les fichiers sélectionnés."""
        if not self.selected_files:
            messagebox.showwarning(
                "Aucun fichier",
                "Veuillez sélectionner au moins un fichier à horodater."
            )
            return
            
        try:
            for file_path in self.selected_files:
                # Créer les sous-dossiers
                timestamp_folder = os.path.join(self.storage_path, "str")
                blockchain_folder = os.path.join(self.storage_path, "blockchain")
                
                for folder in [timestamp_folder, blockchain_folder]:
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                        
                # Utiliser les nouveaux chemins
                self.timestamper.storage_path = timestamp_folder
                self.timestamper.blockchain_path = blockchain_folder
                
                # Options d'horodatage
                options = {
                    'rename': True,
                    'rfc3161': self.rfc3161_var.get(),
                    'blockchain': self.blockchain_var.get()
                }
                
                # Horodater le fichier
                result = self.timestamper.timestamp_file(file_path, options)
                
                # Mettre à jour les statistiques
                self.stats['files_processed'] += 1
                if options['rfc3161']:
                    self.stats['certificates_created'] += 1
                if options['blockchain']:
                    self.stats['blockchain_proofs'] += 1
                    
                # Journal
                self.log_message(
                    f"✓ {os.path.basename(file_path)} horodaté avec succès"
                )
                
                # Synchroniser avec le cloud si activé
                if self.cloud_sync.config['auto_sync']:
                    self.cloud_sync.sync_to_cloud(
                        self.storage_path,
                        callback=self.log_message
                    )
                    
            # Nettoyer
            self.selected_files.clear()
            self.files_text.delete(1.0, tk.END)
            self.update_stats_display()
            
            messagebox.showinfo(
                "Succès",
                "Tous les fichiers ont été horodatés avec succès!"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"Une erreur est survenue lors de l'horodatage : {str(e)}"
            )

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="Site Web", command=self.open_website)
        help_menu.add_separator()
        help_menu.add_command(label="À propos", command=self.show_about)

    def select_document(self):
        """Ouvre une boîte de dialogue pour sélectionner un document."""
        self.document_path = filedialog.askopenfilename(
            title="Sélectionner le document à vérifier",
            filetypes=[
                ("Tous les fichiers", "*.*"),
                ("Documents PDF", "*.pdf"),
                ("Images", "*.png *.jpg *.jpeg"),
                ("Documents Word", "*.doc *.docx")
            ]
        )
        if self.document_path:
            self.doc_label.config(
                text=os.path.basename(self.document_path)
            )

    def select_certificate(self):
        """Ouvre une boîte de dialogue pour sélectionner un certificat."""
        self.cert_path = filedialog.askopenfilename(
            title="Sélectionner le certificat ou la preuve",
            filetypes=[
                ("Certificats", "*.cert"),
                ("Preuves blockchain", "*.blockchain")
            ]
        )
        if self.cert_path:
            self.cert_label.config(
                text=os.path.basename(self.cert_path)
            )

    def update_stats_display(self):
        """Met à jour l'affichage des statistiques."""
        stats_text = (
            f"Fichiers traités : {self.stats['files_processed']}\n"
            f"Certificats créés : {self.stats['certificates_created']}\n"
            f"Preuves blockchain : {self.stats['blockchain_proofs']}\n"
            f"Vérifications : {self.stats['verifications_done']}"
        )
        self.stats_label.config(text=stats_text)

    def log_message(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

    def verify_document(self):
        if not self.document_path or not self.cert_path:
            messagebox.showwarning(
                "Attention",
                "Veuillez sélectionner un document et son certificat/preuve."
            )
            return

        try:
            # Déterminer le type de vérification
            if self.cert_path.endswith('.tsr'):
                self.verify_rfc3161()
            elif self.cert_path.endswith('.blockchain'):
                self.verify_blockchain()

            # Mettre à jour les statistiques
            self.stats['verifications_done'] += 1
            self.update_stats_display()

        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"Une erreur est survenue lors de la vérification : {str(e)}"
            )

    def verify_rfc3161(self):
        try:
            # Vérifier le certificat RFC3161
            is_valid = self.timestamper.verify_rfc3161(
                self.document_path, 
                self.cert_path
            )

            # Lire les détails du certificat
            with open(self.cert_path, 'r') as f:
                cert_data = json.load(f)

            # Afficher le résultat
            if is_valid:
                result = (
                    "✅ Document authentique\n\n"
                    f"Document : {os.path.basename(self.document_path)}\n"
                    f"Date : {cert_data.get('timestamp', 'Non disponible')}\n"
                    f"Hash : {cert_data.get('hash', 'Non disponible')}\n"
                    f"Autorité : {cert_data.get('tsa', 'Non disponible')}"
                )
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, result)
                self.result_text.tag_add("valid", "1.0", "1.end")
            else:
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(
                    tk.END,
                    "❌ Document non authentique ou modifié"
                )
                self.result_text.tag_add("invalid", "1.0", "1.end")

        except Exception as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(
                tk.END,
                f"Erreur lors de la vérification : {str(e)}"
            )

    def verify_blockchain(self):
        try:
            # Vérifier la preuve blockchain
            is_valid = self.timestamper.verify_blockchain(
                self.document_path,
                self.cert_path
            )

            # Lire les détails de la preuve
            with open(self.cert_path, 'r') as f:
                proof_data = json.load(f)

            # Afficher le résultat
            if is_valid:
                result = (
                    "✅ Document authentique\n\n"
                    f"Document : {os.path.basename(self.document_path)}\n"
                    f"Date : {proof_data.get('timestamp', 'Non disponible')}\n"
                    f"Hash : {proof_data.get('hash', 'Non disponible')}\n"
                    f"Transaction : {proof_data.get('txid', 'Non disponible')}"
                )
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, result)
                self.result_text.tag_add("valid", "1.0", "1.end")
            else:
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(
                    tk.END,
                    "❌ Document non authentique ou modifié"
                )
                self.result_text.tag_add("invalid", "1.0", "1.end")

        except Exception as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(
                tk.END,
                f"Erreur lors de la vérification : {str(e)}"
            )

    def open_website(self, event=None):
        """Ouvre le site web de la CC Sud-Avesnois."""
        webbrowser.open(self.WEBSITE)

    def show_about(self):
        """Affiche la boîte de dialogue À propos."""
        about_text = (
            f"Horodatage de Documents v{self.VERSION}\n\n"
            "Application développée pour la CC Sud-Avesnois\n"
            "permettant d'horodater des documents avec\n"
            "certification RFC3161 et blockchain.\n\n"
            " 2024 CC Sud-Avesnois"
        )

        messagebox.showinfo("À propos", about_text)

    def check_updates(self):
        """Vérifie si des mises à jour sont disponibles."""
        try:
            updater = Updater()
            update_info = updater.check_for_updates()
            if update_info and update_info['update_available']:
                if messagebox.askyesno(
                    "Mise à jour disponible",
                    "Une nouvelle version est disponible. Voulez-vous la télécharger ?"):
                    updater.download_update(update_info['download_url'])
        except Exception as e:
            print(f"Erreur lors de la vérification des mises à jour : {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = HorodatageApp(root)
    root.mainloop()
