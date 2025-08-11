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
            ('1.png', '', 0, 0),
            ('2.png', '', 0, 0),
            ('3-day-select.png', '', 0, 0),
            ('4-day-option.png', '', 0, 0),
            ('5-mounth-select.png', '', 0, 0),
            ('6-mounth-option.png', '', 0, 0),
            ('7-year-select.png', '', 0, 0),
            ('8-next-button.png', '', 0, 0),
            ('9-email-input.png', '{email}', 0, 0),
            ('10-psw-input.png', '{psn_password}', 0, 0),
            ('11-re-psw-input.png', '{psn_password}', 0, 0),
            ('12-city-label.png', '', 0, 0),
            ('13-state-label.png', '', 0, 0),
            ('14-postal-code-label.png', '', 0, 0),
            ('15-id-label.png', '', 0, 0),
            ('16-name-input.png', '{first_name}', 0, 0),
            ('17-surname-input.png', '{last_name}', 0, 0),
            ('18-button-confirm-account.png', '', 0, 0),
            ('19-confirm-img.png', '', 0, 0),
            ('20-ok-button-confirm.png', '', 0, 0),
            ('21-next-button-post-confirm.png', '', 0, 200),  # Scroll 200px
            ('22-pin-pre-scroll.png', '', 0, 0),
            ('23-button-post-scroll.png', '', 0, 0)
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
            for i, (template, text_input, click_duration, scroll_pixels) in enumerate(self.automation_sequence, 1):
                self.update_progress(i, total_steps)
                
                # Preparazione log e testo
                processed_text = text_input.format(**account_data) if text_input else ""
                template_name = os.path.splitext(template)[0]
                
                log_parts = [f"🎮 [{i}/{total_steps}] PSN: {template_name}"]
                if processed_text:
                    # Mascheramento dati sensibili nei log
                    if 'email' in text_input.lower() or '@' in processed_text:
                        display_text = processed_text.split('@')[0] + '@***'
                    elif 'password' in text_input.lower():
                        display_text = '*' * len(processed_text)
                    else:
                        display_text = processed_text
                    log_parts.append(f"→ '{display_text}'")
                
                if scroll_pixels > 0:
                    log_parts.append(f"(scroll {scroll_pixels}px)")
                elif click_duration > 0:
                    log_parts.append(f"(click {click_duration}s)")
                else:
                    log_parts.append("(click normale)")
                
                self.logger.info(" ".join(log_parts))
                
                # Esecuzione interazione
                success = self.find_and_interact(template, processed_text, click_duration, scroll_pixels)
                
                if success:
                    action_desc = []
                    if processed_text:
                        action_desc.append("testo")
                    if scroll_pixels > 0:
                        action_desc.append(f"scroll {scroll_pixels}px")
                    elif click_duration > 0:
                        action_desc.append(f"click {click_duration}s")
                    else:
                        action_desc.append("click")
                    self.logger.info(f"✅ {template_name} completato ({' + '.join(action_desc)})")
                else:
                    self.logger.warning(f"⚠️ {template_name} fallito")
                
                # Pausa tra elementi
                if i < total_steps:
                    self.logger.info(f"⏳ Pausa {self.click_delay} secondi...")
                    time.sleep(self.click_delay)
            
            # Risultato finale
            psn_data = {
                'psn_id': psn_id,
                'psn_email': account_data['email'],
                'psn_psw': psn_password,
                'psn_status': 'success',
                'psn_created': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.logger.info(f"🎮 Automazione PSN completata per: {psn_id}")
            return psn_data
            
        except Exception as e:
            self.logger.error(f"❌ Errore automazione PSN: {e}")
            return self._create_failure_data(account_data)
        
        finally:
            self.is_running = False
    
    def _create_failure_data(self, account_data: Dict[str, str]) -> Dict[str, str]:
        """
        Crea dati di fallimento per PSN.
        
        Args:
            account_data: Dati dell'account
            
        Returns:
            Dizionario con dati di fallimento
        """
        return {
            'psn_id': account_data.get('psn_id', ''),
            'psn_email': account_data['email'],
            'psn_psw': account_data.get('psn_password', ''),
            'psn_status': 'failed',
            'psn_created': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_service_info(self) -> Dict[str, str]:
        """
        Restituisce informazioni sul servizio PSN.
        
        Returns:
            Dizionario con informazioni del servizio
        """
        info = super().get_service_info()
        info.update({
            'url': self.psn_url,
            'total_steps': len(self.automation_sequence)
        })
        return info 