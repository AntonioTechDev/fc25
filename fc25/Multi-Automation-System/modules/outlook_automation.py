"""
Outlook Automation Module
=========================

Modulo per l'automazione della creazione account Outlook.
"""

import logging
import os
import time
from typing import Dict

from core.base_automator import BaseAutomator
from core.common_functions import (
    close_all_chrome_windows, 
    open_browser, 
    change_mac_address
)


class OutlookAutomator(BaseAutomator):
    """
    Automator per la creazione account Outlook.
    """
    
    def __init__(self, logger: logging.Logger = None):
        """
        Inizializza l'automator Outlook.
        
        Args:
            logger: Logger per i messaggi
        """
        super().__init__("outlook", "outlook_images", logger)
        
        # Configurazione specifica Outlook
        self.outlook_url = "https://signup.live.com/"
        self.page_load_delay = 15
        self.account_delay = 30
        self.mac_wait_seconds = 10
        
        # Sequenza automazione Outlook (stessa di Outlook_Account_Automation)
        self.automation_sequence = [
            ('email_input.png', '{email}', 0),
            ('next_button.png', '', 0),
            ('password_input.png', '{password}', 0),
            ('next_button.png', '', 0),
            ('birth_day_dropdown.png', '', 0),
            ('birth_day_option.png', '', 0),
            ('birth_month_dropdown.png', '', 0),
            ('birth_month_option.png', '', 0),
            ('birth_year_input.png', '{birth_year}', 0),
            ('date-btn-confirm.png', '', 0),
            ('first_name_input.png', '{first_name}', 0),
            ('last_name_input.png', '{last_name}', 0),
            ('next_button.png', '', 0),
            ('captcha_button.png', '', 13),
            ('step-1-after-captcha.png', '', 0),
            ('step-1-after-captcha.png', '', 0),
            ('step-2-after-captcha.png', '', 0),
            ('step-3-after-captcha.png', '', 20),
            ('step-4-after-captcha.png', '', 0),
            ('step-5-after-captcha.png', '', 20),
            ('step-6-after-captcha.png', '', 0)
        ]
    
    def run_automation(self, account_data: Dict[str, str]) -> Dict[str, str]:
        """
        Esegue l'automazione Outlook per un account.
        
        Args:
            account_data: Dati dell'account
            
        Returns:
            Dizionario con i dati Outlook generati
        """
        self.is_running = True
        self.logger.info("📧 Avvio automazione Outlook...")
        
        try:
            # Preparazione ambiente
            close_all_chrome_windows(self.logger)
            change_mac_address("en0", self.logger)
            time.sleep(self.mac_wait_seconds)
            
            # Apertura browser
            self.logger.info("🌐 Aprendo browser per Outlook...")
            if not open_browser(self.outlook_url, browser="chrome", 
                              incognito=True, logger=self.logger):
                self.logger.error("❌ Impossibile aprire browser")
                return self._create_failure_data(account_data)
            
            self.logger.info(f"⏳ Attendo {self.page_load_delay} secondi dopo apertura browser...")
            time.sleep(self.page_load_delay)
            
            # Esecuzione sequenza automazione
            total_steps = len(self.automation_sequence)
            for i, (template, text_input, click_duration) in enumerate(self.automation_sequence, 1):
                if not self.is_running:
                    self.logger.info("⏹️ Automazione interrotta dall'utente")
                    break
                
                self.update_progress(i, total_steps)
                
                # Sostituzione placeholder nel testo
                if text_input:
                    text_to_type = self.replace_placeholders(text_input, account_data)
                else:
                    text_to_type = ""
                
                # Esecuzione step
                if not self.find_and_interact(template, text_to_type, click_duration):
                    self.logger.error(f"❌ Fallimento step {i}: {template}")
                    return self._create_failure_data(account_data)
                
                # Delay personalizzato per alcuni step
                if template == 'captcha_button.png':
                    self.logger.info("⏳ Attendo 15 secondi per captcha...")
                    time.sleep(15)
                elif template == 'step-3-after-captcha.png':
                    self.logger.info("⏳ Attendo 20 secondi per step 3...")
                    time.sleep(20)
                elif template == 'step-5-after-captcha.png':
                    self.logger.info("⏳ Attendo 20 secondi per step 5...")
                    time.sleep(20)
                else:
                    time.sleep(self.click_delay)
            
            self.logger.info("✅ Automazione Outlook completata con successo!")
            return self._create_success_data(account_data)
            
        except Exception as e:
            self.logger.error(f"❌ Errore automazione Outlook: {e}")
            return self._create_failure_data(account_data)
        
        finally:
            self.is_running = False
    
    def stop_automation(self):
        """
        Ferma l'automazione in corso.
        """
        self.is_running = False
        self.logger.info("⏹️ Richiesta di stop automazione Outlook") 