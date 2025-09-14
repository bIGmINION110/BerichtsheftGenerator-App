# core/data_manager.py
# -*- coding: utf-8 -*-
"""
Modul zur zentralen Verwaltung aller Lese- und Schreibvorgänge für Daten mittels SQLite.
"""

import json
import os
import logging
import sqlite3
from typing import Dict, Any, List, Optional

from core import config

logger = logging.getLogger(__name__)

class DataManager:
    """
    Verwaltet das Laden und Speichern von Konfigurations-, Berichts- und Vorlagendaten in einer SQLite-Datenbank.
    """
    def __init__(self):
        """Initialisiert den DataManager, stellt die Ordner sicher und richtet die Datenbank ein."""
        try:
            os.makedirs(config.DATA_ORDNER, exist_ok=True)
            os.makedirs(config.AUSGABE_ORDNER, exist_ok=True)
        except OSError as e:
            logger.critical(f"Kritischer Fehler: Daten- oder Ausgabeordner konnte nicht erstellt werden. {e}", exc_info=True)
            raise

        self._conn = None  # Wichtig: initial auf None setzen
        self.connect()     # Verbindung über neue Methode herstellen

    def connect(self):
        """Stellt die Datenbankverbindung her."""
        if self._conn is None:
            self._conn = self._create_connection()
            self._create_tables()
            self._migrate_from_json()

    def close(self):
        """Schließt die Datenbankverbindung sicher."""
        if self._conn:
            self._conn.close()
            self._conn = None
            logger.info("Datenbankverbindung geschlossen.")

    def _create_connection(self) -> Optional[sqlite3.Connection]:
        """Erstellt eine Verbindung zur SQLite-Datenbank."""
        try:
            conn = sqlite3.connect(config.DATENBANK_DATEI)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logger.error(f"Fehler beim Verbinden mit der Datenbank: {e}", exc_info=True)
            return None

    def _create_tables(self):
        """Erstellt die notwendigen Tabellen in der Datenbank, falls sie nicht existieren."""
        if not self._conn:
            return

        try:
            cursor = self._conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS konfiguration (
                    schluessel TEXT PRIMARY KEY,
                    wert TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS berichte (
                    bericht_id TEXT PRIMARY KEY,
                    fortlaufende_nr INTEGER,
                    name_azubi TEXT,
                    jahr INTEGER,
                    kalenderwoche INTEGER
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tagebucheintraege (
                    eintrag_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bericht_id TEXT,
                    tag_name TEXT,
                    typ TEXT,
                    stunden TEXT,
                    taetigkeiten TEXT,
                    FOREIGN KEY (bericht_id) REFERENCES berichte (bericht_id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vorlagen (
                    vorlage_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL UNIQUE
                )
            """)
            self._conn.commit()
            logger.info("Datenbank-Tabellen erfolgreich überprüft/erstellt.")
        except sqlite3.Error as e:
            logger.error(f"Fehler beim Erstellen der Tabellen: {e}", exc_info=True)

    def _migrate_from_json(self):
        """Migriert Daten aus alten JSON-Dateien in die Datenbank und löscht die JSON-Dateien."""
        if os.path.exists(config.KONFIG_DATEI_OLD):
            logger.info("Alte Konfigurations-JSON gefunden. Starte Migration...")
            try:
                with open(config.KONFIG_DATEI_OLD, 'r', encoding='utf-8') as f:
                    konfig_data = json.load(f)

                # Speichere die Konfiguration
                self.speichere_konfiguration(konfig_data)
                
                os.remove(config.KONFIG_DATEI_OLD)
                logger.info("Konfigurations-JSON erfolgreich migriert und gelöscht.")
            except Exception as e:
                logger.error(f"Fehler bei der Migration der Konfigurations-JSON: {e}", exc_info=True)

        if os.path.exists(config.BERICHTS_DATEI_OLD):
            logger.info("Alte Berichts-JSON gefunden. Starte Migration...")
            try:
                with open(config.BERICHTS_DATEI_OLD, 'r', encoding='utf-8') as f:
                    berichts_data = json.load(f)
                
                # Importiere die Berichte
                self.importiere_berichte(berichts_data)

                os.remove(config.BERICHTS_DATEI_OLD)
                logger.info("Berichts-JSON erfolgreich migriert und gelöscht.")
            except Exception as e:
                logger.error(f"Fehler bei der Migration der Berichts-JSON: {e}", exc_info=True)
        
        if os.path.exists(config.VORLAGEN_DATEI_OLD):
            logger.info("Alte Vorlagen-JSON gefunden. Starte Migration...")
            try:
                with open(config.VORLAGEN_DATEI_OLD, 'r', encoding='utf-8') as f:
                    vorlagen_data = json.load(f)
                
                self.speichere_vorlagen(vorlagen_data)

                os.remove(config.VORLAGEN_DATEI_OLD)
                logger.info("Vorlagen-JSON erfolgreich migriert und gelöscht.")
            except Exception as e:
                logger.error(f"Fehler bei der Migration der Vorlagen-JSON: {e}", exc_info=True)


    def lade_konfiguration(self) -> Dict[str, Any]:
        """Lädt die Hauptkonfiguration aus der Datenbank."""
        self.connect()
        if not self._conn:
            return {}
        
        try:
            cursor = self._conn.cursor()
            cursor.execute("SELECT schluessel, wert FROM konfiguration")
            rows = cursor.fetchall()
            
            config_dict = {}
            for row in rows:
                try:
                    # Versuche, den Wert als JSON zu laden (für verschachtelte Diktate wie 'einstellungen')
                    config_dict[row['schluessel']] = json.loads(row['wert'])
                except (json.JSONDecodeError, TypeError):
                    # Wenn es kein JSON ist, speichere es als einfachen String/Zahl
                    config_dict[row['schluessel']] = row['wert']
            return config_dict
        except sqlite3.Error as e:
            logger.error(f"Fehler beim Laden der Konfiguration aus der DB: {e}", exc_info=True)
            return {}

    def speichere_konfiguration(self, daten: Dict[str, Any]) -> bool:
        """Speichert die Hauptkonfiguration in der Datenbank."""
        self.connect()
        if not self._conn:
            return False

        try:
            cursor = self._conn.cursor()
            for key, value in daten.items():
                # Komplexe Typen (dict, list) als JSON-String speichern
                if isinstance(value, (dict, list)):
                    value_str = json.dumps(value, ensure_ascii=False)
                else:
                    value_str = str(value)
                
                cursor.execute(
                    "INSERT OR REPLACE INTO konfiguration (schluessel, wert) VALUES (?, ?)",
                    (key, value_str)
                )
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Fehler beim Speichern der Konfiguration in die DB: {e}", exc_info=True)
            return False

    def lade_berichte(self) -> Dict[str, Any]:
        """Lädt alle gespeicherten Berichtsdaten aus der Datenbank."""
        self.connect()
        if not self._conn:
            return {}

        try:
            cursor = self._conn.cursor()
            cursor.execute("""
                SELECT
                    b.bericht_id, b.fortlaufende_nr, b.name_azubi, b.jahr, b.kalenderwoche,
                    t.tag_name, t.typ, t.stunden, t.taetigkeiten
                FROM berichte b
                LEFT JOIN tagebucheintraege t ON b.bericht_id = t.bericht_id
                ORDER BY b.bericht_id, t.eintrag_id
            """)
            
            berichte = {}
            for row in cursor.fetchall():
                bericht_id = row['bericht_id']
                if bericht_id not in berichte:
                    berichte[bericht_id] = {
                        "fortlaufende_nr": row['fortlaufende_nr'],
                        "name_azubi": row['name_azubi'],
                        "jahr": row['jahr'],
                        "kalenderwoche": row['kalenderwoche'],
                        "tage_daten": []
                    }
                
                if row['tag_name']: # Stellt sicher, dass Tagebucheinträge existieren
                    berichte[bericht_id]['tage_daten'].append({
                        "tag_name": row['tag_name'],
                        "typ": row['typ'],
                        "stunden": row['stunden'],
                        "taetigkeiten": row['taetigkeiten']
                    })
            return berichte
        except sqlite3.Error as e:
            logger.error(f"Fehler beim Laden der Berichte aus der DB: {e}", exc_info=True)
            return {}

    def aktualisiere_bericht(self, bericht_daten: Dict[str, Any]) -> bool:
        """Fügt einen neuen Bericht hinzu oder aktualisiert einen bestehenden in der Datenbank."""
        self.connect()
        if not self._conn:
            return False

        bericht_id = f"{bericht_daten['jahr']}-{int(bericht_daten['kalenderwoche']):02d}"
        try:
            cursor = self._conn.cursor()

            # Zuerst den Hauptbericht einfügen oder ersetzen
            cursor.execute(
                "INSERT OR REPLACE INTO berichte (bericht_id, fortlaufende_nr, name_azubi, jahr, kalenderwoche) VALUES (?, ?, ?, ?, ?)",
                (bericht_id, bericht_daten['fortlaufende_nr'], bericht_daten['name_azubi'], bericht_daten['jahr'], bericht_daten['kalenderwoche'])
            )

            # Alte Tageseinträge für diesen Bericht löschen
            cursor.execute("DELETE FROM tagebucheintraege WHERE bericht_id = ?", (bericht_id,))
            
            # Neue Tageseinträge einfügen
            for i, tag_data in enumerate(bericht_daten.get('tage_daten', [])):
                cursor.execute(
                    "INSERT INTO tagebucheintraege (bericht_id, tag_name, typ, stunden, taetigkeiten) VALUES (?, ?, ?, ?, ?)",
                    (bericht_id, config.WOCHENTAGE[i], tag_data['typ'], tag_data['stunden'], tag_data['taetigkeiten'])
                )
            
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Fehler beim Aktualisieren des Berichts in der DB: {e}", exc_info=True)
            self._conn.rollback()
            return False
            
    def importiere_berichte(self, importierte_daten: Dict[str, Any]) -> bool:
        """Fügt eine Sammlung von importierten Berichten zu den bestehenden Daten hinzu."""
        self.connect()
        if not self._conn:
            return False
            
        try:
            for bericht_id, bericht_daten in importierte_daten.items():
                self.aktualisiere_bericht(bericht_daten)
            return True
        except Exception as e:
            logger.error(f"Fehler beim Massenimport von Berichten: {e}", exc_info=True)
            return False


    def loesche_statistiken(self) -> bool:
        """Löscht alle Berichte und Tageseinträge aus der Datenbank."""
        self.connect()
        if not self._conn:
            return False

        try:
            cursor = self._conn.cursor()
            cursor.execute("DELETE FROM tagebucheintraege")
            cursor.execute("DELETE FROM berichte")
            self._conn.commit()
            logger.info("Alle Berichtsdaten (Statistiken) wurden aus der Datenbank gelöscht.")
            return True
        except sqlite3.Error as e:
            logger.error(f"Fehler beim Löschen der Statistiken aus der DB: {e}", exc_info=True)
            self._conn.rollback()
            return False
            
    def lade_vorlagen(self) -> List[str]:
        """Lädt die Textvorlagen aus der Datenbank."""
        self.connect()
        if not self._conn:
            return []
            
        try:
            cursor = self._conn.cursor()
            cursor.execute("SELECT text FROM vorlagen ORDER BY vorlage_id")
            return [row['text'] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Fehler beim Laden der Vorlagen aus der DB: {e}", exc_info=True)
            return []

    def speichere_vorlagen(self, vorlagen_liste: List[str]) -> bool:
        """Speichert die Textvorlagen in der Datenbank (löscht alte und fügt neue ein)."""
        self.connect()
        if not self._conn:
            return False
            
        try:
            cursor = self._conn.cursor()
            cursor.execute("DELETE FROM vorlagen")
            cursor.executemany(
                "INSERT INTO vorlagen (text) VALUES (?)",
                [(vorlage,) for vorlage in vorlagen_liste]
            )
            self._conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Fehler beim Speichern der Vorlagen in die DB: {e}", exc_info=True)
            self._conn.rollback()
            return False
        