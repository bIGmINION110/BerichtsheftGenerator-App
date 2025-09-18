# gui/widgets/accessible_widgets.py
# -*- coding: utf-8 -*-
"""
Definiert barrierefreie CustomTkinter-Widgets.
"""

import customtkinter as ctk
import tkinter as tk
from typing import Callable, Any, Optional
from datetime import datetime, timedelta

# HINWEIS: Der direkte Import von 'accessible_output2' wird hier entfernt.
# Die Sprachausgabe wird zentral über die Hauptanwendung gesteuert.

class AccessibleBase:
    """Basisklasse, um Barrierefreiheitsfunktionen zu teilen."""
    def _initialize_accessibility(self, accessible_text: str, status_callback: Callable[[str], None], speak_callback: Callable[[str, bool], None]):
        """Initialisiert die Bindings für die Barrierefreiheit."""
        self.accessible_text = accessible_text
        self.status_callback = status_callback
        self.speak_callback = speak_callback
        self.bind("<Enter>", self._update_status_bar)
        self.bind("<FocusIn>", self._speak_and_update_status)

    def _update_status_bar(self, event: Any = None):
        """Aktualisiert nur die Statusleiste (für Maus-Hover)."""
        if self.accessible_text and self.status_callback:
            self.status_callback(self.accessible_text)

    def _speak_and_update_status(self, event: Any = None):
        """Spricht den Text und aktualisiert die Statusleiste (für Fokus)."""
        self._update_status_bar()
        if self.accessible_text and self.speak_callback:
            self.speak_callback(self.accessible_text, interrupt=True)

class AccessibleCTkEntry(ctk.CTkEntry, AccessibleBase):
    """
    Eine erweiterte CTkEntry-Klasse, die eine Beschreibung und den Inhalt vorliest
    und eine Pfeiltastennavigation für Zahlen und Zeiten ermöglicht.
    """
    def __init__(self, master: Any, accessible_text: str, status_callback: Callable[[str], None], speak_callback: Callable[[str, bool], None], navigation_mode: Optional[str] = None, **kwargs):
        focus_color = kwargs.pop("focus_color", None)
        super().__init__(master, **kwargs)
        self._initialize_accessibility(accessible_text, status_callback, speak_callback)
        self.bind("<FocusIn>", self._on_get_focus_custom, add="+")
        self.bind("<KeyRelease-Left>", self._speak_current_char)
        self.bind("<KeyRelease-Right>", self._speak_current_char)
        self.bind("<Control-BackSpace>", self._delete_word_backwards)

        if focus_color:
            self._focus_color = focus_color
            self._original_border_width = self.cget("border_width")
            self._original_border_color = self.cget("border_color")
            self.bind("<FocusIn>", self._on_get_focus_border, add="+")
            self.bind("<FocusOut>", self._on_lose_focus_border, add="+")
            
        self.navigation_mode = navigation_mode
        if self.navigation_mode:
            self.bind("<Up>", self._handle_arrow_navigation)
            self.bind("<Down>", self._handle_arrow_navigation)
            self.configure(state="readonly") # Nur bei Navigationsmodus auf readonly setzen

    def _handle_arrow_navigation(self, event: Any):
        """Verarbeitet die Pfeiltasten-Navigation basierend auf dem Modus."""
        if not self.navigation_mode:
            return

        direction = 1 if event.keysym == "Up" else -1
        
        self.configure(state="normal")
        if self.navigation_mode == 'numeric':
            self._navigate_numeric(direction)
        elif self.navigation_mode == 'time':
            self._navigate_time(direction)
        self.configure(state="readonly")
            
        return "break" # Verhindert die standardmäßige Cursor-Bewegung

    def _navigate_numeric(self, direction: int):
        """Erhöht oder verringert einen numerischen Wert."""
        try:
            current_value = int(self.get())
            new_value = current_value + direction
            if new_value < 1:
                new_value = 1
            self.delete(0, "end")
            self.insert(0, str(new_value))
            if self.speak_callback:
                self.speak_callback(str(new_value), interrupt=True)
        except ValueError:
            self.delete(0, "end")
            self.insert(0, "1")
            if self.speak_callback:
                self.speak_callback("1", interrupt=True)

    def _navigate_time(self, direction: int):
        """Erhöht oder verringert die Zeit um 15 Minuten."""
        try:
            h, m = map(int, self.get().split(':'))
            total_minutes = h * 60 + m
            total_minutes += direction * 15
            total_minutes %= (24 * 60) # Umbruch nach 24 Stunden
            
            new_h = total_minutes // 60
            new_m = total_minutes % 60
            new_time_str = f"{new_h:02d}:{new_m:02d}"
            
            self.delete(0, "end")
            self.insert(0, new_time_str)
            if self.speak_callback:
                self.speak_callback(new_time_str, interrupt=True)
        except (ValueError, IndexError):
            default_time = "08:00"
            self.delete(0, "end")
            self.insert(0, default_time)
            if self.speak_callback:
                self.speak_callback(default_time, interrupt=True)

    def _on_get_focus_custom(self, event: Any = None):
        content = self.get()
        if content and self.speak_callback:
            self.after(200, lambda: self.speak_callback(f"Inhalt: {content}", interrupt=False))

    def _delete_word_backwards(self, event: Any = None) -> str:
        if not self.speak_callback:
            return "break"
        try:
            cursor_pos = self.index(tk.INSERT)
            line_content = self.get()
            text_before_cursor = line_content[:cursor_pos]
            words = text_before_cursor.split()
            if not words:
                return "break"
            word_to_delete = words[-1]
            word_start_index = text_before_cursor.rfind(word_to_delete)
            self.delete(word_start_index, cursor_pos)
            self.speak_callback(f"{word_to_delete}", interrupt=True)
        except tk.TclError:
            pass
        return "break"

    def _speak_current_char(self, event: Any = None):
        if not self.speak_callback:
            return
        try:
            cursor_pos = self.index(tk.INSERT)
            if event and event.keysym == 'Left':
                char = self.get()[cursor_pos - 1] if cursor_pos > 0 else None
            else:
                char = self.get()[cursor_pos] if cursor_pos < len(self.get()) else None

            if char and not char.isspace():
                self.speak_callback(char, interrupt=True)
            elif char and char.isspace():
                self.speak_callback("Leerzeichen", interrupt=True)
        except (tk.TclError, IndexError):
            pass
            
    def _on_get_focus_border(self, event: Any = None):
        self.configure(border_width=2, border_color=self._focus_color)

    def _on_lose_focus_border(self, event: Any = None):
        self.configure(border_width=self._original_border_width, border_color=self._original_border_color)

