-- migrations/001_initial_schema.sql
-- Initiales Schema für die Anwendung

-- Tabelle für allgemeine Konfigurationseinstellungen
CREATE TABLE IF NOT EXISTS konfiguration (
    schluessel TEXT PRIMARY KEY,
    wert TEXT NOT NULL
);

-- Tabelle für die Metadaten der Berichte
CREATE TABLE IF NOT EXISTS berichte (
    bericht_id TEXT PRIMARY KEY, -- z.B. "2024-39"
    fortlaufende_nr INTEGER NOT NULL,
    name_azubi TEXT NOT NULL,
    jahr INTEGER NOT NULL,
    kalenderwoche INTEGER NOT NULL
);

-- Tabelle für die einzelnen Tageseinträge, verknüpft mit einem Bericht
CREATE TABLE IF NOT EXISTS tagebucheintraege (
    eintrag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bericht_id TEXT NOT NULL,
    tag_name TEXT NOT NULL, -- z.B. "Montag"
    typ TEXT NOT NULL, -- z.B. "Betrieb", "Schule"
    stunden TEXT NOT NULL,
    taetigkeiten TEXT NOT NULL,
    FOREIGN KEY (bericht_id) REFERENCES berichte (bericht_id) ON DELETE CASCADE
);

-- Tabelle für wiederverwendbare Textvorlagen
CREATE TABLE IF NOT EXISTS vorlagen (
    vorlage_id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL UNIQUE
);

-- Indizes zur Beschleunigung von Abfragen
CREATE INDEX IF NOT EXISTS idx_tagebucheintraege_bericht_id ON tagebucheintraege(bericht_id);