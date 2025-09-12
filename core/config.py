# core/config.py
# -*- coding: utf-8 -*-
"""
Zentrale Konfigurationsdatei für Konstanten und Einstellungen.
"""

import os
import sys
from typing import List, Tuple

# --- Anwendungsinformationen ---
APP_NAME: str = "Berichtsheft-Generator"
VERSION: str = "17.0-Stable"
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

KONFIG_DATEI: str = os.path.join(DATA_ORDNER, "berichtsheft_konfig.json")
BERICHTS_DATEI: str = os.path.join(DATA_ORDNER, "berichts_daten.json")
VORLAGEN_DATEI: str = os.path.join(DATA_ORDNER, "templates.json")
LOGO_DATEI: str = os.path.join(ASSETS_ORDNER, "image.png")
ICON_DATEI: str = os.path.join(ASSETS_ORDNER, "icon.ico")


# --- Kernlogik ---
WOCHENTAGE: List[str] = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]

# --- GUI-Design ---
# Ein modernes, blau-basiertes Farbschema
ACCENT_COLOR: str = "#3B82F6"  # Modernes Blau
HOVER_COLOR: str = "#60A5FA"   # Helleres Blau für Hover-Effekte
FRAME_BG_COLOR: Tuple[str, str] = ("#F1F5F9", "#1E293B") # Helles und dunkles Schiefergrau
SIDEBAR_BG_COLOR: Tuple[str, str] = ("#FFFFFF", "#111827") # Weiß und sehr dunkles Grau
SIDEBAR_BUTTON_FONT: Tuple[str, int] = ("Segoe UI", 16)
SIDEBAR_BUTTON_INACTIVE_COLOR: str = "transparent"
ERROR_COLOR: str = "#EF4444"       # Kräftiges Rot
ERROR_HOVER_COLOR: str = "#DC2626"  # Dunkleres Rot
FOCUS_COLOR: str = "#2563EB"       # Ein etwas dunkleres Blau für den Fokus

# --- Generator-Einstellungen ---
DOCX_FONT_HEADLINE: str = 'Verdana'
DOCX_FONT_BODY: str = 'Verdana'
PDF_FONT_HEADLINE: Tuple[str, str] = ('Verdana', 'B')
PDF_FONT_BODY: Tuple[str, str] = ('Verdana', '')

