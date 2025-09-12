# gui/views/template_view.py
# -*- coding: utf-8 -*-
"""
Definiert die Ansicht zur Verwaltung von Textvorlagen.
"""
import customtkinter as ctk
from tkinter import messagebox
from typing import Optional
from ..widgets.accessible_widgets import AccessibleCTkButton, AccessibleCTkEntry
from core import config

class TemplateView(ctk.CTkFrame):
    """Ansicht zur Verwaltung und zum Einfügen von Textvorlagen."""
    
    def __init__(self, master, app_logic):
        super().__init__(master)
        self.app = app_logic
        self.data_manager = app_logic.data_manager
        
        self.templates: list[str] = []

        self._create_widgets()

    def on_show(self):
        """Lädt die Vorlagen, wenn die Ansicht angezeigt wird."""
        self.templates = self.data_manager.lade_vorlagen()
        self._populate_templates()

    def _save_templates(self):
        """Speichert die aktuelle Liste von Vorlagen."""
        self.data_manager.speichere_vorlagen(self.templates)

    def _create_widgets(self):
        """Erstellt die UI-Elemente der Ansicht."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        entry_frame = ctk.CTkFrame(self)
        entry_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        entry_frame.grid_columnconfigure(0, weight=1)

        self.template_entry = AccessibleCTkEntry(
            entry_frame, 
            placeholder_text="Neue Vorlage hier eingeben...",
            focus_color=config.FOCUS_COLOR,
            accessible_text="Eingabefeld für eine neue Textvorlage.",
            status_callback=self.app.update_status,
            speak_callback=self.app.speak
        )
        self.template_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.template_entry.bind("<Return>", lambda e: self._add_template()) # Hinzufügen mit Enter
        
        AccessibleCTkButton(
            entry_frame, 
            text="Hinzufügen", 
            width=100, 
            command=self._add_template,
            focus_color=config.FOCUS_COLOR,
            accessible_text="Fügt den Text aus dem Eingabefeld als neue Vorlage hinzu.",
            status_callback=self.app.update_status,
            speak_callback=self.app.speak
        ).grid(row=0, column=1)

        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Gespeicherte Vorlagen")
        self.scroll_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def _populate_templates(self):
        """Füllt die Scroll-Liste mit den gespeicherten Vorlagen."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        if not self.templates:
            ctk.CTkLabel(self.scroll_frame, text="Noch keine Vorlagen gespeichert.").pack(pady=10)
            return
            
        for template_text in self.templates:
            frame = ctk.CTkFrame(self.scroll_frame, border_width=2, border_color="transparent")
            frame.pack(fill="x", padx=5, pady=5)
            frame.grid_columnconfigure(0, weight=1)
            
            # Tastaturnavigation für den Frame
            frame.configure(takefocus=True)
            frame.bind("<FocusIn>", lambda e, f=frame: f.configure(border_color=config.FOCUS_COLOR))
            frame.bind("<FocusOut>", lambda e, f=frame: f.configure(border_color="transparent"))
            frame.bind("<Return>", lambda e, t=template_text: self._insert_template(t))
            frame.bind("<space>", lambda e, t=template_text: self._insert_template(t))
            frame.bind("<Delete>", lambda e, t=template_text: self._delete_template(t))
            
            ctk.CTkLabel(frame, text=template_text, wraplength=350, justify="left").grid(row=0, column=0, padx=10, pady=5, sticky="w")
            
            AccessibleCTkButton(
                frame, 
                text="Einfügen", 
                width=80, 
                command=lambda t=template_text: self._insert_template(t),
                focus_color=config.FOCUS_COLOR,
                accessible_text=f"Fügt die Vorlage '{template_text[:30]}...' in das aktive Textfeld ein.",
                status_callback=self.app.update_status,
                speak_callback=self.app.speak
            ).grid(row=0, column=1, padx=5, pady=5)
            AccessibleCTkButton(
                frame, 
                text="Löschen", 
                width=80, 
                fg_color=config.ERROR_COLOR, 
                hover_color=config.ERROR_HOVER_COLOR,
                focus_color=config.FOCUS_COLOR,
                command=lambda t=template_text: self._delete_template(t),
                accessible_text=f"Löscht die Vorlage '{template_text[:30]}...'.",
                status_callback=self.app.update_status,
                speak_callback=self.app.speak
            ).grid(row=0, column=2, padx=5, pady=5)

    def _add_template(self):
        """Fügt eine neue Vorlage hinzu."""
        new_template = self.template_entry.get().strip()
        if new_template and new_template not in self.templates:
            self.templates.append(new_template)
            self._save_templates()
            self._populate_templates()
            self.template_entry.delete(0, "end")
            self.app.speak(f"Vorlage '{new_template[:30]}...' hinzugefügt.")
        elif not new_template:
            messagebox.showwarning("Leere Vorlage", "Die Vorlage darf nicht leer sein.")
        else:
            messagebox.showinfo("Vorlage existiert", "Diese Vorlage ist bereits gespeichert.")

    def _delete_template(self, template_to_delete: str):
        """Löscht eine ausgewählte Vorlage."""
        if messagebox.askyesno("Löschen bestätigen", f"Möchtest du die Vorlage wirklich löschen?\n\n'{template_to_delete}'"):
            self.templates.remove(template_to_delete)
            self._save_templates()
            self._populate_templates()
            self.app.speak(f"Vorlage '{template_to_delete[:30]}...' gelöscht.")

    def _insert_template(self, template_text: str):
        """Fügt den Text in das aktive Textfeld der Berichtsheft-Ansicht ein."""
        berichtsheft_view = self.app.get_berichtsheft_view_reference()
        active_textbox: Optional[ctk.CTkTextbox] = berichtsheft_view.get_active_textbox()
        
        if active_textbox:
            active_textbox.insert("insert", template_text)
            self.app.show_view("berichtsheft")
            self.app.speak(f"Vorlage '{template_text[:30]}...' eingefügt.")
        else:
            messagebox.showwarning("Fehler", "Konnte kein aktives Textfeld finden. Bitte wählen Sie einen Tag im Berichtsheft-Tab aus.")

