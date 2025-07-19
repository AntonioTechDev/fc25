"""
🤖 Automazione Browser - Ottimizzato per Tastiera Italiana con pynput
Script con gestione pynput per caratteri speciali e click hold personalizzabile
"""

import cv2
import numpy as np
import pyautogui  # Solo per mouse e screenshot
import time
import logging
import webbrowser
import subprocess
import platform
from pathlib import Path
from typing import Optional, Tuple

# Importa pynput per gestione tastiera migliorata
try:
    from pynput.keyboard import Key, Controller as KeyboardController
    keyboard = KeyboardController()
    PYNPUT_AVAILABLE = True
    print("✅ pynput disponibile - Usato per input di testo")
except ImportError:
    PYNPUT_AVAILABLE = False
    print("⚠️ pynput non installato - Fallback a pyautogui")
    print("💡 Installa con: pip install pynput")

# =================== CONFIGURAZIONE ===================

# URL e Browser
TARGET_URL = "https://signup.live.com/"
BROWSER = "chrome"  # chrome, firefox, safari
INCOGNITO_MODE = True

# Template Paths con Testi da Inserire e Durata Click
# Formato: (template_path, testo, durata_click_secondi)
# durata_click_secondi: 0 = click normale, >0 = click tenuto per X secondi
AUTOMATION_SEQUENCE = [
    ("./fc25/templates/email_input.png", "f358-fifa@outlook.com", 0),
    ("./fc25/templates/next_button.png", "", 0),  # Click normale
    ("./fc25/templates/password_input.png", "Sdser34df#", 0),
    ("./fc25/templates/next_button.png", "", 0),  # Click normale   
    ("./fc25/templates/birth_day_dropdown.png", "", 0),  # Click tenuto 2 secondi
    ("./fc25/templates/birth_day_option.png", "", 0),
    ("./fc25/templates/birth_month_dropdown.png", "", 0),  # Click tenuto 0 secondi
    ("./fc25/templates/birth_month_option.png", "", 0),
    ("./fc25/templates/birth_year_input.png", "1990", 0),
    ("./fc25/templates/date-btn-confirm.png", "", 0),
    ("./fc25/templates/first_name_input.png", "Mario", 0),
    ("./fc25/templates/last_name_input.png", "Rossi", 0),
    ("./fc25/templates/next_button.png", "", 0),
    ("./fc25/templates/captcha_button.png", "", 13),  # Click tenuto 10 secondi
    ("./fc25/templates/step-1-after-captcha.png", "", 0),
    ("./fc25/templates/step-1-after-captcha.png", "", 0),
    ("./fc25/templates/step-2-after-captcha.png", "", 0),
    ("./fc25/templates/step-3-after-captcha.png", "", 0),
    ("./fc25/templates/step-4-after-captcha.png", "", 0),
    ("./fc25/templates/step-5-after-captcha.png", "", 0),
    ("./fc25/templates/step-6-after-captcha.png", "", 0)
]

# Timing e Comportamento
PAGE_LOAD_DELAY = 8      # Secondi attesa caricamento pagina
CLICK_DELAY = 8         # Secondi tra ogni azione
MATCH_CONFIDENCE = 0.4    # Soglia matching (0.0-1.0)
MAX_RETRIES = 3           # Tentativi per elemento
MOUSE_SPEED = 0.5         # Velocità movimento mouse
TYPING_DELAY = 0.05       # Pausa tra caratteri

# Logging
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(message)s'

# =================== SETUP ===================

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

# =================== FUNZIONI ===================

