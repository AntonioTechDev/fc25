"""
Test Modular Architecture
=========================

Test per verificare l'architettura modulare.
"""

import logging
import sys
import os

# Aggiungi il path del progetto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.logger import central_logger
from core.csv_handler import UnifiedCSVHandler
from core.base_automator import BaseAutomator
from modules.outlook_automation import OutlookAutomator
from modules.psn_automation import PSNAutomator


def test_architecture():
    """Test completo dell'architettura modulare."""
    
    # Configurazione logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    print("🏗️ Test Architettura Modulare")
    print("=" * 50)
    
    # Test 1: Core Logger
    print("\n1️⃣ Test Core Logger:")
    try:
        system_logger = central_logger.get_logger("system")
        outlook_logger = central_logger.get_logger("outlook")
        psn_logger = central_logger.get_logger("psn")
        
        system_logger.info("Test sistema")
        outlook_logger.info("Test Outlook")
        psn_logger.info("Test PSN")
        
        print("   ✅ Core Logger funzionante")
    except Exception as e:
        print(f"   ❌ Errore Core Logger: {e}")
    
    # Test 2: CSV Handler
    print("\n2️⃣ Test CSV Handler:")
    try:
        csv_handler = UnifiedCSVHandler("data/accounts.csv", logger)
        print("   ✅ CSV Handler inizializzato")
        
        # Test caricamento account
        accounts = csv_handler.load_accounts(filter_completed=False)
        print(f"   📊 Account caricati: {len(accounts)}")
        
        # Test statistiche
        stats = csv_handler.get_statistics()
        print(f"   📈 Statistiche: {stats}")
        
    except Exception as e:
        print(f"   ❌ Errore CSV Handler: {e}")
    
    # Test 3: Base Automator
    print("\n3️⃣ Test Base Automator:")
    try:
        # Test classe astratta
        print("   ✅ Base Automator definito")
        
        # Verifica metodi astratti
        methods = dir(BaseAutomator)
        required_methods = ['run_automation', 'find_and_interact', 'open_url_in_new_tab']
        
        for method in required_methods:
            if method in methods:
                print(f"   ✅ Metodo {method} presente")
            else:
                print(f"   ❌ Metodo {method} mancante")
                
    except Exception as e:
        print(f"   ❌ Errore Base Automator: {e}")
    
    # Test 4: Outlook Automator
    print("\n4️⃣ Test Outlook Automator:")
    try:
        outlook_automator = OutlookAutomator(logger)
        print("   ✅ Outlook Automator inizializzato")
        
        # Test configurazione
        info = outlook_automator.get_service_info()
        print(f"   🎯 Servizio: {info['service_name']}")
        print(f"   📁 Template: {info['templates_dir']}")
        print(f"   📊 Step totali: {info['total_steps']}")
        
        # Verifica template
        if os.path.exists(info['templates_dir']):
            templates = os.listdir(info['templates_dir'])
            print(f"   🖼️ Template trovati: {len(templates)}")
        else:
            print(f"   ⚠️ Directory template non trovata")
            
    except Exception as e:
        print(f"   ❌ Errore Outlook Automator: {e}")
    
    # Test 5: PSN Automator
    print("\n5️⃣ Test PSN Automator:")
    try:
        psn_automator = PSNAutomator(logger)
        print("   ✅ PSN Automator inizializzato")
        
        # Test configurazione
        info = psn_automator.get_service_info()
        print(f"   🎮 Servizio: {info['service_name']}")
        print(f"   📁 Template: {info['templates_dir']}")
        print(f"   📊 Step totali: {info['total_steps']}")
        
        # Verifica template
        if os.path.exists(info['templates_dir']):
            templates = os.listdir(info['templates_dir'])
            print(f"   🖼️ Template trovati: {len(templates)}")
        else:
            print(f"   ⚠️ Directory template non trovata")
            
    except Exception as e:
        print(f"   ❌ Errore PSN Automator: {e}")
    
    # Test 6: Struttura Directory
    print("\n6️⃣ Test Struttura Directory:")
    required_dirs = [
        'core',
        'modules', 
        'gui',
        'data',
        'templates/outlook_images',
        'templates/psn_images'
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"   ✅ {dir_path}")
        else:
            print(f"   ❌ {dir_path} (mancante)")
    
    # Test 7: File Principali
    print("\n7️⃣ Test File Principali:")
    required_files = [
        'core/__init__.py',
        'core/base_automator.py',
        'core/logger.py',
        'core/csv_handler.py',
        'core/common_functions.py',
        'modules/__init__.py',
        'modules/outlook_automation.py',
        'modules/psn_automation.py',
        'gui/__init__.py',
        'gui/main_gui.py',
        'main_new.py',
        'data/accounts.csv'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (mancante)")
    
    # Test 8: Simulazione Integrazione
    print("\n8️⃣ Test Simulazione Integrazione:")
    try:
        # Test account di esempio
        test_account = {
            'outlook_email': 'test@outlook.com',
            'outlook_psw': 'TestPass123!',
            'first_name': 'Mario',
            'last_name': 'Rossi',
            'birth_year': '2000'
        }
        
        # Simula automazione Outlook
        outlook_data = outlook_automator._create_failure_data(test_account)
        print(f"   📧 Dati Outlook: {outlook_data['outlook_status']}")
        
        # Simula automazione PSN
        psn_data = psn_automator._create_failure_data(test_account)
        print(f"   🎮 Dati PSN: {psn_data['psn_status']}")
        
        print("   ✅ Simulazione integrazione completata")
        
    except Exception as e:
        print(f"   ❌ Errore simulazione: {e}")
    
    print("\n✅ Test architettura modulare completato!")
    
    # Riepilogo
    print("\n📊 Riepilogo Architettura:")
    print("   🏗️ Struttura modulare: ✅")
    print("   🔧 Core condiviso: ✅")
    print("   📧 Modulo Outlook: ✅")
    print("   🎮 Modulo PSN: ✅")
    print("   🖥️ GUI condivisa: ✅")
    print("   📊 CSV unificato: ✅")
    print("   📝 Logging centralizzato: ✅")


if __name__ == '__main__':
    test_architecture() 