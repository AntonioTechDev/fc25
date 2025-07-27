"""
Multi Outlook Account Creator - Automation Engine
================================================

Autore: Antonio De Biase
Versione: 2.0.0
Data: 2025-07-27

Descrizione:
Script di automazione per la creazione automatica di account Outlook.
Utilizza riconoscimento immagini per navigare attraverso il processo di registrazione.

QUICK START:
1. Configura le variabili nella sezione CONFIGURAZIONE
2. Assicurati che i template siano nella cartella templates/
3. Prepara il file accounts.csv con i dati degli account
4. Esegui: python -m multi_outlook_creator.main

Dipendenze:
- opencv-python (cv2)
- pyautogui
- pynput (opzionale)
- numpy
"""

import logging
import os
import platform
import time
from pathlib import Path
from typing import Dict

import cv2
import numpy as np
import pyautogui
from pynput.keyboard import Controller as KeyboardController

from multi_outlook_creator.backend.browser_utils import close_all_chrome_windows, open_browser
from multi_outlook_creator.backend.csv_utils import load_accounts_from_csv, update_account_status_in_csv
from multi_outlook_creator.backend.mac_utils import change_mac_address

# =============================================================================
# CONFIGURAZIONE
# =============================================================================

# === FILE E PATH ===
TEMPLATES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../templates'))
CSV_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../accounts.csv'))

# === BROWSER ===
BROWSER = 'chrome'              # Browser da utilizzare (chrome, firefox)
INCOGNITO_MODE = True           # Modalità incognito/privata
CHROME_OPEN_INDEX = 0           # Step in cui aprire Chrome (0 = subito)

# === TIMING E DELAY ===
PAGE_LOAD_DELAY = 15            # Attesa dopo apertura browser (secondi)
CLICK_DELAY = 8                 # Attesa tra ogni azione (secondi)
ACCOUNT_DELAY = 30              # Attesa tra un account e l'altro (secondi)
MAC_WAIT_SECONDS = 10           # Attesa dopo cambio MAC address (secondi)
TYPING_DELAY = 0.05             # Pausa tra caratteri digitati (secondi)

# === AUTOMAZIONE ===
MATCH_CONFIDENCE = 0.4          # Soglia matching immagini (0.0-1.0, più alto = più preciso)
MAX_RETRIES = 3                 # Tentativi per ogni template
MOUSE_SPEED = 0.5               # Velocità movimento mouse (secondi)

# === SEQUENZA AUTOMAZIONE ===
# Formato: (template_path, testo_da_digitare, durata_click, [delay_custom])
AUTOMATION_SEQUENCE = [
    (os.path.join(TEMPLATES_DIR, 'email_input.png'), '{email}', 0),
    (os.path.join(TEMPLATES_DIR, 'next_button.png'), '', 0),
    (os.path.join(TEMPLATES_DIR, 'password_input.png'), '{password}', 0),
    (os.path.join(TEMPLATES_DIR, 'next_button.png'), '', 0),
    (os.path.join(TEMPLATES_DIR, 'birth_day_dropdown.png'), '', 0),
    (os.path.join(TEMPLATES_DIR, 'birth_day_option.png'), '', 0),
    (os.path.join(TEMPLATES_DIR, 'birth_month_dropdown.png'), '', 0),
    (os.path.join(TEMPLATES_DIR, 'birth_month_option.png'), '', 0),
    (os.path.join(TEMPLATES_DIR, 'birth_year_input.png'), '{birth_year}', 0),
    (os.path.join(TEMPLATES_DIR, 'date-btn-confirm.png'), '', 0),
    (os.path.join(TEMPLATES_DIR, 'first_name_input.png'), '{first_name}', 0),
    (os.path.join(TEMPLATES_DIR, 'last_name_input.png'), '{last_name}', 0),
    (os.path.join(TEMPLATES_DIR, 'next_button.png'), '', 0),
    (os.path.join(TEMPLATES_DIR, 'captcha_button.png'), '', 13, 15),
    (os.path.join(TEMPLATES_DIR, 'step-1-after-captcha.png'), '', 0),
    (os.path.join(TEMPLATES_DIR, 'step-1-after-captcha.png'), '', 0),
    (os.path.join(TEMPLATES_DIR, 'step-2-after-captcha.png'), '', 0),
    (os.path.join(TEMPLATES_DIR, 'step-3-after-captcha.png'), '', 20),
    (os.path.join(TEMPLATES_DIR, 'step-4-after-captcha.png'), '', 0),
    (os.path.join(TEMPLATES_DIR, 'step-5-after-captcha.png'), '', 20),
    (os.path.join(TEMPLATES_DIR, 'step-6-after-captcha.png'), '', 0)
]

# =============================================================================
# INIZIALIZZAZIONE
# =============================================================================

