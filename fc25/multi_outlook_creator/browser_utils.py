"""
Multi Outlook Account Creator - Browser Utils
===========================================

Autore: Antonio De Biase
Versione: 2.0.0
Data: 2025-07-27

Descrizione:
Funzioni per la gestione del browser (apertura/chiusura).
Supporta Chrome e Firefox in modalità incognito/privata su macOS, Windows e Linux.
"""

import logging
import platform
import subprocess
import time
import webbrowser


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
            webbrowser.open(url)
        
        if logger:
            logger.info(f"✅ Browser aperto: {url}")
        return True
        
    except Exception as e:
        if logger:
            logger.error(f"❌ Errore apertura browser: {e}")
        return False 