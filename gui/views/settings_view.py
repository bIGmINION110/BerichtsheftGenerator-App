# gui/views/settings_view.py
# -*- coding: utf-8 -*-
"""
Definiert die Ansicht für die Anwendungseinstellungen.
"""
import customtkinter as ctk
import tkinter as tk
from typing import Dict, Any

from core import config
from ..widgets.accessible_widgets import AccessibleCTkButton, AccessibleCTkEntry, AccessibleCTkRadioButton

class SettingsView(ctk.CTkFrame):
    """Ansicht zur Verwaltung von globalen Anwendungseinstellungen."""

    def __init__(self, master, app_logic):
        super().__init__(master)
        self.app = app_logic
        self.data_manager = app_logic.data_manager

        self.default_stunden_vars: Dict[str, tk.StringVar] = {}
        self.default_format_var = tk.StringVar(value="docx")

        self._create_widgets()
        self.on_show() # Lade die Daten beim Initialisieren

    def on_show(self):
        """Lädt die Einstellungen, wenn die Ansicht angezeigt wird."""
        self._load_settings()

    def _create_widgets(self):
        """Erstellt die UI-Elemente der Ansicht."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(self, text="Anwendungseinstellungen", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=15, pady=15, sticky="w")

        # --- Frame für Standardstunden ---
        stunden_frame = ctk.CTkFrame(self)
        stunden_frame.grid(row=1, column=0, padx=15, pady=10, sticky="ew")
        stunden_frame.grid_columnconfigure((1, 3), weight=1)
        ctk.CTkLabel(stunden_frame, text="Standard-Arbeitszeiten", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=4, padx=15, pady=(15, 5), sticky="w")

        for i, tag in enumerate(config.WOCHENTAGE):
            self.default_stunden_vars[tag] = tk.StringVar()
            ctk.CTkLabel(stunden_frame, text=f"{tag}:").grid(row=i+1, column=0, padx=(15, 5), pady=8, sticky="w")
            entry = AccessibleCTkEntry(
                stunden_frame,
                textvariable=self.default_stunden_vars[tag],
                width=100,
                focus_color=config.FOCUS_COLOR,
                accessible_text=f"Standard-Stunden für {tag} im Format HH:MM.",
                status_callback=self.app.update_status,
                speak_callback=self.app.speak
            )
            entry.grid(row=i+1, column=1, padx=(0, 15), pady=8, sticky="w")

        # --- Frame für Standardformat ---
        format_frame = ctk.CTkFrame(self)
        format_frame.grid(row=2, column=0, padx=15, pady=10, sticky="new")
        format_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(format_frame, text="Standard-Exportformat", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 5), sticky="w")

        AccessibleCTkRadioButton(format_frame, text="DOCX", variable=self.default_format_var, value="docx",
                                 fg_color=config.ACCENT_COLOR, focus_color=config.FOCUS_COLOR,
                                 accessible_text="Setzt DOCX als Standard-Ausgabeformat.",
                                 status_callback=self.app.update_status,
                                 speak_callback=self.app.speak).grid(row=1, column=0, padx=15, pady=8, sticky="w")

        AccessibleCTkRadioButton(format_frame, text="PDF", variable=self.default_format_var, value="pdf",
                                 fg_color=config.ACCENT_COLOR, focus_color=config.FOCUS_COLOR,
                                 accessible_text="Setzt PDF als Standard-Ausgabeformat.",
                                 status_callback=self.app.update_status,
                                 speak_callback=self.app.speak).grid(row=2, column=0, padx=15, pady=8, sticky="w")

        # --- Speicher-Button ---
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=3, column=0, padx=15, pady=15, sticky="se")
        
        AccessibleCTkButton(
            button_frame, text="Einstellungen speichern",
            command=self._save_settings,
            font=ctk.CTkFont(weight="bold"),
            fg_color=config.ACCENT_COLOR,
            hover_color=config.HOVER_COLOR,
            accessible_text="Speichert alle vorgenommenen Einstellungen.",
            status_callback=self.app.update_status,
            speak_callback=self.app.speak
        ).pack()

    def _load_settings(self):
        """Lädt die aktuellen Einstellungen und füllt die UI-Felder."""
        konfig = self.data_manager.lade_konfiguration()
        einstellungen = konfig.get("einstellungen", {})
        default_stunden = einstellungen.get("default_stunden", {})

        for tag, var in self.default_stunden_vars.items():
            var.set(default_stunden.get(tag, "08:00")) # Fallback auf 08:00

        self.default_format_var.set(einstellungen.get("default_format", "docx"))
        self.app.update_status("Einstellungen geladen.")

    def _save_settings(self):
        """Sammelt die Daten aus der UI und speichert sie in der Konfigurationsdatei."""
        neue_einstellungen = {
            "default_stunden": {tag: var.get() for tag, var in self.default_stunden_vars.items()},
            "default_format": self.default_format_var.get()
        }
        self.app.speichere_einstellungen(neue_einstellungen)
