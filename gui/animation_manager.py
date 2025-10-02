# gui/animation_manager.py
# -*- coding: utf-8 -*-
"""
Eine zentrale Klasse zur Verwaltung von UI-Animationen in der Anwendung.
"""
import math
import customtkinter as ctk
import tkinter as tk
from typing import Callable, Iterable, List, Tuple


class AnimationManager:
    """Kapselt die Logik für Fenster- und Widget-Animationen."""

    def __init__(self, app_instance: ctk.CTk):
        """
        Initialisiert den Manager mit einer Referenz auf das Hauptfenster.

        Args:
            app_instance: Die Instanz der Hauptanwendung (BerichtsheftApp).
        """
        self.app = app_instance
        # Fullscreen-bezogene Attribute (wiederhergestellt)
        self.is_fullscreen = False
        self.original_geometry = ""
        # Animations-Parameter
        self.animation_steps = 8
        self.animation_delay = 12  # ms zwischen Schritten
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
            # Speichere die aktuelle Geometrie, bevor in den Vollbildmodus gewechselt wird
            try:
                self.original_geometry = self.app.geometry()
            except Exception:
                self.original_geometry = f"{self.app.winfo_width()}x{self.app.winfo_height()}+{self.app.winfo_x()}+{self.app.winfo_y()}"
            self._animate_to_fullscreen(0)
        else:
            # Animation zurück zur Originalgröße
            self._animate_to_normal(0)

    def _animate_to_fullscreen(self, step: int):
        """Animiert das Fenster schrittweise zur vollen Bildschirmgröße."""
        if step <= self.animation_steps:
            # Bestimme Startgeometrie fallback-sicher
            try:
                parts = self.original_geometry.split('+')
                size_parts = parts[0].split('x')
                start_w, start_h = int(size_parts[0]), int(size_parts[1])
                start_x, start_y = int(parts[1]), int(parts[2])
            except Exception:
                start_w, start_h = self.app.winfo_width(), self.app.winfo_height()
                start_x, start_y = self.app.winfo_x(), self.app.winfo_y()

            # Zielgeometrie ist der gesamte Bildschirm
            target_w = self.app.winfo_screenwidth()
            target_h = self.app.winfo_screenheight()

            # Lineare Interpolation für einen sanften Übergang
            fraction = step / max(1, self.animation_steps)
            new_w = int(start_w + (target_w - start_w) * fraction)
            new_h = int(start_h + (target_h - start_h) * fraction)

            # Wir verschieben sanft Richtung (0,0)
            new_x = int(start_x * (1 - fraction))
            new_y = int(start_y * (1 - fraction))

            try:
                self.app.geometry(f"{new_w}x{new_h}+{new_x}+{new_y}")
            except Exception:
                # Fallback: setze maximal auf screen size ohne offset
                try:
                    self.app.geometry(f"{new_w}x{new_h}")
                except Exception:
                    pass

            self.app.after(self.animation_delay, lambda: self._animate_to_fullscreen(step + 1))
        else:
            # Am Ende vollständiger Vollbildmodus (setzen auf Bildschirmgröße)
            try:
                self.app.geometry(f"{self.app.winfo_screenwidth()}x{self.app.winfo_screenheight()}+0+0")
            except Exception:
                pass

    def _animate_to_normal(self, step: int):
        """Animiert das Fenster schrittweise zurück zur Originalgröße."""
        # Falls keine originale Geometrie vorhanden, beende
        if not self.original_geometry:
            return

        if step <= self.animation_steps:
            # Aktuelle Geometrie auslesen (Fallback-freundlich)
            try:
                current_w = self.app.winfo_width()
                current_h = self.app.winfo_height()
                current_x = self.app.winfo_x()
                current_y = self.app.winfo_y()
            except Exception:
                try:
                    parts_now = self.app.geometry().split('+')
                    size_parts_now = parts_now[0].split('x')
                    current_w, current_h = int(size_parts_now[0]), int(size_parts_now[1])
                    current_x, current_y = int(parts_now[1]), int(parts_now[2])
                except Exception:
                    current_w = current_h = 0
                    current_x = current_y = 0

            # Zielgeometrie ist die gespeicherte Originalgröße
            try:
                parts = self.original_geometry.split('+')
                size_parts = parts[0].split('x')
                target_w, target_h = int(size_parts[0]), int(size_parts[1])
                target_x, target_y = int(parts[1]), int(parts[2])
            except Exception:
                # falls parse fehlschlägt, setze Ziel auf aktuelle (keine Änderung)
                target_w, target_h = current_w, current_h
                target_x, target_y = current_x, current_y

            # Lineare Interpolation für den Rückweg
            fraction = step / max(1, self.animation_steps)
            new_w = int(current_w - (current_w - target_w) * fraction)
            new_h = int(current_h - (current_h - target_h) * fraction)
            new_x = int(current_x + (target_x - current_x) * fraction)
            new_y = int(current_y + (target_y - current_y) * fraction)

            try:
                self.app.geometry(f"{new_w}x{new_h}+{new_x}+{new_y}")
            except Exception:
                try:
                    self.app.geometry(f"{new_w}x{new_h}")
                except Exception:
                    pass

            self.app.after(self.animation_delay, lambda: self._animate_to_normal(step + 1))
        else:
            # Am Ende die exakte Geometrie wiederherstellen, um Rundungsfehler zu vermeiden
            try:
                self.app.geometry(self.original_geometry)
            except Exception:
                pass

    # ----------------------------
    # View / Wechsel-Animationen
    # ----------------------------
    def slide_in_view(self, widget: ctk.CTkFrame, start_pos: float = 1.5):
        """
        Animiert ein Widget (eine Ansicht) von rechts ins Bild.

        Args:
            widget: Das CTkFrame-Widget, das animiert werden soll.
            start_pos: Die relative Startposition auf der x-Achse (1.0 = ganz rechts).
        """
        if start_pos > 0:
            start_pos -= 0.04  # Animationsgeschwindigkeit
            if widget.winfo_exists():
                widget.place(relx=max(start_pos, 0), rely=0, relwidth=1, relheight=1)
                self.app.after(8, lambda: self.slide_in_view(widget, start_pos))
        else:
            if widget.winfo_exists():
                widget.place(relx=0, rely=0, relwidth=1, relheight=1)


    def slide_out_view(self, widget: ctk.CTkFrame, end_pos: float = -1.0, step: float = 0.04, on_complete: Callable = None):
        """
        Schiebt eine Ansicht nach links aus dem sichtbaren Bereich (Slide-Out).
        """
        if not widget.winfo_exists():
            if on_complete:
                on_complete()
            return

        info = widget.place_info()
        relx = float(info.get("relx", 0))
        relx -= step
        if relx > end_pos:
            widget.place(relx=relx, rely=0, relwidth=1, relheight=1)
            self.app.after(10, lambda: self.slide_out_view(widget, end_pos, step, on_complete))
        else:
            widget.place_forget()
            if on_complete:
                on_complete()

    def fade_in_widget(self, widget: tk.Widget, steps: int = 10, on_complete: Callable = None):
        """
        Fade-In für ein Widget. Hinweis: direkter Widget-Alpha-Support ist in tkinter limitiert.
        Diese Implementation benutzt ein Canvas-Overlay wenn möglich oder als Fallback ein schnelles
        Einblenden über die Fenster-Alpha (betrifft das ganze Fenster).
        """
        root = widget.winfo_toplevel()
        try:
            x = widget.winfo_rootx() - root.winfo_rootx()
            y = widget.winfo_rooty() - root.winfo_rooty()
            w = widget.winfo_width()
            h = widget.winfo_height()
            overlay = tk.Canvas(root, highlightthickness=0)
            overlay.place(x=x, y=y, width=w, height=h)
            rect = overlay.create_rectangle(0, 0, w, h, fill=widget.cget("fg_color") if hasattr(widget, "cget") else "#ffffff")
            step = 1.0 / max(1, steps)

            def _do(i=0):
                if i >= steps:
                    overlay.destroy()
                    if on_complete:
                        on_complete()
                    return
                # Schlichte Stipple-Annäherung für Transparenz-Stufen
                overlay.itemconfigure(rect, stipple="gray" + str(min(75, int(100 - (i / steps) * 100))))
                self.app.after(int(self.animation_delay), lambda: _do(i + 1))

            _do(0)
        except Exception:
            # Fallback: Fenster-Alpha (beeinflusst das komplette Fenster)
            try:
                orig = float(root.attributes("-alpha") or 1.0)
            except Exception:
                orig = 1.0

            def _fade(i=0):
                if i > steps:
                    root.attributes("-alpha", orig)
                    if on_complete:
                        on_complete()
                    return
                root.attributes("-alpha", i / steps)
                self.app.after(self.animation_delay, lambda: _fade(i + 1))

            _fade(0)

    def fade_out_widget(self, widget: tk.Widget, steps: int = 10, on_complete: Callable = None):
        """
        Fade-Out-Animation. Analog zu fade_in_widget (selbe Limitationen).
        """
        root = widget.winfo_toplevel()
        try:
            x = widget.winfo_rootx() - root.winfo_rootx()
            y = widget.winfo_rooty() - root.winfo_rooty()
            w = widget.winfo_width()
            h = widget.winfo_height()
            overlay = tk.Canvas(root, highlightthickness=0)
            overlay.place(x=x, y=y, width=w, height=h)
            rect = overlay.create_rectangle(0, 0, w, h, fill=widget.cget("fg_color") if hasattr(widget, "cget") else "#000000")
            step = 1.0 / max(1, steps)

            def _do(i=0):
                if i >= steps:
                    overlay.destroy()
                    widget.place_forget()
                    if on_complete:
                        on_complete()
                    return
                overlay.itemconfigure(rect, stipple="gray" + str(min(75, int((i / steps) * 100))))
                self.app.after(int(self.animation_delay), lambda: _do(i + 1))

            _do(0)
        except Exception:
            # Fallback: Fenster-Alpha
            try:
                orig = float(root.attributes("-alpha") or 1.0)
            except Exception:
                orig = 1.0

            def _fade(i=0):
                if i > steps:
                    widget.place_forget()
                    root.attributes("-alpha", orig)
                    if on_complete:
                        on_complete()
                    return
                root.attributes("-alpha", (steps - i) / steps)
                self.app.after(self.animation_delay, lambda: _fade(i + 1))

            _fade(0)

    def animated_tabs(self, old_frame: ctk.CTkFrame, new_frame: ctk.CTkFrame, mode: str = "slide"):
        """
        Wechselt zwischen zwei 'Tab'-Frames mit einer Animation.
        mode: "slide" | "fade"
        """
        if mode == "slide":
            # Die neue Ansicht schiebt von rechts herein, die alte wird gleichzeitig nach links geschoben
            new_frame.place(relx=1.0, rely=0, relwidth=1, relheight=1)
            # Starte beide Animationen
            self.slide_in_view(new_frame, start_pos=1.0)

            def _slide_old(pos=0.0):
                pos -= 0.06
                if pos > -1.1:
                    if old_frame.winfo_exists():
                        old_frame.place(relx=pos, rely=0, relwidth=1, relheight=1)
                    self.app.after(10, lambda: _slide_old(pos))
                else:
                    if old_frame.winfo_exists():
                        old_frame.place_forget()

            _slide_old(0.0)
        else:
            # Fade: neue Ansicht überlagert alte und blendet sanft ein
            new_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.fade_in_widget(new_frame)
            # Optional alte ausblenden
            self.fade_out_widget(old_frame, on_complete=lambda: old_frame.place_forget())

    # ----------------------------
    # Feedback für den Nutzer
    # ----------------------------
    def save_button_animation(self, button: ctk.CTkButton, success_text: str = "✓", flash_color: str = "#2ecc71", duration: int = 900):
        """
        Kurze Bestätigungs-Animation für einen Save-Button:
        - Button wechselt kurz die Farbe
        - Zeigt ein Häkchen bzw. success_text
        - Danach Rückkehr zum Originalzustand.
        """
        try:
            orig_text = button.cget("text")
            orig_color = button.cget("fg_color") if "fg_color" in button.configure() else None
            orig_state = {"text": orig_text, "fg_color": orig_color}
        except Exception:
            orig_state = {"text": getattr(button, "text", ""), "fg_color": None}

        def _set_success():
            try:
                if orig_state["fg_color"]:
                    button.configure(fg_color=flash_color)
                button.configure(text=success_text)
                # nach duration zurücksetzen
                self.app.after(duration, _reset)
            except Exception:
                button.configure(text=success_text)
                self.app.after(duration, _reset)

        def _reset():
            try:
                button.configure(text=orig_state["text"])
                if orig_state["fg_color"]:
                    button.configure(fg_color=orig_state["fg_color"])
            except Exception:
                pass

        _set_success()

    def delete_animation(self, item_widget: tk.Widget, remove_callback: Callable = None, flash_color: str = "#e74c3c", steps: int = 6):
        """
        Löscht ein Eintrags-Widget mit einer kurzen Flash- und Fade-Animation.
        """
        try:
            orig_bg = item_widget.cget("bg") if "bg" in item_widget.configure() else None
        except Exception:
            orig_bg = None

        def _flash(i=0):
            if i < steps:
                try:
                    item_widget.configure(bg=flash_color if i % 2 == 0 else orig_bg or "")
                except Exception:
                    pass
                self.app.after(80, lambda: _flash(i + 1))
            else:
                _fade_height(item_widget, on_done=lambda: _final_remove(item_widget))

        def _fade_height(w: tk.Widget, on_done: Callable = None):
            try:
                info = w.place_info()
                if info:
                    relh = float(info.get("relheight", 1.0))
                    step = relh / 8
                    def _shrink(r):
                        if r <= 0:
                            w.place_forget()
                            if on_done:
                                on_done()
                            return
                        w.place_configure(relheight=r)
                        self.app.after(25, lambda: _shrink(r - step))
                    _shrink(relh)
                else:
                    w.after(120, lambda: (w.destroy(), on_done() if on_done else None))
            except Exception:
                try:
                    w.after(120, lambda: (w.destroy(), on_done() if on_done else None))
                except Exception:
                    if on_done:
                        on_done()

        def _final_remove(w):
            try:
                if remove_callback:
                    remove_callback()
                else:
                    w.destroy()
            except Exception:
                pass

        _flash(0)

    def loading_logo_animation(self, logo_widget: tk.Widget, duration: int = 1200, pulse_count: int = 4):
        """
        Kleine animierte Ladeanzeige mit 'Pulsieren' des Logos.
        """
        try:
            info = logo_widget.place_info()
            if info:
                orig_w = float(info.get("relwidth", 0.2))
                orig_h = float(info.get("relheight", 0.2))
                count = 0

                def _pulse(i=0):
                    nonlocal count
                    if count >= pulse_count:
                        logo_widget.place_configure(relwidth=orig_w, relheight=orig_h)
                        return
                    factor = 1.0 + 0.08 * math.sin(i / 6.0 * math.pi)
                    logo_widget.place_configure(relwidth=orig_w * factor, relheight=orig_h * factor)
                    if i >= 12:
                        count += 1
                        i = 0
                    self.app.after(int(duration / (pulse_count * 12)), lambda: _pulse(i + 1))

                _pulse(0)
            else:
                orig_text = getattr(logo_widget, "cget", lambda k: "")("text")
                def _blink(i=0):
                    if i > pulse_count * 2:
                        try:
                            logo_widget.configure(text=orig_text)
                        except Exception:
                            pass
                        return
                    try:
                        logo_widget.configure(text="" if i % 2 == 0 else orig_text)
                    except Exception:
                        pass
                    self.app.after(int(duration / (pulse_count * 2)), lambda: _blink(i + 1))
                _blink(0)
        except Exception:
            pass

    # ----------------------------
    # Visuelle Akzente & "Lebendigkeit"
    # ----------------------------
    def hover_effect(self, widget: tk.Widget, dx: float = 0.01, scale: float = 1.03, duration: int = 120):
        """
        Bindet einen sanften Hover-Effekt an ein Widget.
        """
        try:
            info = widget.place_info()
            orig_relx = float(info.get("relx", 0))
            orig_relwidth = float(info.get("relwidth", 1))
        except Exception:
            orig_relx = None
            orig_relwidth = None

        def _on_enter(e=None):
            if orig_relx is not None:
                widget.place_configure(relx=orig_relx + dx, relwidth=orig_relwidth * scale)
            else:
                try:
                    widget.configure(font=("TkDefaultFont", int(widget.winfo_reqheight() * 0.2)))
                except Exception:
                    pass

        def _on_leave(e=None):
            if orig_relx is not None:
                widget.place_configure(relx=orig_relx, relwidth=orig_relwidth)
            else:
                try:
                    widget.configure(font=("TkDefaultFont", int(widget.winfo_reqheight() * 0.18)))
                except Exception:
                    pass

        widget.bind("<Enter>", _on_enter)
        widget.bind("<Leave>", _on_leave)
        self._hover_states[widget] = (_on_enter, _on_leave)

    def remove_hover_effect(self, widget: tk.Widget):
        """Entfernt einen zuvor gesetzten Hover-Effekt."""
        if widget in self._hover_states:
            enter, leave = self._hover_states.pop(widget)
            try:
                widget.unbind("<Enter>", enter)
                widget.unbind("<Leave>", leave)
            except Exception:
                pass

    def staggered_loading(self, container: tk.Widget, children: Iterable[tk.Widget], delay_between: int = 80, animation: str = "slide"):
        """
        Lädt Kind-Widgets nacheinander mit einer kleinen Verzögerung (Stagger-Effekt).
        """
        children = list(children)

        def _show(i=0):
            if i >= len(children):
                return
            w = children[i]
            try:
                if animation == "slide":
                    w.place_configure(relx=1.1)  # Start rechts
                    self.slide_in_view(w, start_pos=1.1)
                else:
                    w.place_configure(relx=0)
                    self.fade_in_widget(w)
            except Exception:
                try:
                    w.place(relx=0, rely=0)
                except Exception:
                    pass
            self.app.after(delay_between, lambda: _show(i + 1))

        _show(0)

    def focus_animation(self, widget: tk.Widget, color: str = "#4a90e2", width: int = 2, fade_steps: int = 6):
        """
        Animiert den Fokusrahmen beim Focus-In/Focus-Out.
        """
        try:
            orig_thickness = int(widget.cget("highlightthickness") or 0)
            orig_color = widget.cget("highlightbackground") if "highlightbackground" in widget.configure() else None
        except Exception:
            orig_thickness = 0
            orig_color = None

        def _on_focus_in(e=None):
            def _grow(i=0):
                if i > fade_steps:
                    return
                t = int(orig_thickness + (width - orig_thickness) * (i / fade_steps))
                try:
                    widget.configure(highlightthickness=t, highlightbackground=color)
                except Exception:
                    pass
                self.app.after(12, lambda: _grow(i + 1))
            _grow(0)

        def _on_focus_out(e=None):
            def _shrink(i=0):
                if i > fade_steps:
                    try:
                        widget.configure(highlightthickness=orig_thickness, highlightbackground=orig_color)
                    except Exception:
                        pass
                    return
                t = int(width - (width - orig_thickness) * (i / fade_steps))
                try:
                    widget.configure(highlightthickness=t, highlightbackground=color)
                except Exception:
                    pass
                self.app.after(12, lambda: _shrink(i + 1))
            _shrink(0)

        widget.bind("<FocusIn>", _on_focus_in)
        widget.bind("<FocusOut>", _on_focus_out)
        self._focus_states[widget] = (_on_focus_in, _on_focus_out)

    # ----------------------------
    # Animierte Datenvisualisierung
    # ----------------------------
    def animate_bar_chart(self, canvas: tk.Canvas, bar_items: List[int], values: List[float], max_value: float = None, duration: int = 700):
        """
        Animiert Balken in einem Canvas von Höhe 0 bis zur Zielhöhe.
        """
        if not values:
            return
        if max_value is None:
            max_value = max(values)

        steps = max(6, int(self.animation_steps * 2))
        step_delay = max(8, int(duration / steps))

        ch = int(canvas.winfo_height() or canvas.winfo_reqheight() or 200)
        targets = [int((v / max_value) * ch) for v in values]

        def _animate_step(i=1):
            if i > steps:
                return
            fraction = i / steps
            for idx, item_id in enumerate(bar_items):
                target_h = targets[idx]
                current_h = int(target_h * fraction)
                coords = canvas.coords(item_id)
                if len(coords) >= 4:
                    x1, y1, x2, y2 = coords
                    new_y1 = ch - current_h
                    canvas.coords(item_id, x1, new_y1, x2, ch)
            canvas.update_idletasks()
            self.app.after(step_delay, lambda: _animate_step(i + 1))

        _animate_step(1)

    def animate_pie_chart(self, canvas: tk.Canvas, data: List[float], center: Tuple[int, int], radius: int, duration: int = 800):
        """
        Baut ein Tortendiagramm stufenweise auf (Uhrzeigersinn).
        """
        total = sum(data)
        if total <= 0:
            return

        steps = max(8, int(self.animation_steps * 2))
        step_delay = max(8, int(duration / steps))

        start_angle = 0.0
        arcs = []
        extents = [d / total * 360.0 for d in data]
        bbox = (center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius)

        for i, _ in enumerate(data):
            arc = canvas.create_arc(bbox, start=start_angle, extent=0, style=tk.PIESLICE)
            arcs.append(arc)
            start_angle += extents[i]

        def _step(s=1):
            if s > steps:
                start = 0
                for i, arc in enumerate(arcs):
                    canvas.itemconfigure(arc, start=start, extent=extents[i])
                    start += extents[i]
                return
            fraction = s / steps
            start = 0
            for i, arc in enumerate(arcs):
                canvas.itemconfigure(arc, start=start, extent=extents[i] * fraction)
                start += extents[i]
            canvas.update_idletasks()
            self.app.after(step_delay, lambda: _step(s + 1))

        _step(1)

    # ----------------------------
    # Utility / kleine Helfer
    # ----------------------------
    def animate_value(self, setter: Callable[[float], None], start: float, end: float, duration: int = 400, steps: int = None):
        """
        Generische Numerik-Animation: ruft 'setter' mit interpolierten Werten zwischen start und end auf.
        """
        if steps is None:
            steps = max(6, int(self.animation_steps))
        step_delay = max(8, int(duration / steps))

        def _step(i=0):
            if i > steps:
                setter(end)
                return
            frac = i / steps
            val = start + (end - start) * frac
            try:
                setter(val)
            except Exception:
                pass
            self.app.after(step_delay, lambda: _step(i + 1))

        _step(0)