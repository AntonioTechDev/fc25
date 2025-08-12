"""
PSN Automation Module
=====================

Modulo per l'automazione della creazione account PSN.
"""

import logging
import os
import time
from typing import Dict

from core.base_automator import BaseAutomator
from core.common_functions import (
    generate_psn_id,
    generate_psn_password,
    move_browser_to_primary_screen
)


class PSNAutomator(BaseAutomator):
    """
    Automator per la creazione account PSN.
    """
    
    def __init__(self, logger: logging.Logger = None):
        """
        Inizializza l'automator PSN.
        
        Args:
            logger: Logger per i messaggi
        """
        super().__init__("psn", "psn_images", logger)
        
        # Configurazione specifica PSN
        self.psn_url = "https://id.sonyentertainmentnetwork.com/id/create_account_ca/?entry=create_account#/create_account/wizard/entrance?entry=create_account"
        self.page_load_delay = 10
        
        # Sequenza automazione PSN
        self.automation_sequence = [
            ('1.png', '', 0),
            ('2.png', '', 0),
            ('3-day-select.png', '', 0),
            ('4-day-option.png', '', 0),
            ('5-mounth-select.png', '', 0),
            ('6-mounth-option.png', '', 0),
            ('7-year-select.png', '', 0),
            ('8-next-button.png', '', 0),
            ('9-email-input.png', '{email}', 0),
            ('10-psw-input.png', '{psn_password}', 0),
            ('11-re-psw-input.png', '{psn_password}', 0),
            ('12-city-label.png', '', 0),
            ('13-state-label.png', '', 0),
            ('14-postal-code-label.png', '', 0),
            ('15-id-label.png', '', 0),
            ('16-name-input.png', '{first_name}', 0),
            ('17-surname-input.png', '{last_name}', 0),
            ('18-button-confirm-account.png', '', 0),
            ('19-confirm-img.png', '', 0),
            ('20-ok-button-confirm.png', '', 0),
            ('21-next-button-post-confirm.png', '', 0, 200),  # Scroll 200px
            ('22-pin-pre-scroll.png', '', 0),
            ('23-button-post-scroll.png', '', 0)
        ]
    
    def run_automation(self, account_data: Dict[str, str]) -> Dict[str, str]:
        """
        Esegue l'automazione PSN per un account.
        
        Args:
            account_data: Dati dell'account
            
        Returns:
            Dizionario con i dati PSN generati
        """
        self.is_running = True
        self.logger.info("🎮 Avvio automazione PSN...")
        
        # Generazione dati PSN
        psn_id = generate_psn_id(account_data['first_name'], account_data['last_name'])
        psn_password = generate_psn_password(account_data['password'])
        
        self.logger.info(f"🎮 PSN ID generato: {psn_id}")
        self.logger.info(f"🔐 Password PSN generata: {psn_password}")
        
        # Aggiungi dati PSN all'account
        account_data['psn_id'] = psn_id
        account_data['psn_password'] = psn_password
        
        try:
            # Apertura PSN in nuova tab
            if not self.open_url_in_new_tab(self.psn_url):
                return self._create_failure_data(account_data)
            
            time.sleep(self.page_load_delay)
            
            # Sposta browser sul primo schermo se necessario
            move_browser_to_primary_screen('chrome', self.logger)
            
            # Esecuzione sequenza automazione PSN
            total_steps = len(self.automation_sequence)
            for i, step_data in enumerate(self.automation_sequence, 1):
                if not self.is_running:
                    self.logger.info("⏹️ Automazione interrotta dall'utente")
                    break
                
                self.update_progress(i, total_steps)
                
                # Gestione step con scroll
                if len(step_data) == 4:
                    template, text_input, click_duration, scroll_pixels = step_data
                else:
                    template, text_input, click_duration = step_data
                    scroll_pixels = 0
                
                # Sostituzione placeholder nel testo
                if text_input:
                    text_to_type = self.replace_placeholders(text_input, account_data)
                else:
                    text_to_type = ""
                
                # Esecuzione step
                if not self.find_and_interact(template, text_to_type, click_duration, scroll_pixels):
                    self.logger.error(f"❌ Fallimento step {i}: {template}")
                    return self._create_failure_data(account_data)
                
                time.sleep(self.click_delay)
            
            self.logger.info("✅ Automazione PSN completata con successo!")
            return self._create_success_data(account_data)
            
        except Exception as e:
            self.logger.error(f"❌ Errore automazione PSN: {e}")
            return self._create_failure_data(account_data)
        
        finally:
            self.is_running = False
    
    def stop_automation(self):
        """
        Ferma l'automazione in corso.
        """
        self.is_running = False
        self.logger.info("⏹️ Richiesta di stop automazione PSN") 