def open_browser(url: str) -> bool:
    """Apre URL nel browser in modalità incognito"""
    try:
        system = platform.system().lower()
        
        if BROWSER == "chrome":
            if system == "darwin":
                cmd = ["open", "-a", "Google Chrome", "--args", "--incognito", url]
            elif system == "windows":
                cmd = ["start", "chrome", "--incognito", url]
            elif system == "linux":
                cmd = ["google-chrome", "--incognito", url]
            subprocess.run(cmd, shell=(system == "windows"))
            
        elif BROWSER == "firefox":
            if system == "darwin":
                cmd = ["open", "-a", "Firefox", "--args", "--private-window", url]
            elif system == "windows":
                cmd = ["start", "firefox", "-private-window", url]
            elif system == "linux":
                cmd = ["firefox", "--private-window", url]
            subprocess.run(cmd, shell=(system == "windows"))
            
        else:
            webbrowser.open(url)
            
        logger.info(f"✅ Browser aperto: {url}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Errore apertura browser: {e}")
        return False


def type_with_pynput(text: str):
    """Digita testo usando pynput - Gestisce meglio caratteri speciali"""
    
    if not PYNPUT_AVAILABLE:
        logger.error("❌ pynput non disponibile, usa: pip install pynput")
        return False
    
    try:
        logger.info(f"⌨️ Digitando con pynput: {text}")
        
        # pynput gestisce automaticamente layout e caratteri speciali
        keyboard.type(text)
        
        logger.info(f"✅ Testo inserito con successo: {text}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Errore pynput: {e}")
        return False


def type_text_hybrid(text: str):
    """Metodo ibrido: pynput se disponibile, altrimenti pyautogui"""
    
    if PYNPUT_AVAILABLE:
        # Usa pynput per testo (migliore per caratteri speciali)
        return type_with_pynput(text)
    else:
        # Fallback a pyautogui
        logger.info("⚠️ Usando pyautogui come fallback")
        try:
            pyautogui.typewrite(text, interval=0.05)
            logger.info(f"✅ Testo inserito con pyautogui: {text}")
            return True
        except Exception as e:
            logger.error(f"❌ Errore pyautogui: {e}")
            return False


def perform_click(x: int, y: int, hold_duration: float = 0):
    """Esegue click normale o tenuto per durata specificata"""
    
    if hold_duration <= 0:
        # Click normale
        pyautogui.click()
        logger.info("🖱️ Click normale eseguito")
    else:
        # Click tenuto
        logger.info(f"🖱️ Inizio click tenuto per {hold_duration} secondi...")
        pyautogui.mouseDown()
        time.sleep(hold_duration)
        pyautogui.mouseUp()
        logger.info(f"✅ Click tenuto completato ({hold_duration}s)")


