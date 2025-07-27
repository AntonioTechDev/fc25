"""
mac_utils.py - Funzioni per la gestione e lo spoofing del MAC address su macOS
"""
import subprocess
import re
import time
import logging

def check_sudo_access(logger: logging.Logger = None) -> bool:
    """
    Verifica se sudo è disponibile senza password.
    Args:
        logger (logging.Logger): Logger opzionale
    Returns:
        bool: True se sudo è disponibile, False altrimenti
    """
    try:
        result = subprocess.run(['sudo', '-n', 'echo', 'test'], capture_output=True, text=True)
        if result.returncode == 0:
            if logger:
                logger.info("✅ Sudo accesso disponibile")
            return True
        else:
            if logger:
                logger.warning("⚠️ Sudo richiede autenticazione")
            return False
    except Exception:
        if logger:
            logger.error("❌ Errore verifica sudo")
        return False

def check_spoof_mac_installed(logger: logging.Logger = None) -> bool:
    """
    Verifica se spoof-mac è installato.
    Args:
        logger (logging.Logger): Logger opzionale
    Returns:
        bool: True se spoof-mac è installato, False altrimenti
    """
    try:
        result = subprocess.run(['which', 'spoof-mac'], capture_output=True, text=True)
        if result.returncode == 0:
            if logger:
                logger.info("✅ Spoof-mac installato")
            return True
        else:
            if logger:
                logger.warning("⚠️ Spoof-mac non installato")
                logger.info("💡 Installa con: pip install spoof-mac")
            return False
    except Exception:
        if logger:
            logger.error("❌ Errore verifica spoof-mac")
        return False

def get_current_mac(adapter: str = 'en0') -> str:
    """
    Restituisce il MAC address attuale dell'adattatore di rete specificato.
    Args:
        adapter (str): Nome dell'adattatore di rete (es: 'en0' per Wi-Fi su macOS)
    Returns:
        str: MAC address attuale, oppure 'unknown' in caso di errore
    """
    try:
        result = subprocess.run(['ifconfig', adapter], capture_output=True, text=True)
        match = re.search(r'ether ([0-9a-f:]{17})', result.stdout)
        if match:
            return match.group(1)
        return 'unknown'
    except Exception:
        return 'unknown'


def change_mac_address(adapter: str = 'en0', logger: logging.Logger = None) -> bool:
    """
    Cambia il MAC address dell'adattatore specificato usando spoof-mac.
    Richiede permessi sudo. Spegne e riaccende il Wi-Fi per applicare la modifica.
    Args:
        adapter (str): Nome dell'adattatore di rete (default 'en0')
        logger (logging.Logger): Logger opzionale per loggare le operazioni
    Returns:
        bool: True se il cambio è avvenuto con successo, False altrimenti
    """
    try:
        # Verifica se spoof-mac è installato
        if not check_spoof_mac_installed(logger):
            if logger:
                logger.error("❌ Impossibile cambiare MAC address: spoof-mac non installato")
                logger.info("💡 Installa con: brew install spoof-mac")
            return False
            
        old_mac = get_current_mac(adapter)
        if logger:
            logger.info(f"🔄 Cambio MAC address su {adapter}... (MAC attuale: {old_mac})")
        # Spegni Wi-Fi
        subprocess.run(['networksetup', '-setairportpower', adapter, 'off'], check=True)
        if logger:
            logger.info(f"📴 Wi-Fi {adapter} spento")
        # Cambia MAC - prova prima senza password, se fallisce usa autenticazione interattiva
        try:
            # Prima prova senza password
            result = subprocess.run(['sudo', '-n', 'spoof-mac', 'randomize', adapter], capture_output=True, text=True)
            if result.returncode != 0 and "password is required" in result.stderr:
                if logger:
                    logger.info("🔐 Richiesta password sudo per cambio MAC address...")
                # Usa autenticazione interattiva (senza capture_output per permettere input)
                result = subprocess.run(['sudo', 'spoof-mac', 'randomize', adapter], check=False)
        except Exception as e:
            if logger:
                logger.error(f"❌ Errore esecuzione spoof-mac: {e}")
            return False
        # Riaccendi Wi-Fi
        subprocess.run(['networksetup', '-setairportpower', adapter, 'on'], check=True)
        if logger:
            logger.info(f"📶 Wi-Fi {adapter} riacceso")
        new_mac = get_current_mac(adapter)
        if logger:
            logger.info(f"🔁 MAC address cambiato: {old_mac} → {new_mac}")
            logger.info("⏳ Attendo 10 secondi dopo cambio MAC address...")
        time.sleep(10)
        
        # Verifica se il MAC è effettivamente cambiato
        if new_mac != old_mac and new_mac != 'unknown':
            if logger:
                logger.info(f"✅ MAC address cambiato con successo su {adapter}")
            return True
        else:
            if logger:
                logger.warning(f"⚠️ MAC address non è cambiato (rimane: {old_mac})")
                if hasattr(result, 'stderr') and result.stderr:
                    logger.warning(f"⚠️ Errore spoof-mac: {result.stderr.strip()}")
                logger.info("💡 Il cambio MAC address è opzionale, continuo comunque...")
            return False
    except Exception as e:
        if logger:
            logger.error(f"❌ Errore esecuzione spoof-mac: {e}")
        return False 