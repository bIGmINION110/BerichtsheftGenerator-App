# core/config.py
# -*- coding: utf-8 -*-
"""
Zentrale Konfigurationsdatei für Konstanten und Einstellungen.
"""

import os
import sys
from typing import List, Tuple
import customtkinter as ctk

# --- Anwendungsinformationen ---
APP_NAME: str = "Berichtsheft-Generator"
VERSION: str = "17.5.0"
GITHUB_REPO_URL: str = "https://api.github.com/repos/bigminion110/berichtsheftgenerator-app/releases/latest"

# --- Verzeichnisse und Dateipfade ---
if getattr(sys, 'frozen', False):
    BASE_DIR: str = os.path.dirname(sys.executable)
else:
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_ORDNER: str = os.path.join(BASE_DIR, "data")
AUSGABE_ORDNER: str = os.path.join(BASE_DIR, "Ausbildungsnachweise")
ASSETS_ORDNER: str = os.path.join(BASE_DIR, "assets")
LOG_ORDNER: str = os.path.join(BASE_DIR, "logs")
FONTS_ORDNER: str = os.path.join(ASSETS_ORDNER, "fonts")

# --- Datenbank ---
DATENBANK_DATEI: str = os.path.join(DATA_ORDNER, "berichtsheft.db")

# Veraltete JSON-Pfade für die Migration
KONFIG_DATEI_OLD: str = os.path.join(DATA_ORDNER, "berichtsheft_konfig.json")
BERICHTS_DATEI_OLD: str = os.path.join(DATA_ORDNER, "berichts_daten.json")
VORLAGEN_DATEI_OLD: str = os.path.join(DATA_ORDNER, "templates.json")


LOGO_DATEI: str = os.path.join(ASSETS_ORDNER, "image.png")
ICON_DATEI: str = os.path.join(ASSETS_ORDNER, "icon.ico")


# --- Kernlogik ---
WOCHENTAGE: List[str] = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]

# --- GUI-Schriftarten und -Größen ---
def get_ui_font() -> str:
    """Wählt die beste verfügbare Systemschriftart für die Benutzeroberfläche."""
    if sys.platform == "win32":
        return "Segoe UI"
    elif sys.platform == "darwin": # macOS
        return "SF Display"
    else: # Linux und andere
        return "DejaVu Sans"

UI_FONT_FAMILY = get_ui_font()

# --- NEU: Schriftarten initial auf None setzen, um Ladefehler zu vermeiden ---
FONT_NORMAL = None
FONT_BOLD = None
FONT_TITLE = None
FONT_SIDEBAR = None

def initialize_fonts():
    """Initialisiert die globalen Schriftart-Objekte. Muss nach dem CTk-Hauptfenster aufgerufen werden."""
    global FONT_NORMAL, FONT_BOLD, FONT_TITLE, FONT_SIDEBAR
    FONT_NORMAL = ctk.CTkFont(family=UI_FONT_FAMILY, size=15)
    FONT_BOLD = ctk.CTkFont(family=UI_FONT_FAMILY, size=16, weight="bold")
    FONT_TITLE = ctk.CTkFont(family=UI_FONT_FAMILY, size=22, weight="bold")
    FONT_SIDEBAR = ctk.CTkFont(family=UI_FONT_FAMILY, size=18)


# --- GUI-Design ---
# Ein modernes, blau-basiertes Farbschema
ACCENT_COLOR: str = "#3B82F6"  # Modernes Blau
HOVER_COLOR: str = "#60A5FA"   # Helleres Blau für Hover-Effekte
FRAME_BG_COLOR: Tuple[str, str] = ("#F1F5F9", "#1E293B") # Helles und dunkles Schiefergrau
SIDEBAR_BG_COLOR: Tuple[str, str] = ("#FFFFFF", "#111827") # Weiß und sehr dunkles Grau
SIDEBAR_BUTTON_INACTIVE_COLOR: str = "transparent"
ERROR_COLOR: str = "#EF4444"       # Kräftiges Rot
ERROR_HOVER_COLOR: str = "#DC2626"  # Dunkleres Rot
FOCUS_COLOR: str = "#2563EB"       # Ein etwas dunkleres Blau für den Fokus

# --- Generator-Einstellungen ---
# Diese Schriftarten werden mitgeliefert, daher sind sie plattformunabhängig
DOCX_FONT_HEADLINE: str = 'Verdana'
DOCX_FONT_BODY: str = 'Verdana'
PDF_FONT_HEADLINE: Tuple[str, str] = ('Verdana', 'B')
PDF_FONT_BODY: Tuple[str, str] = ('Verdana', '')

