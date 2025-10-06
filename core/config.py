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
VERSION: str = "18.0.1"
GITHUB_LINK: str = "https://github.com/bigminion110/berichtsheftgenerator-app"
GITHUB_REPO_URL: str = "https://api.github.com/repos/bigminion110/berichtsheftgenerator-app/releases/latest"


# --- Verzeichnisse und Dateipfade ---
# KORREKTUR: Robuste Pfad-Ermittlung für Entwicklung und PyInstaller (.exe)
if getattr(sys, 'frozen', False):
    # Wenn die Anwendung "eingefroren" ist (als .exe läuft),
    # ist der Basispfad der temporäre Ordner von PyInstaller.
    BASE_DIR: str = sys._MEIPASS
else:
    # Im Entwicklungsmodus ist es das übergeordnete Verzeichnis von 'core'.
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_FOLDER: str = os.path.join(BASE_DIR, "data")
OUTPUT_FOLDER: str = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else BASE_DIR, "Ausbildungsnachweise")
ASSETS_FOLDER: str = os.path.join(BASE_DIR, "assets")
LOG_FOLDER: str = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else BASE_DIR, "logs")
FONTS_FOLDER: str = os.path.join(ASSETS_FOLDER, "fonts")

# --- Datenbank ---
DATABASE_FILE: str = os.path.join(DATA_FOLDER, "berichtsheft.db")

# Veraltete JSON-Pfade für die Migration
KONFIG_DATEI_OLD: str = os.path.join(DATA_FOLDER, "berichtsheft_konfig.json")
BERICHTS_DATEI_OLD: str = os.path.join(DATA_FOLDER, "berichts_daten.json")
VORLAGEN_DATEI_OLD: str = os.path.join(DATA_FOLDER, "templates.json")


LOGO_FILE: str = os.path.join(ASSETS_FOLDER, "image.png")
ICON_FILE: str = os.path.join(ASSETS_FOLDER, "icon.ico")


# --- Kernlogik ---
DAYS_IN_WEEK: List[str] = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]

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
    FONT_NORMAL = ctk.CTkFont(family=UI_FONT_FAMILY, size=14)
    FONT_BOLD = ctk.CTkFont(family=UI_FONT_FAMILY, size=16, weight="bold")
    FONT_TITLE = ctk.CTkFont(family=UI_FONT_FAMILY, size=22, weight="bold")
    FONT_SIDEBAR = ctk.CTkFont(family=UI_FONT_FAMILY, size=14)

# --- GUI-Design ---
# Ein modernes, blau-basiertes Farbschema
ACCENT_COLOR: str = "#007BFF"  # Helles Blau
HOVER_COLOR: str = "#0056b3"   # Dunkleres Blau für Hover
FRAME_BG_COLOR: Tuple[str, str] = ("#F8F9FA", "#121212") # Helles Grau und fast Schwarz
SIDEBAR_BG_COLOR: Tuple[str, str] = ("#FFFFFF", "#1E1E1E") # Weiß und dunkles Grau
SIDEBAR_BUTTON_INACTIVE_COLOR: str = "transparent"
ERROR_COLOR: str = "#DC3545"       # Rot
ERROR_HOVER_COLOR: str = "#C82333"  # Dunkleres Rot
FOCUS_COLOR: str = "#80BDFF"       # Helles Blau für Fokus
SPELLCHECK_ERROR_COLOR: str = "#52021e"  # Dunkelrot für Rechtschreibfehler
GRAMMAR_ERROR_COLOR: str = "#002f6c" # Dunkelblau für Grammatikfehler

# --- Generator-Einstellungen ---
# Diese Schriftarten werden mitgeliefert, daher sind sie plattformunabhängig
DOCX_FONT_HEADLINE: str = 'Verdana'
DOCX_FONT_BODY: str = 'Verdana'
PDF_FONT_HEADLINE: Tuple[str, str] = ('Verdana', 'B')
PDF_FONT_BODY: Tuple[str, str] = ('Verdana', '')