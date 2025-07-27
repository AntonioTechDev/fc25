#!/usr/bin/env python3
"""
test_gui.py - Script di test per la GUI di monitoraggio log
"""
import logging
import time
import threading
from gui_logger import setup_gui_logging

def test_logging():
    """Testa il sistema di logging con diversi livelli"""
    logger = logging.getLogger(__name__)
    
    # Simula alcuni log di test
    logger.info("🧪 Test GUI di monitoraggio log")
    logger.info("✅ GUI creata con successo")
    logger.warning("⚠️ Questo è un warning di test")
    logger.error("❌ Questo è un errore di test")
    logger.info("📊 Contatore log funzionante")
    logger.info("🎨 Colori per livelli log attivi")
    
    # Simula log in tempo reale
    for i in range(10):
        logger.info(f"🔄 Log di test #{i+1}")
        time.sleep(1)

def main():
    # Configura il logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    
    # Avvia la GUI
    gui_logger = setup_gui_logging()
    
    # Ottieni il logger
    logger = logging.getLogger(__name__)
    logger.info("🚀 Test GUI avviato")
    
    # Avvia il test in un thread separato
    test_thread = threading.Thread(target=test_logging, daemon=True)
    test_thread.start()
    
    try:
        # Avvia il mainloop della GUI
        gui_logger.root.mainloop()
    except KeyboardInterrupt:
        logger.info("⏹️ Test interrotto")

if __name__ == '__main__':
    main() 