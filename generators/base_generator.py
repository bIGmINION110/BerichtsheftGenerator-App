# generators/base_generator.py
# -*- coding: utf-8 -*-
"""
Definiert die abstrakte Basisklasse für alle Dokumentengeneratoren.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
import os
import logging
from core import config

logger = logging.getLogger(__name__)

class BaseGenerator(ABC):
    """
    Abstrakte Basisklasse, die die Struktur für die Erstellung eines Dokuments definiert.
    Die `generate`-Methode ist hier als konkrete Methode implementiert, da der Ablauf
    für alle Generatoren identisch ist.
    """
    def __init__(self, context: Dict[str, Any]):
        """Initialisiert den Generator mit den notwendigen Daten."""
        self.context = context

    @abstractmethod
    def _setup_document(self) -> None:
        """Bereitet das interne Dokumentenobjekt vor (z.B. docx, pdf)."""
        pass

    @abstractmethod
    def _create_header(self) -> None:
        """Erstellt die Kopfzeile des Dokuments."""
        pass

    @abstractmethod
    def _create_body(self) -> None:
        """Erstellt den Hauptteil des Dokuments mit den Tageseinträgen."""
        pass

    @abstractmethod
    def _create_footer(self) -> None:
        """Erstellt die Fußzeile des Dokuments mit Unterschriftsfeldern."""
        pass

    @abstractmethod
    def _save_document(self, dateiname: str) -> None:
        """Speichert das fertiggestellte Dokument."""
        pass

    def generate(self, dateiname: str) -> None:
        """
        Orchestriert den gesamten Erstellungsprozess des Dokuments.
        Diese Methode ist NICHT abstrakt.
        """
        try:
            self._setup_document()
            self._create_header()
            self._create_body()
            self._create_footer()
            
            voller_pfad = os.path.join(config.OUTPUT_FOLDER, dateiname)
            
            # --- KORREKTUR: Sicherstellen, dass der Ausgabeordner existiert ---
            os.makedirs(os.path.dirname(voller_pfad), exist_ok=True)
            
            self._save_document(voller_pfad)
        except Exception as e:
            logger.error(f"Fehler beim Generieren des Dokuments '{dateiname}'.", exc_info=True)
            # Die Exception wird weitergereicht, damit der Controller sie fangen und behandeln kann.
            raise