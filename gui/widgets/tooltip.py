# gui/widgets/tooltip.py
# -*- coding: utf-8 -*-
"""
Definiert eine einfache Tooltip-Klasse für CustomTkinter-Widgets.

HINWEIS: Diese Klasse ist veraltet und sollte nicht mehr verwendet werden.
Sie ist nur für Maus-Interaktionen sichtbar und daher nicht barrierefrei.
Bitte stattdessen die 'AccessibleWidgets' verwenden, die eine Beschreibung
in der Statusleiste anzeigen, was auch für Screenreader und Tastaturnutzer
funktioniert.
"""

import customtkinter as ctk

class Tooltip:
    """
    Erstellt einen Tooltip (ein kleines Textfeld), der erscheint,
    wenn der Mauszeiger über einem Widget schwebt.
    
    VERALTET: Nicht für neue Implementierungen verwenden.
    """
    def __init__(self, widget: ctk.CTkBaseClass, text: str):
        """
        Initialisiert den Tooltip.

        Args:
            widget: Das Widget, an das der Tooltip angehängt werden soll.
            text: Der Text, der im Tooltip angezeigt werden soll.
        """
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        
        # Binden der Events an das Widget
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        """Zeigt das Tooltip-Fenster an."""
        if self.tooltip_window or not self.text:
            return

        # Position des Tooltips berechnen (unterhalb des Widgets)
        x = self.widget.winfo_rootx()
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        # Ein Toplevel-Fenster ohne Fensterdekoration erstellen
        self.tooltip_window = ctk.CTkToplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # Das Label mit dem Tooltip-Text erstellen
        label = ctk.CTkLabel(
            self.tooltip_window,
            text=self.text,
            font=ctk.CTkFont(size=12),
            fg_color=("#333333", "#444444"), # Dunkler Hintergrund
            corner_radius=5,
            padx=8,
            pady=4
        )
        label.pack()

    def hide_tooltip(self, event=None):
        """Versteckt und zerstört das Tooltip-Fenster."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
