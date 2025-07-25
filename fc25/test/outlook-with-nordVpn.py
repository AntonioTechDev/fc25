"""
🤖 Automazione Browser - Multi-Account da CSV
Script con gestione CSV per creazione multipla account Microsoft Live
"""

import cv2
import numpy as np
import pyautogui  # Solo per mouse e screenshot
import time
import logging
import webbrowser
import subprocess
import platform
import csv
from pathlib import Path
from typing import Optional, Tuple, List, Dict

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

# File CSV con dati account
CSV_FILE_PATH = "./fc25/accounts.csv"  # Percorso file CSV
# Formato CSV: email,password,first_name,last_name,birth_year
# Esempio: mario.rossi@outlook.com,Password123!,Mario,Rossi,1990

# Template Paths - Ora con placeholder per dati dinamici
# Formato: (template_path, campo_csv_o_testo_fisso, durata_click_secondi, [custom_click_delay])
AUTOMATION_SEQUENCE = [
    ("./fc25/templates/nord-vpn-icon-MAC.png", "{email}", 0),
    ("./fc25/templates/nord-vpn-disconnet.png", "{email}", 0),
    ("./fc25/templates/nord-vpn-connect.png", "{email}", 0),
    
    ("./fc25/templates/email_input.png", "{email}", 0),
    ("./fc25/templates/next_button.png", "", 0),
    ("./fc25/templates/password_input.png", "{password}", 0),
    ("./fc25/templates/next_button.png", "", 0),   
    
    ("./fc25/templates/birth_day_dropdown.png", "", 0),
    ("./fc25/templates/birth_day_option.png", "", 0),
    ("./fc25/templates/birth_month_dropdown.png", "", 0),
    ("./fc25/templates/birth_month_option.png", "", 0),
    ("./fc25/templates/birth_year_input.png", "{birth_year}", 0),
    ("./fc25/templates/date-btn-confirm.png", "", 0),
    ("./fc25/templates/first_name_input.png", "{first_name}", 0),
    ("./fc25/templates/last_name_input.png", "{last_name}", 0),
    ("./fc25/templates/next_button.png", "", 0),
    
    ("./fc25/templates/captcha_button.png", "", 13, 15),
    ("./fc25/templates/step-1-after-captcha.png", "", 0),
    ("./fc25/templates/step-1-after-captcha.png", "", 0),
    ("./fc25/templates/step-2-after-captcha.png", "", 0),
    ("./fc25/templates/step-3-after-captcha.png", "", 20),
    ("./fc25/templates/step-4-after-captcha.png", "", 0),
    ("./fc25/templates/step-5-after-captcha.png", "", 20),
    ("./fc25/templates/step-6-after-captcha.png", "", 0)
]

# Timing e Comportamento
PAGE_LOAD_DELAY = 8           # Secondi attesa caricamento pagina
CLICK_DELAY = 8              # Secondi tra ogni azione
ACCOUNT_DELAY = 30           # Secondi tra un account e l'altro
MATCH_CONFIDENCE = 0.4       # Soglia matching (0.0-1.0)
MAX_RETRIES = 3              # Tentativi per elemento
MOUSE_SPEED = 0.5            # Velocità movimento mouse
TYPING_DELAY = 0.05          # Pausa tra caratteri

# Logging
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(message)s'

# =================== SETUP ===================

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

# =================== FUNZIONI CSV ===================

def load_accounts_from_csv(csv_path: str) -> List[Dict[str, str]]:
    """Carica account dal file CSV"""
    
    if not Path(csv_path).exists():
        logger.error(f"❌ File CSV non trovato: {csv_path}")
        return []
    
    accounts = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for i, row in enumerate(reader, 1):
                # Verifica che ci siano tutti i campi necessari
                required_fields = ['email', 'password', 'first_name', 'last_name', 'birth_year']
                missing_fields = [field for field in required_fields if field not in row or not row[field].strip()]
                
                if missing_fields:
                    logger.warning(f"⚠️ Riga {i} saltata - Campi mancanti: {missing_fields}")
                    continue
                
                accounts.append({
                    'email': row['email'].strip(),
                    'password': row['password'].strip(),
                    'first_name': row['first_name'].strip(),
                    'last_name': row['last_name'].strip(),
                    'birth_year': row['birth_year'].strip()
                })
                
        logger.info(f"✅ Caricati {len(accounts)} account dal CSV")
        return accounts
        
    except Exception as e:
        logger.error(f"❌ Errore lettura CSV: {e}")
        return []


def replace_placeholders(text: str, account_data: Dict[str, str]) -> str:
    """Sostituisce i placeholder nel testo con dati dell'account"""
    
    if not text:
        return text
        
    # Sostituisce i placeholder {campo} con i valori dell'account
    for field, value in account_data.items():
        placeholder = f"{{{field}}}"
        text = text.replace(placeholder, value)
    
    return text

# =================== FUNZIONI ORIGINALI ===================

