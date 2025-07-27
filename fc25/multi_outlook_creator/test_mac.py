#!/usr/bin/env python3
"""
test_mac.py - Script di test per il cambio MAC address
"""
import logging
from mac_utils import change_mac_address, check_sudo_access, check_spoof_mac_installed

def main():
    # Configura il logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("🧪 Test cambio MAC address")
    
    # Verifica sudo
    if not check_sudo_access(logger):
        logger.error("❌ Test fallito: sudo non disponibile")
        return
    
    # Verifica spoof-mac
    if not check_spoof_mac_installed(logger):
        logger.error("❌ Test fallito: spoof-mac non installato")
        return
    
    # Test cambio MAC
    logger.info("🔄 Test cambio MAC address...")
    success = change_mac_address('en0', logger)
    
    if success:
        logger.info("✅ Test MAC address completato con successo")
    else:
        logger.warning("⚠️ Test MAC address fallito, ma continuo comunque")

if __name__ == '__main__':
    main() 