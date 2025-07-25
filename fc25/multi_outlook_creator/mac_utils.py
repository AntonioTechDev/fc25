"""
mac_utils.py - Funzioni per la gestione e lo spoofing del MAC address su macOS
"""
import subprocess
import re
import time
import logging

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
        old_mac = get_current_mac(adapter)
        if logger:
            logger.info(f"🔄 Cambio MAC address su {adapter}... (MAC attuale: {old_mac})")
        # Spegni Wi-Fi
        subprocess.run(['networksetup', '-setairportpower', adapter, 'off'], check=True)
        if logger:
            logger.info(f"📴 Wi-Fi {adapter} spento")
        # Cambia MAC
        result = subprocess.run(['sudo', '-n', 'spoof-mac', 'randomize', adapter], capture_output=True, text=True)
        # Riaccendi Wi-Fi
        subprocess.run(['networksetup', '-setairportpower', adapter, 'on'], check=True)
        if logger:
            logger.info(f"📶 Wi-Fi {adapter} riacceso")
        new_mac = get_current_mac(adapter)
        if logger:
            logger.info(f"🔁 MAC address cambiato: {old_mac} → {new_mac}")
            logger.info("⏳ Attendo 10 secondi dopo cambio MAC address...")
        time.sleep(10)
        if result.returncode == 0:
            if logger:
                logger.info(f"✅ MAC address cambiato con successo su {adapter}")
            return True
        else:
            if logger:
                logger.error(f"❌ Errore cambio MAC: {result.stderr.strip()}")
            return False
    except Exception as e:
        if logger:
            logger.error(f"❌ Errore esecuzione spoof-mac: {e}")
        return False 