"""
Base Automator
==============

Classe base per tutti i moduli di automazione.
Fornisce interfaccia comune e funzionalità condivise.
"""

import logging
import os
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
import pyautogui


class BaseAutomator(ABC):
    """
    Classe base per tutti i moduli di automazione.
    Fornisce interfaccia comune e funzionalità condivise.
    """
    
    def __init__(self, service_name: str, image_folder: str, logger: logging.Logger = None):
        """
        Inizializza l'automator base.
        
        Args:
            service_name: Nome del servizio (es. 'outlook', 'psn')
            image_folder: Cartella con le immagini template
            logger: Logger per i messaggi
        """
        self.service_name = service_name
        self.logger = logger or logging.getLogger(f"{service_name}_automator")
        
        # Path delle immagini
        self.templates_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), f'../templates/{image_folder}')
        )
        
        # Configurazione di default
        self.match_confidence = 0.4
        self.max_retries = 3
        self.click_delay = 5
        self.scroll_delay = 2
        
        # Stato dell'automazione
        self.is_running = False
        self.current_step = 0
        self.total_steps = 0
        
    def set_config(self, **kwargs):
        """
        Imposta la configurazione dell'automator.
        
        Args:
            **kwargs: Parametri di configurazione
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                self.logger.info(f"🔧 Configurazione {key}: {value}")
    
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
                        # Click normale
                        pyautogui.click()
                        time.sleep(0.1)
                    
                    # Digitazione testo se richiesto
                    if text_to_type:
                        self.logger.info(f"⌨️ Digitando {self.service_name}: {text_to_type}")
                        time.sleep(0.3)
                        
                        # Selezione tutto e cancellazione
                        import platform
                        if platform.system() == "Darwin":
                            pyautogui.hotkey('cmd', 'a')
                        else:
                            pyautogui.hotkey('ctrl', 'a')
                        time.sleep(0.1)
                        pyautogui.press('backspace')
                        time.sleep(0.2)
                        
                        # Digitazione
                        pyautogui.typewrite(text_to_type, interval=0.05)
                        self.logger.info(f"✅ Testo {self.service_name} completato: {text_to_type}")
                    
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
            import platform
            
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
        self.current_step = step
        self.total_steps = total
        progress = (step / total) * 100 if total > 0 else 0
        self.logger.info(f"📊 Progresso {self.service_name}: {step}/{total} ({progress:.1f}%)")
    
    @abstractmethod
    def run_automation(self, account_data: Dict[str, str]) -> Dict[str, str]:
        """
        Esegue l'automazione specifica del servizio.
        
        Args:
            account_data: Dati dell'account
            
        Returns:
            Dizionario con i dati generati
        """
        pass
    
    def get_service_info(self) -> Dict[str, str]:
        """
        Restituisce informazioni sul servizio.
        
        Returns:
            Dizionario con informazioni del servizio
        """
        return {
            'service_name': self.service_name,
            'templates_dir': self.templates_dir,
            'is_running': self.is_running,
            'current_step': self.current_step,
            'total_steps': self.total_steps
        } 