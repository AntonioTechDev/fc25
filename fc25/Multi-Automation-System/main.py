"""
Multi-Automation-System - Main Entry Point
=========================================

Autore: Antonio De Biase
Versione: 1.0.0
Data: 2025-08-12

Descrizione:
Sistema di automazione multi-servizio per Outlook e PSN.
Supporta automazione singola, combinata e GUI di monitoraggio.

QUICK START:
python main.py --outlook    # Solo automazione Outlook
python main.py --psn        # Solo automazione PSN
python main.py --combined   # Automazione combinata
python main.py --gui        # Interfaccia grafica
python main.py --stats      # Statistiche
"""

import argparse
import logging
import sys
import threading
import time

from core.logger import central_logger
from core.csv_handler import UnifiedCSVHandler
from modules.outlook_automation import OutlookAutomator
from modules.psn_automation import PSNAutomator
from gui.gui_logger import setup_gui_logging


class MultiAutomationSystem:
    """
    Sistema principale di automazione multi-servizio.
    """
    
    def __init__(self):
        """Inizializza il sistema di automazione."""
        self.csv_handler = UnifiedCSVHandler("data/accounts.csv", central_logger.get_logger("system"))
        self.outlook_automator = OutlookAutomator(central_logger.get_logger("outlook"))
        self.psn_automator = PSNAutomator(central_logger.get_logger("psn"))
        self.is_running = False
    
    def run_outlook_only(self):
        """Esegue solo l'automazione Outlook."""
        central_logger.log_system("📧 Avvio automazione Outlook...")
        
        try:
            # Mostra riepilogo stati
            summary = self.csv_handler.get_account_status_summary()
            central_logger.log_system(f"📊 Riepilogo stati: {summary['outlook_success']} completati, {summary['outlook_pending']} in attesa, {summary['outlook_failed']} falliti")
            
            # Carica solo account che necessitano processing Outlook
            accounts = self.csv_handler.get_accounts_for_service('outlook')
            if not accounts:
                central_logger.log_system("✅ Tutti gli account Outlook sono già completati!")
                return
            
            central_logger.log_system(f"📊 Processando {len(accounts)} account Outlook")
            
            for i, account in enumerate(accounts, 1):
                if not self.is_running:
                    break
                
                email = account.get('outlook_email', 'N/A')
                current_status = account.get('outlook_status', '').strip()
                central_logger.log_system(f"🔄 Account {i}/{len(accounts)}: {email} (stato: {current_status})")
                
                # Esegui automazione Outlook
                outlook_data = self.outlook_automator.run_automation(account)
                
                # Aggiorna CSV
                self.csv_handler.update_account(account['outlook_email'], 'outlook', outlook_data)
                
                # Pausa tra account
                if i < len(accounts):
                    central_logger.log_system(f"⏳ Pausa 30 secondi...")
                    time.sleep(30)
            
            central_logger.log_system("✅ Automazione Outlook completata!")
            
        except Exception as e:
            central_logger.log_system(f"❌ Errore automazione Outlook: {e}", "ERROR")
    
    def run_psn_only(self):
        """Esegue solo l'automazione PSN."""
        central_logger.log_system("🎮 Avvio automazione PSN...")
        
        try:
            # Mostra riepilogo stati
            summary = self.csv_handler.get_account_status_summary()
            central_logger.log_system(f"📊 Riepilogo stati: {summary['psn_success']} completati, {summary['psn_pending']} in attesa, {summary['psn_failed']} falliti")
            
            # Carica solo account che necessitano processing PSN
            accounts = self.csv_handler.get_accounts_for_service('psn')
            if not accounts:
                central_logger.log_system("✅ Tutti gli account PSN sono già completati!")
                return
            
            central_logger.log_system(f"📊 Processando {len(accounts)} account PSN")
            
            for i, account in enumerate(accounts, 1):
                if not self.is_running:
                    break
                
                email = account.get('outlook_email', 'N/A')
                current_status = account.get('psn_status', '').strip()
                central_logger.log_system(f"🔄 Account {i}/{len(accounts)}: {email} (stato: {current_status})")
                
                # Esegui automazione PSN
                psn_data = self.psn_automator.run_automation(account)
                
                # Aggiorna CSV
                self.csv_handler.update_account(account['outlook_email'], 'psn', psn_data)
                
                # Pausa tra account
                if i < len(accounts):
                    central_logger.log_system(f"⏳ Pausa 30 secondi...")
                    time.sleep(30)
            
            central_logger.log_system("✅ Automazione PSN completata!")
            
        except Exception as e:
            central_logger.log_system(f"❌ Errore automazione PSN: {e}", "ERROR")
    
    def run_combined(self):
        """Esegue automazione Outlook + PSN sequenziale con filtro intelligente."""
        central_logger.log_system("🔄 Avvio automazione combinata Outlook + PSN...")
        
        try:
            # Mostra riepilogo stati
            summary = self.csv_handler.get_account_status_summary()
            central_logger.log_system(f"📊 Riepilogo stati:")
            central_logger.log_system(f"   • Outlook: {summary['outlook_success']} completati, {summary['outlook_pending']} in attesa")
            central_logger.log_system(f"   • PSN: {summary['psn_success']} completati, {summary['psn_pending']} in attesa")
            central_logger.log_system(f"   • Entrambi completati: {summary['both_success']}")
            central_logger.log_system(f"   • Necessitano processing: {summary['needs_processing']}")
            
            # Carica account che necessitano processing per almeno un servizio
            accounts = self.csv_handler.get_accounts_for_service('combined')
            if not accounts:
                central_logger.log_system("✅ Tutti gli account sono completamente processati!")
                return
            
            central_logger.log_system(f"📊 Processando {len(accounts)} account")
            
            for i, account in enumerate(accounts, 1):
                if not self.is_running:
                    break
                
                email = account.get('outlook_email', 'N/A')
                outlook_status = account.get('outlook_status', '').strip()
                psn_status = account.get('psn_status', '').strip()
                
                central_logger.log_system(f"🔄 Account {i}/{len(accounts)}: {email}")
                central_logger.log_system(f"   • Outlook: {outlook_status}")
                central_logger.log_system(f"   • PSN: {psn_status}")
                
                # 1. Esegui automazione Outlook (se necessario)
                if outlook_status != 'success':
                    central_logger.log_system("📧 Avvio automazione Outlook...")
                    outlook_data = self.outlook_automator.run_automation(account)
                    self.csv_handler.update_account(account['outlook_email'], 'outlook', outlook_data)
                    
                    # Aggiorna status per il prossimo controllo
                    if outlook_data.get('outlook_status') == 'success':
                        account['outlook_status'] = 'success'
                else:
                    central_logger.log_system("⏩ Outlook già completato, salto...")
                
                # 2. Esegui automazione PSN (se necessario)
                if psn_status != 'success':
                    central_logger.log_system("🎮 Avvio automazione PSN...")
                    psn_data = self.psn_automator.run_automation(account)
                    self.csv_handler.update_account(account['outlook_email'], 'psn', psn_data)
                else:
                    central_logger.log_system("⏩ PSN già completato, salto...")
                
                # Pausa tra account
                if i < len(accounts):
                    central_logger.log_system(f"⏳ Pausa 30 secondi...")
                    time.sleep(30)
            
            central_logger.log_system("✅ Automazione combinata completata!")
            
        except Exception as e:
            central_logger.log_system(f"❌ Errore automazione combinata: {e}", "ERROR")
    
    def show_statistics(self):
        """Mostra le statistiche dettagliate del sistema."""
        try:
            summary = self.csv_handler.get_account_status_summary()
            
            stats_text = f"""
📊 Statistiche Dettagliate Sistema:
==================================
📧 OUTLOOK:
   • Completati: {summary.get('outlook_success', 0)}
   • In attesa: {summary.get('outlook_pending', 0)}
   • Falliti: {summary.get('outlook_failed', 0)}

🎮 PSN:
   • Completati: {summary.get('psn_success', 0)}
   • In attesa: {summary.get('psn_pending', 0)}
   • Falliti: {summary.get('psn_failed', 0)}

🔄 COMBINATO:
   • Entrambi completati: {summary.get('both_success', 0)}
   • Necessitano processing: {summary.get('needs_processing', 0)}
   • Totale account: {summary.get('total_accounts', 0)}

💡 SUGGERIMENTI:
   • Solo Outlook: {summary.get('outlook_pending', 0) + summary.get('outlook_failed', 0)} account da processare
   • Solo PSN: {summary.get('psn_pending', 0) + summary.get('psn_failed', 0)} account da processare
   • Combinato: {summary.get('needs_processing', 0)} account da processare
            """
            
            print(stats_text)
            central_logger.log_system("📊 Statistiche dettagliate visualizzate")
            
        except Exception as e:
            central_logger.log_system(f"❌ Errore statistiche: {e}", "ERROR")
    
    def run_gui(self):
        """Avvia l'interfaccia grafica."""
        try:
            from gui.main_gui import main as gui_main
            gui_main()
        except Exception as e:
            central_logger.log_system(f"❌ Errore avvio GUI: {e}", "ERROR")
    
    def stop(self):
        """Ferma il sistema."""
        self.is_running = False
        self.outlook_automator.stop_automation()
        self.psn_automator.stop_automation()


