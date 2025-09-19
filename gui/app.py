# gui/app.py
# -*- coding: utf-8 -*-
"""
Die Hauptklasse der Berichtsheft-Generator-Anwendung.
Dient als Controller, der die Ansichten verwaltet und die Hauptlogik bereitstellt.
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional
import logging
import os
import sys
import subprocess
import threading
import webbrowser
try:
    from PIL import Image
except ImportError:
    Image = None

try:
    from accessible_output2 import outputs
    ACCESSIBLE_OUTPUT_AVAILABLE = True
except ImportError:
    outputs = None
    ACCESSIBLE_OUTPUT_AVAILABLE = False


from core import config
from core.data_manager import DataManager
from core.controller import AppController
from core.logic import BerichtsheftLogik

from gui.views.berichtsheft_view import BerichtsheftView
from gui.views.dashboard_view import DashboardView
from gui.views.load_report_view import LoadReportView
from gui.views.template_view import TemplateView
from gui.views.statistics_view import StatisticsView
from gui.views.backup_view import BackupView
from gui.views.import_view import ImportView
from gui.views.settings_view import SettingsView
from .widgets.accessible_widgets import AccessibleCTkButton, AccessibleCTkSwitch
from services.update_service import UpdateService
from .widgets.custom_dialogs import CustomMessagebox


logger = logging.getLogger(__name__)

class BerichtsheftApp(ctk.CTk):
    """
    Die Hauptklasse der Berichtsheft-Generator-Anwendung.
    Verwaltet die verschiedenen Ansichten und die Interaktionen.
    """
    def __init__(self) -> None:
        super().__init__()
        
        # --- KORREKTUR: Schriftarten initialisieren, nachdem das Hauptfenster existiert ---
        config.initialize_fonts()

        self.data_manager = DataManager()
        self.controller = AppController(self.data_manager)
        self.logic = BerichtsheftLogik()
        
        self.speaker = self._initialize_speaker()
        self.screen_reader_active = self.speaker is not None
        
        self.logo_image: Optional[ctk.CTkImage] = None
        self.views: Dict[str, ctk.CTkFrame] = {}
        self.sidebar_buttons: Dict[str, ctk.CTkButton] = {}

        self._setup_window()
        self._create_main_layout()
        self._create_and_register_views()
        self._setup_shortcuts()
        
        self.show_view("berichtsheft")
        
        self.after(500, self._welcome_message)
        self.after(1500, self._start_update_check)
        
        logger.info("GUI erfolgreich initialisiert.")

    def _initialize_speaker(self) -> Optional[Any]:
        """
        Prüft plattformunabhängig, ob ein Screenreader aktiv ist.
        """
        if not ACCESSIBLE_OUTPUT_AVAILABLE:
            logging.info("Bibliothek 'accessible_output2' nicht verfügbar. Sprachausgabe deaktiviert.")
            return None
        
        try:
            # Versucht, den ersten verfügbaren und aktiven Screenreader zu finden.
            try:
                speaker = outputs.nvda.NVDA()
                speaker == outputs.jaws.Jaws()
            except NameError as e:
                logging.info(e + " konnte nicht gefnden werden!")
                
            if speaker.is_active():
                logging.info(f"Aktiver Screenreader '{speaker.name}' erkannt. Sprachausgabe wird aktiviert.")
                return speaker
            else:
                logging.info("Kein aktiver Screenreader gefunden. Sprachausgabe bleibt deaktiviert.")
                return None
        except Exception as e:
            logging.warning(f"Fehler bei der Initialisierung des Screenreaders: {e}")
            return None

    def _welcome_message(self):
        """Gibt eine Willkommensnachricht aus, falls ein Screenreader aktiv ist."""
        self.update_status("Bereit.")
        self.speak(f"Willkommen beim {config.APP_NAME}, Version {config.VERSION}.")


    def _setup_window(self) -> None:
        """Konfiguriert das Hauptfenster."""
        self.title(f"{config.APP_NAME} {config.VERSION}")
        
        # --- NEU: Anwendung im Vollbildmodus starten ---
        if sys.platform == "win32":
            self.state('zoomed')
        else:
            self.attributes('-zoomed', True)
            
        self.minsize(1200, 800)
        
        # --- VERBESSERUNG: Plattformabhängiges Icon-Handling ---
        # .ico wird nur unter Windows zuverlässig unterstützt.
        if sys.platform == "win32" and os.path.exists(config.ICON_DATEI):
            try:
                self.iconbitmap(config.ICON_DATEI)
            except tk.TclError:
                logger.warning("Konnte .ico-Datei nicht laden. Überspringe.")

        ctk.set_appearance_mode("dark")
        self.protocol("WM_DELETE_WINDOW", self.quit)

    def _create_main_layout(self) -> None:
        """Erstellt das grundlegende Layout mit Seitenleiste und Inhaltsbereich."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.status_bar_frame = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.status_bar_frame.grid(row=1, column=0, columnspan=2, sticky="sew")
        self.status_bar = ctk.CTkLabel(self.status_bar_frame, text="", anchor="w", font=config.FONT_NORMAL)
        self.status_bar.pack(side="left", padx=10, pady=2)
        self.progress_bar = ctk.CTkProgressBar(self.status_bar_frame, indeterminate_speed=1.2)
        
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=config.SIDEBAR_BG_COLOR)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsw")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)
        self._create_sidebar_widgets()

        self.view_container = ctk.CTkFrame(self, fg_color=config.FRAME_BG_COLOR)
        self.view_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.view_container.grid_columnconfigure(0, weight=1)
        self.view_container.grid_rowconfigure(0, weight=1)

    def _create_sidebar_widgets(self) -> None:
        """Füllt die Seitenleiste mit Logo, Titel und Navigations-Buttons."""
        if Image and os.path.exists(config.LOGO_DATEI):
            self.logo_image = ctk.CTkImage(Image.open(config.LOGO_DATEI), size=(35, 35))
            ctk.CTkLabel(self.sidebar_frame, image=self.logo_image, text=config.APP_NAME, font=ctk.CTkFont(size=24, weight="bold"), compound="left", padx=20).grid(row=0, column=0, padx=20, pady=25)
        
        buttons_to_create = {
            "berichtsheft": ("Berichtsheft (Strg+1)", "Öffnet die Ansicht zum Erstellen und Bearbeiten von Berichten"),
            "dashboard": ("Dashboard (Strg+2)", "Zeigt eine Zusammenfassung der aktuellen Woche"),
            "load_report": ("Bericht laden (Strg+3)", "Öffnet die Ansicht zum Laden eines gespeicherten Berichts"),
            "import": ("Berichte importieren (Strg+4)", "Öffnet die Ansicht zum Importieren von Word-Dateien"),
            "templates": ("Vorlagen (Strg+5)", "Öffnet die Vorlagenverwaltung"),
            "statistics": ("Statistiken (Strg+6)", "Zeigt Statistiken über alle Berichte an"),
            "backup": ("Backup (Strg+7)", "Öffnet die Ansicht für Datensicherung und Wiederherstellung"),
            "settings": ("Einstellungen (Strg+8)", "Öffnet die Anwendungseinstellungen")
        }

        for i, (view_name, (text, acc_text)) in enumerate(buttons_to_create.items()):
            button = AccessibleCTkButton(self.sidebar_frame, text=text, command=lambda v=view_name: self.show_view(v), 
                                         anchor="w", font=config.FONT_SIDEBAR, fg_color=config.SIDEBAR_BUTTON_INACTIVE_COLOR, 
                                         hover_color=config.HOVER_COLOR,
                                         focus_color=config.FOCUS_COLOR,
                                         height=40,
                                         accessible_text=acc_text, status_callback=self.update_status, speak_callback=self.speak)
            button.grid(row=i + 1, column=0, padx=20, pady=12, sticky="ew")
            self.sidebar_buttons[view_name] = button
        
        bottom_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        bottom_frame.grid(row=8, column=0, padx=20, pady=20, sticky="s")
        
        AccessibleCTkButton(bottom_frame, text="Ordner öffnen", command=self._open_output_folder,
                              font=config.FONT_NORMAL,
                              focus_color=config.FOCUS_COLOR,
                              accessible_text="Öffnet den Ordner mit den erstellten Berichten", 
                              status_callback=self.update_status, speak_callback=self.speak).pack(pady=10)
        
        AccessibleCTkSwitch(bottom_frame, text="Light Mode", command=self._toggle_theme,
                            font=config.FONT_NORMAL,
                            accessible_text="Schaltet zwischen hellem und dunklem Design um",
                            status_callback=self.update_status, speak_callback=self.speak).pack()

    def _create_and_register_views(self) -> None:
        """Erstellt Instanzen aller Ansichten und speichert sie in einem Dictionary."""
        self.views = {
            "berichtsheft": BerichtsheftView(self.view_container, self),
            "dashboard": DashboardView(self.view_container, self),
            "load_report": LoadReportView(self.view_container, self),
            "import": ImportView(self.view_container, self), 
            "templates": TemplateView(self.view_container, self),
            "statistics": StatisticsView(self.view_container, self),
            "backup": BackupView(self.view_container, self),
            "settings": SettingsView(self.view_container, self),
        }
        
    def show_view(self, view_name: str) -> None:
        """Blendet die aktuelle Ansicht aus und zeigt die ausgewählte an."""
        for name, button in self.sidebar_buttons.items():
            button.configure(fg_color=config.ACCENT_COLOR if name == view_name else config.SIDEBAR_BUTTON_INACTIVE_COLOR)
        
        for view in self.views.values():
            view.grid_forget()
        
        view_to_show = self.views.get(view_name)
        if view_to_show:
            if hasattr(view_to_show, 'on_show'):
                view_to_show.on_show()
            
            view_to_show.grid(row=0, column=0, sticky="nsew")
            readable_name = view_name.replace('_', ' ').title()
            self.update_status(f"Ansicht '{readable_name}' geladen.")
            self.speak(f"Ansicht {readable_name}")
        else:
            self.update_status(f"Fehler: Ansicht '{view_name}' nicht gefunden.")
            logger.error(f"Versuch, eine nicht existierende Ansicht anzuzeigen: {view_name}")

    def update_status(self, message: str) -> None:
        """Aktualisiert den Text in der Statusleiste."""
        self.status_bar.configure(text=message)

    def speak(self, message: str, interrupt: bool = True) -> None:
        """Sendet eine Nachricht an den Screenreader, falls einer aktiv ist."""
        if self.screen_reader_active and self.speaker:
            try:
                self.speaker.speak(message, interrupt=interrupt)
            except Exception as e:
                logging.warning(f"Fehler bei der Sprachausgabe: {e}")

    def _toggle_theme(self) -> None:
        """Wechselt zwischen Light- und Dark-Mode."""
        new_mode = "light" if ctk.get_appearance_mode() == "Dark" else "dark"
        ctk.set_appearance_mode(new_mode)
        if "statistics" in self.views and self.views["statistics"].winfo_viewable():
            self.views["statistics"].on_show()

    def _open_output_folder(self) -> None:
        """Öffnet den Ausgabeordner im Dateimanager des Betriebssystems."""
        folder_path = config.AUSGABE_ORDNER
        try:
            os.makedirs(folder_path, exist_ok=True)
            
            if sys.platform == "win32":
                os.startfile(os.path.realpath(folder_path))
            elif sys.platform == "darwin":
                subprocess.run(["open", folder_path], check=True)
            else: # Linux und andere
                subprocess.run(["xdg-open", folder_path], check=True)

            self.update_status(f"Ordner '{folder_path}' geöffnet.")
        except (OSError, subprocess.SubprocessError, FileNotFoundError) as e:
            messagebox.showerror("Fehler", f"Der Ordner '{folder_path}' konnte nicht geöffnet werden:\n{e}")
            logger.error(f"Fehler beim Öffnen des Ausgabeordners: {e}", exc_info=True)

    def speichere_persoenliche_daten(self, name: str, startdatum: str):
        """Speichert Name und Startdatum aus der Einstellungs- oder Berichtsheftansicht."""
        konfig = self.data_manager.lade_konfiguration()
        konfig["name_azubi"] = name
        konfig["startdatum_ausbildung"] = startdatum
        if self.data_manager.speichere_konfiguration(konfig):
            self.update_status("Persönliche Daten gespeichert.")
        else:
            self.update_status("Fehler beim Speichern der persönlichen Daten.")

    def speichere_einstellungen(self, neue_einstellungen: Dict[str, Any]):
        """Speichert die allgemeinen Einstellungen aus der SettingsView."""
        konfig = self.data_manager.lade_konfiguration()
        konfig["einstellungen"] = neue_einstellungen
        if self.data_manager.speichere_konfiguration(konfig):
            self.update_status("Einstellungen erfolgreich gespeichert.")
            messagebox.showinfo("Gespeichert", "Die Einstellungen wurden erfolgreich gespeichert.")
            if "berichtsheft" in self.views:
                 self.views["berichtsheft"].on_show()
        else:
            self.update_status("Fehler beim Speichern der Einstellungen.")
            messagebox.showerror("Fehler", "Die Einstellungen konnten nicht gespeichert werden.")

    def sammle_daten_fuer_bericht(self) -> Optional[Dict[str, Any]]:
        """Sammelt und validiert alle Daten für die Berichtserstellung."""
        berichtsheft_view = self.views["berichtsheft"]
        context = {}
        try:
            # Daten direkt aus der Konfigurationsdatei laden
            konfig = self.data_manager.lade_konfiguration()
            context["name_azubi"] = konfig.get("name_azubi", "")
            startdatum_str = konfig.get("startdatum_ausbildung", "")
            
            if not context["name_azubi"] or not self.logic.valide_datumsformat(startdatum_str):
                messagebox.showerror("Fehlende Daten", "Bitte zuerst Name und Startdatum in den Einstellungen festlegen.")
                self.show_view("settings")
                return None
            
            try:
                context["fortlaufende_nr"] = int(berichtsheft_view.nummer_var.get())
                context["jahr"] = int(berichtsheft_view.jahr_var.get())
                context["kalenderwoche"] = int(berichtsheft_view.kw_var.get())
            except ValueError:
                messagebox.showerror("Eingabefehler", "Bitte eine gültige Zahl für 'Bericht Nr.', 'Jahr' und 'KW' eingeben.")
                return None
            
            context["startdatum_ausbildung_dt"] = datetime.strptime(startdatum_str, "%d.%m.%Y").date()
            start_datum_kw = date.fromisocalendar(context["jahr"], context["kalenderwoche"], 1)
            context["zeitraum_von"] = start_datum_kw.strftime("%d.%m.%Y")
            context["zeitraum_bis"] = (start_datum_kw + timedelta(days=4)).strftime("%d.%m.%Y")
            
            tage_daten = []
            for widgets in berichtsheft_view.tages_widgets:
                typ = widgets["typ"].get()
                taetigkeiten = widgets["taetigkeiten"].get("1.0", "end-1c").strip()
                if typ in ["Urlaub", "Krank", "Feiertag"] and not taetigkeiten:
                    taetigkeiten = "-"
                tage_daten.append({"typ": typ, "stunden": widgets["stunden"].get(), "taetigkeiten": taetigkeiten})
            context["tage_daten"] = tage_daten
            # --- ÄNDERUNG: Das Datum für die Unterschrift ist immer der Freitag der Woche. ---
            context["erstellungsdatum_bericht"] = context["zeitraum_bis"]
            return context
        except (ValueError, TypeError) as e:
            messagebox.showerror("Eingabefehler", str(e))
            logger.warning(f"Validierungsfehler bei der Berichtserstellung: {e}")
            return None

    def erstelle_bericht(self, event: Any = None) -> str:
        """Startet den Prozess der Berichtserstellung."""
        if self.progress_bar.winfo_ismapped():
            self.update_status("Berichtserstellung läuft bereits.")
            return "break"

        berichtsheft_view = self.views["berichtsheft"]
        berichtsheft_view.create_report_button.configure(state="disabled")
        self.progress_bar.pack(side="right", padx=10, pady=2, fill="x", expand=True)
        self.progress_bar.start()
        
        context = self.sammle_daten_fuer_bericht()
        if context:
            gewaehltes_format = berichtsheft_view.format_var.get()
            self.update_status(f"Erstelle {gewaehltes_format.upper()}-Datei...")
            self.after(100, lambda: self._run_generation(context, gewaehltes_format))
        else:
            self._generation_complete()
        return "break"

    def _run_generation(self, context: Dict[str, Any], gewaehltes_format: str) -> None:
        """Führt die eigentliche Generierung im Controller aus."""
        erfolg, nachricht = self.controller.erstelle_bericht(context, gewaehltes_format)
        if erfolg:
            self.update_status(nachricht)
            self.views["berichtsheft"].on_show()
            self.clear_and_prepare_next_report()
        else:
            messagebox.showerror("Fehler", nachricht)
        self._generation_complete()
        
    def _generation_complete(self) -> None:
        """Setzt die UI nach der Berichtserstellung zurück."""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        berichtsheft_view = self.views.get("berichtsheft")
        if berichtsheft_view:
            berichtsheft_view.create_report_button.configure(state="normal")
            self.update_status("Bereit.")

    def clear_and_prepare_next_report(self):
        """Leert die Felder und bereitet den nächsten Bericht vor."""
        berichtsheft_view = self.views["berichtsheft"]
        
        # Felder leeren und Zeiten zurücksetzen
        for widgets in berichtsheft_view.tages_widgets:
            widgets["taetigkeiten"].delete("1.0", "end")
        
        # Datum und Nummer fortschreiben
        current_date = berichtsheft_view.kalender.get_date()
        next_week = current_date + timedelta(weeks=1)
        berichtsheft_view.kalender.set_date(next_week)
        
        current_number = int(berichtsheft_view.nummer_var.get())
        berichtsheft_view.nummer_var.set(str(current_number + 1))
        
        self.update_status("Bereit für den nächsten Bericht.")

    def _setup_shortcuts(self) -> None:
        """Definiert globale Tastenkürzel."""
        self.bind("<Control-g>", self.erstelle_bericht)
        
        view_keys = ["1", "2", "3", "4", "5", "6", "7", "8"]
        view_names = list(self.sidebar_buttons.keys())
        for i, key in enumerate(view_keys):
            if i < len(view_names):
                self.bind(f"<Control-KeyPress-{key}>", lambda event, v=view_names[i]: self.show_view(v))
        
        self.bind("<Control-o>", lambda event: self._open_output_folder())

        self.bind("<Control-Tab>", self.select_next_tab)
        self.bind("<Control-Shift-Tab>", self.select_previous_tab)

    def select_next_tab(self, event: Any = None) -> str:
        """Wählt den nächsten Tab in der Berichtsheft-Ansicht aus."""
        view = self.views.get("berichtsheft")
        if view and isinstance(view, BerichtsheftView):
            view.select_next_tab()
            self.speak(f"Tab {view.tabview.get()} ausgewählt")
        return "break"

    def select_previous_tab(self, event: Any = None) -> str:
        """Wählt den vorherigen Tab in der Berichtsheft-Ansicht aus."""
        view = self.views.get("berichtsheft")
        if view and isinstance(view, BerichtsheftView):
            view.select_previous_tab()
            self.speak(f"Tab {view.tabview.get()} ausgewählt")
        return "break"

    def _start_update_check(self) -> None:
        """Startet die Update-Prüfung in einem separaten Thread."""
        update_thread = threading.Thread(target=self._run_update_check, daemon=True)
        update_thread.start()

    def _run_update_check(self) -> None:
        """Führt die eigentliche Update-Prüfung durch."""
        update_service = UpdateService()
        update_info = update_service.check_for_updates()
        if update_info:
            self.after(0, self._show_update_notification, update_info)

    def _show_update_notification(self, update_info: Dict[str, str]) -> None:
        """Zeigt ein Dialogfenster an, wenn ein Update verfügbar ist."""
        version = update_info.get("version")
        url = update_info.get("url")

        dialog = CustomMessagebox(
            title="Update verfügbar",
            message=f"Eine neue Version ({version}) ist verfügbar!\n\nMöchten Sie die Download-Seite jetzt öffnen?",
            buttons=["Ja, herunterladen", "Später"]
        )
        choice = dialog.get_choice()

        if choice == "Ja, herunterladen" and url:
            webbrowser.open(url)
            self.update_status(f"Download-Seite für Version {version} geöffnet.")

    def get_berichtsheft_view_reference(self) -> 'BerichtsheftView':
        """Gibt eine Referenz auf die Berichtsheft-Ansicht zurück."""
        return self.views["berichtsheft"]

    def reload_all_data(self) -> None:
        """Lädt alle Daten neu und aktualisiert die Ansichten."""
        self.update_status("Lade neue Daten...")
        self.get_berichtsheft_view_reference().on_show()
        
        for view_name, view in self.views.items():
            if view.winfo_viewable() and hasattr(view, 'on_show') and view_name != "import":
                view.on_show()
        
        self.show_view("berichtsheft")
        self.update_status("Daten erfolgreich neu geladen.")

