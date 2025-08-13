"""
PSN Automation Module
=====================

Modulo per l'automazione della creazione account PSN.
"""

import logging
import os
import time
import platform
import pyautogui
from typing import Dict

from core.base_automator import BaseAutomator
from core.common_functions import (
    generate_psn_id,
    generate_psn_password,
    move_browser_to_primary_screen,
    open_browser,
    close_all_chrome_windows,
    change_mac_address
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
        self.page_load_delay = 20
        self.mac_wait_seconds = 20
        
        # Sequenza automazione PSN
        self.automation_sequence = [
            ('1.png', '', 0),
            ('2.png', '', 0),
            ('3-PSN-day-select.png', '', 0, 'dropdown_day'),  # Dropdown giorno: 1 freccia giù + enter
            ('4-PSN-mounth-select.png', '', 0, 'dropdown_month'),  # Dropdown mese: 1 freccia giù + enter
            ('5-PSN-year.png', '', 0, 'dropdown_year'),  # Dropdown anno: 25 frecce giù + enter
            ('9-PSN-avanti.png', '', 0),
            ('6-PSN-email-input.png', '{outlook_email}', 0),
            ('7-PSN-password.png', '{outlook_psw}', 0),
            ('8-PSN-re-password.png', '{outlook_psw}', 0),
            ('8-PSN-re-password.png', '', 0, 0, 'click_below'),  # Click 100px più in giù
            ('9-PSN-avanti.png', '', 0),
            ('10-PSN-accetta-e-crea-account.png', '', 0)
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
        
        # Validazione dati richiesti
        required_fields = ['outlook_email', 'outlook_psw', 'first_name', 'last_name']
        missing_fields = []
        
        for field in required_fields:
            if not account_data.get(field, '').strip():
                missing_fields.append(field)
        
        if missing_fields:
            error_msg = f"❌ Dati mancanti per PSN: {', '.join(missing_fields)}"
            self.logger.error(error_msg)
            return self._create_failure_data(account_data, error_msg)
        
        # Generazione dati PSN
        psn_id = generate_psn_id(account_data['first_name'], account_data['last_name'])
        psn_password = generate_psn_password(account_data['outlook_psw'])
        
        self.logger.info(f"🎮 PSN ID generato: {psn_id}")
        self.logger.info(f"🔐 Password PSN generata: {psn_password}")
        
        # Aggiungi dati PSN all'account
        account_data['psn_id'] = psn_id
        account_data['psn_password'] = psn_password
        
        try:
            # Preparazione ambiente
            close_all_chrome_windows(self.logger)
            change_mac_address("en0", self.logger)
            time.sleep(self.mac_wait_seconds)
            
            # Apertura browser
            self.logger.info("🌐 Aprendo browser per PSN...")
            if not open_browser(self.psn_url, browser="chrome", 
                              incognito=True, logger=self.logger):
                self.logger.error("❌ Impossibile aprire browser")
                return self._create_failure_data(account_data)
            
            self.logger.info(f"⏳ Attendo {self.page_load_delay} secondi dopo apertura browser...")
            time.sleep(self.page_load_delay)
            
            # Sposta browser sul primo schermo se necessario
            move_browser_to_primary_screen('chrome', self.logger)
            
            # Esecuzione sequenza automazione PSN
            total_steps = len(self.automation_sequence)
            page_reload_attempts = 0
            max_page_reloads = 3
            
            for i, step_data in enumerate(self.automation_sequence, 1):
                if not self.is_running:
                    self.logger.info("⏹️ Automazione interrotta dall'utente")
                    break
                
                self.update_progress(i, total_steps)
                
                # Gestione step con scroll e azioni speciali
                if len(step_data) == 4:
                    template, text_input, click_duration, special_action = step_data
                    scroll_pixels = 0
                elif len(step_data) == 5:
                    template, text_input, click_duration, scroll_pixels, special_action = step_data
                else:
                    template, text_input, click_duration = step_data
                    scroll_pixels = 0
                    special_action = None
                
                # Sostituzione placeholder nel testo
                if text_input:
                    text_to_type = self.replace_placeholders(text_input, account_data)
                    # Verifica che i placeholder siano stati sostituiti
                    if '{' in text_to_type and '}' in text_to_type:
                        self.logger.error(f"❌ Placeholder non sostituito: {text_to_type}")
                        return self._create_failure_data(account_data, f"Placeholder non sostituito: {text_to_type}")
                else:
                    text_to_type = ""
                
                # Esecuzione step
                step_success = self.find_and_interact(template, text_to_type, click_duration, scroll_pixels)
                
                # Gestione speciale per il primo step (1.png)
                if not step_success and template == '1.png' and page_reload_attempts < max_page_reloads:
                    page_reload_attempts += 1
                    self.logger.warning(f"⚠️ 1.png non trovato, ricarico pagina (tentativo {page_reload_attempts}/{max_page_reloads})")
                    
                    # Ricarica la pagina
                    if self._reload_page():
                        self.logger.info("✅ Pagina ricaricata, riprovo step 1")
                        time.sleep(5)  # Attendi che la pagina si carichi
                        # Riprova lo stesso step
                        i -= 1  # Torna indietro di uno step
                        continue
                    else:
                        self.logger.error("❌ Impossibile ricaricare la pagina")
                        return self._create_failure_data(account_data, "Impossibile ricaricare la pagina")
                
                elif not step_success:
                    self.logger.error(f"❌ Fallimento step {i}: {template}")
                    return self._create_failure_data(account_data)
                
                # Gestione azioni speciali per dropdown
                if special_action:
                    if not self._handle_dropdown_action(special_action):
                        self.logger.error(f"❌ Fallimento azione dropdown {i}: {special_action}")
                        return self._create_failure_data(account_data)
                
                time.sleep(self.click_delay)
            
            self.logger.info("✅ Automazione PSN completata con successo!")
            return self._create_success_data(account_data)
            
        except Exception as e:
            self.logger.error(f"❌ Errore automazione PSN: {e}")
            return self._create_failure_data(account_data)
        
        finally:
            self.is_running = False
    
    def _handle_dropdown_action(self, action_type: str) -> bool:
        """
        Gestisce le azioni speciali per i dropdown e altre azioni.
        
        Args:
            action_type: Tipo di azione ('dropdown_day', 'dropdown_month', 'dropdown_year', 'click_below')
            
        Returns:
            True se l'azione è riuscita, False altrimenti
        """
        try:
            if action_type == 'dropdown_day':
                self.logger.info("📅 Gestione dropdown giorno: 1 freccia giù + enter")
                time.sleep(1)  # Attendi che il dropdown si apra
                pyautogui.press('down')  # 1 freccia giù
                time.sleep(0.5)
                pyautogui.press('enter')  # Conferma selezione
                
            elif action_type == 'dropdown_month':
                self.logger.info("📅 Gestione dropdown mese: 1 freccia giù + enter")
                time.sleep(1)  # Attendi che il dropdown si apra
                pyautogui.press('down')  # 1 freccia giù
                time.sleep(0.5)
                pyautogui.press('enter')  # Conferma selezione
                
            elif action_type == 'dropdown_year':
                self.logger.info("📅 Gestione dropdown anno: 25 frecce giù + enter")
                time.sleep(1)  # Attendi che il dropdown si apra
                for i in range(25):  # 25 frecce giù
                    pyautogui.press('down')
                    time.sleep(0.1)  # Piccola pausa tra le frecce
                time.sleep(0.5)
                pyautogui.press('enter')  # Conferma selezione
                
            elif action_type == 'click_below':
                self.logger.info("🖱️ Click 100px più in giù e 150px a destra")
                # Ottieni la posizione corrente del mouse
                current_x, current_y = pyautogui.position()
                # Fai click 100px più in giù e 150px a destra
                pyautogui.click(current_x + 150, current_y + 100)
                
            else:
                self.logger.warning(f"⚠️ Azione sconosciuta: {action_type}")
                return False
            
            self.logger.info(f"✅ Azione dropdown completata: {action_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Errore azione dropdown {action_type}: {e}")
            return False
    
    def _reload_page(self) -> bool:
        """
        Ricarica la pagina corrente del browser.
        
        Returns:
            True se il ricaricamento è riuscito, False altrimenti
        """
        try:
            self.logger.info("🔄 Ricaricamento pagina...")
            
            # Usa Cmd+R (macOS) o Ctrl+R (Windows/Linux) per ricaricare
            if platform.system() == "Darwin":
                pyautogui.hotkey('cmd', 'r')
            else:
                pyautogui.hotkey('ctrl', 'r')
            
            time.sleep(2)  # Attendi che il ricaricamento inizi
            
            # Sposta di nuovo la finestra sul primo schermo
            move_browser_to_primary_screen('chrome', self.logger)
            
            self.logger.info("✅ Pagina ricaricata con successo")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Errore ricaricamento pagina: {e}")
            return False
    
    def stop_automation(self):
        """
        Ferma l'automazione in corso.
        """
        self.is_running = False
        self.logger.info("⏹️ Richiesta di stop automazione PSN") 