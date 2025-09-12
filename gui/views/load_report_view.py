# gui/views/load_report_view.py
# -*- coding: utf-8 -*-
"""
Definiert die Ansicht zum Laden eines bestehenden Berichts.
"""
import customtkinter as ctk
import logging
from typing import Dict, Any
from ..widgets.accessible_widgets import AccessibleCTkButton

logger = logging.getLogger(__name__)

class LoadReportView(ctk.CTkFrame):
    """Ansicht zur Auswahl und zum Laden eines gespeicherten Berichts."""
    
    def __init__(self, master, app_logic):
        super().__init__(master)
        self.app = app_logic
        self.data_manager = app_logic.data_manager
        
        self.reports: Dict[str, Any] = {}
        
        self._create_widgets()

    def on_show(self):
        """Wird aufgerufen, wenn die Ansicht sichtbar wird. Lädt die Berichtsliste neu."""
        self.reports = self.data_manager.lade_berichte()
        self._populate_report_list()

    def _create_widgets(self):
        """Erstellt die UI-Elemente der Ansicht."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Gespeicherte Berichte")
        self.scroll_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    def _populate_report_list(self):
        """Füllt die Liste mit den verfügbaren Berichten."""
        # Alte Einträge löschen
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not self.reports:
            ctk.CTkLabel(self.scroll_frame, text="Keine Berichte zum Laden gefunden.").pack(pady=10)
            return

        # Sortiert die Berichte nach Schlüssel (z.B. "2023-52") absteigend
        sorted_reports = sorted(self.reports.items(), key=lambda item: item[0], reverse=True)

        for key, report_data in sorted_reports:
            frame = ctk.CTkFrame(self.scroll_frame)
            frame.pack(fill="x", padx=5, pady=5)
            frame.grid_columnconfigure(0, weight=1)
            
            try:
                nr = report_data.get("fortlaufende_nr", "?")
                kw = report_data.get("kalenderwoche", "?")
                jahr = report_data.get("jahr", "?")
                name = report_data.get("name_azubi", "Unbekannt")
                
                label_text = f"Nr. {nr} - KW {kw}/{jahr} ({name})"
                ctk.CTkLabel(frame, text=label_text, justify="left").grid(row=0, column=0, padx=10, pady=5, sticky="w")
                
                AccessibleCTkButton(
                    frame, 
                    text="Laden", 
                    width=80, 
                    command=lambda data=report_data: self._load_report(data),
                    accessible_text=f"Lädt den Bericht Nr. {nr} für die Kalenderwoche {kw} im Jahr {jahr} von {name}.",
                    status_callback=self.app.update_status,
                    speak_callback=self.app.speak
                ).grid(row=0, column=1, padx=5, pady=5)
            except Exception as e:
                logger.warning(f"Fehler beim Anzeigen des Berichts '{key}': {e}")
                ctk.CTkLabel(frame, text=f"Fehlerhafter Eintrag: {key}", text_color="orange").grid(row=0, column=0, padx=10, pady=5, sticky="w")

    def _load_report(self, report_data: Dict[str, Any]):
        """Ruft die Methode in der Haupt-App auf, um die Daten in die GUI zu laden."""
        logger.info(f"Bericht Nr. {report_data.get('fortlaufende_nr', '?')} wird in die GUI geladen.")
        # Rufe die Methode in der Haupt-App auf, die die UI aktualisiert und die Ansicht wechselt
        self.app.get_berichtsheft_view_reference().load_report_data_into_ui(report_data)

