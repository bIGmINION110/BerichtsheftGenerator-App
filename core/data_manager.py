# core/data_manager.py
# -*- coding: utf-8 -*-
"""
Modul zur zentralen Verwaltung aller Lese- und Schreibvorgänge für Daten.
"""

import json
import os
import logging
from typing import Dict, Any, List

# Importiert die zentralisierten Konstanten
from core import config

# Logger für dieses Modul initialisieren
logger = logging.getLogger(__name__)

class DataManager:
    """
    Verwaltet das Laden und Speichern von Konfigurations-, Berichts- und Vorlagendaten.
    """
    def __init__(self):
        """Initialisiert den DataManager und stellt sicher, dass die Datenordner existieren."""
        try:
            os.makedirs(config.DATA_ORDNER, exist_ok=True)
            os.makedirs(config.AUSGABE_ORDNER, exist_ok=True)
        except OSError as e:
            logger.error(f"Kritischer Fehler: Daten- oder Ausgabeordner konnte nicht erstellt werden. {e}", exc_info=True)
            raise  # Erneutes Auslösen der Exception, da dies ein kritischer Fehler ist

    def _lade_json(self, dateipfad: str, standardwert: Any = None) -> Any:
        """
        Eine generische Methode zum Laden einer JSON-Datei.

        Args:
            dateipfad: Der vollständige Pfad zur JSON-Datei.
            standardwert: Der Wert, der zurückgegeben wird, wenn die Datei nicht existiert oder leer ist.

        Returns:
            Die geladenen Daten oder der Standardwert.
        """
        if not os.path.exists(dateipfad) or os.path.getsize(dateipfad) == 0:
            logger.debug(f"Datei {dateipfad} nicht gefunden oder leer. Gebe Standardwert zurück.")
            return standardwert if standardwert is not None else {}
        try:
            with open(dateipfad, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            logger.error(f"Fehler beim Laden der JSON-Datei: {dateipfad}", exc_info=True)
            return standardwert if standardwert is not None else {}

    def _speichere_json(self, dateipfad: str, daten: Any) -> bool:
        """
        Eine generische Methode zum Speichern von Daten als JSON.

        Args:
            dateipfad: Der vollständige Pfad zur Zieldatei.
            daten: Die zu speichernden Python-Daten (z.B. dict, list).

        Returns:
            True bei Erfolg, sonst False.
        """
        try:
            with open(dateipfad, 'w', encoding='utf-8') as f:
                json.dump(daten, f, ensure_ascii=False, indent=4, default=str)
            logger.debug(f"Daten erfolgreich in {dateipfad} gespeichert.")
            return True
        except IOError:
            logger.error(f"Fehler beim Speichern der JSON-Datei: {dateipfad}", exc_info=True)
            return False

    # --- Spezifische Methoden für jede Datenart ---
    def lade_konfiguration(self) -> Dict[str, Any]:
        """Lädt die Hauptkonfiguration."""
        return self._lade_json(config.KONFIG_DATEI)

    def speichere_konfiguration(self, daten: Dict[str, Any]) -> bool:
        """Speichert die Hauptkonfiguration."""
        return self._speichere_json(config.KONFIG_DATEI, daten)

    def lade_berichte(self) -> Dict[str, Any]:
        """Lädt alle gespeicherten Berichtsdaten."""
        return self._lade_json(config.BERICHTS_DATEI)

    def speichere_berichte(self, daten: Dict[str, Any]) -> bool:
        """Speichert alle Berichtsdaten."""
        return self._speichere_json(config.BERICHTS_DATEI, daten)
        
    def aktualisiere_bericht(self, bericht_daten: Dict[str, Any]) -> bool:
        """Fügt einen neuen Bericht hinzu oder aktualisiert einen bestehenden."""
        alle_berichte = self.lade_berichte()
        schluessel = f"{bericht_daten['jahr']}-{int(bericht_daten['kalenderwoche']):02d}"
        alle_berichte[schluessel] = bericht_daten
        return self.speichere_berichte(alle_berichte)
        
    def importiere_berichte(self, importierte_daten: Dict[str, Any]) -> bool:
        """Fügt eine Sammlung von importierten Berichten zu den bestehenden Daten hinzu."""
        alle_berichte = self.lade_berichte()
        alle_berichte.update(importierte_daten)
        return self.speichere_berichte(alle_berichte)

    def loesche_statistiken(self) -> bool:
        """Löscht die Berichtsdatendatei (die als Basis für Statistiken dient)."""
        try:
            if os.path.exists(config.BERICHTS_DATEI):
                os.remove(config.BERICHTS_DATEI)
                logger.info(f"Berichtsdatendatei {config.BERICHTS_DATEI} wurde gelöscht.")
            return True
        except OSError:
            logger.error(f"Konnte die Berichtsdatendatei nicht löschen: {config.BERICHTS_DATEI}", exc_info=True)
            return False
            
    def lade_vorlagen(self) -> List[str]:
        """Lädt die Textvorlagen."""
        return self._lade_json(config.VORLAGEN_DATEI, standardwert=[])

    def speichere_vorlagen(self, vorlagen_liste: List[str]) -> bool:
        """Speichert die Textvorlagen."""
        return self._speichere_json(config.VORLAGEN_DATEI, vorlagen_liste)
