# generators/pdf_generator.py
# -*- coding: utf-8 -*-
"""
Erstellt Berichtshefte im PDF-Format, basierend auf einer Textvorlage.
"""
import logging
import os
from fpdf import FPDF
from typing import Dict, Any

from generators.base_generator import BaseGenerator
from core import config

logger = logging.getLogger(__name__)

class PdfGenerator(BaseGenerator):
    """
    Spezialisierte Klasse zur Generierung von PDF-Berichtsheften.
    Das Layout orientiert sich an einem einfachen Textformat.
    """
    def __init__(self, context: Dict[str, Any]):
        super().__init__(context)
        self.pdf: FPDF = None

    def _setup_document(self) -> None:
        """Initialisiert das PDF-Dokument mit Standardeinstellungen."""
        self.pdf = FPDF()
        self.pdf.add_page()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        
        # --- KORREKTUR: Lade die Schriftarten aus dem 'assets/fonts'-Ordner ---
        try:
            # Pfad zur normalen Verdana-Schriftart
            font_path = os.path.join(config.FONTS_ORDNER, 'verdana.ttf')
            # Pfad zur fetten Verdana-Schriftart
            font_path_bold = os.path.join(config.FONTS_ORDNER, 'verdanab.ttf')
            
            self.pdf.add_font('Verdana', '', font_path, uni=True)
            self.pdf.add_font('Verdana', 'B', font_path_bold, uni=True)
            
            self.pdf.set_font('Verdana', '', 11)
        except FileNotFoundError:
            logger.error("Verdana-Schriftartdateien nicht im 'assets/fonts'-Ordner gefunden! Stelle sicher, dass 'verdana.ttf' und 'verdanab.ttf' dort liegen.")
            # Fallback auf eine Standard-Schriftart, um einen Totalabsturz zu vermeiden
            self.pdf.set_font('Arial', '', 11)
            # Hier könntest du auch eine Exception werfen, um den Vorgang abzubrechen
            # raise RuntimeError("Benötigte Schriftartdateien fehlen.")


    def _create_header(self) -> None:
        """Erstellt die Kopfzeile des Dokuments."""
        self.pdf.set_font('Verdana', 'B', 20) # Korrigiert: Nutzt die geladene Schriftart
        self.pdf.cell(0, 8, f'Ausbildungsnachweis Nr. {self.context.get("fortlaufende_nr", "")}', 0, 1, 'L')
        
        self.pdf.set_font('Verdana', '', 11)
        azubi = self.context.get("name_azubi", "")
        zeitraum_von = self.context.get("zeitraum_von", "")
        zeitraum_bis = self.context.get("zeitraum_bis", "")
        aj = self.context.get("ausbildungsjahr", "")
        
        header_text = f'Azubi: {azubi}; Zeitraum: {zeitraum_von} bis {zeitraum_bis}; Jahr {aj}'
        self.pdf.cell(0, 8, header_text, 0, 1, 'L')
        # self.pdf.ln(8)

    def _create_body(self) -> None:
        """Füllt das Dokument mit den täglichen Berichtsdaten als Textblöcke."""
        tage_daten = self.context.get("tage_daten", [])
        for i, tag_name in enumerate(config.WOCHENTAGE):
            tag_daten = tage_daten[i] if i < len(tage_daten) else {}
            
            # Info-Zeile für den Tag
            self.pdf.set_font('Verdana', 'B', 12) # Korrigiert
            self.pdf.cell(0, 7, f'{tag_name}; Typ: {tag_daten.get("typ", "")}; Gesamtstunden: {tag_daten.get("stunden", "")}', 0, 1, 'L')

            # Tätigkeiten mit Bullet Points
            self.pdf.set_font('Verdana', '', 11)
            taetigkeiten = tag_daten.get("taetigkeiten", "-").split('\n')
            for item in taetigkeiten:
                if item.strip():
                     # Fügt einen Bullet Point hinzu und rückt den Text etwas ein
                    self.pdf.multi_cell(0, 6, f"• {item.strip()}", 0, 'L')
            # self.pdf.ln(4) # Abstand nach jedem Eintrag

    def _create_footer(self) -> None:
        """Erstellt die Fußzeile mit Datum und Unterschriftsfeldern."""
        # self.pdf.ln(10)
        datum_azubi = self.context.get("erstellungsdatum_bericht", "")
        
        self.pdf.set_font('Verdana', 'B', 12) # Fett für die Überschrift
        self.pdf.cell(0, 7, "Auszubildender", 0, 1, 'L')
        self.pdf.set_font('Verdana', '', 11)
        self.pdf.cell(0, 7, f"Datum: {datum_azubi}; Unterschrift:", 0, 1, 'L')

        # self.pdf.ln(5)

        self.pdf.set_font('Verdana', 'B', 12) # Fett für die Überschrift
        self.pdf.cell(0, 7, "Ausbildender bzw. Ausbilder", 0, 1, 'L')
        self.pdf.set_font('Verdana', '', 11)
        self.pdf.cell(0, 7, "Datum: .................; Unterschrift:", 0, 1, 'L')

    def _save_document(self, dateiname: str) -> None:
        """Speichert die PDF-Datei."""
        try:
            self.pdf.output(dateiname)
            logger.info(f"PDF-Dokument erfolgreich gespeichert: {dateiname}")
        except Exception as e:
            logger.error(f"Fehler beim Speichern des PDF-Dokuments '{dateiname}'.", exc_info=True)
            raise IOError(f"Konnte PDF nicht speichern: {e}")