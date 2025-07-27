import logging
import threading
import time
from multi_outlook_creator.automation import run_automation
from multi_outlook_creator.gui_logger import setup_gui_logging

def run_automation_thread(logger):
    """Esegue l'automazione in un thread separato"""
    try:
        run_automation(logger)
    except Exception as e:
        logger.error(f'❌ Errore critico: {e}')

def main():
    # Configura il logging di base
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    
    # Avvia la GUI di monitoraggio log
    gui_logger = setup_gui_logging()
    
    # Ottieni il logger
    logger = logging.getLogger(__name__)
    logger.info('🇮🇹 Script multi-outlook-account avviato')
    logger.info('🔍 GUI di monitoraggio log attiva')
    
    # Avvia l'automazione in un thread separato
    automation_thread = threading.Thread(target=run_automation_thread, args=(logger,), daemon=True)
    automation_thread.start()
    
    try:
        # Avvia il mainloop della GUI nel thread principale
        gui_logger.root.mainloop()
    except KeyboardInterrupt:
        logger.info('⏹️ Interruzione manuale rilevata')
    finally:
        logger.info('🏁 Script terminato')

if __name__ == '__main__':
    main() 