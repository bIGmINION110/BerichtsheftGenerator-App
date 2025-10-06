# db/database.py
# -*- coding: utf-8 -*-
"""
Verwaltet die SQLite-Datenbankverbindung, Transaktionen und Migrationen.
"""
import sqlite3
import logging
import os
from contextlib import contextmanager
from typing import List, Any, Generator, Optional

logger = logging.getLogger(__name__)

class Database:
    """Kapselt die Verbindung und grundlegende Operationen der SQLite-Datenbank."""

    def __init__(self, db_path: str, migrations_path: str):
        """
        Initialisiert die Datenbank.

        Args:
            db_path: Der Pfad zur SQLite-Datenbankdatei.
            migrations_path: Der Pfad zum Ordner mit den Migrationsskripten.
        """
        self.db_path = db_path
        self.migrations_path = migrations_path
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        """Stellt die Datenbankverbindung her und konfiguriert sie."""
        if self._conn:
            return
        try:
            # KORREKTUR: Erstelle das Verzeichnis nur, wenn es sich nicht um eine In-Memory-DB handelt.
            if self.db_path != ":memory:":
                os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            
            # Wichtige PRAGMA-Einstellungen für Integrität und Performance
            self._conn.execute("PRAGMA foreign_keys = ON;")
            self._conn.execute("PRAGMA journal_mode = WAL;")
            self._conn.execute("PRAGMA synchronous = NORMAL;")
            logger.info(f"Datenbankverbindung zu '{self.db_path}' erfolgreich hergestellt.")
        except sqlite3.Error as e:
            logger.critical(f"Kritischer Fehler beim Verbinden mit der Datenbank: {e}", exc_info=True)
            raise

    def close(self) -> None:
        """Schließt die Datenbankverbindung."""
        if self._conn:
            self._conn.close()
            self._conn = None
            logger.info("Datenbankverbindung geschlossen.")

    @contextmanager
    def transaction(self, read_only: bool = False) -> Generator[sqlite3.Cursor, None, None]:
        """
        Stellt einen kontext-basierten Transaktionsmanager bereit.
        Führt bei Erfolg ein COMMIT durch, bei einer Exception ein ROLLBACK.
        """
        if not self._conn:
            raise sqlite3.OperationalError("Datenbankverbindung ist nicht geöffnet.")
        
        # KORREKTUR: Prüfen, ob bereits eine Transaktion aktiv ist
        in_transaction = self._conn.in_transaction
        
        cursor = self._conn.cursor()
        try:
            if not in_transaction:
                if read_only:
                    cursor.execute("BEGIN DEFERRED;")
                else:
                    cursor.execute("BEGIN IMMEDIATE;")
            yield cursor
            if not in_transaction:
                self._conn.commit()
        except Exception as e:
            if not in_transaction:
                logger.error(f"Transaktion fehlgeschlagen. Führe Rollback durch. Fehler: {e}", exc_info=True)
                self._conn.rollback()
            raise

    def run_migrations(self) -> None:
        """
        Überprüft die aktuelle Schema-Version und führt ausstehende Migrationen aus.
        """
        if not self._conn:
            raise sqlite3.OperationalError("Datenbankverbindung ist nicht geöffnet.")

        try:
            current_version_row = self._conn.execute("PRAGMA user_version;").fetchone()
            current_version = current_version_row[0] if current_version_row else 0
            logger.info(f"Aktuelle Datenbankschema-Version: {current_version}")

            migration_files = sorted([f for f in os.listdir(self.migrations_path) if f.endswith('.sql')])

            for mfile in migration_files:
                try:
                    version = int(mfile.split('_')[0])
                    if version > current_version:
                        logger.info(f"Führe Migration aus: '{mfile}'...")
                        script_path = os.path.join(self.migrations_path, mfile)
                        with open(script_path, 'r', encoding='utf-8') as f:
                            script = f.read()
                        
                        with self.transaction() as cursor:
                            cursor.executescript(script)
                            cursor.execute(f"PRAGMA user_version = {version};")
                        logger.info(f"Migration '{mfile}' erfolgreich angewendet. Neue Version: {version}")
                except (ValueError, IndexError) as e:
                    logger.warning(f"Migrationsdatei '{mfile}' hat ein ungültiges Format und wird übersprungen: {e}")
        except sqlite3.Error as e:
            logger.error(f"Fehler während des Migrationsprozesses: {e}", exc_info=True)
            raise