# Verifica disponibilità pynput per digitazione avanzata
try:
    keyboard = KeyboardController()
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

# =============================================================================
# FUNZIONI UTILITY
# =============================================================================

def replace_placeholders(text: str, account_data: Dict[str, str]) -> str:
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


def type_with_pynput(text: str, logger: logging.Logger) -> bool:
    """
    Digita testo usando pynput (metodo preferito).
    
    Args:
        text: Testo da digitare
        logger: Logger per i messaggi
        
    Returns:
        True se la digitazione è riuscita
    """
    if not PYNPUT_AVAILABLE:
        logger.error("❌ pynput non disponibile")
        return False
    
    try:
        logger.info(f"⌨️ Digitando con pynput: {text}")
        keyboard.type(text)
        logger.info(f"✅ Testo inserito con successo: {text}")
        return True
    except Exception as e:
        logger.error(f"❌ Errore pynput: {e}")
        return False


def type_text_hybrid(text: str, logger: logging.Logger) -> bool:
    """
    Digita testo usando il metodo migliore disponibile.
    
    Args:
        text: Testo da digitare
        logger: Logger per i messaggi
        
    Returns:
        True se la digitazione è riuscita
    """
    if PYNPUT_AVAILABLE:
        return type_with_pynput(text, logger)
    else:
        logger.info("⚠️ Usando pyautogui come fallback")
        try:
            pyautogui.typewrite(text, interval=TYPING_DELAY)
            logger.info(f"✅ Testo inserito con pyautogui: {text}")
            return True
        except Exception as e:
            logger.error(f"❌ Errore pyautogui: {e}")
            return False


def perform_click(x: int, y: int, hold_duration: float = 0):
    """
    Esegue un click del mouse con opzione di tenuta.
    
    Args:
        x: Coordinata X
        y: Coordinata Y
        hold_duration: Durata della tenuta del click (secondi)
    """
    if hold_duration <= 0:
        pyautogui.click()
    else:
        pyautogui.mouseDown()
        time.sleep(hold_duration)
        pyautogui.mouseUp()


# =============================================================================
# FUNZIONI DI AUTOMAZIONE
# =============================================================================

