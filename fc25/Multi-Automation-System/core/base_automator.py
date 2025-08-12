"""
Base Automator
==============

Classe base per tutti gli automator.
"""

import logging
import os
import platform
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
import pyautogui
from pynput.keyboard import Controller as KeyboardController

# Verifica disponibilità pynput per digitazione avanzata
try:
    keyboard = KeyboardController()
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False


class BaseAutomator:
    """
    Classe base per tutti gli automator.
    """
    
    def __init__(self, service_name: str, templates_subdir: str, logger: logging.Logger = None):
        """
        Inizializza l'automator base.
        
        Args:
            service_name: Nome del servizio
            templates_subdir: Sottocartella dei template
            logger: Logger per i messaggi
        """
        self.service_name = service_name
        self.logger = logger or logging.getLogger(__name__)
        self.is_running = False
        
        # Path e configurazione
        self.templates_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', 'templates', templates_subdir
        ))
        
        # Configurazione automazione
        self.match_confidence = 0.4
        self.max_retries = 3
        self.typing_delay = 0.05  # Stesso valore di Outlook_Account_Automation
        self.scroll_delay = 1.0
        self.click_delay = 8
        self.account_delay = 30
    
    def replace_placeholders(self, text: str, account_data: Dict[str, str]) -> str:
        """
        Sostituisce i placeholder nel testo con i valori dell'account.
        
        Args:
            text: Testo con placeholder {field_name}
            account_data: Dizionario con i dati dell'account
            
        Returns:
            Testo con placeholder sostituiti
        """
        if not text:
            return text
        
        for field, value in account_data.items():
            placeholder = f'{{{field}}}'
            text = text.replace(placeholder, value)
        
        return text
    
    def type_with_pynput(self, text: str) -> bool:
        """
        Digita testo usando pynput (metodo preferito).
        
        Args:
            text: Testo da digitare
            
        Returns:
            True se la digitazione è riuscita
        """
        if not PYNPUT_AVAILABLE:
            self.logger.error("❌ pynput non disponibile")
            return False
        
        try:
            self.logger.info(f"⌨️ Digitando con pynput: {text}")
            keyboard.type(text)
            self.logger.info(f"✅ Testo inserito con successo: {text}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Errore pynput: {e}")
            return False
    
    def type_text_hybrid(self, text: str) -> bool:
        """
        Digita testo usando il metodo migliore disponibile.
        
        Args:
            text: Testo da digitare
            
        Returns:
            True se la digitazione è riuscita
        """
        if PYNPUT_AVAILABLE:
            return self.type_with_pynput(text)
        else:
            self.logger.info("⚠️ Usando pyautogui come fallback")
            try:
                pyautogui.typewrite(text, interval=self.typing_delay)
                self.logger.info(f"✅ Testo inserito con pyautogui: {text}")
                return True
            except Exception as e:
                self.logger.error(f"❌ Errore pyautogui: {e}")
                return False
    
    def find_and_interact(self, template_name: str, text_to_type: str = "", 
                         click_hold_duration: float = 0, scroll_pixels: int = 0) -> bool:
        """
        Trova un template sullo schermo e interagisce con esso.
        
        Args:
            template_name: Nome del file template
            text_to_type: Testo da digitare (opzionale)
            click_hold_duration: Durata click (secondi)
            scroll_pixels: Pixel da scrollare (opzionale)
            
        Returns:
            True se l'interazione è riuscita
        """
        template_path = os.path.join(self.templates_dir, template_name)
        
        if not Path(template_path).exists():
            self.logger.error(f"❌ Template {self.service_name} non trovato: {template_path}")
            return False
        
        for attempt in range(self.max_retries):
            self.logger.info(f"🔄 Tentativo {self.service_name} {attempt + 1}/{self.max_retries}: {template_name}")
            
            try:
                # Screenshot e template matching
                screenshot = pyautogui.screenshot()
                screenshot_np = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                template = cv2.imread(template_path)
                
                if template is None:
                    self.logger.error(f"❌ Impossibile caricare template {self.service_name}: {template_path}")
                    return False
                
                # Template matching
                gray_screen = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)
                gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
                result = cv2.matchTemplate(gray_screen, gray_template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)
                match_percent = max_val * 100
                
                self.logger.info(f"📊 Livello corrispondenza {self.service_name}: {match_percent:.1f}% (soglia: {self.match_confidence*100:.1f}%)")
                
                if max_val >= self.match_confidence:
                    # Calcolo coordinate click
                    h, w = gray_template.shape
                    center_x = max_loc[0] + w // 2
                    center_y = max_loc[1] + h // 2
                    
                    # Scaling per schermi ad alta risoluzione
                    logical_width, logical_height = pyautogui.size()
                    physical_height, physical_width = screenshot_np.shape[:2]
                    scale_x = physical_width / logical_width
                    scale_y = physical_height / logical_height
                    final_x = int(center_x / scale_x)
                    final_y = int(center_y / scale_y)
                    
                    # Movimento e click
                    pyautogui.moveTo(final_x, final_y, duration=0.5)
                    time.sleep(0.1)
                    
                    if scroll_pixels > 0:
                        # Scroll verso il basso
                        self.logger.info(f"📜 Scrolling {scroll_pixels}px...")
                        pyautogui.scroll(-scroll_pixels)
                        time.sleep(self.scroll_delay)
                    else:
                        # Click con gestione tenuta
                        if click_hold_duration > 0:
                            pyautogui.mouseDown()
                            time.sleep(click_hold_duration)
                            pyautogui.mouseUp()
                        else:
                            pyautogui.click()
                        time.sleep(0.1)
                    
                    # Digitazione testo se richiesto
                    if text_to_type:
                        self.logger.info(f"⌨️ Digitando {self.service_name}: {text_to_type}")
                        
                        if click_hold_duration <= 0:
                            time.sleep(0.3)
                            pyautogui.click()
                            time.sleep(0.5)
                            
                            # Selezione tutto e cancellazione
                            if platform.system() == "Darwin":
                                pyautogui.hotkey('cmd', 'a')
                            else:
                                pyautogui.hotkey('ctrl', 'a')
                            time.sleep(0.1)
                            pyautogui.press('backspace')
                            time.sleep(0.2)
                        
                        success = self.type_text_hybrid(text_to_type)
                        if success:
                            self.logger.info(f"✅ Testo {self.service_name} completato: {text_to_type}")
                        else:
                            self.logger.warning(f"⚠️ Problemi nell'inserimento testo {self.service_name}: {text_to_type}")
                    else:
                        click_type = f"tenuto {click_hold_duration}s" if click_hold_duration > 0 else "normale"
                        self.logger.info(f"✅ Click {click_type} eseguito!")
                    
                    return True
                
                self.logger.warning(f"⚠️ Confidenza {self.service_name} insufficiente: {match_percent:.1f}%")
                
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"❌ Errore interazione {self.service_name} {template_name}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1)
        
        return False
    
    def open_url_in_new_tab(self, url: str) -> bool:
        """
        Apre un URL in una nuova tab del browser attuale.
        
        Args:
            url: URL da aprire
            
        Returns:
            True se l'apertura è riuscita
        """
        try:
            # Apri nuova tab con URL
            if platform.system() == "Darwin":
                pyautogui.hotkey('cmd', 't')  # Nuova tab
                time.sleep(1)
                pyautogui.hotkey('cmd', 'l')  # Focus URL bar
                time.sleep(0.5)
                pyautogui.typewrite(url)
                time.sleep(0.5)
                pyautogui.press('enter')
            else:
                pyautogui.hotkey('ctrl', 't')  # Nuova tab
                time.sleep(1)
                pyautogui.hotkey('ctrl', 'l')  # Focus URL bar
                time.sleep(0.5)
                pyautogui.typewrite(url)
                time.sleep(0.5)
                pyautogui.press('enter')
            
            self.logger.info(f"🌐 {self.service_name} aperto in nuova tab: {url}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Errore apertura {self.service_name}: {e}")
            return False
    
    def update_progress(self, step: int, total: int):
        """
        Aggiorna il progresso dell'automazione.
        
        Args:
            step: Step corrente
            total: Totale step
        """
        progress = (step / total) * 100
        self.logger.info(f"📊 Progresso {self.service_name}: {step}/{total} ({progress:.1f}%)")
    
    def _create_failure_data(self, account_data: Dict[str, str]) -> Dict[str, str]:
        """
        Crea dati di fallimento per un account.
        
        Args:
            account_data: Dati originali dell'account
            
        Returns:
            Dizionario con dati di fallimento
        """
        return {
            **account_data,
            f'{self.service_name}_status': 'failed',
            f'{self.service_name}_error': 'Automation failed'
        }
    
    def _create_success_data(self, account_data: Dict[str, str], 
                           additional_data: Dict[str, str] = None) -> Dict[str, str]:
        """
        Crea dati di successo per un account.
        
        Args:
            account_data: Dati originali dell'account
            additional_data: Dati aggiuntivi
            
        Returns:
            Dizionario con dati di successo
        """
        result = {
            **account_data,
            f'{self.service_name}_status': 'success'
        }
        
        if additional_data:
            result.update(additional_data)
        
        return result 