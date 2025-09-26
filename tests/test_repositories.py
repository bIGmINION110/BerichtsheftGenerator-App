# tests/test_repositories.py
# -*- coding: utf-8 -*-
import pytest
from typing import Generator
import sys
import os

# Fügt das Hauptverzeichnis des Projekts zum Python-Pfad hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.database import Database
from db.models import Bericht, Tagebucheintrag, Vorlage
from core.data_manager import DataManager # Der neue DataManager als Fassade

@pytest.fixture
def db_manager() -> Generator[DataManager, None, None]:
    """Fixture, das eine saubere In-Memory-DB und einen DataManager für jeden Test bereitstellt."""
    migrations_root_path = os.path.join(os.path.dirname(__file__), '..', 'migrations')
    os.makedirs(migrations_root_path, exist_ok=True)
    
    db = Database(":memory:", migrations_root_path)
    db.connect()
    db.run_migrations()
    manager = DataManager(db)
    yield manager
    db.close()

def test_speichere_und_lade_konfiguration(db_manager: DataManager):
    """Testet das Speichern und Laden von Konfigurationsdaten."""
    config_data = {
        "name_azubi": "Max Mustermann",
        "startdatum_ausbildung": "01.08.2023",
        "einstellungen": {"theme": "dark"}
    }
    
    result = db_manager.speichere_konfiguration(config_data)
    assert result is True
    
    loaded_config = db_manager.lade_konfiguration()
    assert loaded_config["name_azubi"] == "Max Mustermann"
    assert loaded_config["einstellungen"]["theme"] == "dark"

def test_aktualisiere_bericht(db_manager: DataManager):
    """Testet das Hinzufügen und anschließende Laden eines Berichts."""
    bericht_daten = {
        "jahr": 2024,
        "kalenderwoche": 40,
        "fortlaufende_nr": 1,
        "name_azubi": "Max Mustermann",
        "tage_daten": [
            {"typ": "Betrieb", "stunden": "08:00", "taetigkeiten": "Programmieren"},
            {"typ": "Schule", "stunden": "06:00", "taetigkeiten": "Lernen"}
        ]
    }
    
    result = db_manager.aktualisiere_bericht(bericht_daten)
    assert result is True
    
    loaded_berichte = db_manager.lade_berichte()
    bericht_id = "2024-40"
    
    assert bericht_id in loaded_berichte
    assert loaded_berichte[bericht_id]["fortlaufende_nr"] == 1
    assert len(loaded_berichte[bericht_id]["tage_daten"]) == 2
    assert loaded_berichte[bericht_id]["tage_daten"][0]["taetigkeiten"] == "Programmieren"

def test_loesche_bericht(db_manager: DataManager):
    """Testet das Löschen eines Berichts."""
    bericht_daten = {
        "jahr": 2024,
        "kalenderwoche": 41,
        "fortlaufende_nr": 2,
        "name_azubi": "Max Mustermann",
        "tage_daten": []
    }
    db_manager.aktualisiere_bericht(bericht_daten)
    bericht_id = "2024-41"
    
    assert bericht_id in db_manager.lade_berichte()
    
    result = db_manager.loesche_bericht(bericht_id)
    assert result is True
    
    assert bericht_id not in db_manager.lade_berichte()

def test_speichere_und_lade_vorlagen(db_manager: DataManager):
    """Testet das Speichern und Laden von Textvorlagen."""
    vorlagen = ["Vorlage A", "Vorlage B"]
    
    result = db_manager.speichere_vorlagen(vorlagen)
    assert result is True
    
    loaded_vorlagen = db_manager.lade_vorlagen()
    assert len(loaded_vorlagen) == 2
    assert "Vorlage B" in loaded_vorlagen