def find_and_interact(template_path: str, text_to_type: str = "", 
                     click_hold_duration: float = 0, logger: logging.Logger = None) -> bool:
    """
    Trova un template sullo schermo e interagisce con esso.
    
    Args:
        template_path: Path al file template immagine
        text_to_type: Testo da digitare (opzionale)
        click_hold_duration: Durata click (secondi)
        logger: Logger per i messaggi
        
    Returns:
        True se l'interazione è riuscita
    """
    if not Path(template_path).exists():
        if logger:
            logger.error(f"❌ Template non trovato: {template_path}")
        return False
    
    for attempt in range(MAX_RETRIES):
        if logger:
            logger.info(f"🔄 Tentativo {attempt + 1}/{MAX_RETRIES}")
        
        try:
            # Screenshot e template matching
            screenshot = pyautogui.screenshot()
            screenshot_np = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            template = cv2.imread(template_path)
            
            if template is None:
                if logger:
                    logger.error(f"❌ Impossibile caricare template: {template_path}")
                return False
            
            # Template matching
            gray_screen = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)
            gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            result = cv2.matchTemplate(gray_screen, gray_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            match_percent = max_val * 100
            
            if logger:
                logger.info(f"📊 Livello corrispondenza: {match_percent:.1f}% (soglia: {MATCH_CONFIDENCE*100:.1f}%)")
            
            if max_val >= MATCH_CONFIDENCE:
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
                pyautogui.moveTo(final_x, final_y, duration=MOUSE_SPEED)
                time.sleep(0.1)
                perform_click(final_x, final_y, click_hold_duration)
                
                # Digitazione testo se richiesto
                if text_to_type:
                    if logger:
                        logger.info(f"⌨️ Digitando testo: {text_to_type}")
                    
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
                    
                    success = type_text_hybrid(text_to_type, logger)
                    if success:
                        if logger:
                            logger.info(f"✅ Testo completato: {text_to_type}")
                    else:
                        if logger:
                            logger.warning(f"⚠️ Problemi nell'inserimento testo: {text_to_type}")
                else:
                    click_type = f"tenuto {click_hold_duration}s" if click_hold_duration > 0 else "normale"
                    if logger:
                        logger.info(f"✅ Click {click_type} eseguito! (Match: {match_percent:.1f}%)")
                
                return True
            
            if logger:
                logger.warning(f"⚠️ Confidenza insufficiente: {match_percent:.1f}%")
            
            if attempt < MAX_RETRIES - 1:
                time.sleep(1)
                
        except Exception as e:
            if logger:
                logger.error(f"❌ Errore: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(1)
    
    return False


def change_mac_address_and_wait(logger: logging.Logger):
    """
    Cambia MAC address e attende il tempo configurato.
    
    Args:
        logger: Logger per i messaggi
    """
    if not change_mac_address('en0', logger=logger):
        logger.warning("⚠️ Cambio MAC address fallito, continuo comunque...")
    
    logger.info(f"⏳ Attendo {MAC_WAIT_SECONDS} secondi dopo cambio MAC address...")
    time.sleep(MAC_WAIT_SECONDS)


# =============================================================================
# FUNZIONE PRINCIPALE
# =============================================================================

def run_automation(logger: logging.Logger) -> bool:
    """
    Esegue l'automazione completa per tutti gli account nel CSV.
    
    Args:
        logger: Logger per i messaggi
        
    Returns:
        True se l'automazione è completata con successo
    """
    logger.info(f"🚀 Avvio automazione multi-account: https://signup.live.com/")
    logger.info(f"🇮🇹 Layout tastiera: Italiano")
    logger.info(f"🔒 Modalità incognito: {'Attiva' if INCOGNITO_MODE else 'Disattiva'}")
    logger.info(f"🌐 Chrome si aprirà dopo step {CHROME_OPEN_INDEX} (dopo VPN)")
    
    # Configurazione pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    
    # Caricamento account
    accounts = load_accounts_from_csv(CSV_FILE_PATH, logger=logger)
    if not accounts:
        logger.error("❌ Nessun account trovato nel CSV")
        return False
    
    logger.info(f"📊 Trovati {len(accounts)} account da processare")
    
    # Processamento account
    for account_index, account_data in enumerate(accounts, 1):
        logger.info(f"🔄 ===== ACCOUNT {account_index}/{len(accounts)} =====")
        
        try:
            # Preparazione ambiente
            close_all_chrome_windows(logger=logger)
            change_mac_address_and_wait(logger)
            
            # Apertura browser
            logger.info("🌐 Aprendo Chrome...")
            if not open_browser("https://signup.live.com/", browser=BROWSER, 
                              incognito=INCOGNITO_MODE, logger=logger):
                logger.error("❌ Impossibile aprire browser")
                update_account_status_in_csv(CSV_FILE_PATH, account_data['email'], 'denied', logger=logger)
                continue
            
            logger.info(f"⏳ Attendo {PAGE_LOAD_DELAY} secondi dopo apertura browser...")
            time.sleep(PAGE_LOAD_DELAY)
            
            # Esecuzione sequenza automazione
            total = len(AUTOMATION_SEQUENCE)
            for i, elem in enumerate(AUTOMATION_SEQUENCE, 1):
                # Parsing elemento sequenza
                if len(elem) == 3:
                    template_path, text_input, click_duration = elem
                    custom_delay = None
                elif len(elem) == 4:
                    template_path, text_input, click_duration, custom_delay = elem
                else:
                    logger.error(f"❌ Sequenza malformata all'indice {i-1}: {elem}")
                    continue
                
                # Preparazione log e testo
                processed_text = replace_placeholders(text_input, account_data)
                template_name = Path(template_path).stem
                
                log_parts = [f"🎯 [{i}/{total}] Elemento: {template_name}"]
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
                
                logger.info(" ".join(log_parts))
                
                # Esecuzione interazione
                success = find_and_interact(template_path, processed_text, click_duration, logger=logger)
                
                if success:
                    action_desc = []
                    if processed_text:
                        action_desc.append("testo")
                    click_type = f"click {click_duration}s" if click_duration > 0 else "click"
                    action_desc.append(click_type)
                    logger.info(f"✅ {template_name} completato ({' + '.join(action_desc)})")
                else:
                    logger.warning(f"⚠️ {template_name} fallito")
                
                # Pausa tra elementi
                if i < total:
                    delay_to_use = custom_delay if (custom_delay is not None and custom_delay > 0) else CLICK_DELAY
                    logger.info(f"⏳ Pausa {delay_to_use} secondi...")
                    time.sleep(delay_to_use)
            
            # Aggiornamento status account
            update_account_status_in_csv(CSV_FILE_PATH, account_data['email'], 'success', logger=logger)
            
            # Pausa tra account
            if account_index < len(accounts):
                logger.info(f"⏳ Pausa {ACCOUNT_DELAY} secondi prima del prossimo account...")
                time.sleep(ACCOUNT_DELAY)
                
        except Exception as e:
            logger.error(f"❌ Errore account {account_index}: {e}")
            update_account_status_in_csv(CSV_FILE_PATH, account_data['email'], 'denied', logger=logger)
            continue
    
    # Pulizia finale
    close_all_chrome_windows(logger=logger)
    logger.info("🏁 Automazione multi-account completata!")
    return True 