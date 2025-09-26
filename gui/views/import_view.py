# gui/views/import_view.py
# -*- coding: utf-8 -*-
"""
Definiert die Ansicht für den Import von bestehenden DOCX-Berichten.
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
import logging
from ..widgets.accessible_widgets import AccessibleCTkButton
from core import config

logger = logging.getLogger(__name__)

class ImportView(ctk.CTkFrame):
    """
    Ansicht, die es dem Benutzer ermöglicht, DOCX-Dateien auszuwählen
    und deren Inhalt in die Anwendung zu importieren.
    """
    def __init__(self, master, app_logic):
        super().__init__(master)
        self.app = app_logic
        self.controller = app_logic.controller
        
        self.title_font = ctk.CTkFont(family=config.UI_FONT_FAMILY, size=16, weight="bold")
        
        self._create_widgets()

    def _create_widgets(self) -> None:
        """Erstellt die UI-Elemente der Ansicht."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Info-Frame
        info_frame = ctk.CTkFrame(self)
        info_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        info_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(info_frame, text="Berichte aus Word-Dateien importieren", font=self.title_font).pack(pady=(10, 5))
        info_text = (
            "Diese Funktion versucht, die Daten aus bestehenden .docx-Berichtsheften zu extrahieren.\n"
            "Wählen Sie eine oder mehrere Dateien aus. Die importierten Daten werden zur Statistik\n"
            "und zur 'Bericht laden'-Ansicht hinzugefügt.\n\n"
            "Hinweis: Funktioniert am besten mit Berichten, die mit diesem Programm erstellt wurden."
        )
        ctk.CTkLabel(info_frame, text=info_text, justify="center").pack(pady=5, padx=10)
        
        AccessibleCTkButton(
            info_frame, 
            text="Word-Berichte zum Import auswählen...", 
            command=self._select_and_import_files,
            accessible_text="Öffnet einen Dateidialog zur Auswahl von DOCX-Dateien für den Import.",
            status_callback=self.app.update_status,
            speak_callback=self.app.speak
        ).pack(pady=15)

        # Log/Output-Frame
        self.output_frame = ctk.CTkFrame(self)
        self.output_frame.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        self.output_frame.grid_columnconfigure(0, weight=1)
        self.output_frame.grid_rowconfigure(0, weight=1)

        self.output_textbox = ctk.CTkTextbox(self.output_frame, state="disabled", wrap="word")
        self.output_textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    def _log_to_view(self, message: str):
        """Schreibt eine Nachricht in das Textfeld der Ansicht."""
        self.output_textbox.configure(state="normal")
        self.output_textbox.insert("end", message + "\n")
        self.output_textbox.configure(state="disabled")
        self.update_idletasks() # UI sofort aktualisieren

    def _select_and_import_files(self) -> None:
        """Öffnet einen Dateidialog und startet den Importprozess."""
        file_paths = filedialog.askopenfilenames(
            title="Wählen Sie DOCX-Berichtshefte aus",
            filetypes=[("Word-Dokumente", "*.docx")]
        )
        if not file_paths:
            return

        self.output_textbox.configure(state="normal")
        self.output_textbox.delete("1.0", "end")
        self.output_textbox.configure(state="disabled")

        self._log_to_view(f"{len(file_paths)} Datei(en) ausgewählt. Starte Import...")
        
        # KORREKTUR: Das Tupel mit 3 Werten korrekt entpacken
        success_count, failure_count, save_success = self.controller.import_docx_berichte(file_paths)
        
        self._log_to_view("\n--- Import abgeschlossen ---")
        self._log_to_view(f"Erfolgreich eingelesen: {success_count}")
        self._log_to_view(f"Fehlgeschlagen/Übersprungen: {failure_count}")

        if success_count > 0 and save_success:
            self._log_to_view("Datenbank erfolgreich aktualisiert.")
            messagebox.showinfo("Import abgeschlossen", 
                                f"{success_count} Bericht(e) wurden erfolgreich importiert und gespeichert.\n"
                                "Die Daten sind jetzt in der Statistik und unter 'Bericht laden' verfügbar.")
            self.app.reload_all_data()
        elif success_count > 0 and not save_success:
            self._log_to_view("FEHLER: Die eingelesenen Daten konnten nicht in der Datenbank gespeichert werden.")
            messagebox.showerror("Fehler beim Speichern",
                                 "Die Berichte wurden zwar eingelesen, konnten aber nicht in der Datenbank gespeichert werden. "
                                 "Bitte prüfen Sie die Log-Dateien.")
        elif failure_count > 0 and success_count == 0:
            messagebox.showwarning("Import abgeschlossen",
                                   "Es konnten keine Berichte importiert werden. "
                                   "Stellen Sie sicher, dass die Dateien dem erwarteten Format entsprechen.")