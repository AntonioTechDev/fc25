"""
MAC Address Utilities
=====================

Funzioni per la gestione del cambio MAC address.
"""

import logging
import platform
import subprocess
import time
from typing import Optional


def check_spoof_mac_installed(logger: logging.Logger = None) -> bool:
    """
    Verifica se spoof-mac è installato.
    
    Args:
        logger: Logger per i messaggi
        
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
                logger.warning("⚠️ Spoof-mac non installato. Installa con: brew install spoof-mac")
            return False
            
    except Exception as e:
        if logger:
            logger.error(f"❌ Errore verifica spoof-mac: {e}")
        return False


def get_current_mac_address(interface: str = "en0", logger: logging.Logger = None) -> Optional[str]:
    """
    Ottiene l'indirizzo MAC corrente dell'interfaccia.
    
    Args:
        interface: Nome dell'interfaccia di rete
        logger: Logger per i messaggi
        
    Returns:
        Indirizzo MAC corrente o None se errore
    """
    try:
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            cmd = ['ifconfig', interface]
        elif system == "linux":
            cmd = ['ip', 'link', 'show', interface]
        else:
            if logger:
                logger.warning(f"⚠️ Sistema {system} non supportato")
            return None
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Estrai MAC address dalla risposta
            output = result.stdout
            if system == "darwin":
                # Cerca pattern MAC address in ifconfig output
                import re
                mac_pattern = r'ether\s+([0-9a-fA-F:]{17})'
                match = re.search(mac_pattern, output)
                if match:
                    return match.group(1)
            elif system == "linux":
                # Cerca pattern MAC address in ip link output
                import re
                mac_pattern = r'link/ether\s+([0-9a-fA-F:]{17})'
                match = re.search(mac_pattern, output)
                if match:
                    return match.group(1)
        
        if logger:
            logger.warning(f"⚠️ Impossibile ottenere MAC address per {interface}")
        return None
        
    except Exception as e:
        if logger:
            logger.error(f"❌ Errore ottenimento MAC address: {e}")
        return None


def change_mac_address(interface: str = "en0", logger: logging.Logger = None) -> bool:
    """
    Cambia l'indirizzo MAC dell'interfaccia di rete.
    
    Args:
        interface: Nome dell'interfaccia di rete
        logger: Logger per i messaggi
        
    Returns:
        True se il cambio è riuscito, False altrimenti
    """
    try:
        system = platform.system().lower()
        
        if system != "darwin":
            if logger:
                logger.warning(f"⚠️ Cambio MAC address non supportato per {system}")
            return False
        
        # Verifica che spoof-mac sia installato
        if not check_spoof_mac_installed(logger):
            return False
        
        # Ottieni MAC address corrente
        current_mac = get_current_mac_address(interface, logger)
        if current_mac:
            if logger:
                logger.info(f"🔄 Cambio MAC address su {interface}... (MAC attuale: {current_mac})")
        
        # Spegni completamente la Wi-Fi
        if logger:
            logger.info(f"📴 Wi-Fi {interface} spento completamente")
        
        # Disconnetti dalla rete Wi-Fi
        subprocess.run(['sudo', 'networksetup', '-setairportpower', interface, 'off'], 
                      capture_output=True)
        time.sleep(3)
        
        # Cambia MAC address usando spoof-mac (con interfaccia spenta)
        result = subprocess.run(['sudo', 'spoof-mac', 'randomize', interface], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            if logger:
                logger.error(f"❌ Errore cambio MAC address: {result.stderr}")
            # Riaccendi comunque la Wi-Fi in caso di errore
            subprocess.run(['sudo', 'networksetup', '-setairportpower', interface, 'on'], 
                          capture_output=True)
            time.sleep(2)
            return False
        
        # Riaccendi la Wi-Fi
        if logger:
            logger.info(f"📶 Wi-Fi {interface} riacceso")
        
        subprocess.run(['sudo', 'networksetup', '-setairportpower', interface, 'on'], 
                      capture_output=True)
        time.sleep(5)
        
        # Verifica il nuovo MAC address
        new_mac = get_current_mac_address(interface, logger)
        if new_mac and new_mac != current_mac:
            if logger:
                logger.info(f"🔁 MAC address cambiato: {current_mac} → {new_mac}")
                logger.info(f"✅ MAC address cambiato con successo su {interface}")
            return True
        else:
            if logger:
                logger.warning("⚠️ MAC address non cambiato o non verificabile")
            return False
        
    except Exception as e:
        if logger:
            logger.error(f"❌ Errore cambio MAC address: {e}")
        return False


def reset_mac_address(interface: str = "en0", logger: logging.Logger = None) -> bool:
    """
    Resetta l'indirizzo MAC all'originale.
    
    Args:
        interface: Nome dell'interfaccia di rete
        logger: Logger per i messaggi
        
    Returns:
        True se il reset è riuscito, False altrimenti
    """
    try:
        system = platform.system().lower()
        
        if system != "darwin":
            if logger:
                logger.warning(f"⚠️ Reset MAC address non supportato per {system}")
            return False
        
        # Verifica che spoof-mac sia installato
        if not check_spoof_mac_installed(logger):
            return False
        
        if logger:
            logger.info(f"🔄 Reset MAC address su {interface}...")
        
        # Spegni completamente la Wi-Fi
        subprocess.run(['sudo', 'networksetup', '-setairportpower', interface, 'off'], 
                      capture_output=True)
        time.sleep(3)
        
        # Reset MAC address usando spoof-mac (con interfaccia spenta)
        result = subprocess.run(['sudo', 'spoof-mac', 'reset', interface], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            if logger:
                logger.error(f"❌ Errore reset MAC address: {result.stderr}")
            # Riaccendi comunque la Wi-Fi in caso di errore
            subprocess.run(['sudo', 'networksetup', '-setairportpower', interface, 'on'], 
                          capture_output=True)
            time.sleep(2)
            return False
        
        # Riaccendi la Wi-Fi
        subprocess.run(['sudo', 'networksetup', '-setairportpower', interface, 'on'], 
                      capture_output=True)
        time.sleep(5)
        
        if logger:
            logger.info(f"✅ MAC address resettato su {interface}")
        return True
        
    except Exception as e:
        if logger:
            logger.error(f"❌ Errore reset MAC address: {e}")
        return False


def list_network_interfaces(logger: logging.Logger = None) -> list:
    """
    Lista le interfacce di rete disponibili.
    
    Args:
        logger: Logger per i messaggi
        
    Returns:
        Lista delle interfacce di rete
    """
    interfaces = []
    
    try:
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            cmd = ['ifconfig', '-l']
        elif system == "linux":
            cmd = ['ip', 'link', 'show']
        else:
            if logger:
                logger.warning(f"⚠️ Sistema {system} non supportato")
            return interfaces
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            if system == "darwin":
                interfaces = result.stdout.strip().split()
            elif system == "linux":
                # Estrai nomi interfacce da ip link output
                import re
                interface_pattern = r'\d+:\s+(\w+):'
                interfaces = re.findall(interface_pattern, result.stdout)
        
        if logger:
            logger.info(f"📡 Interfacce disponibili: {interfaces}")
            
    except Exception as e:
        if logger:
            logger.error(f"❌ Errore lista interfacce: {e}")
    
    return interfaces 