# tests/test_database.py
# -*- coding: utf-8 -*-
import sqlite3
import pytest
import os
import sys

# Fügt das Hauptverzeichnis des Projekts zum Python-Pfad hinzu,
# damit Module wie 'db' gefunden werden können.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.database import Database

@pytest.fixture
def in_memory_db() -> Database:
    """Fixture, das eine In-Memory-Datenbank für Tests bereitstellt."""
    # Erstelle einen temporären Migrationsordner im Projekt-Root, falls er nicht existiert
    migrations_root_path = os.path.join(os.path.dirname(__file__), '..', 'migrations')
    os.makedirs(migrations_root_path, exist_ok=True)
    
    db = Database(":memory:", migrations_root_path)
    db.connect()
    yield db
    db.close()

def test_connection(in_memory_db: Database):
    """Testet, ob die Verbindung erfolgreich hergestellt und geschlossen wird."""
    assert in_memory_db._conn is not None
    in_memory_db.close()
    assert in_memory_db._conn is None

def test_transaction_commit(in_memory_db: Database):
    """Testet, ob eine erfolgreiche Transaktion committed wird."""
    with in_memory_db.transaction() as cursor:
        cursor.execute("CREATE TABLE test (id INTEGER, name TEXT);")
        cursor.execute("INSERT INTO test VALUES (?, ?);", (1, "Alice"))

    # Überprüfen außerhalb der Transaktion
    result = in_memory_db._conn.execute("SELECT * FROM test").fetchone()
    assert result["name"] == "Alice"

def test_transaction_rollback(in_memory_db: Database):
    """Testet, ob eine fehlerhafte Transaktion zurückgerollt wird."""
    with in_memory_db.transaction() as cursor:
        cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT);")

    try:
        with in_memory_db.transaction() as cursor:
            cursor.execute("INSERT INTO test (id, name) VALUES (?, ?);", (1, "Alice"))
            # Dieser zweite Insert wird fehlschlagen (Primary Key Constraint)
            cursor.execute("INSERT INTO test (id, name) VALUES (?, ?);", (1, "Bob"))
    except sqlite3.IntegrityError:
        pass  # Erwarteter Fehler

    # Überprüfen, ob die Tabelle leer ist, da die Transaktion zurückgerollt wurde
    result = in_memory_db._conn.execute("SELECT COUNT(*) FROM test").fetchone()
    assert result[0] == 0

def test_run_migrations(in_memory_db: Database, tmpdir):
    """Testet den Migrationsmechanismus."""
    # Temporären Migrationsordner erstellen
    migrations_dir = tmpdir.mkdir("migrations")
    m1 = migrations_dir.join("001_create.sql")
    m1.write("CREATE TABLE test (id INTEGER);") # PRAGMA wird von der Methode gesetzt
    m2 = migrations_dir.join("002_alter.sql")
    m2.write("ALTER TABLE test ADD COLUMN name TEXT;")
    
    # Neu initialisieren mit dem temporären Pfad
    db = Database(":memory:", str(migrations_dir))
    db.connect()
    
    # Setze user_version manuell auf 0 für den Test
    db._conn.execute("PRAGMA user_version = 0;")
    
    db.run_migrations()
    
    # Überprüfen, ob beide Migrationen angewendet wurden
    cursor = db._conn.cursor()
    cursor.execute("PRAGMA table_info(test);")
    columns = [row[1] for row in cursor.fetchall()]
    assert "id" in columns
    assert "name" in columns

    version = db._conn.execute("PRAGMA user_version;").fetchone()[0]
    assert version == 2
    
    db.close()