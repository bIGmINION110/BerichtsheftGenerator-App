# gui/views/calendar_view.py
# -*- coding: utf-8 -*-
"""
Definiert die neue Kalender-Ansicht zur Übersicht der Berichte.
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import date, timedelta
import logging

from core import config

try:
    from tkcalendar import Calendar
except ImportError:
    Calendar = None

logger = logging.getLogger(__name__)

class CalendarView(ctk.CTkFrame):
    """
    Eine Ansicht, die einen Kalender anzeigt und die Wochen mit existierenden
    Berichten hervorhebt.
    """
    def __init__(self, master, app_logic):
        super().__init__(master)
        self.app = app_logic
        self.data_manager = app_logic.data_manager
        
        self.reports_by_week: dict[str, dict] = {}
        self.calendar: Optional[Calendar] = None

        if not Calendar:
            self._show_tkcalendar_error()
        else:
            self._create_widgets()

    def on_show(self):
        """Wird aufgerufen, wenn die Ansicht sichtbar wird. Lädt die Berichtsdaten neu."""
        if Calendar:
            self._load_and_highlight_reports()

    def _show_tkcalendar_error(self):
        """Zeigt eine Fehlermeldung an, wenn tkcalendar nicht installiert ist."""
        ctk.CTkLabel(
            self,
            text="Die Bibliothek 'tkcalendar' wird für diese Ansicht benötigt.\nBitte installieren Sie sie mit: pip install tkcalendar",
            font=ctk.CTkFont(size=14),
            text_color="orange",
            wraplength=400
        ).pack(expand=True, padx=20, pady=20)

    def _create_widgets(self):
        """Erstellt die UI-Elemente der Ansicht."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        
        ctk.CTkLabel(header, text="Kalender-Übersicht", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")

        self.calendar_frame = ctk.CTkFrame(self)
        self.calendar_frame.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")
        self.calendar_frame.grid_columnconfigure(0, weight=1)
        self.calendar_frame.grid_rowconfigure(0, weight=1)

        # Kalender-Widget initialisieren
        self.calendar = Calendar(
            self.calendar_frame,
            selectmode='day',
            date_pattern='dd.mm.y',
            showweeknumbers=True
        )
        self.calendar.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.calendar.bind("<<CalendarSelected>>", self._on_date_selected)

    def _load_and_highlight_reports(self):
        """Lädt alle Berichte und hebt die entsprechenden Wochen im Kalender hervor."""
        if not self.calendar:
            return
            
        reports = self.data_manager.lade_berichte()
        self.reports_by_week = {}
        self.calendar.calevent_remove("all") # Alte Markierungen entfernen

        for report_id, report_data in reports.items():
            try:
                year, week = map(int, report_id.split('-'))
                self.reports_by_week[f"{year}-{week}"] = report_data
                
                # Finde den ersten Tag der Kalenderwoche
                report_date = date.fromisocalendar(year, week, 1)
                
                # Markiere die ganze Woche
                for i in range(7):
                    day_to_mark = report_date + timedelta(days=i)
                    self.calendar.calevent_create(
                        day_to_mark,
                        'Bericht vorhanden',
                        'bericht'
                    )
            except (ValueError, TypeError) as e:
                logger.warning(f"Konnte Bericht-ID '{report_id}' nicht für den Kalender parsen: {e}")
        
        # Style für die Markierungen setzen
        self.calendar.tag_config('bericht', background=config.ACCENT_COLOR, foreground='white')
        self.app.update_status("Kalender aktualisiert. Wochen mit Berichten sind markiert.")

    def _on_date_selected(self, event=None):
        """Wird aufgerufen, wenn ein Datum im Kalender ausgewählt wird."""
        if not self.calendar:
            return
            
        try:
            selected_date_str = self.calendar.get_date()
            selected_date = datetime.strptime(selected_date_str, self.calendar['date_pattern']).date()
            year, week, _ = selected_date.isocalendar()
            
            report_key = f"{year}-{week}"
            
            if report_key in self.reports_by_week:
                report_data = self.reports_by_week[report_key]
                
                if messagebox.askyesno(
                    "Bericht laden",
                    f"Möchten Sie den Bericht für die KW {week}/{year} laden?",
                    parent=self
                ):
                    self.app.get_berichtsheft_view_reference().load_report_data_into_ui(report_data)
                    self.app.show_view("berichtsheft", run_on_show=False)
            else:
                self.app.update_status(f"Für die KW {week}/{year} wurde kein Bericht gefunden.")

        except Exception as e:
            logger.error(f"Fehler bei der Auswahl eines Datums im Kalender: {e}", exc_info=True)
            self.app.update_status("Fehler beim Verarbeiten des Datums.")
            