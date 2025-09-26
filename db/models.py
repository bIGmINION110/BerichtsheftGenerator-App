# app/db/models.py
# -*- coding: utf-8 -*-
"""
Definiert Datenklassen (Models) zur typensicheren Repräsentation von Datenbankobjekten.
"""
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Tagebucheintrag:
    """Repräsentiert einen einzelnen Tageseintrag in einem Bericht."""
    tag_name: str
    typ: str
    stunden: str
    taetigkeiten: str
    bericht_id: Optional[str] = None
    eintrag_id: Optional[int] = None

@dataclass
class Bericht:
    """Repräsentiert ein komplettes Berichtsheft für eine Woche."""
    bericht_id: str
    fortlaufende_nr: int
    name_azubi: str
    jahr: int
    kalenderwoche: int
    tage_daten: List[Tagebucheintrag] = field(default_factory=list)

@dataclass
class Vorlage:
    """Repräsentiert eine Textvorlage."""
    text: str
    vorlage_id: Optional[int] = None