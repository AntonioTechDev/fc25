"""
Browser Utilities
=================

Funzioni per la gestione del browser (Chrome, Firefox).
"""

import logging
import os
import platform
import subprocess
import time
import webbrowser


def close_all_chrome_windows(logger: logging.Logger = None):
    """
    Chiude tutte le finestre di Chrome.
    
    Args:
        logger: Logger per i messaggi
    """
    try:
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            # AppleScript per chiudere Chrome
            script = '''
            tell application "Google Chrome"
                quit
            end tell
            '''
            subprocess.run(["osascript", "-e", script], capture_output=True)
            
        elif system == "windows":
            subprocess.run(["taskkill", "/f", "/im", "chrome.exe"], 
                         capture_output=True)
            
        elif system == "linux":
            subprocess.run(["pkill", "-f", "chrome"], capture_output=True)
        
        # Attendi che Chrome si chiuda
        time.sleep(2)
        
        if logger:
            logger.info("✅ Tutte le finestre Chrome chiuse")
            
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
        logger: Logger per i messaggi
        
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
        
        # Attendi che il browser si apra
        time.sleep(2)
        
        if logger:
            logger.info(f"✅ Browser aperto: {url}")
        return True
        
    except Exception as e:
        if logger:
            logger.error(f"❌ Errore apertura browser: {e}")
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
            logger.error(f"❌ Errore spostamento finestra: {e}")
        return False 