def run_automation_thread(system: MultiAutomationSystem, mode: str):
    """
    Esegue l'automazione in un thread separato.
    
    Args:
        system: Istanza del sistema
        mode: Modalità di esecuzione
    """
    try:
        system.is_running = True
        
        if mode == 'outlook':
            system.run_outlook_only()
        elif mode == 'psn':
            system.run_psn_only()
        elif mode == 'combined':
            system.run_combined()
        elif mode == 'stats':
            system.show_statistics()
        elif mode == 'gui':
            system.run_gui()
            
    except Exception as e:
        central_logger.log_system(f'❌ Errore critico: {e}', "ERROR")
    finally:
        system.is_running = False


def main():
    """
    Funzione principale che avvia la GUI e l'automazione.
    """
    parser = argparse.ArgumentParser(description='Multi-Automation-System')
    parser.add_argument('--outlook', action='store_true', help='Esegui solo automazione Outlook')
    parser.add_argument('--psn', action='store_true', help='Esegui solo automazione PSN')
    parser.add_argument('--combined', action='store_true', help='Esegui automazione combinata')
    parser.add_argument('--gui', action='store_true', help='Avvia interfaccia grafica')
    parser.add_argument('--stats', action='store_true', help='Mostra statistiche')
    
    args = parser.parse_args()
    
    # Se nessun argomento è specificato, mostra l'help
    if not any([args.outlook, args.psn, args.combined, args.gui, args.stats]):
        parser.print_help()
        return
    
    # Configurazione logging di base
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    
    # Avvia GUI di monitoraggio log
    gui_logger = setup_gui_logging()
    
    # Ottieni logger
    logger = logging.getLogger(__name__)
    logger.info('🚀 Multi-Automation-System avviato')
    logger.info('🔍 GUI di monitoraggio log attiva')
    
    # Crea istanza del sistema
    system = MultiAutomationSystem()
    
    # Determina la modalità
    if args.outlook:
        mode = 'outlook'
        logger.info('📧 Modalità: Solo Outlook')
    elif args.psn:
        mode = 'psn'
        logger.info('🎮 Modalità: Solo PSN')
    elif args.combined:
        mode = 'combined'
        logger.info('🔄 Modalità: Combinata')
    elif args.stats:
        mode = 'stats'
        logger.info('📊 Modalità: Statistiche')
    elif args.gui:
        mode = 'gui'
        logger.info('🖥️ Modalità: GUI')
    
    # Avvia automazione in thread separato
    automation_thread = threading.Thread(target=run_automation_thread, 
                                       args=(system, mode), daemon=True)
    automation_thread.start()
    
    try:
        # Avvia mainloop della GUI nel thread principale
        gui_logger.root.mainloop()
    except KeyboardInterrupt:
        logger.info('⏹️ Interruzione manuale rilevata')
        system.stop()
    finally:
        logger.info('🏁 Sistema terminato')


if __name__ == '__main__':
    main() 