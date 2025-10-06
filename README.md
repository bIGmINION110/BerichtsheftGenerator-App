# Report Booklet Generator
A desktop application for the easy creation and management of training records, specifically tailored to the requirements of the Blista (Center for Vocational Training). The application is developed with Python and the CustomTkinter framework and places a strong focus on accessibility for screen reader users.

## ✨ Key Features
**Create & Export Reports**: Create daily and weekly reports and export them as DOCX or PDF files.

**Template Management**: Save recurring activities as templates to quickly insert them into new reports.

**Load & Edit**: Saved reports can be loaded and edited at any time.

**Data Import**: Import existing report booklets from Word files (.docx) to continue managing them in the application.

**Statistics**: Get a visual overview of hours worked, vacation days, sick days, and more, broken down by training year.

**Backup & Restore**: Back up all your data (reports, configurations, templates) into a single ZIP file or restore it from one.

**Accessibility**: Comprehensive support for screen readers (like NVDA and Jaws) through the accessible_output2 library is integrated, including speech output for almost all actions.

**Automatic Updates**: The application automatically checks for new versions on startup and notifies you if an update is available.

## 🛠️ Technology Stack
- Programming Language: Python
- GUI Framework: CustomTkinter
- Database: SQLite
- Document Generation:
    - python-docx for .docx files
    - fpdf2 for .pdf files
    - Accessibility: accessible_output2
    - Charts & Statistics: matplotlib
    - Calendar Widget: tkcalendar

## 🚀 Installation & Start
To run the project locally, follow these steps:

* Clone the repository:
```bash
git clone [https://github.com/bigminion110/berichtsheftgenerator-app.git](https://github.com/bigminion110/berichtsheftgenerator-app.git)
cd berichtsheftgenerator-app
```
Install dependencies:
It is recommended to use a virtual environment.
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```
Then, install the required packages from the requirements.txt file:
```bash
pip install -r requirements.txt
```

Start the application:
Run the main.py file to launch the application:
```bash
python main.py
```
## 📂 Project Structure
The project is divided into logical modules to ensure a clear separation of concerns:

* `/core/´: Contains the central business logic, configuration (config.py), and the application controller (controller.py).
* `/db/`: Responsible for database interaction, including schema management (database.py) and data models (models.py).
* `/generators/`: Includes the logic for creating DOCX (docx_generator.py) and PDF (pdf_generator.py) files.
* `/gui/`: Defines the graphical user interface.
* `/views/`: Each main view of the application (e.g., berichtsheft_view.py, settings_view.py) is defined here as its own class.
* `/widgets/`: Reusable, accessible UI components (accessible_widgets.py).
* `/services/`: Encapsulates external services such as the update check (update_service.py), data import (importer_service.py), and backup functionality (backup_service.py).
* `/tests/`: Contains unit tests to ensure the functionality of the database and repository layers.
* `main.py`: The main entry point that initializes and starts the application.


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
