# services/update_service.py
# -*- coding: utf-8 -*-
"""
Dienst zur Überprüfung auf Anwendungsupdates.
"""
import logging
import json
import re
import urllib.request
from typing import Optional, Dict

from core import config

logger = logging.getLogger(__name__)

class UpdateService:
    """
    Prüft auf GitHub, ob eine neuere Version der Anwendung verfügbar ist.
    """
    def check_for_updates(self) -> Optional[Dict[str, str]]:
        """
        Fragt die GitHub-API nach dem neuesten Release ab und vergleicht die Version.

        Returns:
            Ein Dictionary mit 'version' und 'url' des neuen Releases,
            oder None, wenn keine neuere Version verfügbar ist oder ein Fehler auftritt.
        """
        try:
            logger.info("Suche nach Anwendungsupdates...")
            # Setzt einen User-Agent, da die GitHub-API dies erfordert.
            req = urllib.request.Request(
                config.GITHUB_REPO_URL, 
                headers={'User-Agent': 'Berichtsheft-Generator-App'}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    latest_version_str = data.get("tag_name", "")
                    release_url = data.get("html_url")

                    if latest_version_str and release_url:
                        logger.info(f"Aktuelle Version: {config.VERSION}, Neueste Version: {latest_version_str}")
                        
                        # Extrahiere nur die Zahlen für einen robusten Vergleich
                        current_version_match = re.search(r'(\d+\.\d+)', config.VERSION)
                        latest_version_match = re.search(r'(\d+\.\d+)', latest_version_str)
                        
                        if current_version_match and latest_version_match:
                            current_version_num = float(current_version_match.group(1))
                            latest_version_num = float(latest_version_match.group(1))

                            if latest_version_num > current_version_num:
                                logger.info(f"Eine neuere Version ({latest_version_str}) wurde gefunden.")
                                return {"version": latest_version_str, "url": release_url}

                        logger.info("Die Anwendung ist auf dem neuesten Stand.")
                        return None
                else:
                    logger.warning(f"Fehler bei der Abfrage der GitHub-API, Status: {response.status}")
                    return None
        except Exception as e:
            # exc_info=False, um die Logs bei Netzwerkfehlern nicht zu überfluten
            logger.error(f"Fehler bei der Suche nach Updates: {e}", exc_info=False)
            return None
