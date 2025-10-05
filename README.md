# Berichtsheft-Generator
Eine Desktop-Anwendung zur einfachen Erstellung und Verwaltung von Ausbildungsnachweisen, speziell zugeschnitten auf die Anforderungen der Blista (Zentrum für Berufliche Bildung). Die Anwendung ist mit Python und dem CustomTkinter-Framework entwickelt und legt einen starken Fokus auf Barrierefreiheit für Screenreader-Nutzer.

## ✨ Hauptfunktionen
**Berichte Erstellen & Exportieren:** Erstelle tägliche und wöchentliche Berichte und exportiere sie als DOCX- oder PDF-Dateien.

**Vorlagen-Verwaltung:** Speichere wiederkehrende Tätigkeiten als Vorlagen, um sie schnell in neue Berichte einfügen zu können.

**Laden & Bearbeiten:** Gespeicherte Berichte können jederzeit geladen und weiterbearbeitet werden.

**Daten-Import:** Importiere bereits existierende Berichtshefte aus Word-Dateien (.docx), um sie in der Anwendung weiter zu verwalten.

**Statistiken:** Erhalte eine visuelle Übersicht über geleistete Stunden, Urlaubstage, Krankheitstage und mehr, aufgeteilt nach Ausbildungsjahren.

**Backup & Wiederherstellung:** Sichere alle deine Daten (Berichte, Konfigurationen, Vorlagen) in einer einzigen ZIP-Datei oder stelle sie daraus wieder her.

**Barrierefreiheit:** Eine umfassende Unterstützung für Screenreader (wie NVDA und Jaws) durch die accessible_output2-Bibliothek ist integriert, inklusive Sprachausgabe für fast alle Aktionen.

**Automatische Updates:** Die Anwendung prüft beim Start automatisch auf neue Versionen und benachrichtigt dich, wenn ein Update verfügbar ist.

## 🛠️ Technologie-Stack
- Programmiersprache: Python
- GUI-Framework: CustomTkinter
- Datenbank: SQLite
- Dokumenten-Erstellung:
    - python-docx für .docx-Dateien
    - fpdf2 für .pdf-Dateien
    - Barrierefreiheit: accessible_output2
    - Diagramme & Statistiken: matplotlib
    - Kalender-Widget: tkcalendar

## 🚀 Installation & Start
Um das Projekt lokal auszuführen, befolge diese Schritte:

* Repository klonen:

```bash
git clone https://github.com/bigminion110/berichtsheftgenerator-app.git
cd berichtsheftgenerator-app
```

* Abhängigkeiten installieren:
Es wird empfohlen, eine virtuelle Umgebung zu verwenden.

```bash
python -m venv .venv
source .venv/bin/activate  # Auf Windows: .venv\Scripts\activate
```

* Installiere dann die benötigten Pakete aus der requirements.txt-Datei:
```bash
pip install -r requirements.txt
```

* Anwendung starten:
Führe die main.py Datei aus, um die Anwendung zu starten:
```bash
python main.py
```

## 📂 Projektstruktur
Das Projekt ist in logische Module unterteilt, um eine klare Trennung der Zuständigkeiten zu gewährleisten:

- `/core/`: Enthält die zentrale Geschäftslogik, Konfiguration (config.py) und den Anwendungs-Controller (controller.py).

- `/db/`: Verantwortlich für die Datenbank-Interaktion, inklusive des Schema-Managements (database.py) und der Datenmodelle (models.py).

- `/generators/`: Beinhaltet die Logik zur Erstellung der DOCX- (docx_generator.py) und PDF-Dateien (pdf_generator.py).

- `/gui/`: Definiert die grafische Benutzeroberfläche.

- `/views/`: Jede Hauptansicht der Anwendung (z.B. berichtsheft_view.py, settings_view.py) ist hier als eigene Klasse definiert.

- **/widgets/:** Wiederverwendbare, barrierefreie UI-Komponenten (accessible_widgets.py).

- `/services/` Kapselt externe Dienste wie den Update-Check (update_service.py), den Daten-Import (importer_service.py) und die Backup-Funktionalität (backup_service.py).

- `/tests/`: Enthält Unit-Tests, um die Funktionalität der Datenbank- und Repository-Schichten sicherzustellen.

- `main.py`: Der Haupteinstiegspunkt, der die Anwendung initialisiert und startet.
