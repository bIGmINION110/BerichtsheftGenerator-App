# gui/views/load_report_view.py
# -*- coding: utf-8 -*-
"""
Definiert die Ansicht zum Laden eines bestehenden Berichts.
"""
import customtkinter as ctk
import logging
from tkinter import messagebox
from typing import Dict, Any, List
from ..widgets.accessible_widgets import AccessibleCTkButton
from core import config

logger = logging.getLogger(__name__)

class LoadReportView(ctk.CTkFrame):
    """Ansicht zur Auswahl und zum Laden eines gespeicherten Berichts."""

    def __init__(self, master, app_logic):
        super().__init__(master)
        self.app = app_logic
        self.data_manager = app_logic.data_manager

        self.reports: Dict[str, Any] = {}
        self.report_frames: List[ctk.CTkFrame] = []
        self.current_focus_index = 0

        self._create_widgets()

    def on_show(self):
        """Wird aufgerufen, wenn die Ansicht sichtbar wird. Lädt die Berichtsliste neu."""
        self.reports = self.data_manager.lade_berichte()
        self._populate_report_list()
        # Setzt den Fokus auf das erste Element, wenn die Ansicht geöffnet wird
        if self.report_frames:
            self.after(100, lambda: self.report_frames[0].focus_set())

    def _create_widgets(self):
        """Erstellt die UI-Elemente der Ansicht."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Eine zusätzliche Zeile für die Aktionen

        # Frame für Aktionen wie "Alle löschen"
        action_frame = ctk.CTkFrame(self)
        action_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")
        action_frame.grid_columnconfigure(0, weight=1)

        AccessibleCTkButton(
            action_frame,
            text="Alle Berichte löschen",
            fg_color=config.ERROR_COLOR,
            hover_color=config.ERROR_HOVER_COLOR,
            command=self._delete_all_reports,
            accessible_text="Löscht alle gespeicherten Berichte nach einer Bestätigung.",
            status_callback=self.app.update_status,
            speak_callback=self.app.speak
        ).pack(side="right", padx=10, pady=10)

        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Gespeicherte Berichte")
        self.scroll_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

    def _populate_report_list(self):
        """Füllt die Liste mit den verfügbaren Berichten."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.report_frames = []

        if not self.reports:
            ctk.CTkLabel(self.scroll_frame, text="Keine Berichte zum Laden gefunden.").pack(pady=10)
            return

        sorted_reports = sorted(self.reports.items(), key=lambda item: item[0], reverse=True)

        for key, report_data in sorted_reports:
            frame = ctk.CTkFrame(self.scroll_frame)
            frame.pack(fill="x", padx=5, pady=5)
            frame.grid_columnconfigure(0, weight=1)
            
            # Wichtige Metadaten für die Tastaturnavigation speichern
            frame.report_id = key
            frame.report_data = report_data
            
            self.report_frames.append(frame)

            try:
                nr = report_data.get("fortlaufende_nr", "?")
                kw = report_data.get("kalenderwoche", "?")
                jahr = report_data.get("jahr", "?")
                name = report_data.get("name_azubi", "Unbekannt")
                
                label_text = f"Nr. {nr} - KW {kw}/{jahr} ({name})"
                ctk.CTkLabel(frame, text=label_text, justify="left").grid(row=0, column=0, padx=10, pady=5, sticky="w")
                
                load_button = AccessibleCTkButton(
                    frame,
                    text="Laden",
                    width=80,
                    command=lambda data=report_data: self._load_report(data),
                    accessible_text=f"Lädt den Bericht Nr. {nr} für die Kalenderwoche {kw} im Jahr {jahr} von {name}.",
                    status_callback=self.app.update_status,
                    speak_callback=self.app.speak,
                )
                load_button.grid(row=0, column=1, padx=5, pady=5)
                
                delete_button = AccessibleCTkButton(
                    frame,
                    text="Löschen",
                    width=80,
                    fg_color=config.ERROR_COLOR,
                    hover_color=config.ERROR_HOVER_COLOR,
                    command=lambda report_id=key: self._delete_report(report_id),
                    accessible_text=f"Löscht den Bericht Nr. {nr} für die Kalenderwoche {kw} im Jahr {jahr} von {name}.",
                    status_callback=self.app.update_status,
                    speak_callback=self.app.speak,
                )
                delete_button.grid(row=0, column=2, padx=5, pady=5)

                # Binden der Aktionen an den Frame
                frame.bind("<Return>", lambda event, data=report_data: self._load_report(data))
                frame.bind("<Delete>", lambda event, report_id=key: self._delete_report(report_id))
                
                # Visuelles Feedback bei Fokus
                frame.bind("<FocusIn>", lambda event, f=frame: self._on_focus_in(f))
                frame.bind("<FocusOut>", lambda event, f=frame: self._on_focus_out(f))

            except Exception as e:
                logger.warning(f"Fehler beim Anzeigen des Berichts '{key}': {e}")
                ctk.CTkLabel(frame, text=f"Fehlerhafter Eintrag: {key}", text_color="orange").grid(row=0, column=0, padx=10, pady=5, sticky="w")

    def _on_focus_in(self, widget: ctk.CTkFrame):
        """Hebt den Frame hervor, wenn er den Fokus erhält."""
        widget.configure(fg_color=config.HOVER_COLOR)
        # Scrollt zum fokussierten Element, falls es außerhalb des sichtbaren Bereichs ist
        self.scroll_frame._parent_canvas.yview_moveto(widget.winfo_y() / self.scroll_frame._parent_canvas.winfo_height())


    def _on_focus_out(self, widget: ctk.CTkFrame):
        """Setzt die Farbe des Frames zurück, wenn er den Fokus verliert."""
        widget.configure(fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"])

    def _navigate_reports(self, event):
        """Ermöglicht die Navigation mit den Pfeiltasten."""
        if not self.winfo_viewable() or not self.report_frames:
            return

        if event.keysym == "Down":
            self.current_focus_index = (self.current_focus_index + 1) % len(self.report_frames)
        elif event.keysym == "Up":
            self.current_focus_index = (self.current_focus_index - 1 + len(self.report_frames)) % len(self.report_frames)
        else:
            return

        self.report_frames[self.current_focus_index].focus_set()
    
    def _load_report(self, report_data: Dict[str, Any]):
        """Ruft die Methode in der Haupt-App auf, um die Daten in die GUI zu laden."""
        logger.info(f"Bericht Nr. {report_data.get('fortlaufende_nr', '?')} wird in die GUI geladen.")
        self.app.get_berichtsheft_view_reference().load_report_data_into_ui(report_data)
        self.app.show_view("berichtsheft", run_on_show=False)
        
    def _delete_report(self, report_id: str):
        """Löscht einen Bericht aus der Datenbank mit einer Animation."""
        if not messagebox.askyesno("Löschen bestätigen", f"Möchtest du den Bericht für ID '{report_id}' wirklich löschen?"):
            return

        frame_to_delete = next((f for f in self.report_frames if hasattr(f, 'report_id') and f.report_id == report_id), None)

        def perform_delete():
            if self.app.controller.delete_bericht(report_id):
                self.on_show()  # Lädt die Liste neu
            else:
                messagebox.showerror("Fehler", "Bericht konnte nicht gelöscht werden.")

        if frame_to_delete:
            self.app.animation_manager.delete_animation(frame_to_delete, remove_callback=perform_delete)
        else:
            perform_delete()  # Fallback, falls Frame nicht gefunden wird

    def _delete_all_reports(self):
        """Löscht alle Berichte nach einer Bestätigung."""
        if messagebox.askyesno("Alle Berichte löschen", "Bist du sicher, dass du ALLE gespeicherten Berichte unwiderruflich löschen möchtest?"):
            if self.app.controller.loesche_alle_berichte():
                messagebox.showinfo("Erfolg", "Alle Berichte wurden gelöscht.")
                self.on_show()
            else:
                messagebox.showerror("Fehler", "Ein Fehler ist beim Löschen der Berichte aufgetreten.")