class AccessibleCTkButton(ctk.CTkButton, AccessibleBase):
    """Erweiterter CTkButton mit Barrierefreiheitsfunktionen."""
    def __init__(self, master: Any, accessible_text: str, status_callback: Callable[[str], None], speak_callback: Callable[[str, bool], None], **kwargs):
        focus_color = kwargs.pop("focus_color", None)
        super().__init__(master, **kwargs)
        self._initialize_accessibility(accessible_text, status_callback, speak_callback)
        
        if focus_color:
            self._focus_color = focus_color
            self._original_border_width = self.cget("border_width")
            self._original_border_color = self.cget("border_color")
            self.bind("<FocusIn>", self._on_get_focus_border, add="+")
            self.bind("<FocusOut>", self._on_lose_focus_border, add="+")

        self.bind("<Return>", self._on_action_key)
        self.bind("<space>", self._on_action_key)
    
    def _on_action_key(self, event: Any = None):
        self.invoke()
        
    def _on_get_focus_border(self, event: Any = None):
        self.configure(border_width=2, border_color=self._focus_color)

    def _on_lose_focus_border(self, event: Any = None):
        self.configure(border_width=self._original_border_width, border_color=self._original_border_color)
        
class AccessibleCTkComboBox(ctk.CTkComboBox, AccessibleBase):
    """Erweiterter CTkComboBox mit Pfeiltasten-Navigation durch die Optionen."""
    def __init__(self, master: Any, accessible_text: str, status_callback: Callable[[str], None], speak_callback: Callable[[str, bool], None], **kwargs):
        focus_color = kwargs.pop("focus_color", None)
        super().__init__(master, **kwargs)
        self._initialize_accessibility(accessible_text, status_callback, speak_callback)
        
        self.bind("<FocusIn>", self._on_get_focus_custom, add="+")
        
        if focus_color:
            self._focus_color = focus_color
            self._original_border_width = self.cget("border_width")
            self._original_border_color = self.cget("border_color")
            self.bind("<FocusIn>", self._on_get_focus_border, add="+")
            self.bind("<FocusOut>", self._on_lose_focus_border, add="+")
            
        self.bind("<Up>", self._navigate_options)
        self.bind("<Down>", self._navigate_options)

    def _navigate_options(self, event: Any):
        """Schaltet mit den Pfeiltasten durch die verfügbaren Werte."""
        if not self._values:
            return "break"

        try:
            current_index = self._values.index(self.get())
        except ValueError:
            current_index = -1 

        direction = -1 if event.keysym == "Up" else 1
        new_index = (current_index + direction) % len(self._values)
        
        new_value = self._values[new_index]
        self.set(new_value)
        
        if self._command:
            self._command(new_value)
            
        if self.speak_callback:
            self.speak_callback(new_value, interrupt=True)
            
        return "break"

    def _on_get_focus_custom(self, event: Any = None):
        content = self.get()
        if content and self.speak_callback:
            self.after(200, lambda: self.speak_callback(f"Ausgewählt: {content}", interrupt=False))
            
    def _on_get_focus_border(self, event: Any = None):
        self.configure(border_width=2, border_color=self._focus_color)

    def _on_lose_focus_border(self, event: Any = None):
        self.configure(border_width=self._original_border_width, border_color=self._original_border_color)

