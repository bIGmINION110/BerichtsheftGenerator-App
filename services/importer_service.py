# services/importer_service.py
# -*- coding: utf-8 -*-
"""
Dienst zur Kapselung der Logik für den Import von DOCX-Berichtsheften.
"""

import logging
import re
import os
from typing import Dict, Optional, Any, List
from docx import Document
from datetime import datetime

from core import config

logger = logging.getLogger(__name__)

class ImporterService:
    """
    Liest Daten aus einem vorhandenen DOCX-Berichtsheft und wandelt sie in ein strukturiertes Format um.
    """
    def _extract_from_regex(self, text: str, pattern: str) -> Optional[str]:
        """Hilfsfunktion, um einen Wert mit Regex aus einem Text zu extrahieren."""
        match = re.search(pattern, text)
        return match.group(1).strip() if match else None

    def parse_docx(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Analysiert eine einzelne DOCX-Datei und extrahiert die Berichtsdaten.

        Args:
            file_path: Der Pfad zur DOCX-Datei.

        Returns:
            Ein Dictionary mit den extrahierten Daten oder None bei einem Fehler.
        """
        # NEUE PRÜFUNG: Ignoriere temporäre Word-Dateien, die mit ~$ beginnen
        if os.path.basename(file_path).startswith('~$'):
            logger.debug(f"Überspringe temporäre Word-Datei: {os.path.basename(file_path)}")
            return None
            
        try:
            doc = Document(file_path)
            full_text = "\n".join([p.text for p in doc.paragraphs])

            # --- Extraktion der Kopfdaten ---
            context: Dict[str, Any] = {}

            context["fortlaufende_nr"] = self._extract_from_regex(full_text, r"Ausbildungsnachweis Nr\. (\d+)")
            context["name_azubi"] = self._extract_from_regex(full_text, r"Azubi: (.*?);")
            zeitraum_von_str = self._extract_from_regex(full_text, r"Zeitraum: (\d{2}\.\d{2}\.\d{4})")
            
            if not all([context["fortlaufende_nr"], context["name_azubi"], zeitraum_von_str]):
                logger.warning(f"Datei '{os.path.basename(file_path)}' hat kein erwartetes Kopfzeilenformat. Überspringe.")
                return None

            # Datum umwandeln und KW/Jahr berechnen
            start_datum = datetime.strptime(zeitraum_von_str, "%d.%m.%Y").date()
            jahr, kw, _ = start_datum.isocalendar()
            context["jahr"] = str(jahr)
            context["kalenderwoche"] = str(kw)
            context["fortlaufende_nr"] = int(context["fortlaufende_nr"])

            # --- Extraktion der Tagesdaten ---
            tage_daten: List[Dict[str, str]] = []
            current_day_activities = []
            current_day_info = {}

            for para in doc.paragraphs:
                is_day_header = False
                for wochentag in config.WOCHENTAGE:
                    if wochentag in para.text:
                        # Wenn ein neuer Tag beginnt, speichere die Daten des vorherigen
                        if current_day_info:
                            current_day_info["taetigkeiten"] = "\n".join(current_day_activities).strip()
                            tage_daten.append(current_day_info)
                            current_day_activities = []

                        current_day_info = {
                            "typ": self._extract_from_regex(para.text, r"Typ: (\w+)") or "Betrieb",
                            "stunden": self._extract_from_regex(para.text, r"Gesamtstunden: ([\d:]+)") or "0:00"
                        }
                        is_day_header = True
                        break # Nächster Paragraph, da dies eine Kopfzeile war
                
                if not is_day_header and current_day_info:
                    # Wenn es sich um einen "List Bullet"-Stil handelt, ist es eine Tätigkeit
                    if para.style.name == 'List Bullet' and para.text.strip():
                        current_day_activities.append(para.text.strip())

            # Speichere die Daten des letzten Tages
            if current_day_info:
                current_day_info["taetigkeiten"] = "\n".join(current_day_activities).strip()
                tage_daten.append(current_day_info)
            
            context["tage_daten"] = tage_daten
            
            # Fülle fehlende Tage auf, falls das Dokument unvollständig war
            while len(tage_daten) < len(config.WOCHENTAGE):
                tage_daten.append({"typ": "-", "stunden": "0:00", "taetigkeiten": "-"})


            logger.info(f"Datei '{os.path.basename(file_path)}' erfolgreich analysiert.")
            return context

        except Exception as e:
            logger.error(f"Fehler beim Analysieren der Datei '{os.path.basename(file_path)}': {e}", exc_info=True)
            return None

