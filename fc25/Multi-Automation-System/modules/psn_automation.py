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
import subprocess
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
from core.nordvpn_handler import NordVPNHandler


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
        
        # Configurazione NordVPN
        self.nordvpn_handler = NordVPNHandler(self, self.logger)
        
        # Sequenza automazione PSN
        self.automation_sequence = [
            ('1.png', '', 0),
            ('2.png', '', 0),
            ('3-PSN-day-select.png', '', 0, 'dropdown_day'),  # Dropdown giorno: 1 freccia giù + enter
            ('4-PSN-mounth-select.png', '', 0, 'dropdown_month'),  # Dropdown mese: 1 freccia giù + enter
            ('5-PSN-year.png', '', 0, 'dropdown_year'),  # Dropdown anno: 25 frecce giù + enter
            ('9-PSN-avanti.png', '', 0),
            ('6-PSN-email-input.png', '{outlook_email}', 0),
             ('', '', 0, 100),  # Scroll di 100px verso il basso
            ('7-PSN-password.png', '{outlook_psw}', 0),
            ('8-PSN-re-password.png', '{outlook_psw}', 0),
            ('8-PSN-re-password.png', '', 0, 0, 'click_below'),  # Click 100px più in giù
            ('9-PSN-avanti.png', '', 0),
            ('', '', 0, 100),  # Scroll di 100px verso il basso
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
            
            # Cambio IP obbligatorio (come MAC address)
            self.logger.info("🔧 Cambio IP obbligatorio con NordVPN...")
            if self.nordvpn_handler.initialize_nordvpn():
                self.logger.info("✅ Cambio IP completato con successo")
            else:
                self.logger.warning("⚠️ Fallimento cambio IP, continuo senza VPN")
            
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
                    template, text_input, click_duration, fourth_param = step_data
                    # Controlla se il quarto parametro è un numero (scroll) o stringa (azione)
                    if isinstance(fourth_param, int):
                        scroll_pixels = fourth_param
                        special_action = None
                    else:
                        scroll_pixels = 0
                        special_action = fourth_param
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
                if template == '' and scroll_pixels > 0:
                    # Step di solo scroll senza template
                    self.logger.info(f"📜 Eseguo scroll di {scroll_pixels}px")
                    self._perform_mouse_scroll(scroll_pixels)
                    time.sleep(1)  # Attendi che lo scroll si completi
                    step_success = True
                elif template == '':
                    # Template vuoto senza scroll - salta questo step
                    self.logger.info("⏭️ Step con template vuoto - salto")
                    step_success = True
                else:
                    # Step normale con template
                    # Se è un bottone "avanti", salva URL prima del click
                    is_forward_button = 'avanti' in template.lower()
                    url_before = ""
                    if is_forward_button:
                        url_before = self._get_current_url()
                        self.logger.info(f"🔗 URL prima del click: {url_before}")
                    
                    step_success = self.find_and_interact(template, text_to_type, click_duration, scroll_pixels)
                    
                    # Se è un bottone "avanti", verifica cambio URL
                    if step_success and is_forward_button:
                        step_success = self._verify_url_change(url_before, template, i)
                
                # Verifica alert di errore solo dopo click su bottoni "avanti"
                if step_success and template != '' and 'avanti' in template.lower():
                    step_success = self._check_for_alert_and_retry(template, text_to_type, click_duration, scroll_pixels, i)
                
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
    


    def _get_current_url(self) -> str:
        """
        Ottiene l'URL corrente del browser Chrome.
        
        Returns:
            URL corrente o stringa vuota se non riuscito
        """
        try:
            # Usa AppleScript per ottenere l'URL di Chrome (macOS)
            if platform.system() == "Darwin":
                script = '''
                tell application "Google Chrome"
                    return URL of active tab of front window
                end tell
                '''
                result = subprocess.run(['osascript', '-e', script], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return result.stdout.strip()
            return ""
        except Exception as e:
            self.logger.error(f"❌ Errore ottenimento URL: {e}")
            return ""

    def _verify_url_change(self, url_before: str, template: str, step_index: int) -> bool:
        """
        Verifica se l'URL è cambiato dopo il click su un bottone "avanti" con retry.
        
        Args:
            url_before: URL prima del click
            template: Nome del template dello step
            step_index: Indice dello step
            
        Returns:
            True se l'URL è cambiato o se non è possibile verificare, False altrimenti
        """
        try:
            if not url_before:
                self.logger.warning(f"⚠️ Impossibile verificare cambio URL per step {step_index}: URL iniziale vuoto")
                return True  # Continua se non possiamo verificare
            
            max_retries = 2  # Massimo 2 tentativi di verifica URL
            wait_times = [5, 15, 20]  # Tempi di attesa: 5s, 15s, 20s
            
            for attempt in range(max_retries + 1):
                # Attendi che la pagina si carichi
                wait_time = wait_times[attempt]
                self.logger.info(f"⏳ Attendo {wait_time} secondi per caricamento pagina (tentativo {attempt + 1}/{max_retries + 1})")
                time.sleep(wait_time)
                
                # Ottieni URL corrente
                url_after = self._get_current_url()
                
                if not url_after:
                    self.logger.warning(f"⚠️ Impossibile ottenere URL dopo click per step {step_index} (tentativo {attempt + 1})")
                    if attempt < max_retries:
                        continue
                    return True  # Continua se non possiamo verificare
                
                # Verifica se l'URL è cambiato
                if url_before != url_after:
                    self.logger.info(f"✅ URL cambiato correttamente per step {step_index}")
                    self.logger.info(f"🔗 Da: {url_before}")
                    self.logger.info(f"🔗 A: {url_after}")
                    return True
                else:
                    if attempt < max_retries:
                        self.logger.warning(f"⚠️ URL non è cambiato per step {step_index} (tentativo {attempt + 1}/{max_retries + 1})")
                    else:
                        self.logger.warning(f"⚠️ URL non è cambiato per step {step_index} dopo {max_retries + 1} tentativi: {template}")
                        self.logger.info("🔍 Verifico se è presente alert PSN...")
                        
                        # Verifica alert PSN se URL non è cambiato
                        alert_found = self.find_and_interact('alert-psn-error.png', '', 0)
                        if alert_found:
                            self.logger.warning("⚠️ Alert di errore PSN trovato - URL non cambiato a causa di errore")
                            return False
                        else:
                            self.logger.warning("🔄 Nessun alert trovato - possibile caricamento molto lento")
                            return False
                
        except Exception as e:
            self.logger.error(f"❌ Errore verifica cambio URL step {step_index}: {e}")
            return True  # Continua in caso di errore

    def _check_for_alert_and_retry(self, template: str, text_to_type: str, click_duration: float, scroll_pixels: int, step_index: int) -> bool:
        """
        Verifica se è presente l'alert di errore PSN e ripete lo step se necessario.
        
        Args:
            template: Nome del template dello step
            text_to_type: Testo da digitare
            click_duration: Durata del click
            scroll_pixels: Pixel di scroll
            step_index: Indice dello step
            
        Returns:
            True se lo step è riuscito, False altrimenti
        """
        try:
            # Attendi 5 secondi per permettere all'alert di apparire
            time.sleep(5)
            
            # Cerca l'alert di errore
            alert_found = self.find_and_interact('alert-psn-error.png', '', 0)
            
            if alert_found:
                self.logger.warning(f"⚠️ Alert di errore PSN trovato dopo step {step_index}: {template}")
                self.logger.info("🔄 Ripeto lo step...")
                
                # Attendi che l'alert scompaia
                time.sleep(3)
                
                # Ripeti lo step
                retry_success = self.find_and_interact(template, text_to_type, click_duration, scroll_pixels)
                
                if retry_success:
                    self.logger.info("✅ Step ripetuto con successo")
                    return True
                else:
                    self.logger.error(f"❌ Step {step_index} fallito anche al retry")
                    return False
            else:
                # Nessun alert trovato, step completato con successo
                self.logger.info(f"✅ Step {step_index} completato senza errori")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Errore verifica alert step {step_index}: {e}")
            return True  # Continua anche in caso di errore nella verifica

    def _perform_mouse_scroll(self, pixels: int):
        """
        Esegue uno scroll naturale come la rotellina del mouse.
        
        Args:
            pixels: Numero di pixel da scorrere (positivo = giù, negativo = su)
        """
        try:
            # Simula scroll naturale con rotellina del mouse
            # Un "click" della rotellina = circa 3 righe di testo
            scroll_clicks = max(1, pixels // 30)  # Almeno 1 click
            
            if pixels > 0:
                # Scroll verso il basso (come rotellina verso il basso)
                pyautogui.vscroll(-scroll_clicks)  # Negativo per scroll verso il basso
            else:
                # Scroll verso l'alto (come rotellina verso l'alto)
                pyautogui.vscroll(abs(scroll_clicks))
                
            self.logger.info(f"📜 Scroll naturale eseguito: {scroll_clicks} click rotellina ({pixels}px)")
            
        except Exception as e:
            self.logger.error(f"❌ Errore durante lo scroll: {e}")

    def stop_automation(self):
        """
        Ferma l'automazione in corso.
        """
        self.is_running = False
        self.logger.info("⏹️ Richiesta di stop automazione PSN") 