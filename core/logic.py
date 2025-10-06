# core/logic.py
# -*- coding: utf-8 -*-
"""
Modul für die zentrale Geschäftslogik des Berichtsheft-Generators.

Diese Datei enthält die Klasse `BerichtsheftLogik`, die Methoden zur
Datenberechnung (z.B. Ausbildungsjahr) und zur Validierung kapselt.
"""

from datetime import date, datetime
import re
import logging

logger = logging.getLogger(__name__)

class BerichtsheftLogik:
    """
    Kapselt die Geschäftslogik für Berechnungen und Validierungen.
    """
    @staticmethod
    def parse_time_to_decimal(time_str: str) -> float:
        """
        Wandelt einen Zeit-String (z.B. "08:15") in eine Dezimalzahl um (z.B. 8.25).
        Diese Funktion wird zentral von Dashboard und Statistiken genutzt.

        Args:
            time_str: Die Zeit im Format "HH:MM".

        Returns:
            Die Zeit als Dezimalzahl. Gibt 0.0 bei einem Fehler zurück.
        """
        try:
            h, m = map(int, time_str.split(':'))
            return h + m / 60.0
        except (ValueError, TypeError):
            logger.warning(f"Ungültiges Zeitformat '{time_str}' konnte nicht umgewandelt werden.")
            return 0.0


    @staticmethod
    def berechne_ausbildungsjahr(startdatum_ausbildung: date, aktuelles_datum_bericht: date) -> int:
        """
        Berechnet das aktuelle Ausbildungsjahr.

        Args:
            startdatum_ausbildung: Das Startdatum der Ausbildung.
            aktuelles_datum_bericht: Das Datum, für das das Ausbildungsjahr berechnet werden soll.

        Returns:
            Das berechnete Ausbildungsjahr als ganze Zahl.
        """
        if not isinstance(startdatum_ausbildung, date) or not isinstance(aktuelles_datum_bericht, date):
            raise TypeError("startdatum_ausbildung und aktuelles_datum_bericht müssen date-Objekte sein.")

        if aktuelles_datum_bericht < startdatum_ausbildung:
            return 0
        
        delta = aktuelles_datum_bericht - startdatum_ausbildung
        ausbildungsjahr = int(delta.days / 365.25) + 1
        return ausbildungsjahr

    @staticmethod
    def generate_filename(ausbildungsjahr: int, kw: int, jahr: int, name_azubi: str, fortlauf_nr: int) -> str:
        """
        Generiert einen standardisierten Dateinamen für das Berichtsheft.

        Args:
            ausbildungsjahr: Das aktuelle Ausbildungsjahr.
            kw: Die Kalenderwoche.
            jahr: Das Jahr.
            name_azubi: Der Name des Auszubildenden.
            fortlauf_nr: Die fortlaufende Nummer des Berichts.

        Returns:
            Den formatierten Dateinamen als String.
        """
        if not all(isinstance(arg, int) for arg in [ausbildungsjahr, kw, jahr, fortlauf_nr]):
            raise TypeError("Ausbildungsjahr, KW, Jahr und fortlaufende Nummer müssen ganze Zahlen sein.")
        if not isinstance(name_azubi, str):
            raise TypeError("Name des Auszubildenden muss ein String sein.")
        
        name_fuer_datei = name_azubi.replace(" ", "_").replace(".", "_")
        name_fuer_datei = re.sub(r'[^a-zA-Z0-9_]', '', name_fuer_datei)
        name_fuer_datei = re.sub(r'_+', '_', name_fuer_datei).strip('_')
        name_fuer_datei = name_fuer_datei[:30] or "Azubi"

        return f"Ausbildungsnachweis_AJ{ausbildungsjahr}_KW{kw:02d}_{jahr}_Nr{fortlauf_nr}_{name_fuer_datei}"

    @staticmethod
    def valide_datumsformat(datum_str: str) -> bool:
        """
        Prüft, ob ein String dem Format TT.MM.JJJJ entspricht.

        Args:
            datum_str: Der zu prüfende String.

        Returns:
            True, wenn das Format gültig ist, sonst False.
        """
        try:
            datetime.strptime(datum_str, "%d.%m.%Y")
            return True
        except ValueError:
            return False
