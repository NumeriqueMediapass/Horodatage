"""
Module de prévisualisation des documents.

Permet de prévisualiser les fichiers PDF et images dans l'interface.
"""

import os
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk


class DocumentPreview(ttk.Frame):
    """Widget de prévisualisation des documents."""
    
    def __init__(self, parent, **kwargs):
        """Initialise le widget de prévisualisation.
        
        Args:
            parent: Widget parent
            **kwargs: Arguments supplémentaires pour ttk.Frame
        """
        super().__init__(parent, **kwargs)
        
        # Configuration de l'affichage
        self.canvas = tk.Canvas(
            self,
            bg='white',
            highlightthickness=0
        )
        self.canvas.pack(expand=True, fill='both')
        
        # Scrollbars
        self.vsb = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview
        )
        self.hsb = ttk.Scrollbar(
            self,
            orient="horizontal",
            command=self.canvas.xview
        )
        self.canvas.configure(
            yscrollcommand=self.vsb.set,
            xscrollcommand=self.hsb.set
        )
        
        # Layout
        self.vsb.pack(side="right", fill="y")
        self.hsb.pack(side="bottom", fill="x")
        
        # Variables
        self.current_file = None
        self.current_image = None
        self.zoom_level = 1.0
        
        # Bindings
        self.canvas.bind('<Configure>', self._on_resize)
        self.bind_all('<Control-plus>', self.zoom_in)
        self.bind_all('<Control-minus>', self.zoom_out)
        self.bind_all('<Control-0>', self.zoom_reset)
        
    def preview_file(self, file_path):
        """Affiche la prévisualisation d'un fichier.
        
        Args:
            file_path: Chemin vers le fichier à prévisualiser
        """
        if not file_path or not os.path.exists(file_path):
            return
            
        self.current_file = file_path
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if ext == '.pdf':
                self._preview_pdf(file_path)
            elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                self._preview_image(file_path)
            else:
                self._show_message("Type de fichier non supporté")
        except Exception as e:
            self._show_message(f"Erreur : {str(e)}")
            
    def _preview_pdf(self, file_path):
        """Prévisualise un fichier PDF."""
        try:
            # Ouvrir le PDF
            doc = fitz.open(file_path)
            # Récupérer la première page
            page = doc[0]
            # Convertir en image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            # Convertir en image PIL
            img = Image.frombytes(
                "RGB",
                [pix.width, pix.height],
                pix.samples
            )
            # Afficher
            self._display_image(img)
            doc.close()
        except Exception as e:
            self._show_message(f"Erreur PDF : {str(e)}")
            
    def _preview_image(self, file_path):
        """Prévisualise une image."""
        try:
            img = Image.open(file_path)
            self._display_image(img)
        except Exception as e:
            self._show_message(f"Erreur image : {str(e)}")
            
    def _display_image(self, img):
        """Affiche une image dans le canvas."""
        # Redimensionner l'image pour qu'elle tienne dans le canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Calculer le ratio
        img_ratio = img.width / img.height
        canvas_ratio = canvas_width / canvas_height
        
        if img_ratio > canvas_ratio:
            new_width = canvas_width
            new_height = int(canvas_width / img_ratio)
        else:
            new_height = canvas_height
            new_width = int(canvas_height * img_ratio)
            
        # Appliquer le zoom
        new_width = int(new_width * self.zoom_level)
        new_height = int(new_height * self.zoom_level)
        
        # Redimensionner
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convertir en PhotoImage
        self.current_image = ImageTk.PhotoImage(img)
        
        # Afficher
        self.canvas.delete("all")
        self.canvas.create_image(
            canvas_width//2,
            canvas_height//2,
            image=self.current_image,
            anchor="center"
        )
        
        # Configurer le scrolling
        self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        )
        
    def _show_message(self, message):
        """Affiche un message dans le canvas."""
        self.canvas.delete("all")
        self.canvas.create_text(
            self.canvas.winfo_width()//2,
            self.canvas.winfo_height()//2,
            text=message,
            fill="gray",
            font=("Segoe UI", 12)
        )
        
    def _on_resize(self, event):
        """Gère le redimensionnement de la fenêtre."""
        if self.current_file:
            self.preview_file(self.current_file)
            
    def zoom_in(self, event=None):
        """Augmente le zoom."""
        self.zoom_level *= 1.2
        if self.current_file:
            self.preview_file(self.current_file)
            
    def zoom_out(self, event=None):
        """Diminue le zoom."""
        self.zoom_level /= 1.2
        if self.current_file:
            self.preview_file(self.current_file)
            
    def zoom_reset(self, event=None):
        """Réinitialise le zoom."""
        self.zoom_level = 1.0
        if self.current_file:
            self.preview_file(self.current_file)
