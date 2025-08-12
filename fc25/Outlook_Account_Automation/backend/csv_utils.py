"""
CSV Utilities
=============

Funzioni per la gestione dei file CSV degli account.
"""

import csv
import logging
import os
from typing import Dict, List, Optional


def load_accounts_from_csv(csv_path: str, logger: logging.Logger = None) -> List[Dict[str, str]]:
    """
    Carica gli account dal file CSV.
    
    Args:
        csv_path: Path al file CSV
        logger: Logger per i messaggi
        
    Returns:
        Lista di dizionari con i dati degli account
    """
    accounts = []
    
    try:
        if not os.path.exists(csv_path):
            if logger:
                logger.error(f"❌ File CSV non trovato: {csv_path}")
            return accounts
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                # Filtra account già processati
                if row.get('status', '').lower() not in ['completed', 'success']:
                    accounts.append(row)
        
        if logger:
            logger.info(f"📊 Caricati {len(accounts)} account da {csv_path}")
            
    except Exception as e:
        if logger:
            logger.error(f"❌ Errore caricamento CSV: {e}")
    
    return accounts


def update_account_status_in_csv(csv_path: str, email: str, status: str, 
                                logger: logging.Logger = None) -> bool:
    """
    Aggiorna lo status di un account nel file CSV.
    
    Args:
        csv_path: Path al file CSV
        email: Email dell'account da aggiornare
        status: Nuovo status
        logger: Logger per i messaggi
        
    Returns:
        True se l'aggiornamento è riuscito, False altrimenti
    """
    try:
        if not os.path.exists(csv_path):
            if logger:
                logger.error(f"❌ File CSV non trovato: {csv_path}")
            return False
        
        # Leggi tutto il file
        rows = []
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames
            rows = list(reader)
        
        # Trova e aggiorna l'account
        updated = False
        for row in rows:
            if row.get('email', '').strip() == email.strip():
                row['status'] = status
                updated = True
                break
        
        if not updated:
            if logger:
                logger.warning(f"⚠️ Account {email} non trovato nel CSV")
            return False
        
        # Scrivi il file aggiornato
        with open(csv_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        if logger:
            logger.info(f"✅ Status aggiornato per {email}: {status}")
        return True
        
    except Exception as e:
        if logger:
            logger.error(f"❌ Errore aggiornamento CSV: {e}")
        return False


def create_csv_template(csv_path: str, logger: logging.Logger = None) -> bool:
    """
    Crea un template CSV con le colonne necessarie.
    
    Args:
        csv_path: Path al file CSV da creare
        logger: Logger per i messaggi
        
    Returns:
        True se la creazione è riuscita, False altrimenti
    """
    try:
        fieldnames = [
            'email', 'password', 'first_name', 'last_name', 
            'birth_year', 'status', 'created_at', 'notes'
        ]
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
        
        if logger:
            logger.info(f"✅ Template CSV creato: {csv_path}")
        return True
        
    except Exception as e:
        if logger:
            logger.error(f"❌ Errore creazione template CSV: {e}")
        return False


def validate_csv_format(csv_path: str, logger: logging.Logger = None) -> bool:
    """
    Valida il formato del file CSV.
    
    Args:
        csv_path: Path al file CSV
        logger: Logger per i messaggi
        
    Returns:
        True se il formato è valido, False altrimenti
    """
    try:
        if not os.path.exists(csv_path):
            if logger:
                logger.error(f"❌ File CSV non trovato: {csv_path}")
            return False
        
        required_fields = ['email', 'password', 'first_name', 'last_name', 'birth_year']
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # Verifica campi richiesti
            missing_fields = [field for field in required_fields if field not in reader.fieldnames]
            
            if missing_fields:
                if logger:
                    logger.error(f"❌ Campi mancanti nel CSV: {missing_fields}")
                return False
            
            # Verifica che ci siano righe
            rows = list(reader)
            if not rows:
                if logger:
                    logger.warning("⚠️ File CSV vuoto")
                return True  # Non è un errore, solo un warning
        
        if logger:
            logger.info(f"✅ Formato CSV valido: {len(rows)} righe trovate")
        return True
        
    except Exception as e:
        if logger:
            logger.error(f"❌ Errore validazione CSV: {e}")
        return False


def get_accounts_count(csv_path: str, logger: logging.Logger = None) -> Dict[str, int]:
    """
    Conta gli account per status.
    
    Args:
        csv_path: Path al file CSV
        logger: Logger per i messaggi
        
    Returns:
        Dizionario con il conteggio per status
    """
    counts = {'total': 0, 'pending': 0, 'completed': 0, 'failed': 0, 'other': 0}
    
    try:
        if not os.path.exists(csv_path):
            return counts
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                counts['total'] += 1
                status = row.get('status', '').lower()
                
                if status in ['completed', 'success']:
                    counts['completed'] += 1
                elif status in ['failed', 'error', 'denied']:
                    counts['failed'] += 1
                elif status in ['pending', '']:
                    counts['pending'] += 1
                else:
                    counts['other'] += 1
        
        if logger:
            logger.info(f"📊 Conteggio account: {counts}")
            
    except Exception as e:
        if logger:
            logger.error(f"❌ Errore conteggio account: {e}")
    
    return counts 