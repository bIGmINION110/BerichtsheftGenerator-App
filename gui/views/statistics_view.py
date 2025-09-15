# gui/views/statistics_view.py
# -*- coding: utf-8 -*-
"""
Definiert die Ansicht zur Anzeige von Statistiken.
"""
import customtkinter as ctk
from tkinter import messagebox
from collections import defaultdict
from typing import Dict, Any
import logging

from ..widgets.accessible_widgets import AccessibleCTkButton
from core import config # Import für FOCUS_COLOR

try:
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class StatisticsView(ctk.CTkFrame):
    """Ansicht zur Anzeige von Statistiken über alle erstellten Berichte."""

    def __init__(self, master, app_logic):
        super().__init__(master)
        self.app = app_logic
        self.data_manager = app_logic.data_manager
        
        self.pie_chart_canvas = None
        self.bar_chart_canvas = None

        self._create_widgets()
        
    def on_show(self):
        """Wird aufgerufen, wenn die Ansicht sichtbar wird. Lädt die Daten neu."""
        self._load_and_display_stats()
        if not MATPLOTLIB_AVAILABLE:
            self._show_matplotlib_error()

    def _get_theme_colors(self) -> Dict[str, str]:
        """Gibt die passenden Farben für den aktuellen App-Modus zurück."""
        if ctk.get_appearance_mode() == "Dark":
            return {"bg": "#2B2B2B", "text": "#FFFFFF", "bars": config.ACCENT_COLOR}
        else:
            return {"bg": "#EBEBEB", "text": "#000000", "bars": config.ACCENT_COLOR}

    def _create_widgets(self):
        """Erstellt die UI-Elemente des Fensters."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header_frame, text="Statistik-Übersicht", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        clear_button = AccessibleCTkButton(
            header_frame, 
            text="Statistiken zurücksetzen", 
            fg_color=config.ERROR_COLOR, 
            hover_color=config.ERROR_HOVER_COLOR,
            focus_color=config.FOCUS_COLOR,
            command=self._clear_stats,
            accessible_text="Löscht alle Berichtsdaten und setzt die Statistiken zurück.",
            status_callback=self.app.update_status,
            speak_callback=self.app.speak
        )
        clear_button.grid(row=0, column=1, padx=10, pady=5, sticky="e")

        self.summary_frame = ctk.CTkFrame(self)
        self.summary_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.summary_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.pie_chart_frame = ctk.CTkFrame(self)
        self.pie_chart_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.pie_chart_frame.grid_rowconfigure(0, weight=1)
        self.pie_chart_frame.grid_columnconfigure(0, weight=1)

        self.bar_chart_frame = ctk.CTkFrame(self)
        self.bar_chart_frame.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        self.bar_chart_frame.grid_rowconfigure(0, weight=1)
        self.bar_chart_frame.grid_columnconfigure(0, weight=1)
        
        self.no_data_label = ctk.CTkLabel(self, text="Keine Daten für Statistiken verfügbar.", font=ctk.CTkFont(size=16))
        self.matplotlib_error_label = ctk.CTkLabel(self, 
            text="Hinweis: Die 'matplotlib' Bibliothek wird für Diagramme benötigt.\nInstallieren mit: pip install matplotlib",
            font=ctk.CTkFont(size=12), text_color="orange", wraplength=400
        )

    def _show_matplotlib_error(self):
        """Zeigt eine Hinweismeldung, wenn Matplotlib nicht installiert ist."""
        self.matplotlib_error_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

    def _clear_stats(self):
        """Löscht alle Berichtsdaten nach Bestätigung."""
        if messagebox.askyesno("Bestätigen", "Möchtest du wirklich alle gesammelten Berichtsdaten unwiderruflich löschen?"):
            if self.data_manager.loesche_statistiken():
                messagebox.showinfo("Erfolg", "Alle Statistiken wurden zurückgesetzt.")
                self._load_and_display_stats()
            else:
                messagebox.showerror("Fehler", "Die Statistiken konnten nicht gelöscht werden.")

    def _clear_previous_data(self):
        """Bereinigt alte Diagramme und Labels."""
        self.no_data_label.grid_forget()
        self.matplotlib_error_label.grid_forget()
        for widget in self.summary_frame.winfo_children():
            widget.destroy()
        if self.pie_chart_canvas:
            self.pie_chart_canvas.get_tk_widget().destroy()
            self.pie_chart_canvas = None
        if self.bar_chart_canvas:
            self.bar_chart_canvas.get_tk_widget().destroy()
            self.bar_chart_canvas = None
        for frame in [self.pie_chart_frame, self.bar_chart_frame]:
            for widget in frame.winfo_children():
                widget.destroy()

    def _load_and_display_stats(self):
        """Lädt die Berichtsdaten und erstellt die Visualisierungen."""
        self._clear_previous_data()
        
        berichte = self.data_manager.lade_berichte()
        if not berichte:
            self.no_data_label.grid(row=2, column=0, columnspan=2, padx=10, pady=20)
            return

        total_reports = len(berichte)
        total_hours = 0
        stunden_pro_typ = defaultdict(float)
        tage_pro_typ = defaultdict(int)
        jahres_stunden = defaultdict(float)
        
        for bericht in berichte.values():
            for tag in bericht.get("tage_daten", []):
                stunden_str = tag.get("stunden", "0:0")
                typ = tag.get("typ", "Unbekannt")
                
                dezimal_stunden = self.app.logic.parse_time_to_decimal(stunden_str)
                total_hours += dezimal_stunden
                stunden_pro_typ[typ] += dezimal_stunden
                tage_pro_typ[typ] += 1
                
                if bericht.get("jahr"):
                    jahres_stunden[str(bericht.get("jahr"))] += dezimal_stunden

        self._update_summary_labels(total_reports, total_hours, stunden_pro_typ, tage_pro_typ)
        
        if MATPLOTLIB_AVAILABLE:
            if sum(tage_pro_typ.values()) > 0:
                try:
                    self._create_pie_chart(tage_pro_typ, "Tageverteilung nach Typ")
                except Exception:
                    logging.error("Fehler beim Erstellen des Kuchendiagramms.", exc_info=True)
                    ctk.CTkLabel(self.pie_chart_frame, text="Fehler beim Erstellen des Diagramms.").pack()
            else:
                ctk.CTkLabel(self.pie_chart_frame, text="Keine Tage für Diagramm.").pack(expand=True)

            if jahres_stunden and sum(jahres_stunden.values()) > 0:
                try:
                    self._create_bar_chart(jahres_stunden, "Gesamtstunden pro Jahr")
                except Exception:
                    logging.error("Fehler beim Erstellen des Balkendiagramms.", exc_info=True)
                    ctk.CTkLabel(self.bar_chart_frame, text="Fehler beim Erstellen des Diagramms.").pack()
            else:
                 ctk.CTkLabel(self.bar_chart_frame, text="Keine Stunden für Diagramm.").pack(expand=True)
        else:
            ctk.CTkLabel(self.pie_chart_frame, text="Matplotlib nicht installiert.").pack(expand=True)
            ctk.CTkLabel(self.bar_chart_frame, text="Matplotlib nicht installiert.").pack(expand=True)

    def _update_summary_labels(self, total_reports, total_hours, stunden_pro_typ, tage_pro_typ):
        """Aktualisiert die Text-Labels mit den zusammengefassten Daten."""
        # Erste Zeile: Allgemeine Infos
        ctk.CTkLabel(self.summary_frame, text=f"Gesamtanzahl Berichte\n{total_reports}", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=5)
        ctk.CTkLabel(self.summary_frame, text=f"Gesamtstunden\n{total_hours:.2f}", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=1, pady=5)
        ctk.CTkLabel(self.summary_frame, text=f"Betriebsstunden\n{stunden_pro_typ.get('Betrieb', 0):.2f}", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=2, pady=5)
        ctk.CTkLabel(self.summary_frame, text=f"Schulstunden\n{stunden_pro_typ.get('Schule', 0):.2f}", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=3, pady=5)

        # Zweite Zeile: Tage-Zusammenfassung
        ctk.CTkLabel(self.summary_frame, text=f"Urlaubstage\n{tage_pro_typ.get('Urlaub', 0)}", font=ctk.CTkFont(size=16, weight="bold")).grid(row=1, column=0, pady=5)
        ctk.CTkLabel(self.summary_frame, text=f"Krankheitstage\n{tage_pro_typ.get('Krank', 0)}", font=ctk.CTkFont(size=16, weight="bold")).grid(row=1, column=1, pady=5)
        ctk.CTkLabel(self.summary_frame, text=f"Feiertage\n{tage_pro_typ.get('Feiertag', 0)}", font=ctk.CTkFont(size=16, weight="bold")).grid(row=1, column=2, pady=5)


    def _create_pie_chart(self, data: Dict, title: str):
        """Erstellt und rendert ein Kuchendiagramm."""
        colors = self._get_theme_colors()
        
        filtered_data = {label: size for label, size in data.items() if size > 0}
        labels = filtered_data.keys()
        sizes = filtered_data.values()
        
        fig, ax = plt.subplots(facecolor=colors["bg"])
        # Zeigt die absolute Anzahl der Tage im Diagramm an
        autopct = lambda p: '{:.0f}'.format(p * sum(sizes) / 100)
        
        ax.pie(sizes, labels=labels, autopct=autopct, startangle=90, textprops={'color': colors["text"]})
        ax.axis('equal')
        ax.set_title(title, color=colors["text"])
        
        self.pie_chart_canvas = FigureCanvasTkAgg(fig, master=self.pie_chart_frame)
        self.pie_chart_canvas.draw()
        self.pie_chart_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        
        # Textliche Zusammenfassung für Barrierefreiheit
        summary_text = "Zusammenfassung Kuchendiagramm: " + ", ".join([f"{label}: {size} Tage" for label, size in filtered_data.items()])
        summary_label = ctk.CTkLabel(self.pie_chart_frame, text=summary_text, wraplength=400, justify="center")
        summary_label.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        plt.close(fig)

    def _create_bar_chart(self, data: Dict, title: str):
        """Erstellt und rendert ein Balkendiagramm."""
        colors = self._get_theme_colors()
        jahre = sorted(data.keys())
        stunden = [data[jahr] for jahr in jahre]

        fig, ax = plt.subplots(facecolor=colors["bg"])
        ax.bar(jahre, stunden, color=colors["bars"])
        
        ax.set_title(title, color=colors["text"])
        ax.set_ylabel('Stunden', color=colors["text"])
        ax.set_xlabel('Jahr', color=colors["text"])
        ax.tick_params(axis='x', colors=colors["text"])
        ax.tick_params(axis='y', colors=colors["text"])
        ax.spines['bottom'].set_color(colors["text"])
        ax.spines['left'].set_color(colors["text"])
        ax.spines['top'].set_color(colors["bg"])
        ax.spines['right'].set_color(colors["bg"])
        ax.set_facecolor(colors["bg"])
        
        self.bar_chart_canvas = FigureCanvasTkAgg(fig, master=self.bar_chart_frame)
        self.bar_chart_canvas.draw()
        self.bar_chart_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        
        # Textliche Zusammenfassung für Barrierefreiheit
        summary_text = "Zusammenfassung Balkendiagramm: " + ", ".join([f"Jahr {jahr}: {stunde:.2f} Stunden" for jahr, stunde in zip(jahre, stunden)])
        summary_label = ctk.CTkLabel(self.bar_chart_frame, text=summary_text, wraplength=400, justify="center")
        summary_label.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        plt.close(fig)
