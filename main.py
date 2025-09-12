# main.py
# -*- coding: utf-8 -*-
"""
Der Haupteinstiegspunkt für die Berichtsheft-Generator-Anwendung.

Diese Datei initialisiert das Logging und startet die grafische Benutzeroberfläche (GUI).
"""
import sys
import os
import logging

# Stellt sicher, dass die übergeordneten Verzeichnisse im Python-Pfad sind,
# damit Module wie 'core' und 'gui' korrekt importiert werden können.
# Dieser Block ist wichtig, wenn das Skript direkt ausgeführt wird.
try:
    # Dieser Pfad-Trick ist nützlich für die Entwicklung.
    # Für eine gebaute Anwendung (z.B. mit PyInstaller) ist er oft nicht nötig.
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
except Exception:
    # Falls __file__ nicht definiert ist (seltene Fälle), fahre ohne Pfadänderung fort
    pass

from core.logger_config import setup_logging
from gui.app import BerichtsheftApp

def main() -> None:
    """
    Hauptfunktion: Konfiguriert das Logging und startet die Anwendung.
    """
    # Das Logging muss als Allererstes initialisiert werden,
    # damit alle nachfolgenden Ereignisse (auch Fehler beim Start)
    # erfasst werden können.
    setup_logging()
    
    logging.info("Anwendung wird gestartet.")

    # Die Hauptanwendung (GUI) wird erstellt und gestartet.
    try:
        app = BerichtsheftApp()
        app.mainloop()
    except Exception as e:
        # Fängt alle unerwarteten Fehler beim Start der GUI ab
        logging.critical("Ein schwerwiegender Fehler hat die Anwendung beendet.", exc_info=True)
        # Optional: Zeige dem Benutzer eine einfache Fehlermeldung an
        # import tkinter as tk
        # from tkinter import messagebox
        # root = tk.Tk()
        # root.withdraw()
        # messagebox.showerror("Fatal Error", f"Ein unerwarteter Fehler ist aufgetreten: {e}\nDie Anwendung wird beendet. Bitte prüfen Sie die Log-Dateien.")

    logging.info("Anwendung wurde normal beendet.")

if __name__ == "__main__":
    main()