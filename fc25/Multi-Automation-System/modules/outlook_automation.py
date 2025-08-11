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
    change_mac_address,
    replace_placeholders
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
        
        # Sequenza automazione Outlook
        self.automation_sequence = [
            ('email_input.png', '{email}', 0, 0),
            ('next_button.png', '', 0, 0),
            ('password_input.png', '{password}', 0, 0),
            ('next_button.png', '', 0, 0),
            ('birth_day_dropdown.png', '', 0, 0),
            ('birth_day_option.png', '', 0, 0),
            ('birth_month_dropdown.png', '', 0, 0),
            ('birth_month_option.png', '', 0, 0),
            ('birth_year_input.png', '{birth_year}', 0, 0),
            ('date-btn-confirm.png', '', 0, 0),
            ('first_name_input.png', '{first_name}', 0, 0),
            ('last_name_input.png', '{last_name}', 0, 0),
            ('next_button.png', '', 0, 0),
            ('captcha_button.png', '', 13, 15),
            ('step-1-after-captcha.png', '', 0, 0),
            ('step-1-after-captcha.png', '', 0, 0),
            ('step-2-after-captcha.png', '', 0, 0),
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
            for i, (template, text_input, click_duration, custom_delay) in enumerate(self.automation_sequence, 1):
                self.update_progress(i, total_steps)
                
                # Preparazione log e testo
                processed_text = replace_placeholders(text_input, account_data)
                template_name = os.path.splitext(template)[0]
                
                log_parts = [f"📧 [{i}/{total_steps}] Outlook: {template_name}"]
                if processed_text:
                    # Mascheramento dati sensibili nei log
                    if 'email' in text_input.lower() or '@' in processed_text:
                        display_text = processed_text.split('@')[0] + '@***'
                    elif 'password' in text_input.lower():
                        display_text = '*' * len(processed_text)
                    else:
                        display_text = processed_text
                    log_parts.append(f"→ '{display_text}'")
                
                if click_duration > 0:
                    log_parts.append(f"(click {click_duration}s)")
                else:
                    log_parts.append("(click normale)")
                
                if custom_delay and custom_delay > 0:
                    log_parts.append(f"[delay custom: {custom_delay}s]")
                
                self.logger.info(" ".join(log_parts))
                
                # Esecuzione interazione
                success = self.find_and_interact(template, processed_text, click_duration)
                
                if success:
                    action_desc = []
                    if processed_text:
                        action_desc.append("testo")
                    click_type = f"click {click_duration}s" if click_duration > 0 else "click"
                    action_desc.append(click_type)
                    self.logger.info(f"✅ {template_name} completato ({' + '.join(action_desc)})")
                else:
                    self.logger.warning(f"⚠️ {template_name} fallito")
                
                # Pausa tra elementi
                if i < total_steps:
                    delay_to_use = custom_delay if (custom_delay is not None and custom_delay > 0) else self.click_delay
                    self.logger.info(f"⏳ Pausa {delay_to_use} secondi...")
                    time.sleep(delay_to_use)
            
            # Risultato finale
            outlook_data = {
                'outlook_email': account_data['email'],
                'outlook_psw': account_data['password'],
                'outlook_status': 'success',
                'outlook_created': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.logger.info(f"✅ Automazione Outlook completata per: {account_data['email']}")
            return outlook_data
            
        except Exception as e:
            self.logger.error(f"❌ Errore automazione Outlook: {e}")
            return self._create_failure_data(account_data)
        
        finally:
            self.is_running = False
    
    def _create_failure_data(self, account_data: Dict[str, str]) -> Dict[str, str]:
        """
        Crea dati di fallimento per Outlook.
        
        Args:
            account_data: Dati dell'account
            
        Returns:
            Dizionario con dati di fallimento
        """
        return {
            'outlook_email': account_data['email'],
            'outlook_psw': account_data['password'],
            'outlook_status': 'failed',
            'outlook_created': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_service_info(self) -> Dict[str, str]:
        """
        Restituisce informazioni sul servizio Outlook.
        
        Returns:
            Dizionario con informazioni del servizio
        """
        info = super().get_service_info()
        info.update({
            'url': self.outlook_url,
            'total_steps': len(self.automation_sequence)
        })
        return info 