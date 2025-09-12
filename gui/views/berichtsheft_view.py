# gui/views/berichtsheft_view.py
# -*- coding: utf-8 -*-
"""
Definiert die Hauptansicht zum Erstellen und Bearbeiten von Berichten.
"""
import customtkinter as ctk
import tkinter as tk
from typing import Dict, Any, List, Optional
from datetime import date, timedelta
from core import config
from gui.widgets.accessible_widgets import (
    AccessibleCTkEntry, 
    AccessibleCTkButton, 
    AccessibleCTkComboBox, 
    AccessibleCTkRadioButton,
    AccessibleCTkTextbox
)

try:
    from tkcalendar import DateEntry
except ImportError:
    DateEntry = None

class BerichtsheftView(ctk.CTkFrame):
    """Die Hauptansicht zum Erstellen und Bearbeiten von Berichten."""
    def __init__(self, master, app_logic):
        super().__init__(master, fg_color=config.FRAME_BG_COLOR)
        self.app = app_logic

        self.main_font = ctk.CTkFont(family="Segoe UI", size=13)
        self.bold_font = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        
        # UI Widgets
        self.tages_widgets: List[Dict[str, Any]] = []
        self.kalender: Optional[DateEntry] = None
        self.kopf_frame: Optional[ctk.CTkFrame] = None
        self.start_entry: Optional[AccessibleCTkEntry] = None
        
        # Variablen für Widgets
        self.name_var = tk.StringVar()
        self.startdatum_var = tk.StringVar()
        self.nummer_var = tk.StringVar()
        self.jahr_var = tk.StringVar()
        self.kw_var = tk.StringVar()
        self.format_var = tk.StringVar()
        
        self.default_border_color: Optional[str] = None
        
        self._create_widgets()
        self.on_show() # Initiales Laden und Anzeigen der Daten
        
    def _create_widgets(self):
        """Erstellt alle Widgets in dieser Ansicht."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        header_data_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_data_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        header_data_frame.grid_columnconfigure(1, weight=1)
        
        # Erstellt den Frame für persönliche Daten, der später ein-/ausgeblendet wird
        self._create_kopfdaten_widgets(header_data_frame)
        self._create_wochendaten_widgets(header_data_frame)
        
        self._create_daily_entry_tabs()
        self._create_action_buttons()

    def _create_kopfdaten_widgets(self, parent):
        """Erstellt den Frame, der nur angezeigt wird, wenn keine Daten in den Einstellungen sind."""
        self.kopf_frame = ctk.CTkFrame(parent)
        # grid() wird in on_show() aufgerufen
        
        self.kopf_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(self.kopf_frame, text="Persönliche Daten (Bitte in Einstellungen festlegen)", font=self.bold_font).grid(row=0, column=0, columnspan=2, pady=15, padx=15, sticky="w")
        
        ctk.CTkLabel(self.kopf_frame, text="Name des Azubis:", font=self.main_font).grid(row=1, column=0, sticky="w", padx=15, pady=8)
        name_entry = AccessibleCTkEntry(self.kopf_frame, textvariable=self.name_var, font=self.main_font, focus_color=config.FOCUS_COLOR, accessible_text="Eingabefeld für den Namen des Auszubildenden.", status_callback=self.app.update_status, speak_callback=self.app.speak)
        name_entry.grid(row=1, column=1, sticky="ew", padx=15, pady=8)
        
        ctk.CTkLabel(self.kopf_frame, text="Start Ausbildung:", font=self.main_font).grid(row=2, column=0, sticky="w", padx=15, pady=8)
        self.start_entry = AccessibleCTkEntry(
            self.kopf_frame, textvariable=self.startdatum_var, placeholder_text="TT.MM.JJJJ", font=self.main_font,
            focus_color=config.FOCUS_COLOR, accessible_text="Startdatum der Ausbildung im Format Tag.Monat.Jahr.", 
            status_callback=self.app.update_status, speak_callback=self.app.speak)
        self.start_entry.grid(row=2, column=1, sticky="ew", padx=15, pady=8)
        self.default_border_color = self.start_entry.cget("border_color")
        
        # Trace zur Validierung des Datumsformats hinzufügen
        self.startdatum_var.trace_add("write", self._validate_start_date)

        # Button, um direkt zu den Einstellungen zu springen
        settings_button = AccessibleCTkButton(self.kopf_frame, text="Zu den Einstellungen", command=lambda: self.app.show_view("settings"), 
                                              font=self.main_font, focus_color=config.FOCUS_COLOR,
                                              accessible_text="Öffnet die Einstellungen, um Name und Startdatum festzulegen.",
                                              status_callback=self.app.update_status, speak_callback=self.app.speak)
        settings_button.grid(row=3, column=1, padx=15, pady=10, sticky="e")


    def _create_wochendaten_widgets(self, parent):
        woche_frame = ctk.CTkFrame(parent)
        woche_frame.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="nsew")
        woche_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(woche_frame, text="Berichtsdaten", font=self.bold_font).grid(row=0, column=0, columnspan=3, pady=15, padx=15, sticky="w")
        ctk.CTkLabel(woche_frame, text="Bericht Nr.:", font=self.main_font).grid(row=1, column=0, sticky="w", padx=15, pady=8)
        nummer_entry = AccessibleCTkEntry(woche_frame, textvariable=self.nummer_var, font=self.main_font, focus_color=config.FOCUS_COLOR, accessible_text="Eingabefeld für die fortlaufende Berichtsnummer.", status_callback=self.app.update_status, speak_callback=self.app.speak)
        nummer_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=15, pady=8)
        ctk.CTkLabel(woche_frame, text="Woche wählen:", font=self.main_font).grid(row=2, column=0, sticky="w", padx=15, pady=8)
        
        kalender_container = ctk.CTkFrame(woche_frame, fg_color="transparent")
        kalender_container.grid(row=2, column=1, columnspan=2, sticky="ew", padx=15, pady=8)
        
        if DateEntry:
            self.kalender = DateEntry(kalender_container, width=12, date_pattern='dd.mm.y', font=("Segoe UI", 11))
            self.kalender.pack(side="left")
            self.kalender.bind("<<DateEntrySelected>>", self._update_kw_from_kalender)
            self.kalender.bind("<FocusIn>", lambda e: self.app.update_status("Kalender zur Auswahl des Berichtsdatums. Ändert automatisch die Kalenderwoche."))
        else:
            ctk.CTkLabel(kalender_container, text="tkcalendar fehlt!", text_color="orange").pack(side="left")

        ctk.CTkLabel(kalender_container, text="KW:", font=self.main_font).pack(side="left", padx=(10, 2))
        self.kw_entry = AccessibleCTkEntry(kalender_container, textvariable=self.kw_var, width=40, font=self.main_font,
                                           focus_color=config.FOCUS_COLOR,
                                           accessible_text="Manuelle Eingabe der Kalenderwoche.",
                                           status_callback=self.app.update_status,
                                           speak_callback=self.app.speak)
        self.kw_entry.pack(side="left")
        ctk.CTkLabel(kalender_container, text="Jahr:", font=self.main_font).pack(side="left", padx=(10, 2))
        self.jahr_entry = AccessibleCTkEntry(kalender_container, textvariable=self.jahr_var, width=60, font=self.main_font,
                                             focus_color=config.FOCUS_COLOR,
                                             accessible_text="Manuelle Eingabe des Jahres.",
                                             status_callback=self.app.update_status,
                                             speak_callback=self.app.speak)
        self.jahr_entry.pack(side="left")

        self.kw_var.trace_add("write", self._update_kalender_from_kw)
        self.jahr_var.trace_add("write", self._update_kalender_from_kw)

    def _create_daily_entry_tabs(self):
        self.tabview = ctk.CTkTabview(self, corner_radius=8, segmented_button_selected_color=config.ACCENT_COLOR, segmented_button_selected_hover_color=config.HOVER_COLOR)
        self.tabview.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        for i, tag_name in enumerate(config.WOCHENTAGE):
            tab = self.tabview.add(tag_name)
            tab.grid_columnconfigure(0, weight=1)
            tab.grid_rowconfigure(1, weight=1)
            header_frame = ctk.CTkFrame(tab, fg_color="transparent")
            header_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
            ctk.CTkLabel(header_frame, text="Typ:", font=self.main_font).pack(side="left", padx=(5, 5))
            typ_var = tk.StringVar(value="Betrieb")
            typ_combo = AccessibleCTkComboBox(header_frame, variable=typ_var, values=["Betrieb", "Schule", "Urlaub", "Krank", "Feiertag"], 
                                              width=120, font=self.main_font,
                                              focus_color=config.FOCUS_COLOR,
                                              accessible_text=f"Auswahl des Tätigkeitstyps für {tag_name}.",
                                              status_callback=self.app.update_status,
                                              speak_callback=self.app.speak)
            typ_combo.pack(side="left", padx=(0, 20))
            ctk.CTkLabel(header_frame, text="Stunden:", font=self.main_font).pack(side="left", padx=(5, 5))
            stunden_var = tk.StringVar()
            stunden_entry = AccessibleCTkEntry(master=header_frame, textvariable=stunden_var, width=70, font=self.main_font, 
                                               focus_color=config.FOCUS_COLOR,
                                               accessible_text=f"Eingabefeld für die Stundenanzahl am {tag_name}.", 
                                               status_callback=self.app.update_status,
                                               speak_callback=self.app.speak)
            stunden_entry.pack(side="left")
            
            def on_typ_select_factory(s_var, t_name):
                def on_typ_select(choice):
                    if choice in ["Urlaub", "Krank", "Feiertag"]:
                        s_var.set("0:00")
                    self.app.speak(f"{t_name} Typ auf {choice} gesetzt.")
                return on_typ_select

            typ_combo.configure(command=on_typ_select_factory(stunden_var, tag_name))

            taetigkeiten_text = AccessibleCTkTextbox(
                tab, 
                font=self.main_font, 
                wrap="word", 
                corner_radius=6, 
                border_width=1,
                focus_color=config.FOCUS_COLOR,
                accessible_text=f"Tätigkeiten für {tag_name}. Pfeiltasten hoch/runter lesen die aktuelle Zeile.",
                status_callback=self.app.update_status,
                speak_callback=self.app.speak
            )
            taetigkeiten_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
            self.tages_widgets.append({"typ": typ_var, "stunden": stunden_var, "taetigkeiten": taetigkeiten_text})

    def _create_action_buttons(self):
        action_frame = ctk.CTkFrame(self)
        action_frame.grid(row=2, column=0, columnspan=2, sticky="sew", padx=10, pady=10)
        action_frame.grid_columnconfigure(0, weight=1)
        format_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
        format_frame.pack(side="left", padx=10, pady=5)
        ctk.CTkLabel(format_frame, text="Format:", font=self.main_font).pack(side="left")
        AccessibleCTkRadioButton(format_frame, text="DOCX", variable=self.format_var, value="docx", font=self.main_font, 
                                 fg_color=config.ACCENT_COLOR,
                                 focus_color=config.FOCUS_COLOR,
                                 accessible_text="Wählt DOCX als Ausgabeformat für den Bericht.",
                                 status_callback=self.app.update_status,
                                 speak_callback=self.app.speak).pack(side="left", padx=5)
        AccessibleCTkRadioButton(format_frame, text="PDF", variable=self.format_var, value="pdf", font=self.main_font, 
                                 fg_color=config.ACCENT_COLOR,
                                 focus_color=config.FOCUS_COLOR,
                                 accessible_text="Wählt PDF als Ausgabeformat für den Bericht.",
                                 status_callback=self.app.update_status,
                                 speak_callback=self.app.speak).pack(side="left", padx=5)
        self.create_report_button = AccessibleCTkButton(action_frame, text="Erstellen (Strg+G)", command=self.app.erstelle_bericht, 
                                                        font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), height=35, 
                                                        fg_color=config.ACCENT_COLOR, hover_color=config.HOVER_COLOR,
                                                        focus_color=config.FOCUS_COLOR,
                                                        accessible_text="Erstellt das Berichtsheft mit den eingegebenen Daten im ausgewählten Format.",
                                                        status_callback=self.app.update_status,
                                                        speak_callback=self.app.speak)
        self.create_report_button.pack(side="right", padx=10, pady=5)

    def on_show(self):
        """Lädt die Konfiguration und passt die Sichtbarkeit der Widgets an."""
        konfig = self.app.data_manager.lade_konfiguration()
        name_azubi = konfig.get("name_azubi", "")
        startdatum_ausbildung = konfig.get("startdatum_ausbildung", "")

        # Blendet den Frame für persönliche Daten aus, wenn diese in den Einstellungen gesetzt sind
        if name_azubi and self.app.logic.valide_datumsformat(startdatum_ausbildung):
            self.kopf_frame.grid_forget()
        else:
            self.kopf_frame.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")

        # Setzt die internen Variablen, damit sie für die Berichtserstellung verfügbar sind
        self.name_var.set(name_azubi)
        self.startdatum_var.set(startdatum_ausbildung)
        
        einstellungen = konfig.get("einstellungen", {})
        self.format_var.set(einstellungen.get("default_format", "docx"))
        
        default_stunden = einstellungen.get("default_stunden", {})
        default_typen = einstellungen.get("default_typen", {})

        for i, tag_name in enumerate(config.WOCHENTAGE):
            if i < len(self.tages_widgets):
                widgets = self.tages_widgets[i]
                default_typ = default_typen.get(tag_name, "Betrieb")
                widgets["typ"].set(default_typ)
                
                if default_typ in ["Urlaub", "Krank", "Feiertag"]:
                    widgets["stunden"].set("0:00")
                else:
                    default_zeit = default_stunden.get(tag_name, "08:00")
                    widgets["stunden"].set(default_zeit)

        letztes_jahr = konfig.get("letzte_bericht_jahr")
        letzte_kw = konfig.get("letzte_bericht_kw")
        letzte_nr = konfig.get("letzte_bericht_nummer", 0)
        vorschlag_datum = date.today()
        if letztes_jahr and letzte_kw:
            try:
                vorschlag_datum = date.fromisocalendar(letztes_jahr, letzte_kw, 1) + timedelta(weeks=1)
            except ValueError:
                pass
        if self.kalender:
            self.kalender.set_date(vorschlag_datum)
        
        self._update_kw_from_kalender()
        self.nummer_var.set(str(letzte_nr + 1))


    def load_report_data_into_ui(self, report_data: Dict[str, Any]):
        """Lädt die Daten eines spezifischen Berichts in die GUI-Felder."""
        self.nummer_var.set(report_data.get("fortlaufende_nr", ""))
        kw, jahr = report_data.get("kalenderwoche"), report_data.get("jahr")
        if kw and jahr:
            self.kw_var.set(str(kw))
            self.jahr_var.set(str(jahr))

        for i, tag_data in enumerate(report_data.get("tage_daten", [])):
            if i < len(self.tages_widgets):
                widgets = self.tages_widgets[i]
                widgets["typ"].set(tag_data.get("typ", "Betrieb"))
                widgets["stunden"].set(tag_data.get("stunden", "00:00"))
                widgets["taetigkeiten"].delete("1.0", "end")
                widgets["taetigkeiten"].insert("1.0", tag_data.get("taetigkeiten", ""))
        self.app.update_status(f"Bericht Nr. {self.nummer_var.get()} geladen.")
        self.app.speak(f"Bericht für Kalenderwoche {kw}, Jahr {jahr} geladen.")
        self.app.show_view("berichtsheft")

    def _update_kw_from_kalender(self, event: Any = None):
        if not self.kalender: return
        selected_date = self.kalender.get_date()
        iso_year, iso_week, _ = selected_date.isocalendar()
        
        if not (self.kw_var.get() == str(iso_week) and self.jahr_var.get() == str(iso_year)):
            self.kw_var.set(str(iso_week))
            self.jahr_var.set(str(iso_year))
            status_message = f"Kalenderwoche {iso_week}, Jahr {iso_year} ausgewählt."
            self.app.update_status(status_message)
            self.app.speak(status_message, interrupt=False)

    def _update_kalender_from_kw(self, *args: Any):
        """Aktualisiert das Kalenderdatum, wenn KW oder Jahr manuell geändert werden."""
        if not self.kalender or not self.winfo_viewable(): return
        
        try:
            kw = int(self.kw_var.get())
            jahr = int(self.jahr_var.get())
            
            if kw > 53 or kw < 1 or jahr < 1900 or jahr > 2100:
                return
            
            new_date = date.fromisocalendar(jahr, kw, 1)
            
            if self.kalender.get_date() != new_date:
                self.kalender.set_date(new_date)

        except (ValueError, TypeError):
            pass

    def _validate_start_date(self, *args: Any):
        datum_str = self.startdatum_var.get()
        is_valid = self.app.logic.valide_datumsformat(datum_str) if datum_str else True
        if self.start_entry and self.default_border_color:
            if is_valid:
                self.start_entry.configure(border_color=self.default_border_color)
                # Nur speichern, wenn das Format gültig ist
                self.app.speichere_persoenliche_daten(self.name_var.get(), datum_str)
            else:
                self.start_entry.configure(border_color=config.ERROR_COLOR)
                self.app.update_status("Fehler: Ungültiges Datumsformat. Bitte TT.MM.JJJJ verwenden.")
                self.app.speak("Ungültiges Datumsformat")

    def get_active_textbox(self) -> Optional[ctk.CTkTextbox]:
        """Gibt die Textbox des aktuell ausgewählten Tabs zurück."""
        try:
            active_tab_name = self.tabview.get()
            current_tab_index = config.WOCHENTAGE.index(active_tab_name)
            return self.tages_widgets[current_tab_index]["taetigkeiten"]
        except (ValueError, IndexError):
            return None

    def select_next_tab(self):
        """Wählt den nächsten Tab aus."""
        try:
            current_index = self.tabview.index(self.tabview.get())
            next_index = (current_index + 1) % len(config.WOCHENTAGE)
            next_tab_name = config.WOCHENTAGE[next_index]
            self.tabview.set(next_tab_name)
        except Exception:
            self.tabview.set(config.WOCHENTAGE[0])

    def select_previous_tab(self):
        """Wählt den vorherigen Tab aus."""
        try:
            current_index = self.tabview.index(self.tabview.get())
            prev_index = (current_index - 1 + len(config.WOCHENTAGE)) % len(config.WOCHENTAGE)
            prev_tab_name = config.WOCHENTAGE[prev_index]
            self.tabview.set(prev_tab_name)
        except Exception:
            self.tabview.set(config.WOCHENTAGE[0])

