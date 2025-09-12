# gui/views/settings_view.py
# -*- coding: utf-8 -*-
"""
Definiert die Ansicht für die Anwendungseinstellungen.
"""
import customtkinter as ctk
import tkinter as tk
from typing import Dict, Any

from core import config
from ..widgets.accessible_widgets import AccessibleCTkButton, AccessibleCTkEntry, AccessibleCTkRadioButton, AccessibleCTkComboBox

class SettingsView(ctk.CTkFrame):
    """Ansicht zur Verwaltung von globalen Anwendungseinstellungen."""

    def __init__(self, master, app_logic):
        super().__init__(master)
        self.app = app_logic
        self.data_manager = app_logic.data_manager

        # Variablen für UI-Elemente
        self.name_var = tk.StringVar()
        self.startdatum_var = tk.StringVar()
        self.default_stunden_vars: Dict[str, tk.StringVar] = {}
        self.default_typen_vars: Dict[str, tk.StringVar] = {}
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

        # --- Frame für alle Einstellungen ---
        settings_container = ctk.CTkScrollableFrame(self)
        settings_container.grid(row=1, column=0, rowspan=2, padx=15, pady=10, sticky="nsew")
        settings_container.grid_columnconfigure(0, weight=1)
        
        # --- Persönliche Daten ---
        persoenliche_daten_frame = ctk.CTkFrame(settings_container)
        persoenliche_daten_frame.pack(fill="x", padx=0, pady=5)
        persoenliche_daten_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(persoenliche_daten_frame, text="Persönliche Daten", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 5), sticky="w")
        
        ctk.CTkLabel(persoenliche_daten_frame, text="Name des Azubis:").grid(row=1, column=0, padx=(15, 5), pady=8, sticky="w")
        name_entry = AccessibleCTkEntry(
            persoenliche_daten_frame, textvariable=self.name_var, focus_color=config.FOCUS_COLOR,
            accessible_text="Name des Auszubildenden. Wird für alle Berichte verwendet.",
            status_callback=self.app.update_status, speak_callback=self.app.speak)
        name_entry.grid(row=1, column=1, padx=(0, 15), pady=8, sticky="ew")

        ctk.CTkLabel(persoenliche_daten_frame, text="Start der Ausbildung:").grid(row=2, column=0, padx=(15, 5), pady=8, sticky="w")
        start_entry = AccessibleCTkEntry(
            persoenliche_daten_frame, textvariable=self.startdatum_var, placeholder_text="TT.MM.JJJJ", focus_color=config.FOCUS_COLOR,
            accessible_text="Startdatum der Ausbildung im Format Tag.Monat.Jahr.",
            status_callback=self.app.update_status, speak_callback=self.app.speak)
        start_entry.grid(row=2, column=1, padx=(0, 15), pady=8, sticky="ew")


        # --- Standard-Typen und Stunden in einem Frame ---
        defaults_frame = ctk.CTkFrame(settings_container)
        defaults_frame.pack(fill="x", padx=0, pady=5, expand=True)
        defaults_frame.grid_columnconfigure((0, 1), weight=1)

        typen_frame = ctk.CTkFrame(defaults_frame, fg_color="transparent")
        typen_frame.grid(row=0, column=0, padx=15, pady=10, sticky="ns")
        typen_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(typen_frame, text="Standard-Typen", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 5), sticky="w")

        for i, tag in enumerate(config.WOCHENTAGE):
            self.default_typen_vars[tag] = tk.StringVar()
            ctk.CTkLabel(typen_frame, text=f"{tag}:").grid(row=i + 1, column=0, padx=(15, 5), pady=8, sticky="w")
            combo = AccessibleCTkComboBox(
                typen_frame, variable=self.default_typen_vars[tag], values=["Betrieb", "Schule"], width=120,
                focus_color=config.FOCUS_COLOR, accessible_text=f"Standard-Typ für {tag}.",
                status_callback=self.app.update_status, speak_callback=self.app.speak)
            combo.grid(row=i + 1, column=1, padx=(0, 15), pady=8, sticky="w")

        stunden_frame = ctk.CTkFrame(defaults_frame, fg_color="transparent")
        stunden_frame.grid(row=0, column=1, padx=15, pady=10, sticky="ns")
        stunden_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(stunden_frame, text="Standard-Arbeitszeiten", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 5), sticky="w")

        for i, tag in enumerate(config.WOCHENTAGE):
            self.default_stunden_vars[tag] = tk.StringVar()
            ctk.CTkLabel(stunden_frame, text=f"{tag}:").grid(row=i+1, column=0, padx=(15, 5), pady=8, sticky="w")
            entry = AccessibleCTkEntry(
                stunden_frame, textvariable=self.default_stunden_vars[tag], width=100, focus_color=config.FOCUS_COLOR,
                accessible_text=f"Standard-Stunden für {tag} im Format HH:MM.",
                status_callback=self.app.update_status, speak_callback=self.app.speak)
            entry.grid(row=i+1, column=1, padx=(0, 15), pady=8, sticky="w")

        # --- Standard-Exportformat ---
        format_frame = ctk.CTkFrame(settings_container)
        format_frame.pack(fill="x", padx=0, pady=5)
        format_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(format_frame, text="Standard-Exportformat", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 5), sticky="w")

        AccessibleCTkRadioButton(format_frame, text="DOCX", variable=self.default_format_var, value="docx",
                                 fg_color=config.ACCENT_COLOR, focus_color=config.FOCUS_COLOR,
                                 accessible_text="Setzt DOCX als Standard-Ausgabeformat.",
                                 status_callback=self.app.update_status, speak_callback=self.app.speak).grid(row=1, column=0, padx=15, pady=8, sticky="w")

        AccessibleCTkRadioButton(format_frame, text="PDF", variable=self.default_format_var, value="pdf",
                                 fg_color=config.ACCENT_COLOR, focus_color=config.FOCUS_COLOR,
                                 accessible_text="Setzt PDF als Standard-Ausgabeformat.",
                                 status_callback=self.app.update_status, speak_callback=self.app.speak).grid(row=2, column=0, padx=15, pady=8, sticky="w")

        # --- Speicher-Button ---
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=3, column=0, padx=15, pady=15, sticky="sew")
        
        AccessibleCTkButton(
            button_frame, text="Einstellungen speichern",
            command=self._save_settings, font=ctk.CTkFont(weight="bold"), fg_color=config.ACCENT_COLOR,
            hover_color=config.HOVER_COLOR, accessible_text="Speichert alle vorgenommenen Einstellungen.",
            status_callback=self.app.update_status, speak_callback=self.app.speak
        ).pack(anchor="e")

    def _load_settings(self):
        """Lädt die aktuellen Einstellungen und füllt die UI-Felder."""
        konfig = self.data_manager.lade_konfiguration()
        self.name_var.set(konfig.get("name_azubi", ""))
        self.startdatum_var.set(konfig.get("startdatum_ausbildung", ""))

        einstellungen = konfig.get("einstellungen", {})
        
        default_typen = einstellungen.get("default_typen", {})
        for tag, var in self.default_typen_vars.items():
            var.set(default_typen.get(tag, "Betrieb"))

        default_stunden = einstellungen.get("default_stunden", {})
        for tag, var in self.default_stunden_vars.items():
            var.set(default_stunden.get(tag, "08:00"))
        
        self.default_format_var.set(einstellungen.get("default_format", "docx"))
        self.app.update_status("Einstellungen geladen.")

    def _save_settings(self):
        """Sammelt die Daten aus der UI und speichert sie in der Konfigurationsdatei."""
        # Persönliche Daten direkt in der Haupt-App speichern lassen
        self.app.speichere_persoenliche_daten(
            self.name_var.get(),
            self.startdatum_var.get()
        )
        
        # Andere Einstellungen speichern
        neue_einstellungen = {
            "default_stunden": {tag: var.get() for tag, var in self.default_stunden_vars.items()},
            "default_typen": {tag: var.get() for tag, var in self.default_typen_vars.items()},
            "default_format": self.default_format_var.get()
        }
        self.app.speichere_einstellungen(neue_einstellungen)

