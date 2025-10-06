# core/logger_config.py
# -*- coding: utf-8 -*-
"""
Konfiguriert das zentrale Logging-System für die Anwendung.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from core import config

# Definiert den Speicherort für die Log-Dateien
LOG_DATEI = os.path.join(config.LOG_FOLDER, "berichtsheft_generator.log")

def setup_logging() -> None:
    """
    Richtet das Logging für die gesamte Anwendung ein.

    - Erstellt einen Logger.
    - Konfiguriert einen File-Handler, der Lognachrichten in eine rotierende Datei schreibt.
    - Konfiguriert einen Stream-Handler für die Ausgabe in der Konsole (für Debugging).
    - Setzt das Loglevel auf INFO.
    - Reduziert die Ausführlichkeit von Drittanbieter-Bibliotheken.
    """
    # Sicherstellen, dass der Log-Ordner existiert
    os.makedirs(config.LOG_FOLDER, exist_ok=True)

    # Ein einheitliches Format für alle Log-Nachrichten definieren
    formatter = logging.Formatter(
        '%(asctime)s - %(name)-25s - %(levelname)-8s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Root-Logger abrufen, damit er anwendungsweit verfügbar ist
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG) # Standard-Loglevel für unsere App-Module

    # Verhindern, dass Handler mehrfach hinzugefügt werden
    if logger.hasHandlers():
        logger.handlers.clear()

    # File-Handler erstellen, der die Log-Dateien bei 1MB Größe rotiert
    file_handler = RotatingFileHandler(
        LOG_DATEI, maxBytes=1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Zusätzlich einen Konsolen-Handler für direktes Feedback beim Entwickeln
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # --- WICHTIG: Log-Level für geschwätzige Bibliotheken anpassen ---
    # Setzt das Logging für Matplotlib und Pillow auf WARNING, um DEBUG-Spam zu vermeiden.
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)
    # --- Ende der Anpassung ---

    logging.info("Logging wurde erfolgreich initialisiert.")