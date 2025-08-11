"""
Multi Outlook Account Creator - MAC Address Utils
===============================================

Autore: Antonio De Biase
Versione: 2.0.0
Data: 2025-07-27

Descrizione:
Funzioni per la gestione e lo spoofing del MAC address su macOS.
Utilizza spoof-mac per cambiare dinamicamente l'indirizzo MAC.

Dipendenze:
- spoof-mac (installato via Homebrew)
- Permessi sudo per il cambio MAC

QUICK START:
brew install spoof-mac
sudo -v  # Estendi timestamp sudo
"""

import logging
import re
import subprocess
import time


# =============================================================================
# CONFIGURAZIONE
# =============================================================================

DEFAULT_ADAPTER = 'en0'  # Adattatore di rete predefinito (Wi-Fi su macOS)


def check_sudo_access(logger: logging.Logger = None) -> bool:
    """
    Verifica se sudo è disponibile senza password.
    
    Args:
        logger: Logger opzionale per i messaggi
        
    Returns:
        True se sudo è disponibile, False altrimenti
    """
    try:
        result = subprocess.run(['sudo', '-n', 'echo', 'test'], 
                              capture_output=True, text=True)
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
        logger: Logger opzionale per i messaggi
        
    Returns:
        True se spoof-mac è installato, False altrimenti
    """
    try:
        result = subprocess.run(['which', 'spoof-mac'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            if logger:
                logger.info("✅ Spoof-mac installato")
            return True
        else:
            if logger:
                logger.warning("⚠️ Spoof-mac non installato")
                logger.info("💡 Installa con: brew install spoof-mac")
            return False
    except Exception:
        if logger:
            logger.error("❌ Errore verifica spoof-mac")
        return False


def get_current_mac(adapter: str = DEFAULT_ADAPTER) -> str:
    """
    Restituisce il MAC address attuale dell'adattatore di rete.
    
    Args:
        adapter: Nome dell'adattatore di rete (es: 'en0' per Wi-Fi su macOS)
        
    Returns:
        MAC address attuale, oppure 'unknown' in caso di errore
    """
    try:
        result = subprocess.run(['ifconfig', adapter], 
                              capture_output=True, text=True)
        match = re.search(r'ether ([0-9a-f:]{17})', result.stdout)
        if match:
            return match.group(1)
        return 'unknown'
    except Exception:
        return 'unknown'


def change_mac_address(adapter: str = DEFAULT_ADAPTER, logger: logging.Logger = None) -> bool:
    """
    Cambia il MAC address dell'adattatore specificato usando spoof-mac.
    
    Richiede permessi sudo. Spegne e riaccende il Wi-Fi per applicare la modifica.
    
    Args:
        adapter: Nome dell'adattatore di rete (default 'en0')
        logger: Logger opzionale per i messaggi
        
    Returns:
        True se il cambio è avvenuto con successo, False altrimenti
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
        subprocess.run(['networksetup', '-setairportpower', adapter, 'off'], 
                      check=True)
        if logger:
            logger.info(f"📴 Wi-Fi {adapter} spento")
        
        # Cambia MAC - ora funziona senza password grazie alla configurazione sudoers
        try:
            result = subprocess.run(['sudo', '-n', 'spoof-mac', 'randomize', adapter], 
                                  capture_output=True, text=True)
        except Exception as e:
            if logger:
                logger.error(f"❌ Errore esecuzione spoof-mac: {e}")
            return False
        
        # Riaccendi Wi-Fi
        subprocess.run(['networksetup', '-setairportpower', adapter, 'on'], 
                      check=True)
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