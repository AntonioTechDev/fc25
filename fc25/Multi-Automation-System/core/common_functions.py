"""
Common Functions
================

Funzioni comuni condivise tra tutti i moduli.
"""

import logging
import os
import platform
import random
import string
import subprocess
import time
from typing import Dict, List, Optional, Tuple


def detect_multi_monitor_setup(logger: logging.Logger = None) -> bool:
    """
    Rileva se il sistema ha più di un monitor.
    
    Args:
        logger: Logger opzionale per i messaggi
        
    Returns:
        True se ci sono più monitor, False altrimenti
    """
    try:
        import pyautogui
        
        if platform.system().lower() == "darwin":  # macOS
            # Usa AppleScript per rilevare i monitor
            script = '''
            tell application "System Events"
                return count of desktops
            end tell
            '''
            result = subprocess.run(["osascript", "-e", script], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                monitor_count = int(result.stdout.strip())
                if monitor_count > 1:
                    if logger:
                        logger.info(f"🖥️ Rilevati {monitor_count} monitor")
                    return True
                else:
                    if logger:
                        logger.info("🖥️ Setup monitor singolo rilevato")
                    return False
            else:
                if logger:
                    logger.warning(f"⚠️ Errore AppleScript: {result.stderr}")
                return False
        else:
            # Per altri sistemi, usa pyautogui.size() come fallback
            screen_width, screen_height = pyautogui.size()
            # Se la larghezza è molto grande, probabilmente ci sono più monitor
            if screen_width > 3000:  # Soglia arbitraria
                if logger:
                    logger.info("🖥️ Multi-monitor rilevato (fallback)")
                return True
            else:
                if logger:
                    logger.info("🖥️ Monitor singolo rilevato (fallback)")
                return False
            
    except Exception as e:
        if logger:
            logger.warning(f"⚠️ Errore rilevamento monitor: {e}")
        return False


def move_browser_to_primary_screen(browser: str = "chrome", logger: logging.Logger = None):
    """
    Sposta la finestra del browser sul primo schermo (utile per setup multi-monitor).
    
    Args:
        browser: Nome del browser ('chrome', 'firefox')
        logger: Logger opzionale per i messaggi
        
    Returns:
        True se lo spostamento è riuscito, False altrimenti
    """
    try:
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            if browser == "chrome":
                # AppleScript per spostare Chrome sul primo schermo
                script = '''
                tell application "Google Chrome"
                    activate
                    set bounds of front window to {0, 0, 1200, 800}
                end tell
                '''
            elif browser == "firefox":
                # AppleScript per spostare Firefox sul primo schermo
                script = '''
                tell application "Firefox"
                    activate
                    set bounds of front window to {0, 0, 1200, 800}
                end tell
                '''
            else:
                return False
                
            result = subprocess.run(["osascript", "-e", script], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                if logger:
                    logger.info(f"🖥️ Finestra {browser} spostata sul primo schermo")
                return True
            else:
                if logger:
                    logger.warning(f"⚠️ Errore spostamento {browser}: {result.stderr}")
                return False
                
        elif system == "windows":
            # TODO: Implementare per Windows se necessario
            if logger:
                logger.info("ℹ️ Spostamento finestra non implementato per Windows")
            return True
            
        elif system == "linux":
            # TODO: Implementare per Linux se necessario
            if logger:
                logger.info("ℹ️ Spostamento finestra non implementato per Linux")
            return True
            
    except Exception as e:
        if logger:
            logger.warning(f"⚠️ Errore spostamento finestra {browser}: {e}")
        return False


def close_all_chrome_windows(logger: logging.Logger = None):
    """
    Chiude tutte le finestre di Google Chrome aperte sul sistema.
    
    Args:
        logger: Logger opzionale per i messaggi
    """
    try:
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            subprocess.run(["osascript", "-e", 'tell application "Google Chrome" to quit'], 
                         capture_output=True)
            if logger:
                logger.info("🗙 Chiuse tutte le finestre Chrome (macOS)")
        elif system == "windows":
            subprocess.run(["taskkill", "/f", "/im", "chrome.exe"], 
                         capture_output=True, shell=True)
            if logger:
                logger.info("🗙 Chiuse tutte le finestre Chrome (Windows)")
        elif system == "linux":
            subprocess.run(["pkill", "-f", "chrome"], capture_output=True)
            if logger:
                logger.info("🗙 Chiuse tutte le finestre Chrome (Linux)")
        
        # Pausa per assicurarsi che Chrome si chiuda completamente
        time.sleep(2)
        
    except Exception as e:
        if logger:
            logger.warning(f"⚠️ Errore chiusura Chrome: {e}")


def open_browser(url: str, browser: str = "chrome", incognito: bool = True, 
                logger: logging.Logger = None) -> bool:
    """
    Apre l'URL specificato nel browser scelto, in modalità incognito se richiesto.
    
    Args:
        url: URL da aprire
        browser: Nome del browser ('chrome', 'firefox')
        incognito: Se True, apre in modalità incognito/privata
        logger: Logger opzionale per i messaggi
        
    Returns:
        True se il browser è stato aperto con successo, False altrimenti
    """
    try:
        system = platform.system().lower()
        
        if browser == "chrome":
            if system == "darwin":  # macOS
                cmd = ["open", "-a", "Google Chrome", "--args", "--incognito", url]
            elif system == "windows":
                cmd = ["start", "chrome", "--incognito", url]
            elif system == "linux":
                cmd = ["google-chrome", "--incognito", url]
            subprocess.run(cmd, shell=(system == "windows"))
            
        elif browser == "firefox":
            if system == "darwin":  # macOS
                cmd = ["open", "-a", "Firefox", "--args", "--private-window", url]
            elif system == "windows":
                cmd = ["start", "firefox", "-private-window", url]
            elif system == "linux":
                cmd = ["firefox", "--private-window", url]
            subprocess.run(cmd, shell=(system == "windows"))
            
        else:
            import webbrowser
            webbrowser.open(url)
        
        # Attendi che il browser si apra
        time.sleep(2)
        
        # Sposta la finestra sul primo schermo (utile per setup multi-monitor)
        move_browser_to_primary_screen(browser, logger)
        
        if logger:
            logger.info(f"✅ Browser aperto: {url}")
        return True
        
    except Exception as e:
        if logger:
            logger.error(f"❌ Errore apertura browser: {e}")
        return False


def generate_random_string(length: int = 8, include_special: bool = False) -> str:
    """
    Genera una stringa casuale.
    
    Args:
        length: Lunghezza della stringa
        include_special: Se includere caratteri speciali
        
    Returns:
        Stringa casuale generata
    """
    chars = string.ascii_letters + string.digits
    if include_special:
        chars += "!@#$%^&*"
    
    return ''.join(random.choice(chars) for _ in range(length))


def generate_psn_id(first_name: str, last_name: str, min_length: int = 3, 
                   max_length: int = 16) -> str:
    """
    Genera un PSN ID casuale rispettando i criteri PSN.
    
    Args:
        first_name: Nome dell'utente
        last_name: Cognome dell'utente
        min_length: Lunghezza minima
        max_length: Lunghezza massima
        
    Returns:
        PSN ID generato
    """
    allowed_chars = string.ascii_letters + string.digits + "-_"
    
    # Base: nome + cognome + numeri casuali
    base = f"{first_name.lower()}{last_name.lower()}"
    
    # Rimuovi caratteri non validi
    base = ''.join(c for c in base if c in allowed_chars)
    
    # Aggiungi numeri casuali se necessario
    if len(base) < min_length:
        base += ''.join(random.choices(string.digits, k=min_length - len(base)))
    
    # Tronca se troppo lungo
    if len(base) > max_length:
        base = base[:max_length]
    
    # Aggiungi suffisso casuale per unicità
    suffix = ''.join(random.choices(string.digits, k=3))
    psn_id = f"{base}{suffix}"
    
    return psn_id


def generate_psn_password(base_password: str = None) -> str:
    """
    Genera una password per PSN.
    
    Args:
        base_password: Password base da modificare (opzionale)
        
    Returns:
        Password PSN generata
    """
    if base_password:
        # Modifica la password base
        password = base_password.replace('Sdser4df#', 'Psn2024!')
    else:
        # Genera nuova password
        password = ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%", k=12))
    
    return password


def change_mac_address(interface: str = "en0", logger: logging.Logger = None):
    """
    Cambia l'indirizzo MAC dell'interfaccia specificata.
    
    Args:
        interface: Nome dell'interfaccia di rete
        logger: Logger opzionale per i messaggi
    """
    try:
        if platform.system().lower() == "darwin":  # macOS
            # Usa spoof-mac per cambiare MAC address
            cmd = ["sudo", "-n", "/opt/homebrew/bin/spoof-mac", "randomize", interface]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                if logger:
                    logger.info(f"🔁 MAC address cambiato su {interface}")
            else:
                if logger:
                    logger.warning(f"⚠️ Errore cambio MAC: {result.stderr}")
        else:
            if logger:
                logger.info("ℹ️ Cambio MAC non implementato per questo sistema")
                
    except Exception as e:
        if logger:
            logger.error(f"❌ Errore cambio MAC address: {e}")


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


def validate_email(email: str) -> bool:
    """
    Valida il formato di un indirizzo email.
    
    Args:
        email: Email da validare
        
    Returns:
        True se l'email è valida
    """
    import re
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def sanitize_filename(filename: str) -> str:
    """
    Sanitizza un nome file rimuovendo caratteri non validi.
    
    Args:
        filename: Nome file da sanitizzare
        
    Returns:
        Nome file sanitizzato
    """
    # Caratteri non validi per i file system
    invalid_chars = '<>:"/\\|?*'
    
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    return filename


def create_backup_file(file_path: str, backup_dir: str = None) -> str:
    """
    Crea un backup di un file.
    
    Args:
        file_path: Path del file da backupare
        backup_dir: Directory per il backup (opzionale)
        
    Returns:
        Path del file di backup
    """
    try:
        if not os.path.exists(file_path):
            return ""
        
        if backup_dir is None:
            backup_dir = os.path.join(os.path.dirname(file_path), 'backups')
        
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)
        
        backup_filename = f"{name}_backup_{timestamp}{ext}"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        import shutil
        shutil.copy2(file_path, backup_path)
        
        return backup_path
        
    except Exception as e:
        logging.error(f"❌ Errore creazione backup: {e}")
        return "" 