class AccessibleCTkRadioButton(ctk.CTkRadioButton, AccessibleBase):
    """Erweiterter CTkRadioButton mit Barrierefreiheitsfunktionen."""
    def __init__(self, master: Any, accessible_text: str, status_callback: Callable[[str], None], speak_callback: Callable[[str, bool], None], **kwargs):
        focus_color = kwargs.pop("focus_color", None)
        super().__init__(master, **kwargs)
        self._initialize_accessibility(accessible_text, status_callback, speak_callback)

        if focus_color:
            self._focus_color = focus_color
            self._original_text_color = self.cget("text_color")
            self._original_fg_color = self.cget("fg_color")
            
            self.bind("<FocusIn>", self._on_get_focus_highlight, add="+")
            self.bind("<FocusOut>", self._on_lose_focus_highlight, add="+")
    
    def _on_get_focus_highlight(self, event: Any = None):
        self.configure(fg_color=self._focus_color)

    def _on_lose_focus_highlight(self, event: Any = None):
        self.configure(fg_color=self._original_fg_color)


class AccessibleCTkSwitch(ctk.CTkSwitch, AccessibleBase):
    """Erweiterter CTkSwitch mit Barrierefreiheitsfunktionen."""
    def __init__(self, master: Any, accessible_text: str, status_callback: Callable[[str], None], speak_callback: Callable[[str, bool], None], **kwargs):
        kwargs.pop("focus_color", None)
        super().__init__(master, **kwargs)
        self._initialize_accessibility(accessible_text, status_callback, speak_callback)
        self.bind("<Return>", self._on_action_key)
        self.bind("<space>", self._on_action_key)

    def _on_action_key(self, event: Any = None):
        self.toggle()
        

class AccessibleCTkTextbox(ctk.CTkTextbox, AccessibleBase):
    """Erweiterte CTkTextbox, die die aktuelle Zeile für Screenreader vorliest."""
    def __init__(self, master: Any, accessible_text: str, status_callback: Callable[[str], None], speak_callback: Callable[[str, bool], None], **kwargs):
        focus_color = kwargs.pop("focus_color", None)
        super().__init__(master, **kwargs)
        self._initialize_accessibility(accessible_text, status_callback, speak_callback)
        self.bind("<FocusIn>", self._on_textbox_focus_in, add="+")
        self.bind("<KeyRelease-Up>", self._speak_current_line)
        self.bind("<KeyRelease-Down>", self._speak_current_line)
        self.bind("<KeyRelease-Left>", self._speak_current_char)
        self.bind("<KeyRelease-Right>", self._speak_current_char)
        self.bind("<Control-BackSpace>", self._delete_word_backwards)

        if focus_color:
            self._focus_color = focus_color
            self._original_border_width = self.cget("border_width")
            self._original_border_color = self.cget("border_color")
            self.bind("<FocusIn>", self._on_get_focus_border, add="+")
            self.bind("<FocusOut>", self._on_lose_focus_border, add="+")

    def _on_textbox_focus_in(self, event: Any = None):
        self._speak_and_update_status(event)
        self.after(200, self._speak_current_line)

    def _delete_word_backwards(self, event: Any = None) -> str:
        if not self.speak_callback:
            return "break"
        try:
            cursor_index = self.index(tk.INSERT)
            line_start = self.index(f"{cursor_index} linestart")
            line_content = self.get(line_start, cursor_index)
            
            words = line_content.split()
            if not words:
                return "break" 
            
            word_to_delete = words[-1]
            word_start_index = line_content.rfind(word_to_delete)
            
            delete_start_index = f"{cursor_index.split('.')[0]}.{word_start_index}"
            
            self.delete(delete_start_index, cursor_index)
            self.speak_callback(f"{word_to_delete}", interrupt=True)
            
        except tk.TclError:
            pass 
        
        return "break" 

    def _speak_current_line(self, event: Any = None):
        if not self.speak_callback:
            return
            
        try:
            line_index = self.index(tk.INSERT).split('.')[0]
            line_content = self.get(f"{line_index}.0", f"{line_index}.end").strip()
            
            if line_content:
                self.speak_callback(line_content, interrupt=True)
            else:
                self.speak_callback("Leere Zeile", interrupt=True)
        except tk.TclError:
            pass

    def _speak_current_char(self, event: Any = None):
        if not self.speak_callback:
            return
        
        try:
            if event and event.keysym == 'Left':
                char = self.get(f"{tk.INSERT}-1c")
            else:
                char = self.get(tk.INSERT)
                
            if char and not char.isspace():
                self.speak_callback(char, interrupt=True)
            elif char and char.isspace():
                self.speak_callback("Leerzeichen", interrupt=True)

        except tk.TclError:
            pass
            
    def _on_get_focus_border(self, event: Any = None):
        self.configure(border_width=2, border_color=self._focus_color)

    def _on_lose_focus_border(self, event: Any = None):
        self.configure(border_width=self._original_border_width, border_color=self._original_border_color)
        