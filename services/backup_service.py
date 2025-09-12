# services/backup_service.py
# -*- coding: utf-8 -*-
"""
Dienst zur Kapselung der Logik für den Datenexport und -import.
"""

import os
import zipfile
import logging
import shutil
from typing import Tuple

from core import config

logger = logging.getLogger(__name__)

class BackupService:
    """
    Stellt Methoden zum Sichern und Wiederherstellen von Anwendungsdaten bereit.
    """
    def export_all_data_to_zip(self, zip_path: str) -> Tuple[bool, str]:
        """Sammelt alle Datendateien UND erstellten Berichte und speichert sie in einem ZIP-Archiv."""
        try:
            folders_to_backup = [config.DATA_ORDNER, config.AUSGABE_ORDNER]
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for folder in folders_to_backup:
                    if not os.path.isdir(folder):
                        logger.warning(f"Zu sichernder Ordner '{folder}' nicht gefunden. Überspringe.")
                        continue
                    for root, _, files in os.walk(folder):
                        for file in files:
                            file_path = os.path.join(root, file)
                            # Speichert die Dateien mit relativem Pfad zum Basisverzeichnis
                            archive_name = os.path.relpath(file_path, start=config.BASE_DIR)
                            zipf.write(file_path, arcname=archive_name)
            
            logger.info(f"Alle Daten erfolgreich nach '{zip_path}' exportiert.")
            return True, "Alle Daten und Berichte wurden erfolgreich exportiert."
        except Exception as e:
            logger.error(f"Fehler beim Exportieren der Daten nach '{zip_path}'.", exc_info=True)
            return False, f"Fehler beim Exportieren der Daten: {e}"

    def import_all_data_from_zip(self, zip_path: str) -> Tuple[bool, str]:
        """Extrahiert alle Dateien aus einem ZIP-Archiv in die entsprechenden Ordner."""
        try:
            if not zipfile.is_zipfile(zip_path):
                logger.warning(f"Importversuch mit ungültiger ZIP-Datei: {zip_path}")
                return False, "Die ausgewählte Datei ist kein gültiges ZIP-Archiv."

            # Temporäre Backup-Pfade
            data_old = config.DATA_ORDNER + "_old"
            ausgabe_old = config.AUSGABE_ORDNER + "_old"
            
            # Alte Backup-Verzeichnisse entfernen, falls vorhanden
            if os.path.exists(data_old): shutil.rmtree(data_old)
            if os.path.exists(ausgabe_old): shutil.rmtree(ausgabe_old)

            # Aktuelle Daten sichern durch Umbenennen
            if os.path.exists(config.DATA_ORDNER):
                os.rename(config.DATA_ORDNER, data_old)
            if os.path.exists(config.AUSGABE_ORDNER):
                os.rename(config.AUSGABE_ORDNER, ausgabe_old)

            try:
                with zipfile.ZipFile(zip_path, 'r') as zipf:
                    # Extrahiert alle Dateien in das Basisverzeichnis der Anwendung
                    zipf.extractall(config.BASE_DIR) 
                
                # Wenn erfolgreich, alte Backups löschen
                if os.path.exists(data_old): shutil.rmtree(data_old)
                if os.path.exists(ausgabe_old): shutil.rmtree(ausgabe_old)
                
                logger.info(f"Alle Daten erfolgreich aus '{zip_path}' importiert.")
                return True, "Alle Daten und Berichte wurden erfolgreich importiert."

            except Exception as e:
                # Bei Fehlern den alten Zustand wiederherstellen
                logger.error(f"Fehler beim Extrahieren des Backups: {e}. Stelle alten Zustand wieder her.", exc_info=True)
                if os.path.exists(data_old):
                    if os.path.exists(config.DATA_ORDNER): shutil.rmtree(config.DATA_ORDNER)
                    os.rename(data_old, config.DATA_ORDNER)
                if os.path.exists(ausgabe_old):
                    if os.path.exists(config.AUSGABE_ORDNER): shutil.rmtree(config.AUSGABE_ORDNER)
                    os.rename(ausgabe_old, config.AUSGABE_ORDNER)
                return False, f"Fehler beim Import: {e}. Der vorherige Zustand wurde wiederhergestellt."

        except Exception as e:
            logger.error(f"Fehler beim Importieren der Daten aus '{zip_path}'.", exc_info=True)
            return False, f"Fehler beim Importieren der Daten: {e}"