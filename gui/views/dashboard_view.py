# gui/views/dashboard_view.py
# -*- coding: utf-8 -*-
"""
Definiert die Ansicht für eine wöchentliche Dashboard-Ansicht.
"""
import customtkinter as ctk
from collections import defaultdict
from typing import List, Dict, Any

class DashboardView(ctk.CTkFrame):
    """
    Eine Ansicht, die eine Zusammenfassung der aktuellen Wochendaten aus der
    Berichtsheft-Ansicht anzeigt.
    """
    def __init__(self, master, app_logic):
        super().__init__(master)
        self.app = app_logic
        
        self._create_widgets()

    def on_show(self):
        """Wird aufgerufen, wenn die Ansicht sichtbar wird. Lädt die Daten neu."""
        self._calculate_and_display_summary()

    def _create_widgets(self) -> None:
        """Erstellt die UI-Elemente der Ansicht."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Zusammenfassung der Woche", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=15, pady=15)

        self.summary_frame = ctk.CTkFrame(self)
        self.summary_frame.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")
        self.summary_frame.grid_columnconfigure(0, weight=1)

    def _get_current_week_data(self) -> List[Dict[str, Any]]:
        """Holt die aktuellen Daten aus der Berichtsheft-Ansicht."""
        berichtsheft_view = self.app.get_berichtsheft_view_reference()
        week_data = []
        for widgets in berichtsheft_view.tages_widgets:
            week_data.append({
                "typ": widgets["typ"].get(),
                "stunden": widgets["stunden"].get()
            })
        return week_data

    def _calculate_and_display_summary(self) -> None:
        """
        Berechnet die Gesamtstunden und die Stunden pro Typ und zeigt sie an.
        """
        # Alte Einträge löschen
        for widget in self.summary_frame.winfo_children():
            widget.destroy()

        week_data = self._get_current_week_data()
        stunden_pro_typ = defaultdict(float)
        gesamtstunden = 0.0

        for day in week_data:
            stunden_str = day.get("stunden", "0:0")
            # Nutzt die zentrale Logik-Funktion zur Umrechnung
            dezimal_stunden = self.app.logic.parse_time_to_decimal(stunden_str)
            stunden_pro_typ[day.get("typ", "Unbekannt")] += dezimal_stunden
            gesamtstunden += dezimal_stunden
        
        # UI-Elemente für die Zusammenfassung erstellen
        for typ, stunden in sorted(stunden_pro_typ.items()):
            label_text = f"{typ}: {stunden:.2f} Stunden"
            ctk.CTkLabel(self.summary_frame, text=label_text, font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=5)
            
        # Trennlinie
        ctk.CTkFrame(self.summary_frame, height=2, fg_color="gray50").pack(fill="x", padx=20, pady=10)

        # Gesamtstunden anzeigen
        total_label_text = f"Gesamt: {gesamtstunden:.2f} Stunden"
        ctk.CTkLabel(self.summary_frame, text=total_label_text, font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=5)