def close_all_chrome_windows():
    """Chiude tutte le finestre Chrome aperte"""
    try:
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            # Chiude Chrome completamente
            subprocess.run(["osascript", "-e", 'tell application "Google Chrome" to quit'], 
                         capture_output=True)
            logger.info("🗙 Chiuse tutte le finestre Chrome (macOS)")
            
        elif system == "windows":  # Windows
            # Termina tutti i processi Chrome
            subprocess.run(["taskkill", "/f", "/im", "chrome.exe"], 
                         capture_output=True, shell=True)
            logger.info("🗙 Chiuse tutte le finestre Chrome (Windows)")
            
        elif system == "linux":  # Linux
            # Termina tutti i processi Chrome
            subprocess.run(["pkill", "-f", "chrome"], 
                         capture_output=True)
            logger.info("🗙 Chiuse tutte le finestre Chrome (Linux)")
            
        # Pausa per assicurarsi che Chrome si chiuda completamente
        time.sleep(2)
        
    except Exception as e:
        logger.warning(f"⚠️ Errore chiusura Chrome: {e}")


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


def run_single_account_automation(account_data: Dict[str, str]) -> bool:
    """Esegue automazione per un singolo account"""
    
    logger.info(f"👤 Iniziando automazione per: {account_data['email']}")
    
    # Processa sequenza con dati dell'account
    total = len(AUTOMATION_SEQUENCE)
    
    for i, elem in enumerate(AUTOMATION_SEQUENCE, 1):
        # Supporta tuple da 3 o 4 elementi
        if len(elem) == 3:
            template_path, text_input, click_duration = elem
            custom_delay = None
        elif len(elem) == 4:
            template_path, text_input, click_duration, custom_delay = elem
        else:
            logger.error(f"❌ Sequenza malformata all'indice {i-1}: {elem}")
            continue
        
        # Sostituisce placeholder con dati reali
        processed_text = replace_placeholders(text_input, account_data)
        
        template_name = Path(template_path).stem
        
        # Log descrittivo
        log_parts = [f"🎯 [{i}/{total}] Elemento: {template_name}"]
        if processed_text:
            # Maschera email e password nei log per privacy
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
        
        logger.info(" ".join(log_parts))
        
        success = find_and_interact(template_path, processed_text, click_duration)
        
        if success:
            action_desc = []
            if processed_text:
                action_desc.append("testo")
            click_type = f"click {click_duration}s" if click_duration > 0 else "click"
            action_desc.append(click_type)
            logger.info(f"✅ {template_name} completato ({' + '.join(action_desc)})")
        else:
            logger.warning(f"⚠️ {template_name} fallito")
            # Continua comunque con il prossimo step
        
        # Pausa tra elementi
        if i < total:
            delay_to_use = custom_delay if (custom_delay is not None and custom_delay > 0) else CLICK_DELAY
            logger.info(f"⏳ Pausa {delay_to_use} secondi...")
            time.sleep(delay_to_use)
    
    logger.info(f"✅ Automazione completata per: {account_data['email']}")
    return True


def run_automation():
    """Esegue automazione completa per tutti gli account"""
    
    logger.info(f"🚀 Avvio automazione multi-account: {TARGET_URL}")
    logger.info(f"🇮🇹 Layout tastiera: Italiano")
    logger.info(f"🔒 Modalità incognito: {'Attiva' if INCOGNITO_MODE else 'Disattiva'}")
    
    # Carica account dal CSV
    accounts = load_accounts_from_csv(CSV_FILE_PATH)
    
    if not accounts:
        logger.error("❌ Nessun account trovato nel CSV")
        return False
    
    logger.info(f"📊 Trovati {len(accounts)} account da processare")
    
    # Processa ogni account
    for account_index, account_data in enumerate(accounts, 1):
        logger.info(f"🔄 ===== ACCOUNT {account_index}/{len(accounts)} =====")
        
        try:
            # Chiudi tutte le finestre Chrome prima di aprire la nuova
            logger.info("🧹 Pulizia finestre Chrome...")
            close_all_chrome_windows()
            
            # Apri browser fresco per questo account
            if not open_browser(TARGET_URL):
                logger.error(f"❌ Impossibile aprire browser per account {account_index}")
                continue
            
            # Attendi caricamento
            logger.info(f"⏳ Attendo {PAGE_LOAD_DELAY} secondi...")
            time.sleep(PAGE_LOAD_DELAY)
            
            # Esegui automazione per questo account
            success = run_single_account_automation(account_data)
            
            if success:
                logger.info(f"✅ Account {account_index} completato con successo!")
            else:
                logger.warning(f"⚠️ Account {account_index} completato con errori")
            
            # Pausa tra account (tranne ultimo)
            if account_index < len(accounts):
                logger.info(f"⏳ Pausa {ACCOUNT_DELAY} secondi prima del prossimo account...")
                time.sleep(ACCOUNT_DELAY)
                
        except Exception as e:
            logger.error(f"❌ Errore account {account_index}: {e}")
            continue
    
    # Cleanup finale - chiude tutte le finestre Chrome
    logger.info("🧹 Cleanup finale...")
    close_all_chrome_windows()
    
    logger.info("🏁 Automazione multi-account completata!")
    return True


# =================== MAIN ===================

if __name__ == "__main__":
    try:
        logger.info("🔄 Script automazione multi-account da CSV")
        run_automation()
        print("🎉 Automazione multi-account completata!")
        
    except KeyboardInterrupt:
        print("\n🛑 Interrotto dall'utente")
        
    except Exception as e:
        print(f"❌ Errore: {e}")