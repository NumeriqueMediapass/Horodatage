import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
from datetime import datetime
import json
from timestamper import TimeStamper
from PIL import Image, ImageTk
from theme import ModernTheme
from updater import Updater
import sys
import webbrowser

class HorodatageApp:
    VERSION = "1.0.0"
    WEBSITE = "https://cc-sudavesnois.fr"
    
    def __init__(self, root):
        self.root = root
        self.root.title(f"Horodatage de Documents v{self.VERSION}")
        self.root.state('zoomed')
        
        # Obtenir le chemin de base (fonctionne avec PyInstaller)
        if getattr(sys, 'frozen', False):
            self.base_path = sys._MEIPASS
        else:
            self.base_path = os.path.dirname(os.path.abspath(__file__))
            
        # Configuration de l'icône
        icon_path = os.path.join(self.base_path, "assets", "icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
            try:
                import ctypes
                myappid = f'ccsudavesnois.horodatage.v{self.VERSION}'
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            except Exception:
                pass

        # Initialisation du thème
        self.root.configure(bg=ModernTheme.BACKGROUND)
        ModernTheme.setup_theme()

        # Création du menu
        self.create_menu()

        # Initialisation du TimeStamper
        self.timestamper = TimeStamper()

        # Variables pour la vérification
        self.document_path = None
        self.cert_path = None
        self.selected_files = []
        
        # Dossier de stockage par défaut
        self.storage_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Horodatage")
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
        
        # Initialiser les statistiques
        self.stats = {
            'files_processed': 0,
            'certificates_created': 0,
            'blockchain_proofs': 0,
            'verifications_done': 0
        }

        # Création des widgets
        self.create_widgets()
        
        # Vérifier les mises à jour
        self.check_updates()
        
    def check_updates(self):
        """Vérifie si une mise à jour est disponible"""
        updater = Updater()
        self.root.after(1000, updater.propose_update)  # Vérifier après 1 seconde

    def create_widgets(self):
        # Frame principale avec padding
        main_frame = ttk.Frame(self.root, style="Modern.TFrame", padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # En-tête avec logo et titre
        header_frame = ModernTheme.create_card_frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))

        # Layout en deux colonnes pour l'en-tête
        header_content = ttk.Frame(header_frame, style="Card.TFrame")
        header_content.pack(fill="x", padx=10, pady=10)

        # Colonne gauche : Logo
        logo_path = os.path.join(self.base_path, "assets", "Logo_S-A.png")
        if os.path.exists(logo_path):
            logo_frame, logo_label = ModernTheme.create_logo_frame(header_content, logo_path)
            if logo_frame:
                logo_frame.pack(side="left", padx=(0, 20))
                if logo_label:
                    logo_label.bind("<Button-1>", self.open_website)
                    tooltip = "Cliquez pour visiter le site de la CC Sud-Avesnois"
                    ModernTheme.create_tooltip(logo_label, tooltip)

        # Colonne droite : Statistiques
        stats_frame = ttk.Frame(header_content, style="Card.TFrame")
        stats_frame.pack(side="right", fill="x", expand=True)

        # Ligne de statistiques
        self.stats_row = ttk.Frame(stats_frame, style="Card.TFrame")
        self.stats_row.pack(fill="x", pady=10)

        # Création des widgets de statistiques
        stats_data = [
            ("Fichiers traités", self.stats['files_processed']),
            ("Certificats créés", self.stats['certificates_created']),
            ("Preuves blockchain", self.stats['blockchain_proofs']),
            ("Vérifications", self.stats['verifications_done'])
        ]

        for title, value in stats_data:
            stat_widget = ModernTheme.create_stats_frame(
                self.stats_row,
                title,
                value
            )
            stat_widget.pack(side="left", fill="x", expand=True, padx=5)

        # Création du notebook (système d'onglets)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Onglets
        self.timestamp_tab = ttk.Frame(self.notebook, style="Modern.TFrame")
        self.verify_tab = ttk.Frame(self.notebook, style="Modern.TFrame")
        
        self.notebook.add(self.timestamp_tab, text=" Horodater un fichier")
        self.notebook.add(self.verify_tab, text=" Vérifier un document")

        self.create_timestamp_tab()
        self.create_verify_tab()

    def create_timestamp_tab(self):
        # Frame principale de l'onglet
        main_frame = ttk.Frame(self.timestamp_tab, style="Modern.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Colonne gauche (70% de la largeur)
        left_frame = ttk.Frame(main_frame, style="Modern.TFrame")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Zone de dépôt de fichiers
        dropzone = ModernTheme.create_card_frame(left_frame)
        dropzone.pack(fill="both", expand=True)

        dropzone_label = ttk.Label(
            dropzone,
            text=" Déposez vos fichiers ici ou",
            style="Modern.TLabel",
            font=("Segoe UI", 14)
        )
        dropzone_label.pack(pady=(20, 10))

        select_button = ModernTheme.create_rounded_button(
            dropzone,
            " Sélectionner des fichiers",
            self.select_files,
            "SUCCESS"
        )
        select_button.pack(pady=(0, 20))

        # Liste des fichiers
        self.files_text = tk.Text(
            dropzone,
            height=10,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            bg=ModernTheme.CARD_BG,
            fg=ModernTheme.TEXT,
            relief="flat"
        )
        self.files_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Colonne droite (30% de la largeur)
        right_frame = ttk.Frame(main_frame, style="Modern.TFrame")
        right_frame.pack(side="right", fill="both", padx=(10, 0))
        right_frame_inner = ttk.Frame(right_frame, style="Modern.TFrame", width=300)
        right_frame_inner.pack(fill="both", expand=True)
        right_frame_inner.pack_propagate(False)  # Empêche la frame de se redimensionner

        # Options d'horodatage
        options_frame = ModernTheme.create_card_frame(right_frame_inner)
        options_frame.pack(fill="x", pady=(0, 20))

        options_title = ttk.Label(
            options_frame,
            text=" Options d'horodatage",
            style="Modern.TLabel",
            font=("Segoe UI", 12, "bold")
        )
        options_title.pack(anchor="w", pady=(0, 10))

        # Dossier de stockage
        storage_frame = ttk.Frame(options_frame, style="Card.TFrame")
        storage_frame.pack(fill="x", pady=(0, 10))

        storage_label = ttk.Label(
            storage_frame,
            text=" Dossier de stockage :",
            style="Modern.TLabel"
        )
        storage_label.pack(anchor="w")

        storage_path_frame = ttk.Frame(storage_frame, style="Card.TFrame")
        storage_path_frame.pack(fill="x", pady=(5, 0))

        self.storage_label = ttk.Label(
            storage_path_frame,
            text=self.storage_path,
            style="Modern.TLabel",
            wraplength=180  # Réduit pour laisser plus de place au bouton
        )
        self.storage_label.pack(side="left", fill="x", expand=True)

        # Bouton de sélection du dossier
        storage_button = ModernTheme.create_rounded_button(
            storage_path_frame,
            "Parcourir",
            self.select_storage_path,
            "PRIMARY",
            icon="📂"
        )
        storage_button.pack(side="right", padx=(5, 0))

        ttk.Separator(options_frame, orient="horizontal").pack(fill="x", pady=10)

        # Options
        self.rename_var = tk.BooleanVar(value=True)
        self.rfc3161_var = tk.BooleanVar(value=True)
        self.blockchain_var = tk.BooleanVar(value=False)

        options = [
            (self.rename_var, " Renommer les fichiers avec horodatage"),
            (self.rfc3161_var, " Certificat d'horodatage RFC3161"),
            (self.blockchain_var, " Stockage blockchain")
        ]

        for var, text in options:
            ttk.Checkbutton(
                options_frame,
                text=text,
                variable=var,
                style="Modern.TCheckbutton"
            ).pack(anchor="w", pady=5)

        # Bouton d'horodatage
        self.timestamp_button = ModernTheme.create_rounded_button(
            right_frame_inner,
            "🕒 Horodater les fichiers",
            self.timestamp_files,
            "PRIMARY"
        )
        self.timestamp_button.pack(fill="x", pady=20)

        # Journal des opérations
        log_frame = ModernTheme.create_card_frame(right_frame_inner)
        log_frame.pack(fill="both", expand=True)

        log_title = ttk.Label(
            log_frame,
            text=" Journal des opérations",
            style="Modern.TLabel",
            font=("Segoe UI", 12, "bold")
        )
        log_title.pack(anchor="w", pady=(0, 10))

        self.log_text = tk.Text(
            log_frame,
            height=8,
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            bg=ModernTheme.CARD_BG,
            fg=ModernTheme.TEXT,
            relief="flat"
        )
        self.log_text.pack(fill="both", expand=True)

    def create_verify_tab(self):
        # Frame principale de l'onglet
        main_frame = ttk.Frame(self.verify_tab, style="Modern.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Colonne gauche (70%)
        left_frame = ttk.Frame(main_frame, style="Modern.TFrame")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Section document
        doc_frame = ModernTheme.create_card_frame(left_frame)
        doc_frame.pack(fill="x", pady=(0, 20))

        doc_title = ttk.Label(
            doc_frame,
            text=" Document à vérifier",
            style="Modern.TLabel",
            font=("Segoe UI", 12, "bold")
        )
        doc_title.pack(anchor="w", pady=(0, 10))

        doc_content = ttk.Frame(doc_frame, style="Card.TFrame")
        doc_content.pack(fill="x", pady=(0, 10))

        self.doc_label = ttk.Label(
            doc_content,
            text="Aucun document sélectionné",
            style="Modern.TLabel"
        )
        self.doc_label.pack(side="left", fill="x", expand=True)

        select_doc_button = ModernTheme.create_rounded_button(
            doc_content,
            " Sélectionner",
            self.select_document,
            "SUCCESS"
        )
        select_doc_button.pack(side="right", padx=5)

        # Section certificat
        cert_frame = ModernTheme.create_card_frame(left_frame)
        cert_frame.pack(fill="x")

        cert_title = ttk.Label(
            cert_frame,
            text=" Certificat ou Preuve",
            style="Modern.TLabel",
            font=("Segoe UI", 12, "bold")
        )
        cert_title.pack(anchor="w", pady=(0, 10))

        cert_content = ttk.Frame(cert_frame, style="Card.TFrame")
        cert_content.pack(fill="x", pady=(0, 10))

        self.cert_label = ttk.Label(
            cert_content,
            text="Aucun certificat sélectionné",
            style="Modern.TLabel"
        )
        self.cert_label.pack(side="left", fill="x", expand=True)

        select_cert_button = ModernTheme.create_rounded_button(
            cert_content,
            " Sélectionner",
            self.select_certificate,
            "INFO"
        )
        select_cert_button.pack(side="right", padx=5)

        # Colonne droite (30%)
        right_frame = ttk.Frame(main_frame, style="Modern.TFrame")
        right_frame.pack(side="right", fill="both", padx=(10, 0))
        right_frame_inner = ttk.Frame(right_frame, style="Modern.TFrame", width=300)
        right_frame_inner.pack(fill="both", expand=True)
        right_frame_inner.pack_propagate(False)  # Empêche la frame de se redimensionner

        # Bouton de vérification
        verify_button = ModernTheme.create_rounded_button(
            right_frame_inner,
            "✓ Vérifier l'authenticité",
            self.verify_document,
            "PRIMARY"
        )
        verify_button.pack(fill="x", pady=(0, 20))

        # Résultats
        result_frame = ModernTheme.create_card_frame(right_frame_inner)
        result_frame.pack(fill="both", expand=True)

        result_title = ttk.Label(
            result_frame,
            text=" Résultats de la vérification",
            style="Modern.TLabel",
            font=("Segoe UI", 12, "bold")
        )
        result_title.pack(anchor="w", pady=(0, 10))

        self.result_text = tk.Text(
            result_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            bg=ModernTheme.CARD_BG,
            fg=ModernTheme.TEXT,
            relief="flat"
        )
        self.result_text.pack(fill="both", expand=True)

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="Site Web", command=self.open_website)
        help_menu.add_separator()
        help_menu.add_command(label="À propos", command=self.show_about)

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Sélectionner les fichiers à horodater",
            filetypes=[("Tous les fichiers", "*.*")]
        )

        self.selected_files = list(files)
        self.update_file_list()

    def update_file_list(self):
        self.files_text.delete(1.0, tk.END)
        for file in self.selected_files:
            self.files_text.insert(tk.END, f"- {os.path.basename(file)}\n")

    def log_message(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

    def timestamp_files(self):
        if not self.selected_files:
            messagebox.showwarning(
                "Aucun fichier",
                "Veuillez sélectionner au moins un fichier à horodater."
            )
            return

        try:
            for file_path in self.selected_files:
                # Créer les sous-dossiers dans le dossier de stockage
                timestamp_folder = os.path.join(self.storage_path, "str")
                blockchain_folder = os.path.join(self.storage_path, "blockchain")
                
                for folder in [timestamp_folder, blockchain_folder]:
                    if not os.path.exists(folder):
                        os.makedirs(folder)

                # Utiliser les nouveaux chemins pour le stockage
                self.timestamper.storage_path = timestamp_folder
                self.timestamper.blockchain_path = blockchain_folder

                # Options d'horodatage
                options = {
                    'rename': self.rename_var.get(),
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
                
                # Mettre à jour l'affichage des statistiques
                self.update_stats_display()

                # Ajouter le résultat au journal
                self.log_text.insert(tk.END, f"✓ {os.path.basename(file_path)} horodaté avec succès\n")
                self.log_text.see(tk.END)

            # Effacer la liste des fichiers sélectionnés
            self.selected_files.clear()
            self.files_text.delete(1.0, tk.END)
            
            messagebox.showinfo(
                "Succès",
                "Tous les fichiers ont été horodatés avec succès!"
            )

        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"Une erreur est survenue lors de l'horodatage : {str(e)}"
            )

    def select_document(self):
        self.document_path = filedialog.askopenfilename(
            title="Sélectionner le document à vérifier",
            filetypes=[("Tous les fichiers", "*.*")]
        )
        if self.document_path:
            self.doc_label.config(text=os.path.basename(self.document_path))
            
    def select_certificate(self):
        self.cert_path = filedialog.askopenfilename(
            title="Sélectionner le certificat ou la preuve",
            filetypes=[
                ("Tous les certificats", "*.tsr *.blockchain"),
                ("Certificat RFC3161", "*.tsr"),
                ("Preuve Blockchain", "*.blockchain")
            ]
        )
        if self.cert_path:
            self.cert_label.config(text=os.path.basename(self.cert_path))
            
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
            is_valid = self.timestamper.verify_rfc3161(self.document_path, self.cert_path)
            
            # Lire les détails du certificat
            with open(self.cert_path, 'r') as f:
                cert_data = json.load(f)
                
            self.result_text.insert(tk.END, "=== Vérification du Certificat RFC3161 ===\n\n")
            
            if is_valid:
                self.result_text.insert(tk.END, " Le document est authentique!\n\n")
            else:
                self.result_text.insert(tk.END, " ATTENTION: Le document a été modifié!\n\n")
                
            self.result_text.insert(tk.END, f" Date d'horodatage: {cert_data['timestamp']}\n")
            self.result_text.insert(tk.END, f" Service TSA: {cert_data['tsa_url']}\n")
            self.result_text.insert(tk.END, f" Hash du document: {cert_data['hash']}\n")
            
        except Exception as e:
            raise Exception(f"Erreur lors de la vérification RFC3161: {str(e)}")
            
    def verify_blockchain(self):
        try:
            # Vérifier la preuve blockchain
            is_valid = self.timestamper.verify_blockchain(self.document_path, self.cert_path)
            
            # Lire les détails de la preuve
            with open(self.cert_path, 'r') as f:
                proof_data = json.load(f)
                
            self.result_text.insert(tk.END, "=== Vérification de la Preuve Blockchain ===\n\n")
            
            if is_valid:
                self.result_text.insert(tk.END, " Le document est authentique!\n\n")
            else:
                self.result_text.insert(tk.END, " ATTENTION: Le document a été modifié!\n\n")
                
            self.result_text.insert(tk.END, f" Date d'horodatage: {proof_data['timestamp']}\n")
            self.result_text.insert(tk.END, f" Blockchain: {proof_data['blockchain']}\n")
            self.result_text.insert(tk.END, f" Réseau: {proof_data['network']}\n")
            self.result_text.insert(tk.END, f" Hash du document: {proof_data['file_hash']}\n")
            
        except Exception as e:
            raise Exception(f"Erreur lors de la vérification blockchain: {str(e)}")

    def open_website(self, event=None):
        """Ouvre le site web de la CC Sud-Avesnois"""
        webbrowser.open("https://cc-sudavesnois.fr")

    def show_about(self):
        about_text = f"""Horodatage de Documents v{self.VERSION}

Une application développée pour la CC Sud-Avesnois
{self.WEBSITE}

Cette application permet d'horodater vos documents avec :
- Renommage automatique avec horodatage
- Certification RFC3161
- Stockage blockchain

 2025 CC Sud-Avesnois - Tous droits réservés"""
        
        messagebox.showinfo("À propos", about_text)

    def select_storage_path(self):
        new_path = filedialog.askdirectory(
            title="Sélectionner le dossier de stockage",
            initialdir=self.storage_path
        )
        if new_path:
            self.storage_path = new_path
            self.storage_label.configure(text=self.storage_path)
            # Créer le dossier s'il n'existe pas
            if not os.path.exists(self.storage_path):
                os.makedirs(self.storage_path)

    def update_stats_display(self):
        """Met à jour l'affichage des statistiques"""
        stats_data = [
            ("Fichiers traités", self.stats['files_processed']),
            ("Certificats créés", self.stats['certificates_created']),
            ("Preuves blockchain", self.stats['blockchain_proofs']),
            ("Vérifications", self.stats['verifications_done'])
        ]

        # Mettre à jour chaque widget de statistique
        stats_widgets = self.stats_row.winfo_children()
        for widget, (title, value) in zip(stats_widgets, stats_data):
            # Trouver le label de valeur (deuxième enfant)
            value_label = [child for child in widget.winfo_children() if isinstance(child, ttk.Label)][1]
            value_label.configure(text=str(value))


if __name__ == "__main__":
    root = tk.Tk()
    app = HorodatageApp(root)
    root.mainloop()
