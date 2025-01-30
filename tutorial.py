"""
Module de tutoriels interactifs.

Guide l'utilisateur à travers les fonctionnalités de l'application.
"""

import tkinter as tk
from tkinter import ttk
import json
import os


class TutorialStep:
    """Représente une étape du tutoriel."""
    
    def __init__(self, title, message, target=None, position="bottom"):
        """Initialise une étape du tutoriel.
        
        Args:
            title: Titre de l'étape
            message: Description de l'étape
            target: Widget cible (None pour message central)
            position: Position de la bulle (top, bottom, left, right)
        """
        self.title = title
        self.message = message
        self.target = target
        self.position = position


class TutorialManager:
    """Gère les tutoriels interactifs."""
    
    def __init__(self, root):
        """Initialise le gestionnaire de tutoriels.
        
        Args:
            root: Fenêtre principale de l'application
        """
        self.root = root
        self.current_tutorial = None
        self.current_step = 0
        self.overlay = None
        self.bubble = None
        
        # Charger les tutoriels
        self.tutorials = self._load_tutorials()
        
    def _load_tutorials(self):
        """Charge les tutoriels depuis le fichier JSON."""
        tutorials_file = os.path.join(
            os.path.dirname(__file__),
            "assets",
            "tutorials.json"
        )
        
        if os.path.exists(tutorials_file):
            with open(tutorials_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
        
    def start_tutorial(self, tutorial_id):
        """Démarre un tutoriel.
        
        Args:
            tutorial_id: Identifiant du tutoriel à démarrer
        """
        if tutorial_id not in self.tutorials:
            return
            
        self.current_tutorial = self.tutorials[tutorial_id]
        self.current_step = 0
        self._show_current_step()
        
    def _show_current_step(self):
        """Affiche l'étape courante du tutoriel."""
        if not self.current_tutorial:
            return
            
        steps = self.current_tutorial['steps']
        if self.current_step >= len(steps):
            self._end_tutorial()
            return
            
        step = steps[self.current_step]
        
        # Créer l'overlay si nécessaire
        if not self.overlay:
            self.overlay = tk.Canvas(
                self.root,
                highlightthickness=0,
                bg='#0009'
            )
            self.overlay.place(
                x=0, y=0,
                relwidth=1, relheight=1
            )
            
        # Créer la bulle d'info
        if self.bubble:
            self.bubble.destroy()
            
        self.bubble = tk.Frame(
            self.root,
            bg='white',
            relief='solid',
            bd=1
        )
        
        # Titre
        ttk.Label(
            self.bubble,
            text=step['title'],
            font=('Segoe UI', 12, 'bold'),
            background='white'
        ).pack(padx=10, pady=(10,5))
        
        # Message
        ttk.Label(
            self.bubble,
            text=step['message'],
            wraplength=300,
            background='white'
        ).pack(padx=10, pady=(0,10))
        
        # Boutons
        buttons = ttk.Frame(self.bubble, style='Card.TFrame')
        buttons.pack(fill='x', padx=10, pady=(0,10))
        
        if self.current_step > 0:
            ttk.Button(
                buttons,
                text="← Précédent",
                command=self._previous_step,
                style='Outline.TButton'
            ).pack(side='left')
            
        if self.current_step < len(steps) - 1:
            ttk.Button(
                buttons,
                text="Suivant →",
                command=self._next_step
            ).pack(side='right')
        else:
            ttk.Button(
                buttons,
                text="Terminer",
                command=self._end_tutorial
            ).pack(side='right')
            
        # Positionner la bulle
        if 'target' in step and step['target']:
            target = self.root.nametowidget(step['target'])
            if target:
                self._position_bubble(target, step.get('position', 'bottom'))
        else:
            # Centrer la bulle
            self.bubble.place(relx=0.5, rely=0.5, anchor='center')
            
    def _position_bubble(self, target, position):
        """Positionne la bulle par rapport à la cible."""
        # Obtenir les coordonnées de la cible
        x = target.winfo_rootx() - self.root.winfo_rootx()
        y = target.winfo_rooty() - self.root.winfo_rooty()
        w = target.winfo_width()
        h = target.winfo_height()
        
        # Positionner la bulle
        if position == "top":
            self.bubble.place(
                x=x + w//2,
                y=y - 10,
                anchor='s'
            )
        elif position == "bottom":
            self.bubble.place(
                x=x + w//2,
                y=y + h + 10,
                anchor='n'
            )
        elif position == "left":
            self.bubble.place(
                x=x - 10,
                y=y + h//2,
                anchor='e'
            )
        else:  # right
            self.bubble.place(
                x=x + w + 10,
                y=y + h//2,
                anchor='w'
            )
            
    def _next_step(self):
        """Passe à l'étape suivante."""
        self.current_step += 1
        self._show_current_step()
        
    def _previous_step(self):
        """Revient à l'étape précédente."""
        self.current_step -= 1
        self._show_current_step()
        
    def _end_tutorial(self):
        """Termine le tutoriel."""
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None
            
        if self.bubble:
            self.bubble.destroy()
            self.bubble = None
            
        self.current_tutorial = None
        self.current_step = 0
