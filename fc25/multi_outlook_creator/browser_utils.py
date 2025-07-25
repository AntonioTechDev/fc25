"""
browser_utils.py - Funzioni per la gestione del browser (apertura/chiusura)
"""
import subprocess
import platform
import webbrowser
import logging

def close_all_chrome_windows(logger: logging.Logger = None):
    """
    Chiude tutte le finestre di Google Chrome aperte sul sistema operativo corrente.
    Args:
        logger (logging.Logger): Logger opzionale per loggare le operazioni
    """
    try:
        system = platform.system().lower()
        if system == "darwin":  # macOS
            subprocess.run(["osascript", "-e", 'tell application "Google Chrome" to quit'], capture_output=True)
            if logger:
                logger.info("🗙 Chiuse tutte le finestre Chrome (macOS)")
        elif system == "windows":
            subprocess.run(["taskkill", "/f", "/im", "chrome.exe"], capture_output=True, shell=True)
            if logger:
                logger.info("🗙 Chiuse tutte le finestre Chrome (Windows)")
        elif system == "linux":
            subprocess.run(["pkill", "-f", "chrome"], capture_output=True)
            if logger:
                logger.info("🗙 Chiuse tutte le finestre Chrome (Linux)")
        # Pausa per assicurarsi che Chrome si chiuda completamente
        import time; time.sleep(2)
    except Exception as e:
        if logger:
            logger.warning(f"⚠️ Errore chiusura Chrome: {e}")

def open_browser(url: str, browser: str = "chrome", incognito: bool = True, logger: logging.Logger = None) -> bool:
    """
    Apre l'URL specificato nel browser scelto, in modalità incognito se richiesto.
    Args:
        url (str): URL da aprire
        browser (str): Nome del browser ('chrome', 'firefox', ...)
        incognito (bool): Se True, apre in modalità incognito/privata
        logger (logging.Logger): Logger opzionale
    Returns:
        bool: True se il browser è stato aperto con successo, False altrimenti
    """
    try:
        system = platform.system().lower()
        if browser == "chrome":
            if system == "darwin":
                cmd = ["open", "-a", "Google Chrome", "--args", "--incognito", url]
            elif system == "windows":
                cmd = ["start", "chrome", "--incognito", url]
            elif system == "linux":
                cmd = ["google-chrome", "--incognito", url]
            subprocess.run(cmd, shell=(system == "windows"))
        elif browser == "firefox":
            if system == "darwin":
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