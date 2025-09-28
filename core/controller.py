# core/controller.py
# -*- coding: utf-8 -*-
"""
Steuert die Anwendungslogik und agiert als Bindeglied zwischen GUI und Daten.
"""
import logging
from datetime import date
from typing import Dict, Any, Tuple, List
import os

from core.logic import BerichtsheftLogik
from core.data_manager import DataManager
from generators.docx_generator import DocxGenerator
from generators.pdf_generator import PdfGenerator
from services.backup_service import BackupService
from services.importer_service import ImporterService

# Logger für dieses Modul initialisieren
logger = logging.getLogger(__name__)

class AppController:
    """
    Das "Gehirn" der Anwendung. Kapselt die Hauptlogik.
    """
    def __init__(self, data_manager: DataManager):
        """
        Initialisiert den Controller.

        Args:
            data_manager: Eine Instanz des DataManagers für den Datenzugriff.
        """
        self.data_manager = data_manager
        self.backup_service = BackupService(self.data_manager) # DataManager übergeben
        self.importer_service = ImporterService()
        logger.info("AppController wurde initialisiert.")

    def erstelle_bericht(self, context: Dict[str, Any], format: str) -> Tuple[bool, str]:
        """
        Validiert die Daten, erstellt den Bericht und speichert Konfiguration sowie Statistik.

        Args:
            context: Die aus der GUI gesammelten Daten.
            format: Das gewünschte Ausgabeformat ("docx" oder "pdf").

        Returns:
            Ein Tupel bestehend aus einem Boolean für den Erfolg und einer Statusnachricht.
        """
        logger.info(f"Anfrage zur Erstellung eines Berichts im Format '{format}' erhalten.")
        try:
            # 1. Daten anreichern und validieren (wird bereits in sammle_daten erledigt)
            # Hier wird angenommen, dass 'context' bereits alle nötigen Daten enthält.
            
            # 2. Dateinamen generieren
            logic = BerichtsheftLogik()
            dateiname_basis = logic.generiere_dateinamen(
                ausbildungsjahr=context["ausbildungsjahr"],
                kw=context["kalenderwoche"],
                jahr=context["jahr"],
                name_azubi=context["name_azubi"],
                fortlauf_nr=context["fortlaufende_nr"]
            )
            dateiname = f"{dateiname_basis}.{format}"
            logger.debug(f"Dateiname generiert: {dateiname}")

            # 3. Passenden Generator auswählen und ausführen
            generator = DocxGenerator(context) if format == "docx" else PdfGenerator(context)
            generator.generate(dateiname)

            # 4. Daten in der Datenbank speichern (wird jetzt separat gehandhabt)
            self.speichere_bericht_daten(context)

            return True, f"Bericht '{dateiname}' erfolgreich erstellt!"

        except ValueError as e:
            logger.error(f"Ungültige Daten bei der Berichtserstellung: {e}", exc_info=True)
            return False, f"Fehler in den Eingabedaten: {e}"
        except FileNotFoundError as e:
            logger.error(f"Eine benötigte Datei wurde nicht gefunden: {e}", exc_info=True)
            return False, f"Eine benötigte Datei fehlt. Details in der Log-Datei."
        except Exception as e:
            # Den vollständigen Fehler in die Log-Datei schreiben
            logger.error("Allgemeiner Fehler bei der Erstellung des Berichts.", exc_info=True)
            # Dem Benutzer nur eine einfache Nachricht geben
            return False, "Ein unerwarteter Fehler ist aufgetreten. Details in der Log-Datei."

    def speichere_bericht_daten(self, context: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Speichert die aktuellen Berichtsdaten in der Datenbank, ohne eine Datei zu generieren.
        """
        try:
            self.data_manager.aktualisiere_bericht(context)
            logger.info(f"Berichtsdaten für KW {context['kalenderwoche']}/{context['jahr']} gespeichert.")

            neue_konfig_daten = {
                "letzte_bericht_nummer": context["fortlaufende_nr"],
                "letzte_bericht_kw": context["kalenderwoche"],
                "letzte_bericht_jahr": context["jahr"]
            }
            self._aktualisiere_konfiguration(neue_konfig_daten)

            return True, f"Bericht Nr. {context['fortlaufende_nr']} (KW {context['kalenderwoche']}) erfolgreich gespeichert!"
        except Exception as e:
            logger.error("Allgemeiner Fehler beim Speichern der Berichtsdaten.", exc_info=True)
            return False, "Ein Fehler ist beim Speichern aufgetreten. Details in der Log-Datei."


    def _aktualisiere_konfiguration(self, updates: Dict[str, Any]) -> None:
        """Lädt die Konfig, aktualisiert sie und speichert sie wieder."""
        konfig = self.data_manager.lade_konfiguration()
        konfig.update(updates)
        if self.data_manager.speichere_konfiguration(konfig):
            logger.debug("Konfiguration erfolgreich aktualisiert.")
        else:
            logger.warning("Konfiguration konnte nicht gespeichert werden.")


    def export_all_data(self, zip_path: str) -> Tuple[bool, str]:
        """Delegiert den Export an den BackupService."""
        logger.info(f"Starte Datenexport nach: {zip_path}")
        return self.backup_service.export_all_data_to_zip(zip_path)

    def import_all_data(self, zip_path: str) -> Tuple[bool, str]:
        """Delegiert den Import an den BackupService."""
        logger.info(f"Starte Datenimport von: {zip_path}")
        return self.backup_service.import_all_data_from_zip(zip_path)
        
    def import_docx_berichte(self, file_paths: List[str]) -> Tuple[int, int, bool]:
        """
        Importiert Berichtsdaten aus einer Liste von DOCX-Dateien.

        Args:
            file_paths: Eine Liste von Pfaden zu den DOCX-Dateien.

        Returns:
            Ein Tupel (erfolgreich_importiert, fehlerhaft, erfolg_speichern).
        """
        logger.info(f"Starte DOCX-Import für {len(file_paths)} Dateien.")
        
        importierte_daten = {}
        erfolgreich = 0
        fehlerhaft = 0

        for path in file_paths:
            logger.debug(f"Verarbeite Datei: {os.path.basename(path)}")
            bericht_daten = self.importer_service.parse_docx(path)
            if bericht_daten:
                schluessel = f"{bericht_daten['jahr']}-{int(bericht_daten['kalenderwoche']):02d}"
                if schluessel in importierte_daten:
                    logger.warning(f"Doppelter Eintrag für Schlüssel '{schluessel}'. Bisheriger Bericht wird überschrieben durch Datei: {os.path.basename(path)}")
                importierte_daten[schluessel] = bericht_daten
                erfolgreich += 1
            else:
                fehlerhaft += 1
        
        erfolg_speichern = False
        if importierte_daten:
            logger.info(f"Speichere {len(importierte_daten)} importierte Berichte.")
            erfolg_speichern = self.data_manager.importiere_berichte(importierte_daten)
        
        return erfolgreich, fehlerhaft, erfolg_speichern


    def delete_bericht(self, bericht_id: str) -> bool:
        """Löscht einen Bericht aus der Datenbank."""
        return self.data_manager.loesche_bericht(bericht_id)