# src/berichtsheft/gui/easing_functions.py
# -*- coding: utf-8 -*-
"""
Sammlung von Easing-Funktionen für weichere Animationen.
"""
import math

def linear(t: float) -> float:
    """Lineare Interpolation."""
    return t

def ease_in_quad(t: float) -> float:
    """Quadratisches Easing In."""
    return t * t

def ease_out_quad(t: float) -> float:
    """Quadratisches Easing Out."""
    return t * (2 - t)

def ease_in_out_quad(t: float) -> float:
    """Quadratisches Easing In und Out."""
    if t < 0.5:
        return 2 * t * t
    return -1 + (4 - 2 * t) * t

def ease_in_cubic(t: float) -> float:
    """Kubisches Easing In."""
    return t * t * t

def ease_out_cubic(t: float) -> float:
    """Kubisches Easing Out."""
    t -= 1
    return t * t * t + 1

def ease_in_out_cubic(t: float) -> float:
    """Kubisches Easing In und Out."""
    if t < 0.5:
        return 4 * t * t * t
    t -= 1
    return 1 + 4 * t * t * t

def ease_out_quint(t: float) -> float:
    """Quintisches Easing Out."""
    t -= 1
    return t * t * t * t * t + 1

def ease_in_out_sine(t: float) -> float:
    """Sinus-Easing In und Out."""
    return -0.5 * (math.cos(math.pi * t) - 1)
