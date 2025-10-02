# core/data_manager.py
# -*- coding: utf-8 -*-
"""
Modul zur zentralen Verwaltung aller Lese- und Schreibvorgänge für Daten mittels SQLite.
Diese Klasse agiert als Fassade und Repository für die Datenbank.
"""
import json
import logging
from typing import Dict, Any, List, Optional

from db.database import Database
from db.models import Bericht, Tagebucheintrag, Vorlage

logger = logging.getLogger(__name__)

class DataManager:
    """Verwaltet alle CRUD-Operationen (Create, Read, Update, Delete) für die Anwendung."""

    def __init__(self, db: Database):
        """
        Initialisiert den DataManager mit einer Datenbankinstanz.

        Args:
            db: Eine Instanz der Database-Klasse.
        """
        self.db = db

    def lade_konfiguration(self) -> Dict[str, Any]:
        """Lädt die gesamte Konfiguration aus der Datenbank."""
        config_data = {}
        query = "SELECT schluessel, wert FROM konfiguration"
        try:
            with self.db.transaction() as cursor:
                for row in cursor.execute(query):
                    # Versuche, JSON-Werte zu parsen
                    try:
                        config_data[row['schluessel']] = json.loads(row['wert'])
                    except (json.JSONDecodeError, TypeError):
                        config_data[row['schluessel']] = row['wert']
            return config_data
        except self.db._conn.Error as e:
            logger.error(f"Fehler beim Laden der Konfiguration: {e}", exc_info=True)
            return {}

    def speichere_konfiguration(self, config_data: Dict[str, Any]) -> bool:
        """Speichert die Konfiguration in der Datenbank (UPSERT)."""
        query = "INSERT OR REPLACE INTO konfiguration (schluessel, wert) VALUES (?, ?)"
        try:
            with self.db.transaction() as cursor:
                for key, value in config_data.items():
                    # Komplexe Typen (dict, list) als JSON-String speichern
                    if isinstance(value, (dict, list)):
                        cursor.execute(query, (key, json.dumps(value)))
                    else:
                        cursor.execute(query, (key, value))
            return True
        except self.db._conn.Error as e:
            logger.error(f"Fehler beim Speichern der Konfiguration: {e}", exc_info=True)
            return False

    def lade_berichte(self) -> Dict[str, Dict[str, Any]]:
        """Lädt alle Berichte und die zugehörigen Tagebucheinträge."""
        berichte_query = "SELECT * FROM berichte"
        eintraege_query = "SELECT * FROM tagebucheintraege WHERE bericht_id = ?"
        berichte_map = {}
        try:
            with self.db.transaction() as cursor:
                # Zuerst alle Berichte laden
                for row in cursor.execute(berichte_query):
                    bericht = dict(row)
                    bericht['tage_daten'] = []
                    berichte_map[bericht['bericht_id']] = bericht
                
                # Dann für jeden Bericht die Einträge hinzufügen
                for bericht_id, bericht_data in berichte_map.items():
                    for entry_row in cursor.execute(eintraege_query, (bericht_id,)):
                        bericht_data['tage_daten'].append(dict(entry_row))
            return berichte_map
        except self.db._conn.Error as e:
            logger.error(f"Fehler beim Laden der Berichte: {e}", exc_info=True)
            return {}

    def aktualisiere_bericht(self, context: Dict[str, Any]) -> bool:
        """Aktualisiert oder erstellt einen Bericht und seine Einträge in einer einzigen Transaktion."""
        try:
            with self.db.transaction() as cursor:
                self._aktualisiere_bericht_in_transaktion(cursor, context)
            return True
        except self.db._conn.Error as e:
            bericht_id = f"{context.get('jahr', 'Ubekannt')}-{context.get('kalenderwoche', 'Ubekannt'):02d}"
            logger.error(f"Fehler beim Aktualisieren des Berichts '{bericht_id}': {e}", exc_info=True)
            return False

    def _aktualisiere_bericht_in_transaktion(self, cursor: Any, context: Dict[str, Any]):
        """
        Führt die Logik zum Aktualisieren eines Berichts innerhalb einer bestehenden Transaktion aus.
        Wird von `aktualisiere_bericht` und `importiere_berichte` genutzt.
        """
        # KORREKTUR: Stellt sicher, dass die Kalenderwoche ein Integer ist für die Formatierung.
        kw = int(context['kalenderwoche'])
        bericht_id = f"{context['jahr']}-{kw:02d}"

        upsert_bericht = """
            INSERT OR REPLACE INTO berichte (bericht_id, fortlaufende_nr, name_azubi, jahr, kalenderwoche)
            VALUES (?, ?, ?, ?, ?)
        """
        delete_eintraege = "DELETE FROM tagebucheintraege WHERE bericht_id = ?"
        insert_eintrag = """
            INSERT INTO tagebucheintraege (bericht_id, tag_name, typ, stunden, taetigkeiten)
            VALUES (?, ?, ?, ?, ?)
        """
        
        # Bericht aktualisieren/einfügen
        cursor.execute(upsert_bericht, (
            bericht_id, context['fortlaufende_nr'], context['name_azubi'],
            context['jahr'], kw
        ))
        
        # Alte Einträge für diesen Bericht löschen
        cursor.execute(delete_eintraege, (bericht_id,))
        
        # Neue Einträge einfügen
        from core.config import WOCHENTAGE
        for i, tag_daten in enumerate(context['tage_daten']):
            if i < len(WOCHENTAGE):
                cursor.execute(insert_eintrag, (
                    bericht_id, WOCHENTAGE[i], tag_daten.get('typ', '-'),
                    tag_daten.get('stunden', '0:00'), tag_daten.get('taetigkeiten', '-')
                ))


    def loesche_bericht(self, bericht_id: str) -> bool:
        """Löscht einen Bericht und seine Einträge explizit."""
        delete_entries_query = "DELETE FROM tagebucheintraege WHERE bericht_id = ?"
        delete_report_query = "DELETE FROM berichte WHERE bericht_id = ?"
        try:
            with self.db.transaction() as cursor:
                # KORREKTUR: Zuerst die abhängigen Einträge löschen
                cursor.execute(delete_entries_query, (bericht_id,))
                # Dann den Hauptbericht löschen
                cursor.execute(delete_report_query, (bericht_id,))
            logger.info(f"Bericht '{bericht_id}' und zugehörige Einträge erfolgreich gelöscht.")
            return True
        except self.db._conn.Error as e:
            logger.error(f"Fehler beim Löschen des Berichts '{bericht_id}': {e}", exc_info=True)
            return False

    def lade_vorlagen(self) -> List[str]:
        """Lädt alle Textvorlagen."""
        query = "SELECT text FROM vorlagen ORDER BY text"
        try:
            with self.db.transaction() as cursor:
                return [row['text'] for row in cursor.execute(query)]
        except self.db._conn.Error as e:
            logger.error(f"Fehler beim Laden der Vorlagen: {e}", exc_info=True)
            return []

    def speichere_vorlagen(self, vorlagen: List[str]) -> bool:
        """Löscht alle alten Vorlagen und speichert die neue Liste."""
        delete_query = "DELETE FROM vorlagen"
        insert_query = "INSERT INTO vorlagen (text) VALUES (?)"
        try:
            with self.db.transaction() as cursor:
                cursor.execute(delete_query)
                cursor.executemany(insert_query, [(v,) for v in vorlagen])
            return True
        except self.db._conn.Error as e:
            logger.error(f"Fehler beim Speichern der Vorlagen: {e}", exc_info=True)
            return False
            
    def loesche_alle_berichte(self) -> bool:
        """Löscht alle Berichte und Tagebucheinträge aus der Datenbank."""
        try:
            with self.db.transaction() as cursor:
                cursor.execute("DELETE FROM tagebucheintraege;")
                cursor.execute("DELETE FROM berichte;")
            logger.info("Alle Berichtsdaten wurden aus der Datenbank gelöscht.")
            return True
        except self.db._conn.Error as e:
            logger.error(f"Fehler beim Löschen aller Berichte: {e}", exc_info=True)
            return False
            
    def importiere_berichte(self, berichte_daten: Dict[str, Any]) -> bool:
        """
        Importiert mehrere Berichte in einer einzigen, performanten Transaktion.
        Gibt bei einem Fehler `False` zurück, damit der Controller den Fehler anzeigen kann.
        """
        try:
            with self.db.transaction() as cursor:
                for bericht_id, context in berichte_daten.items():
                    self._aktualisiere_bericht_in_transaktion(cursor, context)
            logger.info(f"{len(berichte_daten)} Berichte erfolgreich importiert.")
            return True
        except self.db._conn.Error as e:
            logger.error(f"Fehler beim Massenimport von Berichten: {e}", exc_info=True)
            return False # Wichtig: Signalisiert dem Controller einen Fehler
            
    def close_db_connection(self):
        """Delegiert das Schließen der DB-Verbindung."""
        self.db.close()

    def connect_db_connection(self):
        """Delegiert das Öffnen der DB-Verbindung."""
        self.db.connect()