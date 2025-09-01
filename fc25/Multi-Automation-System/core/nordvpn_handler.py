"""
NordVPN Handler
==============

Modulo per gestire l'automazione NordVPN.
"""

import logging
import os
import time
from typing import Optional


class NordVPNHandler:
    """
    Gestore per l'automazione NordVPN.
    """
    
    def __init__(self, base_automator, logger: logging.Logger = None):
        """
        Inizializza il gestore NordVPN.
        
        Args:
            base_automator: Istanza del BaseAutomator per le funzioni di base
            logger: Logger per i messaggi
        """
        self.base_automator = base_automator
        self.logger = logger or logging.getLogger(__name__)
        
        # Directory template VPN
        self.vpn_templates_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', 'templates', 'vpn_images'
        ))
    
    def initialize_nordvpn(self) -> bool:
        """
        Inizializza NordVPN con connessione all'Italia.
        
        Returns:
            True se l'inizializzazione è riuscita
        """
        try:
            self.logger.info("🔧 Avvio cambio IP con NordVPN...")
            
            # Salva directory originale
            original_templates_dir = self.base_automator.templates_dir
            
            # Cambia directory per i template VPN
            self.base_automator.templates_dir = self.vpn_templates_dir
            
            # Step 1: Clicca sull'icona NordVPN
            self.logger.info("🔧 Step 1: Clicco sull'icona NordVPN")
            if not self.base_automator.find_and_interact('step-1-nord-vpn-icon.png', '', 0):
                self.logger.error("❌ Impossibile trovare l'icona NordVPN")
                self.base_automator.templates_dir = original_templates_dir
                return False
            
            time.sleep(2)
            
            # Step 2: Prova a cliccare su VPN Italia attiva (se esiste)
            self.logger.info("🔧 Step 2: Provo a cliccare su VPN Italia attiva")
            if self.base_automator.find_and_interact('vpn-italy-active.png', '', 0):
                self.logger.info("✅ VPN Italia già attiva, riconnessa con successo")
            else:
                self.logger.info("🔧 VPN Italia non attiva, procedo con connessione")
                
                # Step 3: Clicca sulla searchbar
                self.logger.info("🔧 Step 3: Clicco sulla searchbar")
                if not self.base_automator.find_and_interact('step-2-searchbar.png', '', 0):
                    self.logger.error("❌ Impossibile trovare la searchbar")
                    self.base_automator.templates_dir = original_templates_dir
                    return False
                
                time.sleep(1)
                
                # Step 4: Clicca su Italia (prima volta)
                self.logger.info("🔧 Step 4: Clicco su Italia (prima volta)")
                if not self.base_automator.find_and_interact('vpn-italy-first-time.png', '', 0):
                    self.logger.error("❌ Impossibile trovare Italia (prima volta)")
                    self.base_automator.templates_dir = original_templates_dir
                    return False
            
            # Attendi che la connessione si stabilisca
            time.sleep(5)
            
            self.logger.info("✅ Cambio IP NordVPN completato")
            
            # Ripristina directory originale
            self.base_automator.templates_dir = original_templates_dir
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Errore inizializzazione NordVPN: {e}")
            # Ripristina directory originale in caso di errore
            if hasattr(self.base_automator, 'templates_dir'):
                self.base_automator.templates_dir = original_templates_dir
            return False
    

