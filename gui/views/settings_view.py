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

        # --- VERBESSERUNG: Plattformunabhängige Schriftart verwenden ---
        self.main_font = ctk.CTkFont(family=config.UI_FONT_FAMILY, size=13)
        self.bold_font = ctk.CTkFont(family=config.UI_FONT_FAMILY, size=14, weight="bold")
        self.title_font = ctk.CTkFont(family=config.UI_FONT_FAMILY, size=18, weight="bold")

        # Variablen für UI-Elemente
        self.name_var = tk.StringVar()
        self.startdatum_var = tk.StringVar()
        self.default_stunden_vars: Dict[str, tk.StringVar] = {}
        self.default_typen_vars: Dict[str, tk.StringVar] = {}
        self.default_format_var = tk.StringVar(value="docx")
        self.animation_type_var = tk.StringVar(value="slide") # NEU

        self._create_widgets()
        self.on_show() # Lade die Daten beim Initialisieren

    def on_show(self):
        """Lädt die Einstellungen, wenn die Ansicht angezeigt wird."""
        self._load_settings()

    def _create_widgets(self):
        """Erstellt die UI-Elemente der Ansicht."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) 

        ctk.CTkLabel(self, text="Anwendungseinstellungen", font=self.title_font).grid(row=0, column=0, padx=15, pady=15, sticky="w")

        # --- Frame für alle Einstellungen ---
        settings_container = ctk.CTkScrollableFrame(self)
        settings_container.grid(row=1, column=0, rowspan=2, padx=15, pady=10, sticky="nsew")
        settings_container.grid_columnconfigure(0, weight=1)
        
        # --- Persönliche Daten ---
        persoenliche_daten_frame = ctk.CTkFrame(settings_container, corner_radius=8)
        persoenliche_daten_frame.pack(fill="x", padx=0, pady=5)
        persoenliche_daten_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(persoenliche_daten_frame, text="Persönliche Daten", font=self.bold_font).grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 5), sticky="w")
        
        ctk.CTkLabel(persoenliche_daten_frame, text="Name des Azubis:", font=self.main_font).grid(row=1, column=0, padx=(15, 5), pady=8, sticky="w")
        name_entry = AccessibleCTkEntry(
            persoenliche_daten_frame, textvariable=self.name_var, font=self.main_font, corner_radius=8, focus_color=config.FOCUS_COLOR,
            accessible_text="Name des Auszubildenden. Wird für alle Berichte verwendet.",
            status_callback=self.app.update_status, speak_callback=self.app.speak)
        name_entry.grid(row=1, column=1, padx=(0, 15), pady=8, sticky="ew")
        name_entry.configure(state="normal")

        ctk.CTkLabel(persoenliche_daten_frame, text="Start der Ausbildung:", font=self.main_font).grid(row=2, column=0, padx=(15, 5), pady=8, sticky="w")
        start_entry = AccessibleCTkEntry(
            persoenliche_daten_frame, textvariable=self.startdatum_var, placeholder_text="TT.MM.JJJJ", font=self.main_font, corner_radius=8, focus_color=config.FOCUS_COLOR,
            accessible_text="Startdatum der Ausbildung im Format Tag.Monat.Jahr.",
            status_callback=self.app.update_status, speak_callback=self.app.speak)
        start_entry.grid(row=2, column=1, padx=(0, 15), pady=8, sticky="ew")
        start_entry.configure(state="normal")

        # --- GUI-Einstellungen (Animationen) --- NEU
        gui_frame = ctk.CTkFrame(settings_container, corner_radius=8)
        gui_frame.pack(fill="x", padx=0, pady=5, expand=True)
        gui_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(gui_frame, text="Darstellung", font=self.bold_font).grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 5), sticky="w")
        
        ctk.CTkLabel(gui_frame, text="Animationstyp:", font=self.main_font).grid(row=1, column=0, padx=(15, 5), pady=8, sticky="w")
        animation_menu = ctk.CTkOptionMenu(
            gui_frame, variable=self.animation_type_var, values=["slide", "fade", "zoom"], font=self.main_font, corner_radius=8)
        animation_menu.grid(row=1, column=1, padx=(0, 15), pady=8, sticky="w")


        # --- Standard-Typen und Stunden in einem Frame ---
        defaults_frame = ctk.CTkFrame(settings_container, corner_radius=8)
        defaults_frame.pack(fill="x", padx=0, pady=5, expand=True)
        defaults_frame.grid_columnconfigure((0, 1), weight=1)

        typen_frame = ctk.CTkFrame(defaults_frame, fg_color="transparent")
        typen_frame.grid(row=0, column=0, padx=15, pady=10, sticky="ns")
        typen_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(typen_frame, text="Standard-Typen", font=self.bold_font).grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 5), sticky="w")

        for i, tag in enumerate(config.DAYS_IN_WEEK):
            self.default_typen_vars[tag] = tk.StringVar()
            ctk.CTkLabel(typen_frame, text=f"{tag}:", font=self.main_font).grid(row=i + 1, column=0, padx=(15, 5), pady=8, sticky="w")
            combo = AccessibleCTkComboBox(
                typen_frame, variable=self.default_typen_vars[tag], values=["Betrieb", "Schule"], width=120, font=self.main_font, corner_radius=8,
                focus_color=config.FOCUS_COLOR, accessible_text=f"Standard-Typ für {tag}.",
                status_callback=self.app.update_status, speak_callback=self.app.speak)
            combo.grid(row=i + 1, column=1, padx=(0, 15), pady=8, sticky="w")

        stunden_frame = ctk.CTkFrame(defaults_frame, fg_color="transparent")
        stunden_frame.grid(row=0, column=1, padx=15, pady=10, sticky="ns")
        stunden_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(stunden_frame, text="Standard-Arbeitszeiten", font=self.bold_font).grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 5), sticky="w")

        for i, tag in enumerate(config.DAYS_IN_WEEK):
            self.default_stunden_vars[tag] = tk.StringVar()
            ctk.CTkLabel(stunden_frame, text=f"{tag}:", font=self.main_font).grid(row=i+1, column=0, padx=(15, 5), pady=8, sticky="w")
            entry = AccessibleCTkEntry(
                stunden_frame, textvariable=self.default_stunden_vars[tag], width=100, font=self.main_font, corner_radius=8, focus_color=config.FOCUS_COLOR,
                accessible_text=f"Standard-Stunden für {tag} im Format HH:MM.",
                status_callback=self.app.update_status, speak_callback=self.app.speak, navigation_mode='time')
            entry.grid(row=i+1, column=1, padx=(0, 15), pady=8, sticky="w")

        # --- Standard-Exportformat ---
        format_frame = ctk.CTkFrame(settings_container, corner_radius=8)
        format_frame.pack(fill="x", padx=0, pady=5)
        format_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(format_frame, text="Standard-Exportformat", font=self.bold_font).grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 5), sticky="w")

        AccessibleCTkRadioButton(format_frame, text="DOCX", variable=self.default_format_var, value="docx", font=self.main_font,
                                 fg_color=config.ACCENT_COLOR, focus_color=config.FOCUS_COLOR,
                                 accessible_text="Setzt DOCX als Standard-Ausgabeformat.",
                                 status_callback=self.app.update_status, speak_callback=self.app.speak).grid(row=1, column=0, padx=15, pady=8, sticky="w")

        AccessibleCTkRadioButton(format_frame, text="PDF", variable=self.default_format_var, value="pdf", font=self.main_font,
                                 fg_color=config.ACCENT_COLOR, focus_color=config.FOCUS_COLOR,
                                 accessible_text="Setzt PDF als Standard-Ausgabeformat.",
                                 status_callback=self.app.update_status, speak_callback=self.app.speak).grid(row=2, column=0, padx=15, pady=8, sticky="w")

        # --- Speicher-Button ---
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=3, column=0, padx=15, pady=15, sticky="sew")
        
        AccessibleCTkButton(
            button_frame, text="Einstellungen speichern",
            command=self._save_settings, font=self.bold_font, fg_color=config.ACCENT_COLOR,
            hover_color=config.HOVER_COLOR, corner_radius=8, accessible_text="Speichert alle vorgenommenen Einstellungen.",
            status_callback=self.app.update_status, speak_callback=self.app.speak
        ).pack(anchor="e")

    def _load_settings(self):
        """Lädt die aktuellen Einstellungen und füllt die UI-Felder."""
        konfig = self.data_manager.lade_konfiguration()
        self.name_var.set(konfig.get("name_azubi", ""))
        self.startdatum_var.set(konfig.get("startdatum_ausbildung", ""))

        einstellungen = konfig.get("einstellungen", {})
        
        self.animation_type_var.set(einstellungen.get("animation_type", "slide"))
        self.default_format_var.set(einstellungen.get("default_format", "docx"))
        
        default_typen = einstellungen.get("default_typen", {})
        for tag, var in self.default_typen_vars.items():
            var.set(default_typen.get(tag, "Betrieb"))

        default_stunden = einstellungen.get("default_stunden", {})
        for tag, var in self.default_stunden_vars.items():
            var.set(default_stunden.get(tag, "08:00"))
        
        self.app.update_status("Einstellungen geladen.")

    def _save_settings(self):
        """Sammelt die Daten aus der UI und speichert sie in der Konfigurationsdatei."""
        self.app.speichere_persoenliche_daten(
            self.name_var.get(),
            self.startdatum_var.get()
        )
        
        neue_einstellungen = {
            "default_stunden": {tag: var.get() for tag, var in self.default_stunden_vars.items()},
            "default_typen": {tag: var.get() for tag, var in self.default_typen_vars.items()},
            "default_format": self.default_format_var.get(),
            "animation_type": self.animation_type_var.get()
        }
        self.app.speichere_einstellungen(neue_einstellungen)