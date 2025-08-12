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
    
    def load_accounts(self, filter_completed: bool = False, service_filter: str = None) -> List[Dict[str, str]]:
        """
        Carica gli account dal CSV con filtro intelligente.
        
        Args:
            filter_completed: Se True, filtra gli account già completati
            service_filter: Filtro per servizio specifico ('outlook', 'psn', 'combined')
            
        Returns:
            Lista di account filtrati
        """
        if not os.path.exists(self.csv_path):
            self.logger.error(f"❌ File CSV non trovato: {self.csv_path}")
            return []
        
        accounts = []
        skipped_count = 0
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for i, row in enumerate(reader, 1):
                    # Salta righe completamente vuote
                    if not row or all((v is None or str(v).strip() == '') for v in row.values()):
                        continue
                    
                    # Applica filtro intelligente
                    should_process = self._should_process_account(row, service_filter)
                    
                    if not should_process:
                        skipped_count += 1
                        email = row.get('outlook_email', 'N/A')
                        outlook_status = row.get('outlook_status', '').strip()
                        psn_status = row.get('psn_status', '').strip()
                        
                        if service_filter == 'outlook' and outlook_status == 'success':
                            self.logger.info(f"⏩ Account Outlook già completato: {email}")
                        elif service_filter == 'psn' and psn_status == 'success':
                            self.logger.info(f"⏩ Account PSN già completato: {email}")
                        elif service_filter == 'combined' and outlook_status == 'success' and psn_status == 'success':
                            self.logger.info(f"⏩ Account completamente processato: {email}")
                        continue
                    
                    # Assicura che tutti i campi siano presenti
                    for col in self._get_all_columns():
                        if col not in row:
                            row[col] = ''
                    
                    accounts.append(row)
            
            self.logger.info(f"✅ Caricati {len(accounts)} account dal CSV (saltati {skipped_count})")
            return accounts
            
        except Exception as e:
            self.logger.error(f"❌ Errore caricamento CSV: {e}")
            return []
    
    def _should_process_account(self, account: Dict[str, str], service_filter: str = None) -> bool:
        """
        Determina se un account deve essere processato basandosi sul filtro del servizio.
        
        Args:
            account: Dati dell'account
            service_filter: Filtro per servizio ('outlook', 'psn', 'combined')
            
        Returns:
            True se l'account deve essere processato
        """
        # Gestione sicura dei valori None
        outlook_status = account.get('outlook_status')
        psn_status = account.get('psn_status')
        
        # Converti in stringa e pulisci
        outlook_status = str(outlook_status).strip().lower() if outlook_status is not None else ''
        psn_status = str(psn_status).strip().lower() if psn_status is not None else ''
        
        # Stati che indicano necessità di riprocessamento
        needs_processing_states = ['', 'pending', 'failed', 'error', 'timeout', 'none']
        
        if service_filter == 'outlook':
            # Processa solo se Outlook non è completato
            return outlook_status != 'success' or outlook_status in needs_processing_states
            
        elif service_filter == 'psn':
            # Processa solo se PSN non è completato
            return psn_status != 'success' or psn_status in needs_processing_states
            
        elif service_filter == 'combined':
            # Processa se almeno uno dei due servizi non è completato
            outlook_needs_processing = outlook_status != 'success' or outlook_status in needs_processing_states
            psn_needs_processing = psn_status != 'success' or psn_status in needs_processing_states
            return outlook_needs_processing or psn_needs_processing
            
        else:
            # Nessun filtro, processa tutto
            return True
    
    def get_account_status_summary(self) -> Dict[str, int]:
        """
        Ottiene un riepilogo degli stati degli account.
        
        Returns:
            Dizionario con conteggi degli stati
        """
        try:
            accounts = self.load_accounts(filter_completed=False)
            
            summary = {
                'total_accounts': len(accounts),
                'outlook_success': 0,
                'outlook_pending': 0,
                'outlook_failed': 0,
                'psn_success': 0,
                'psn_pending': 0,
                'psn_failed': 0,
                'both_success': 0,
                'needs_processing': 0
            }
            
            for account in accounts:
                # Gestione sicura dei valori None
                outlook_status_raw = account.get('outlook_status')
                psn_status_raw = account.get('psn_status')
                
                outlook_status = str(outlook_status_raw).strip().lower() if outlook_status_raw is not None else ''
                psn_status = str(psn_status_raw).strip().lower() if psn_status_raw is not None else ''
                
                # Conteggio stati Outlook
                if outlook_status == 'success':
                    summary['outlook_success'] += 1
                elif outlook_status in ['', 'pending', 'failed', 'error', 'timeout']:
                    summary['outlook_pending'] += 1
                else:
                    summary['outlook_failed'] += 1
                
                # Conteggio stati PSN
                if psn_status == 'success':
                    summary['psn_success'] += 1
                elif psn_status in ['', 'pending', 'failed', 'error', 'timeout']:
                    summary['psn_pending'] += 1
                else:
                    summary['psn_failed'] += 1
                
                # Conteggio entrambi completati
                if outlook_status == 'success' and psn_status == 'success':
                    summary['both_success'] += 1
                
                # Conteggio che necessitano processing
                if self._should_process_account(account, 'combined'):
                    summary['needs_processing'] += 1
            
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ Errore calcolo riepilogo: {e}")
            return {}
    
    def get_accounts_for_service(self, service: str) -> List[Dict[str, str]]:
        """
        Ottiene gli account che necessitano processing per un servizio specifico.
        
        Args:
            service: Servizio ('outlook', 'psn', 'combined')
            
        Returns:
            Lista di account da processare
        """
        return self.load_accounts(filter_completed=True, service_filter=service)
    
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