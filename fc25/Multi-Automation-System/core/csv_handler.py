"""
Unified CSV Handler
===================

Gestione CSV unificata per tutti i moduli.
Gestione dinamica delle colonne e validazione dati.
"""

import csv
import logging
import os
import shutil
import time
from pathlib import Path
from typing import Dict, List, Optional, Set


class UnifiedCSVHandler:
    """
    Gestore CSV unificato per tutti i moduli.
    """
    
    def __init__(self, csv_path: str, logger: logging.Logger = None):
        """
        Inizializza il gestore CSV.
        
        Args:
            csv_path: Path al file CSV
            logger: Logger per i messaggi
        """
        self.csv_path = csv_path
        self.logger = logger or logging.getLogger(__name__)
        self.backup_dir = os.path.join(os.path.dirname(csv_path), 'backups')
        
        # Crea directory backup se non esiste
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Schema base delle colonne
        self.base_columns = ['id', 'timestamp']
        
        # Colonne per ogni servizio
        self.service_columns = {
            'outlook': [
                'outlook_email', 'outlook_psw', 'outlook_status', 'outlook_created'
            ],
            'psn': [
                'psn_id', 'psn_email', 'psn_psw', 'psn_status', 'psn_created'
            ]
        }
        
        # Inizializza il file CSV se non esiste
        self._initialize_csv()
    
    def _initialize_csv(self):
        """Inizializza il file CSV con tutte le colonne necessarie."""
        if not os.path.exists(self.csv_path):
            self._create_new_csv()
        else:
            self._update_csv_schema()
    
    def _create_new_csv(self):
        """Crea un nuovo file CSV con tutte le colonne."""
        all_columns = self._get_all_columns()
        
        with open(self.csv_path, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(all_columns)
        
        self.logger.info(f"📄 Creato nuovo file CSV: {self.csv_path}")
    
    def _update_csv_schema(self):
        """Aggiorna lo schema del CSV esistente."""
        try:
            # Leggi il CSV esistente
            with open(self.csv_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader, [])
                rows = list(reader)
            
            # Ottieni tutte le colonne necessarie
            all_columns = self._get_all_columns()
            
            # Trova colonne mancanti
            missing_columns = [col for col in all_columns if col not in header]
            
            if missing_columns:
                self.logger.info(f"📄 Aggiornamento schema CSV: {missing_columns}")
                
                # Aggiungi colonne mancanti
                for row in rows:
                    while len(row) < len(all_columns):
                        row.append('')
                
                # Scrivi il CSV aggiornato
                with open(self.csv_path, 'w', encoding='utf-8', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(all_columns)
                    writer.writerows(rows)
                
                self.logger.info(f"✅ Schema CSV aggiornato con {len(missing_columns)} colonne")
            
        except Exception as e:
            self.logger.error(f"❌ Errore aggiornamento schema CSV: {e}")
    
    def _get_all_columns(self) -> List[str]:
        """Ottiene tutte le colonne necessarie."""
        all_columns = self.base_columns.copy()
        
        for service_columns in self.service_columns.values():
            all_columns.extend(service_columns)
        
        return all_columns
    
    def load_accounts(self, filter_completed: bool = True) -> List[Dict[str, str]]:
        """
        Carica gli account dal CSV.
        
        Args:
            filter_completed: Se True, filtra gli account già completati
            
        Returns:
            Lista di account
        """
        if not os.path.exists(self.csv_path):
            self.logger.error(f"❌ File CSV non trovato: {self.csv_path}")
            return []
        
        accounts = []
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for i, row in enumerate(reader, 1):
                    # Salta righe completamente vuote
                    if not row or all((v is None or str(v).strip() == '') for v in row.values()):
                        continue
                    
                    # Filtra account completati se richiesto
                    if filter_completed:
                        outlook_completed = row.get('outlook_status', '').strip().lower() == 'success'
                        psn_completed = row.get('psn_status', '').strip().lower() == 'success'
                        
                        if outlook_completed and psn_completed:
                            self.logger.info(f"⏩ Account già completato: {row.get('outlook_email', 'N/A')}")
                            continue
                    
                    # Assicura che tutti i campi siano presenti
                    for col in self._get_all_columns():
                        if col not in row:
                            row[col] = ''
                    
                    accounts.append(row)
            
            self.logger.info(f"✅ Caricati {len(accounts)} account dal CSV")
            return accounts
            
        except Exception as e:
            self.logger.error(f"❌ Errore caricamento CSV: {e}")
            return []
    
    def update_account(self, email: str, service: str, data: Dict[str, str]):
        """
        Aggiorna i dati di un account per un servizio specifico.
        
        Args:
            email: Email dell'account
            service: Nome del servizio ('outlook' o 'psn')
            data: Dati da aggiornare
        """
        try:
            # Leggi tutti i dati
            with open(self.csv_path, 'r', encoding='utf-8') as file:
                reader = list(csv.DictReader(file))
                fieldnames = reader[0].keys() if reader else self._get_all_columns()
            
            # Trova e aggiorna l'account
            updated = False
            for row in reader:
                if row.get('outlook_email', '').strip() == email.strip():
                    # Aggiorna i dati del servizio
                    for key, value in data.items():
                        if key in fieldnames:
                            row[key] = value
                    
                    # Aggiorna timestamp
                    row['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    updated = True
                    break
            
            if updated:
                # Scrivi di nuovo il CSV
                with open(self.csv_path, 'w', encoding='utf-8', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(reader)
                
                self.logger.info(f"📝 Aggiornati dati {service} per {email}")
            else:
                self.logger.warning(f"⚠️ Account non trovato: {email}")
                
        except Exception as e:
            self.logger.error(f"❌ Errore aggiornamento CSV: {e}")
    
    def add_account(self, account_data: Dict[str, str]):
        """
        Aggiunge un nuovo account al CSV.
        
        Args:
            account_data: Dati dell'account
        """
        try:
            # Assicura che tutti i campi siano presenti
            all_columns = self._get_all_columns()
            for col in all_columns:
                if col not in account_data:
                    account_data[col] = ''
            
            # Aggiungi timestamp
            account_data['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
            
            # Aggiungi ID se non presente
            if not account_data.get('id'):
                account_data['id'] = str(int(time.time()))
            
            # Scrivi nel CSV
            with open(self.csv_path, 'a', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=all_columns)
                writer.writerow(account_data)
            
            self.logger.info(f"📝 Aggiunto nuovo account: {account_data.get('outlook_email', 'N/A')}")
            
        except Exception as e:
            self.logger.error(f"❌ Errore aggiunta account: {e}")
    
    def create_backup(self) -> str:
        """
        Crea un backup del file CSV.
        
        Returns:
            Path del file di backup
        """
        try:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(self.backup_dir, f'accounts_backup_{timestamp}.csv')
            
            shutil.copy2(self.csv_path, backup_path)
            
            self.logger.info(f"💾 Backup creato: {backup_path}")
            return backup_path
            
        except Exception as e:
            self.logger.error(f"❌ Errore creazione backup: {e}")
            return ""
    
    def get_missing_data(self, account: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Identifica i dati mancanti per un account.
        
        Args:
            account: Dati dell'account
            
        Returns:
            Dizionario con servizi e campi mancanti
        """
        missing_data = {}
        
        for service, columns in self.service_columns.items():
            missing_fields = []
            for col in columns:
                if not account.get(col, '').strip():
                    missing_fields.append(col)
            
            if missing_fields:
                missing_data[service] = missing_fields
        
        return missing_data
    
    def validate_account(self, account: Dict[str, str]) -> bool:
        """
        Valida i dati di un account.
        
        Args:
            account: Dati dell'account
            
        Returns:
            True se l'account è valido
        """
        # Controlla campi obbligatori
        required_fields = ['outlook_email', 'outlook_psw', 'outlook_status']
        
        for field in required_fields:
            if not account.get(field, '').strip():
                self.logger.warning(f"⚠️ Campo mancante: {field}")
                return False
        
        # Controlla formato email
        email = account.get('outlook_email', '')
        if '@' not in email:
            self.logger.warning(f"⚠️ Formato email non valido: {email}")
            return False
        
        return True
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Ottiene statistiche sui dati CSV.
        
        Returns:
            Dizionario con statistiche
        """
        try:
            accounts = self.load_accounts(filter_completed=False)
            
            stats = {
                'total_accounts': len(accounts),
                'outlook_completed': 0,
                'psn_completed': 0,
                'both_completed': 0,
                'pending': 0
            }
            
            for account in accounts:
                outlook_completed = account.get('outlook_status', '').strip().lower() == 'success'
                psn_completed = account.get('psn_status', '').strip().lower() == 'success'
                
                if outlook_completed:
                    stats['outlook_completed'] += 1
                if psn_completed:
                    stats['psn_completed'] += 1
                if outlook_completed and psn_completed:
                    stats['both_completed'] += 1
                else:
                    stats['pending'] += 1
            
            return stats
            
        except Exception as e:
            self.logger.error(f"❌ Errore calcolo statistiche: {e}")
            return {} 