# gui/animation_manager.py
# -*- coding: utf-8 -*-
"""
Eine zentrale Klasse zur Verwaltung von UI-Animationen in der Anwendung.
"""
import math
import customtkinter as ctk
import tkinter as tk
from typing import Callable, Iterable, List, Tuple, Optional

from . import easing_functions as easing


def _interpolate_color(color1: str, color2: str, fraction: float) -> str:
    """Interpoliert zwischen zwei Hex-Farben."""
    try:
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        r = int(r1 + (r2 - r1) * fraction)
        g = int(g1 + (g2 - g1) * fraction)
        b = int(b1 + (b2 - b1) * fraction)
        return f"#{r:02x}{g:02x}{b:02x}"
    except (ValueError, IndexError):
        # Fallback, wenn die Farben kein gültiges Hex-Format haben
        return color2


class AnimationManager:
    """Kapselt die Logik für Fenster- und Widget-Animationen."""

    def __init__(self, app_instance: ctk.CTk):
        """
        Initialisiert den Manager mit einer Referenz auf das Hauptfenster.

        Args:
            app_instance: Die Instanz der Hauptanwendung (BerichtsheftApp).
        """
        self.app = app_instance
        # Fullscreen-bezogene Attribute
        self.is_fullscreen = False
        self.original_geometry = ""
        # Animations-Parameter
        self.animation_steps = 18  # Erhöht für weichere Animationen
        self.animation_delay = 10  # ms zwischen Schritten
        # Hilfsdaten für Hover/Fokus
        self._hover_states = {}
        self._focus_states = {}

    # ----------------------------
    # Screen / Fullscreen Animationen
    # ----------------------------
    def toggle_fullscreen(self, event=None):
        """Wechselt zwischen Vollbild- und normaler Fensteransicht mit Animation."""
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            try:
                self.original_geometry = self.app.geometry()
            except Exception:
                self.original_geometry = f"{self.app.winfo_width()}x{self.app.winfo_height()}+{self.app.winfo_x()}+{self.app.winfo_y()}"
            self._animate_to_fullscreen(0)
        else:
            self._animate_to_normal(0)

    def _animate_to_fullscreen(self, step: int):
        """Animiert das Fenster schrittweise zur vollen Bildschirmgröße mit Easing."""
        if step <= self.animation_steps:
            try:
                parts = self.original_geometry.split('+')
                size_parts = parts[0].split('x')
                start_w, start_h = int(size_parts[0]), int(size_parts[1])
                start_x, start_y = int(parts[1]), int(parts[2])
            except Exception:
                start_w, start_h = self.app.winfo_width(), self.app.winfo_height()
                start_x, start_y = self.app.winfo_x(), self.app.winfo_y()

            target_w = self.app.winfo_screenwidth()
            target_h = self.app.winfo_screenheight()

            # Verwendung einer Easing-Funktion
            fraction = easing.ease_out_cubic(step / self.animation_steps)
            
            new_w = int(start_w + (target_w - start_w) * fraction)
            new_h = int(start_h + (target_h - start_h) * fraction)
            new_x = int(start_x * (1 - fraction))
            new_y = int(start_y * (1 - fraction))

            try:
                self.app.geometry(f"{new_w}x{new_h}+{new_x}+{new_y}")
            except Exception:
                pass

            self.app.after(self.animation_delay, lambda: self._animate_to_fullscreen(step + 1))
        else:
            try:
                self.app.geometry(f"{self.app.winfo_screenwidth()}x{self.app.winfo_screenheight()}+0+0")
            except Exception:
                pass

    def _animate_to_normal(self, step: int):
        """Animiert das Fenster schrittweise zurück zur Originalgröße mit Easing."""
        if not self.original_geometry:
            return

        if step <= self.animation_steps:
            try:
                current_w, current_h = self.app.winfo_width(), self.app.winfo_height()
                current_x, current_y = self.app.winfo_x(), self.app.winfo_y()
            except Exception:
                return

            try:
                parts = self.original_geometry.split('+')
                size_parts = parts[0].split('x')
                target_w, target_h = int(size_parts[0]), int(size_parts[1])
                target_x, target_y = int(parts[1]), int(parts[2])
            except Exception:
                return

            # Startwerte sind die Vollbildgröße
            start_w, start_h = self.app.winfo_screenwidth(), self.app.winfo_screenheight()
            start_x, start_y = 0, 0
            
            fraction = easing.ease_out_cubic(step / self.animation_steps)

            new_w = int(start_w - (start_w - target_w) * fraction)
            new_h = int(start_h - (start_h - target_h) * fraction)
            new_x = int(start_x + (target_x - start_x) * fraction)
            new_y = int(start_y + (target_y - start_y) * fraction)
            
            try:
                self.app.geometry(f"{new_w}x{new_h}+{new_x}+{new_y}")
            except Exception:
                pass
            
            self.app.after(self.animation_delay, lambda: self._animate_to_normal(step + 1))
        else:
            try:
                self.app.geometry(self.original_geometry)
            except Exception:
                pass

    # ----------------------------
    # View / Wechsel-Animationen
    # ----------------------------
    def slide_in_view(self, widget: ctk.CTkFrame, start_pos: float = 1.0, on_complete: Optional[Callable] = None):
        """Animiert ein Widget (eine Ansicht) von rechts ins Bild."""
        self.animate_value(
            lambda val: widget.place(relx=val, rely=0, relwidth=1, relheight=1) if widget.winfo_exists() else None,
            start=start_pos,
            end=0.0,
            duration=350,
            easing_func=easing.ease_out_cubic,
            on_complete=on_complete
        )

    def slide_out_view(self, widget: ctk.CTkFrame, end_pos: float = -1.0, on_complete: Optional[Callable] = None):
        """Schiebt eine Ansicht nach links aus dem sichtbaren Bereich (Slide-Out)."""
        start_pos = float(widget.place_info().get("relx", 0))
        self.animate_value(
            lambda val: widget.place(relx=val, rely=0, relwidth=1, relheight=1) if widget.winfo_exists() else None,
            start=start_pos,
            end=end_pos,
            duration=350,
            easing_func=easing.ease_out_cubic,
            on_complete=on_complete
        )

    def zoom_in_widget(self, widget: ctk.CTkFrame, on_complete: Optional[Callable] = None):
        """Zoomt eine Ansicht von klein zur vollen Größe."""
        widget.place(relx=0.5, rely=0.5, relwidth=0, relheight=0, anchor="center")
        
        def on_zoom_finished():
            if widget.winfo_exists():
                widget.place_forget()
                widget.grid(row=0, column=0, sticky="nsew")
            if on_complete:
                on_complete()

        self.animate_value(
            lambda val: widget.place(relx=0.5, rely=0.5, relwidth=val, relheight=val, anchor="center") if widget.winfo_exists() else None,
            start=0.0,
            end=1.0,
            duration=300,
            easing_func=easing.ease_out_quad,
            on_complete=on_zoom_finished
        )
        
    def fade_in_widget(self, widget: ctk.CTkFrame, on_complete: Optional[Callable] = None):
        """Fadet ein Widget ein, indem seine Farbe vom Hintergrund zur Zielfarbe animiert wird."""
        widget.place(relx=0, rely=0, relwidth=1, relheight=1)
        widget.lift()

        try:
            target_color_tuple = widget.cget("fg_color")
            start_color_tuple = widget.master.cget("fg_color")
            
            mode_index = 1 if ctk.get_appearance_mode() == "Dark" else 0
            
            target_color = target_color_tuple[mode_index]
            start_color = start_color_tuple[mode_index]

        except Exception:
            if on_complete:
                on_complete()
            return

        def color_setter(fraction: float):
            if widget.winfo_exists():
                new_color = _interpolate_color(start_color, target_color, fraction)
                widget.configure(fg_color=new_color)
        
        self.animate_value(
            setter=lambda val: color_setter(val),
            start=0.0,
            end=1.0,
            duration=350,
            easing_func=easing.ease_in_quad,
            on_complete=on_complete
        )
        
    def fade_out_widget(self, widget: ctk.CTkFrame, on_complete: Optional[Callable] = None):
        """Fadet ein Widget aus, indem seine Farbe zur Hintergrundfarbe animiert wird."""
        widget.lower()

        try:
            start_color_tuple = widget.cget("fg_color")
            end_color_tuple = widget.master.cget("fg_color")
            
            mode_index = 1 if ctk.get_appearance_mode() == "Dark" else 0
            
            start_color = start_color_tuple[mode_index]
            end_color = end_color_tuple[mode_index]

        except Exception:
            if on_complete:
                on_complete()
            return

        def color_setter(fraction: float):
            if widget.winfo_exists():
                new_color = _interpolate_color(start_color, end_color, fraction)
                widget.configure(fg_color=new_color)
        
        self.animate_value(
            setter=lambda val: color_setter(val),
            start=0.0,
            end=1.0,
            duration=300,
            easing_func=easing.ease_out_quad,
            on_complete=on_complete
        )

    def animated_tabs(self, old_frame: Optional[ctk.CTkFrame], new_frame: ctk.CTkFrame, mode: str = "slide"):
        """
        Wechselt zwischen zwei 'Tab'-Frames mit einer Animation.
        mode: "slide" | "fade" | "zoom"
        """
        if old_frame == new_frame:
            return

        if old_frame:
            manager = old_frame.winfo_manager()
            if manager == "grid":
                old_frame.grid_forget()
            elif manager == "place":
                old_frame.place_forget()

        if mode == "slide":
            new_frame.place(relx=1.0, rely=0, relwidth=1, relheight=1)
            self.slide_in_view(new_frame)
            if old_frame:
                self.slide_out_view(old_frame, on_complete=lambda: old_frame.place_forget())
        
        elif mode == "fade":
            if old_frame:
                self.fade_out_widget(old_frame, on_complete=lambda: old_frame.place_forget())
            self.fade_in_widget(new_frame)

        elif mode == "zoom":
            self.zoom_in_widget(new_frame)
        
        else:
            new_frame.grid(row=0, column=0, sticky="nsew")
            new_frame.lift()


    def animate_value(self, setter: Callable[[float], None], start: float, end: float, duration: int = 400, steps: Optional[int] = None, easing_func: Callable = easing.linear, on_complete: Optional[Callable] = None):
        """
        Generische Numerik-Animation: ruft 'setter' mit interpolierten Werten zwischen start und end auf.
        """
        if steps is None:
            steps = duration // self.animation_delay
            
        step_delay = max(1, duration // steps)

        def _step(i=0):
            if i > steps:
                try:
                    setter(end)
                except Exception:
                    pass
                if on_complete:
                    on_complete()
                return
            
            fraction = easing_func(i / steps)
            val = start + (end - start) * fraction
            
            try:
                setter(val)
            except Exception:
                pass
            
            self.app.after(step_delay, lambda: _step(i + 1))

        _step(0)

    # ----------------------------
    # Feedback für den Nutzer
    # ----------------------------
    def save_button_animation(self, button: ctk.CTkButton, success_text: str = "✓", flash_color: str = "#2ecc71", duration: int = 900):
        """
        Kurze Bestätigungs-Animation für einen Save-Button.
        """
        try:
            orig_text = button.cget("text")
            orig_color = button.cget("fg_color")
            orig_state = {"text": orig_text, "fg_color": orig_color}
        except Exception:
            orig_state = {"text": getattr(button, "text", ""), "fg_color": None}

        def _set_success():
            try:
                button.configure(fg_color=flash_color, text=success_text)
                self.app.after(duration, _reset)
            except Exception:
                pass

        def _reset():
            try:
                button.configure(text=orig_state["text"], fg_color=orig_state["fg_color"])
            except Exception:
                pass

        _set_success()

    def delete_animation(self, item_widget: tk.Widget, remove_callback: Optional[Callable] = None, flash_color: str = "#e74c3c", steps: int = 6):
        """
        Löscht ein Eintrags-Widget mit einer kurzen Flash- und Fade-Animation.
        """
        try:
            orig_bg = item_widget.cget("fg_color")
        except Exception:
            orig_bg = None

        def _flash(i=0):
            if i < steps:
                try:
                    current_color = flash_color if i % 2 == 0 else orig_bg
                    if current_color:
                        item_widget.configure(fg_color=current_color)
                except Exception:
                    pass
                self.app.after(80, lambda: _flash(i + 1))
            else:
                _fade_height(item_widget, on_done=lambda: _final_remove(item_widget))

        def _fade_height(w: tk.Widget, on_done: Optional[Callable] = None):
            try:
                h = w.winfo_height()
                self.animate_value(
                    lambda val: w.configure(height=int(val)),
                    start=h,
                    end=0,
                    duration=200,
                    on_complete=on_done
                )
            except Exception:
                if on_done:
                    on_done()

        def _final_remove(w):
            if remove_callback:
                remove_callback()
            else:
                try:
                    w.destroy()
                except Exception:
                    pass
        
        _flash(0)