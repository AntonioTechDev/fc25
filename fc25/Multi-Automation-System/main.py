"""
Multi-Automation System - Main Entry Point
==========================================

Entry point principale per il sistema di automazione modulare.
Supporta esecuzione standalone, combinata e GUI.
"""

import argparse
import logging
import sys
import time
from typing import Dict, List

from core.logger import central_logger
from core.csv_handler import UnifiedCSVHandler
from modules.outlook_automation import OutlookAutomator
from modules.psn_automation import PSNAutomator


class MultiAutomationSystem:
    """
    Sistema principale di automazione modulare.
    """
    
    def __init__(self, csv_path: str = "data/accounts.csv"):
        """
        Inizializza il sistema di automazione.
        
        Args:
            csv_path: Path al file CSV
        """
        self.csv_handler = UnifiedCSVHandler(csv_path, central_logger.get_logger("system"))
        
        # Inizializza automator
        self.outlook_automator = OutlookAutomator(central_logger.get_logger("outlook"))
        self.psn_automator = PSNAutomator(central_logger.get_logger("psn"))
        
        # Stato del sistema
        self.is_running = False
    
    def run_outlook_only(self):
        """Esegue solo l'automazione Outlook."""
        central_logger.log_system("📧 Avvio automazione Outlook...")
        
        try:
            accounts = self.csv_handler.load_accounts()
            if not accounts:
                central_logger.log_system("⚠️ Nessun account da processare")
                return
            
            central_logger.log_system(f"📊 Processando {len(accounts)} account Outlook")
            
            for i, account in enumerate(accounts, 1):
                if not self.is_running:
                    break
                
                central_logger.log_system(f"🔄 Account {i}/{len(accounts)}: {account.get('outlook_email', 'N/A')}")
                
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
            accounts = self.csv_handler.load_accounts()
            if not accounts:
                central_logger.log_system("⚠️ Nessun account da processare")
                return
            
            central_logger.log_system(f"📊 Processando {len(accounts)} account PSN")
            
            for i, account in enumerate(accounts, 1):
                if not self.is_running:
                    break
                
                central_logger.log_system(f"🔄 Account {i}/{len(accounts)}: {account.get('outlook_email', 'N/A')}")
                
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
        """Esegue automazione Outlook + PSN sequenziale."""
        central_logger.log_system("🔄 Avvio automazione combinata Outlook + PSN...")
        
        try:
            accounts = self.csv_handler.load_accounts()
            if not accounts:
                central_logger.log_system("⚠️ Nessun account da processare")
                return
            
            central_logger.log_system(f"📊 Processando {len(accounts)} account")
            
            for i, account in enumerate(accounts, 1):
                if not self.is_running:
                    break
                
                central_logger.log_system(f"🔄 Account {i}/{len(accounts)}: {account.get('outlook_email', 'N/A')}")
                
                # 1. Esegui automazione Outlook
                central_logger.log_system("📧 Avvio automazione Outlook...")
                outlook_data = self.outlook_automator.run_automation(account)
                self.csv_handler.update_account(account['outlook_email'], 'outlook', outlook_data)
                
                # 2. Esegui automazione PSN (se Outlook è riuscito)
                if outlook_data.get('outlook_status') == 'success':
                    central_logger.log_system("🎮 Avvio automazione PSN...")
                    psn_data = self.psn_automator.run_automation(account)
                    self.csv_handler.update_account(account['outlook_email'], 'psn', psn_data)
                else:
                    central_logger.log_system("⚠️ Outlook fallito, salto PSN")
                
                # Pausa tra account
                if i < len(accounts):
                    central_logger.log_system(f"⏳ Pausa 30 secondi...")
                    time.sleep(30)
            
            central_logger.log_system("✅ Automazione combinata completata!")
            
        except Exception as e:
            central_logger.log_system(f"❌ Errore automazione combinata: {e}", "ERROR")
    
    def show_statistics(self):
        """Mostra le statistiche del sistema."""
        try:
            stats = self.csv_handler.get_statistics()
            
            stats_text = f"""
📊 Statistiche Sistema:
=====================
• Account totali: {stats.get('total_accounts', 0)}
• Outlook completati: {stats.get('outlook_completed', 0)}
• PSN completati: {stats.get('psn_completed', 0)}
• Entrambi completati: {stats.get('both_completed', 0)}
• In attesa: {stats.get('pending', 0)}
            """
            
            print(stats_text)
            central_logger.log_system("📊 Statistiche visualizzate")
            
        except Exception as e:
            central_logger.log_system(f"❌ Errore statistiche: {e}", "ERROR")
    
    def stop(self):
        """Ferma il sistema di automazione."""
        self.is_running = False
        central_logger.log_system("⏹️ Sistema fermato")


def main():
    """Funzione principale."""
    parser = argparse.ArgumentParser(description="Multi-Automation System")
    parser.add_argument("--outlook", action="store_true", help="Esegui solo automazione Outlook")
    parser.add_argument("--psn", action="store_true", help="Esegui solo automazione PSN")
    parser.add_argument("--combined", action="store_true", help="Esegui Outlook + PSN sequenziale")
    parser.add_argument("--gui", action="store_true", help="Avvia GUI")
    parser.add_argument("--stats", action="store_true", help="Mostra statistiche")
    parser.add_argument("--csv", default="data/accounts.csv", help="Path al file CSV")
    
    args = parser.parse_args()
    
    # Configurazione logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Inizializza sistema
        system = MultiAutomationSystem(args.csv)
        system.is_running = True
        
        if args.gui:
            # Avvia GUI
            from gui.main_gui import MainGUI
            gui = MainGUI()
            gui.run()
            
        elif args.outlook:
            # Solo Outlook
            system.run_outlook_only()
            
        elif args.psn:
            # Solo PSN
            system.run_psn_only()
            
        elif args.combined:
            # Combinato
            system.run_combined()
            
        elif args.stats:
            # Statistiche
            system.show_statistics()
            
        else:
            # Nessun argomento, mostra help
            parser.print_help()
            
    except KeyboardInterrupt:
        central_logger.log_system("⏹️ Interruzione utente")
        system.stop()
    except Exception as e:
        central_logger.log_system(f"❌ Errore sistema: {e}", "ERROR")
        sys.exit(1)


if __name__ == "__main__":
    main() 