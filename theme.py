"""
Module de gestion du thème moderne de l'application.

Ce module définit l'apparence visuelle de l'application avec :
- Une palette de couleurs moderne et cohérente
- Des styles pour les widgets Tkinter
- Des constantes pour les polices et les dimensions
- Des fonctions utilitaires pour le style
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class ModernTheme:
    """Définit le thème moderne de l'application."""
    
    # Couleurs principales
    BACKGROUND = "#1A1B1E"  # Fond sombre
    CARD_BG = "#25262B"     # Fond des cartes légèrement plus clair
    PRIMARY = "#7048E8"     # Violet pour les actions principales
    PRIMARY_HOVER = "#5B3BC2"  # Violet clair pour le hover
    SUCCESS = "#1DB954"     # Vert pour les actions positives
    SUCCESS_HOVER = "#1A9548"  # Vert clair pour le hover
    INFO = "#3B82F6"        # Bleu pour les informations
    INFO_HOVER = "#2563EB"  # Bleu clair pour le hover
    WARNING = "#F59E0B"     # Jaune pour les avertissements
    WARNING_HOVER = "#D97706"  # Jaune clair pour le hover
    DANGER = "#EF4444"      # Rouge pour les erreurs
    ERROR_HOVER = "#DC2626"  # Rouge clair pour le hover
    TEXT = "#FFFFFF"        # Texte principal (blanc)
    TEXT_SECONDARY = "#A1A1AA"  # Texte secondaire (gris clair)
    TEXT_HOVER = "#000000"  # Texte noir pour le hover
    HOVER_COLOR = "#333333"  # Couleur de fond pour le survol
    
    # Mapping des couleurs pour le hover
    HOVER_COLORS = {
        'PRIMARY': PRIMARY_HOVER,
        'SUCCESS': SUCCESS_HOVER,
        'INFO': INFO_HOVER,
        'WARNING': WARNING_HOVER,
        'ERROR': ERROR_HOVER
    }

    @classmethod
    def setup_theme(cls):
        """Configure le thème pour tous les widgets de l'application.
        
        Cette méthode doit être appelée au démarrage de l'application pour
        appliquer le style moderne à tous les widgets.
        """
        style = ttk.Style()
        style.theme_use('clam')  # Base theme
        
        # Frame moderne
        style.configure(
            "Modern.TFrame",
            background=cls.CARD_BG
        )
        
        # Frame carte
        style.configure(
            "Card.TFrame",
            background=cls.CARD_BG,
            relief="flat"
        )
        
        # Labels modernes
        style.configure(
            "Modern.TLabel",
            background=cls.CARD_BG,
            foreground=cls.TEXT,
            font=("Segoe UI", 10)
        )
        
        # Checkbuttons modernes avec hover effect
        style.configure(
            "Modern.TCheckbutton",
            background=cls.CARD_BG,
            foreground=cls.TEXT,
            font=("Segoe UI", 10)
        )
        style.map(
            "Modern.TCheckbutton",
            background=[("active", cls.CARD_BG)],
            foreground=[("active", cls.TEXT_HOVER)])  # Texte noir au hover
        
        # Configuration du Notebook (onglets)
        style.configure(
            "TNotebook",
            background=cls.BACKGROUND,
            borderwidth=0,
            tabmargins=[2, 5, 2, 0]
        )
        style.configure(
            "TNotebook.Tab",
            background=cls.CARD_BG,
            foreground=cls.TEXT,
            lightcolor=cls.BACKGROUND,
            borderwidth=0,
            font=("Segoe UI", 10),
            padding=[20, 10],
            focuscolor=cls.PRIMARY
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", cls.PRIMARY)],
            foreground=[("selected", cls.TEXT)],
            expand=[("selected", [1, 1, 1, 0])]
        )

    @classmethod
    def create_card_frame(cls, parent):
        """Crée un cadre style carte avec coins arrondis et ombre"""
        frame = ttk.Frame(parent, style="Card.TFrame", padding=10)
        return frame

    @classmethod
    def create_rounded_button(cls, parent, text, command, color_type, icon=None):
        """Crée un bouton moderne avec coins arrondis et effet hover
        
        Args:
            parent: Widget parent
            text: Texte du bouton
            command: Fonction à exécuter
            color_type: Type de couleur (PRIMARY, SUCCESS, INFO, etc.)
            icon: Icône optionnelle à afficher avant le texte
        """
        frame = ttk.Frame(parent, style="Modern.TFrame")
        
        # Obtenir les couleurs
        base_color = getattr(cls, color_type)
        hover_color = cls.HOVER_COLORS.get(color_type, cls.PRIMARY_HOVER)
        
        # Création du bouton avec tkinter
        button = tk.Button(
            frame,
            text=text if not icon else f"{icon} {text}",
            command=command,
            bg=base_color,
            fg=cls.TEXT,
            relief="flat",
            activebackground=hover_color,
            activeforeground=cls.TEXT,
            bd=0,
            padx=15,
            pady=5,
            font=("Segoe UI", 9),
            cursor="hand2"
        )
        button.pack(fill="both", expand=True)

        # Arrondir les coins
        button.bind('<Configure>', lambda e: button.configure(
            highlightthickness=0,
            borderwidth=0
        ))

        return frame

    @classmethod
    def create_stats_frame(cls, parent, title, value, subtitle=""):
        """Crée un cadre de statistiques"""
        frame = ttk.Frame(parent, style="Card.TFrame")
        
        title_label = ttk.Label(
            frame,
            text=title,
            style="Modern.TLabel",
            font=("Segoe UI", 10),
            foreground=cls.TEXT_SECONDARY
        )
        title_label.pack(anchor="w")
        
        value_label = ttk.Label(
            frame,
            text=str(value),
            style="Modern.TLabel",
            font=("Segoe UI", 24, "bold")
        )
        value_label.pack(anchor="w", pady=(0, 5))
        
        if subtitle:
            subtitle_label = ttk.Label(
                frame,
                text=subtitle,
                style="Modern.TLabel",
                font=("Segoe UI", 8),
                foreground=cls.TEXT_SECONDARY
            )
            subtitle_label.pack(anchor="w")
        
        return frame

    @classmethod
    def create_logo_frame(cls, parent, logo_path, width=150):
        """Crée un cadre avec logo redimensionné"""
        frame = ttk.Frame(parent, style="Card.TFrame")
        
        try:
            # Charger et redimensionner le logo
            logo_image = Image.open(logo_path)
            ratio = width / logo_image.width
            height = int(logo_image.height * ratio)
            logo_image = logo_image.resize((width, height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(logo_image)
            
            # Créer le label avec le logo
            label = tk.Label(
                frame,
                image=photo,
                bg=cls.CARD_BG,
                cursor="hand2"  # Curseur main au survol
            )
            label.image = photo  # Garder une référence
            label.pack(padx=10, pady=10)
            
            # Ajouter un effet de survol
            def on_enter(e):
                label.configure(bg=cls.HOVER_COLOR)
            def on_leave(e):
                label.configure(bg=cls.CARD_BG)
                
            label.bind("<Enter>", on_enter)
            label.bind("<Leave>", on_leave)
            
            return frame, label
            
        except Exception as e:
            print(f"Erreur lors du chargement du logo : {str(e)}")
            return frame, None

    @staticmethod
    def create_tooltip(widget, text):
        """Crée une infobulle pour un widget"""
        def enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            # Style de l'infobulle
            label = tk.Label(
                tooltip,
                text=text,
                justify='left',
                background="#2A2A2A",
                foreground="#FFFFFF",
                relief='solid',
                borderwidth=1,
                font=("Segoe UI", 9)
            )
            label.pack()
            
            widget.tooltip = tooltip
            
        def leave(event):
            if hasattr(widget, "tooltip"):
                widget.tooltip.destroy()
                
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)
