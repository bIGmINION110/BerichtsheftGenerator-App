# main.py
# -*- coding: utf-8 -*-
"""
Der Haupteinstiegspunkt für die Berichtsheft-Generator-Anwendung.

Diese Datei initialisiert das Logging und startet die grafische Benutzeroberfläche (GUI).
"""
import sys
import os
import logging
import tkinter as tk
from tkinter import messagebox

# KORREKTUR: Die problematische sys.path-Anweisung wurde entfernt.
# Das Skript sollte aus dem Hauptverzeichnis (berichtsheftgenerator-app) ausgeführt werden.

from core.logger_config import setup_logging
from gui.app import BerichtsheftApp

def main() -> None:
    """
    Hauptfunktion: Konfiguriert das Logging und startet die Anwendung.
    """
    try:
        # Das Logging muss als Allererstes initialisiert werden.
        setup_logging()
        logging.info("Anwendung wird gestartet.")

        # Die Hauptanwendung (GUI) wird erstellt und gestartet.
        app = BerichtsheftApp()
        app.mainloop()

    except Exception as e:
        # Fängt alle unerwarteten Fehler beim Start der GUI ab
        logging.critical("Ein schwerwiegender Fehler hat die Anwendung beendet.", exc_info=True)
        
        # Zeigt dem Benutzer eine einfache Fehlermeldung an.
        # Dies ist wichtig, falls das Logging selbst fehlschlägt.
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Fataler Fehler",
            f"Ein unerwarteter Fehler ist aufgetreten: {e}\n\n"
            "Die Anwendung wird beendet. Bitte prüfen Sie die Log-Dateien im 'logs'-Ordner."
        )
        sys.exit(1) # Beendet das Programm mit einem Fehlercode

    logging.info("Anwendung wurde normal beendet.")

if __name__ == "__main__":
    main()