# gui/views/help_view.py
# -*- coding: utf-8 -*-
"""
Definiert die Hilfe-Ansicht, die eine Übersicht der Tastenkombinationen anzeigt.
"""
import customtkinter as ctk
from core import config

class HelpView(ctk.CTkFrame):
    """Eine Ansicht, die alle wichtigen Tastenkombinationen auflistet."""

    def __init__(self, master, app_logic):
        super().__init__(master)
        self.app = app_logic
        
        self.title_font = ctk.CTkFont(family=config.UI_FONT_FAMILY, size=18, weight="bold")
        self.header_font = ctk.CTkFont(family=config.UI_FONT_FAMILY, size=14, weight="bold")
        self.normal_font = ctk.CTkFont(family=config.UI_FONT_FAMILY, size=13)
        
        self._create_widgets()

    def _create_widgets(self):
        """Erstellt die UI-Elemente der Ansicht."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Übersicht der Tastenkombinationen", font=self.title_font).grid(
            row=0, column=0, padx=15, pady=15, sticky="w"
        )
        
        scroll_frame = ctk.CTkScrollableFrame(self)
        scroll_frame.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)

        # Container Frame für ein besseres Layout
        container = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        container.pack(fill="x", expand=True, padx=10, pady=5)
        container.grid_columnconfigure(0, weight=1) # Linker Abstand
        container.grid_columnconfigure(2, weight=1) # Rechter Abstand

        # --- Globale Aktionen ---
        ctk.CTkLabel(container, text="Globale Aktionen", font=self.header_font).grid(
            row=0, column=1, pady=(10, 5), sticky="w"
        )
        self._add_shortcut(container, 1, "Bericht erstellen:", "Strg + G")
        self._add_shortcut(container, 2, "Bericht nur speichern:", "Strg + S")
        self._add_shortcut(container, 3, "leere Bericht vorbereiten:", "Strg + N")
        self._add_shortcut(container, 4, "Ausgabeordner öffnen:", "Strg + O")

        # --- Navigation ---
        ctk.CTkLabel(container, text="Navigation", font=self.header_font).grid(
            row=5, column=1, pady=(20, 5), sticky="w"
        )
        self._add_shortcut(container, 6, "Ansicht: Berichtsheft", "Strg + 1")
        self._add_shortcut(container, 7, "Ansicht: Bericht laden", "Strg + L")
        self._add_shortcut(container, 8, "Ansicht: Importieren", "Strg + 3")
        self._add_shortcut(container, 9, "Ansicht: Vorlagen", "Strg + 4")
        self._add_shortcut(container, 10, "Ansicht: Statistiken", "Strg + 5")
        self._add_shortcut(container, 11, "Ansicht: Backup", "Strg + 6")
        self._add_shortcut(container, 12, "Ansicht: Einstellungen", "Strg + 7")
        self._add_shortcut(container, 13, "Nächster Tag (Tab):", "Strg + Tab")
        self._add_shortcut(container, 14, "Vorheriger Tag (Tab):", "Strg + Umschalt + Tab")

        # --- Textbearbeitung ---
        ctk.CTkLabel(container, text="Textbearbeitung (in Eingabefeldern)", font=self.header_font).grid(
            row=15, column=1, pady=(20, 5), sticky="w"
        )
        self._add_shortcut(container, 16, "Wort links löschen:", "Strg + Rücktaste")
        self._add_shortcut(container, 17, "Wort rechts löschen:", "Strg + Entf")
        
        # --- Bericht laden Ansicht ---
        '''ctk.CTkLabel(container, text="In der 'Bericht laden' Ansicht", font=self.header_font).grid(
            row=18, column=1, pady=(20, 5), sticky="w"
        )
        self._add_shortcut(container, 19, "Eintrag auswählen:", "Pfeil Hoch / Runter")
        self._add_shortcut(container, 20, "Auswahl laden:", "Enter / Leertaste")
        self._add_shortcut(container, 21, "Auswahl löschen:", "Entf")'''

    
    
    def _add_shortcut(self, master, row, description, keys):
        """Hilfsfunktion zum Hinzufügen einer Shortcut-Zeile."""
        ctk.CTkLabel(master, text=description, font=self.normal_font, anchor="w").grid(
            row=row, column=1, padx=20, pady=2, sticky="w"
        )
        ctk.CTkLabel(master, text=keys, font=self.normal_font, anchor="e", text_color="gray60").grid(
            row=row, column=1, padx=20, pady=2, sticky="e"
        )