def find_and_interact(template_path: str, text_to_type: str = "", click_hold_duration: float = 0) -> bool:
    """Trova template e ci clicca sopra, opzionalmente digita testo e tiene premuto click"""
    
    if not Path(template_path).exists():
        logger.error(f"❌ Template non trovato: {template_path}")
        return False
    
    for attempt in range(MAX_RETRIES):
        logger.info(f"🔄 Tentativo {attempt + 1}/{MAX_RETRIES}")
        
        try:
            # Cattura schermo
            screenshot = pyautogui.screenshot()
            screenshot_np = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Carica template
            template = cv2.imread(template_path)
            if template is None:
                logger.error(f"❌ Impossibile caricare template: {template_path}")
                return False
            
            # Template matching
            gray_screen = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)
            gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            
            result = cv2.matchTemplate(gray_screen, gray_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            
            # Log livello corrispondenza
            match_percent = max_val * 100
            logger.info(f"📊 Livello corrispondenza: {match_percent:.1f}% (soglia: {MATCH_CONFIDENCE*100:.1f}%)")
            
            if max_val >= MATCH_CONFIDENCE:
                # Calcola centro elemento
                h, w = gray_template.shape
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                
                # Conversione coordinate Retina
                logical_width, logical_height = pyautogui.size()
                physical_height, physical_width = screenshot_np.shape[:2]
                
                scale_x = physical_width / logical_width
                scale_y = physical_height / logical_height
                
                final_x = int(center_x / scale_x)
                final_y = int(center_y / scale_y)
                
                # Muovi mouse alla posizione
                logger.info(f"🎯 Posizionamento su: ({final_x}, {final_y})")
                pyautogui.moveTo(final_x, final_y, duration=MOUSE_SPEED)
                time.sleep(0.1)
                
                # Esegui click normale o tenuto
                perform_click(final_x, final_y, click_hold_duration)
                
                # Se c'è testo da digitare
                if text_to_type:
                    logger.info(f"⌨️ Digitando testo: {text_to_type}")
                    
                    # Secondo click per assicurare focus (solo se non era un click tenuto)
                    if click_hold_duration <= 0:
                        time.sleep(0.3)
                        pyautogui.click()
                        time.sleep(0.5)
                        
                        # Pulisce campo esistente
                        if platform.system() == "Darwin":
                            pyautogui.hotkey('cmd', 'a')
                        else:
                            pyautogui.hotkey('ctrl', 'a')
                        time.sleep(0.1)
                        pyautogui.press('backspace')
                        time.sleep(0.2)
                    
                    # Digita testo usando metodo ibrido pynput/pyautogui
                    success = type_text_hybrid(text_to_type)
                    
                    if success:
                        logger.info(f"✅ Testo completato: {text_to_type}")
                    else:
                        logger.warning(f"⚠️ Problemi nell'inserimento testo: {text_to_type}")
                else:
                    click_type = f"tenuto {click_hold_duration}s" if click_hold_duration > 0 else "normale"
                    logger.info(f"✅ Click {click_type} eseguito! (Match: {match_percent:.1f}%)")
                
                return True
            
            logger.warning(f"⚠️ Confidenza insufficiente: {match_percent:.1f}%")
            
            if attempt < MAX_RETRIES - 1:
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"❌ Errore: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(1)
    
    return False


def run_automation():
    """Esegue automazione completa"""
    
    logger.info(f"🚀 Avvio automazione: {TARGET_URL}")
    logger.info(f"🇮🇹 Layout tastiera: Italiano")
    logger.info(f"🔒 Modalità incognito: {'Attiva' if INCOGNITO_MODE else 'Disattiva'}")
    
    # Apri browser
    if not open_browser(TARGET_URL):
        logger.error("❌ Impossibile aprire browser")
        return False
    
    # Attendi caricamento
    logger.info(f"⏳ Attendo {PAGE_LOAD_DELAY} secondi...")
    time.sleep(PAGE_LOAD_DELAY)
    
    # Processa sequenza
    total = len(AUTOMATION_SEQUENCE)
    
    for i, (template_path, text_input, click_duration) in enumerate(AUTOMATION_SEQUENCE, 1):
        
        template_name = Path(template_path).stem
        
        # Log descrittivo
        log_parts = [f"🎯 [{i}/{total}] Elemento: {template_name}"]
        if text_input:
            log_parts.append(f"→ '{text_input}'")
        if click_duration > 0:
            log_parts.append(f"(click {click_duration}s)")
        else:
            log_parts.append("(click normale)")
            
        logger.info(" ".join(log_parts))
        
        success = find_and_interact(template_path, text_input, click_duration)
        
        if success:
            action_desc = []
            if text_input:
                action_desc.append("testo")
            click_type = f"click {click_duration}s" if click_duration > 0 else "click"
            action_desc.append(click_type)
            logger.info(f"✅ {template_name} completato ({' + '.join(action_desc)})")
        else:
            logger.warning(f"⚠️ {template_name} fallito")
        
        # Pausa tra elementi
        if i < total:
            logger.info(f"⏳ Pausa {CLICK_DELAY} secondi...")
            time.sleep(CLICK_DELAY)
    
    logger.info("🏁 Automazione terminata!")
    return True


# =================== MAIN ===================

if __name__ == "__main__":
    try:
        logger.info("🇮🇹 Script ottimizzato per tastiera italiana con click hold")
        run_automation()
        print("🎉 Automazione completata!")
        
    except KeyboardInterrupt:
        print("\n🛑 Interrotto dall'utente")
        
    except Exception as e:
        print(f"❌ Errore: {e}")