"""
Multi Outlook Account Creator - Main Entry Point
===============================================

Autore: Antonio De Biase
Versione: 2.0.0
Data: 2025-07-27

Descrizione:
Punto di ingresso principale per l'automazione multi-account Outlook.
Avvia la GUI di monitoraggio log e l'automazione in thread separati.

QUICK START:
python -m multi_outlook_creator.main
"""

import logging
import threading
import time

from multi_outlook_creator.backend.automation import run_automation
from multi_outlook_creator.frontend.gui_logger import setup_gui_logging


def run_automation_thread(logger: logging.Logger):
    """
    Esegue l'automazione in un thread separato.
    
    Args:
        logger: Logger per i messaggi
    """
    try:
        run_automation(logger)
    except Exception as e:
        logger.error(f'❌ Errore critico: {e}')


def main():
    """
    Funzione principale che avvia la GUI e l'automazione.
    """
    # Configurazione logging di base
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    
    # Avvia GUI di monitoraggio log
    gui_logger = setup_gui_logging()
    
    # Ottieni logger
    logger = logging.getLogger(__name__)
    logger.info('🇮🇹 Script multi-outlook-account avviato')
    logger.info('🔍 GUI di monitoraggio log attiva')
    
    # Avvia automazione in thread separato
    automation_thread = threading.Thread(target=run_automation_thread, 
                                       args=(logger,), daemon=True)
    automation_thread.start()
    
    try:
        # Avvia mainloop della GUI nel thread principale
        gui_logger.root.mainloop()
    except KeyboardInterrupt:
        logger.info('⏹️ Interruzione manuale rilevata')
    finally:
        logger.info('🏁 Script terminato')


if __name__ == '__main__':
    main() 