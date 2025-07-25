import logging
from multi_outlook_creator.automation import run_automation

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.info('🇮🇹 Script multi-outlook-account avviato')
    run_automation(logger)

if __name__ == '__main__':
    main() 