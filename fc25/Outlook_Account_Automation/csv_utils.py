"""
Multi Outlook Account Creator - CSV Utils
=======================================

Autore: Antonio De Biase
Versione: 2.0.0
Data: 2025-07-27

Descrizione:
Funzioni per la gestione del file CSV degli account.
Carica gli account, esclude quelli già completati e aggiorna lo status.

Formato CSV atteso:
email,password,first_name,last_name,birth_year,status
"""

import csv
import logging
from pathlib import Path
from typing import Dict, List


# =============================================================================
# CONFIGURAZIONE
# =============================================================================

REQUIRED_FIELDS = ['email', 'password', 'first_name', 'last_name', 'birth_year', 'status']


def load_accounts_from_csv(csv_path: str, logger: logging.Logger = None) -> List[Dict[str, str]]:
    """
    Carica gli account dal file CSV, escludendo quelli con status 'success'.
    
    Aggiorna il file aggiungendo colonne/campi mancanti e logga eventuali problemi.
    
    Args:
        csv_path: Path al file CSV
        logger: Logger opzionale per i messaggi
        
    Returns:
        Lista di account da processare
    """
    if not Path(csv_path).exists():
        if logger:
            logger.error(f"❌ File CSV non trovato: {csv_path}")
        return []
    
    accounts = []
    updated_rows = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for i, row in enumerate(reader, 1):
                # Salta righe completamente vuote
                if not row or all((v is None or str(v).strip() == '') for v in row.values()):
                    continue
                
                # Assicura che tutti i campi richiesti siano presenti
                for field in REQUIRED_FIELDS:
                    if field not in row or row[field] is None:
                        row[field] = ''
                
                # Salta gli account già completati con status 'success'
                if row['status'].strip().lower() == 'success':
                    if logger:
                        logger.info(f"⏩ Account già completato (success): {row['email']}")
                    updated_rows.append(row)
                    continue
                
                # Verifica che i campi minimi siano presenti
                missing_fields = [field for field in REQUIRED_FIELDS[:-1] 
                                if not row[field].strip()]
                if missing_fields:
                    if logger:
                        logger.warning(f"⚠️ Riga {i} saltata - Campi mancanti: {missing_fields}")
                    updated_rows.append(row)
                    continue
                
                accounts.append({
                    'email': row['email'].strip(),
                    'password': row['password'].strip(),
                    'first_name': row['first_name'].strip(),
                    'last_name': row['last_name'].strip(),
                    'birth_year': row['birth_year'].strip()
                })
                updated_rows.append(row)
        
        # Aggiorna il file CSV se necessario (aggiunge colonne/campi vuoti)
        with open(csv_path, 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=REQUIRED_FIELDS)
            writer.writeheader()
            writer.writerows(updated_rows)
        
        if logger:
            logger.info(f"✅ Caricati {len(accounts)} account dal CSV (solo da processare)")
        
        return accounts
        
    except Exception as e:
        if logger:
            logger.error(f"❌ Errore lettura CSV: {e}")
        return []


def update_account_status_in_csv(csv_path: str, email: str, status: str, 
                               logger: logging.Logger = None):
    """
    Aggiorna la colonna 'status' per l'account con la email specificata nel CSV.
    
    Args:
        csv_path: Path al file CSV
        email: Email dell'account da aggiornare
        status: Nuovo status ('success' o 'denied')
        logger: Logger opzionale per i messaggi
    """
    try:
        # Leggi tutti i dati
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = list(csv.DictReader(file))
            fieldnames = reader[0].keys() if reader else REQUIRED_FIELDS
            
            if 'status' not in fieldnames:
                fieldnames = list(fieldnames) + ['status']
        
        # Aggiorna lo status
        for row in reader:
            if row['email'].strip() == email.strip():
                row['status'] = status
        
        # Scrivi di nuovo il CSV
        with open(csv_path, 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(reader)
        
        if logger:
            logger.info(f"📝 Aggiornato status '{status}' per {email} nel CSV")
            
    except Exception as e:
        if logger:
            logger.error(f"❌ Errore aggiornamento CSV: {e}") 