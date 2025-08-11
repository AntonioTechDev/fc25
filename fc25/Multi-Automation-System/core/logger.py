"""
Centralized Logging System
==========================

Sistema di logging centralizzato per tutti i moduli.
Integrazione con GUI e formattazione modulare.
"""

import logging
import queue
import threading
import time
from typing import Dict, List, Optional


class CentralizedLogger:
    """
    Sistema di logging centralizzato per tutti i moduli.
    """
    
    def __init__(self):
        """Inizializza il logger centralizzato."""
        self.log_queue = queue.Queue()
        self.loggers: Dict[str, logging.Logger] = {}
        self.gui_handler = None
        self.is_running = False
        
    def get_logger(self, module_name: str) -> logging.Logger:
        """
        Ottiene un logger per un modulo specifico.
        
        Args:
            module_name: Nome del modulo (es. 'outlook', 'psn', 'system')
            
        Returns:
            Logger configurato per il modulo
        """
        if module_name not in self.loggers:
            logger = logging.getLogger(module_name)
            logger.setLevel(logging.INFO)
            
            # Handler per la coda GUI
            if self.gui_handler:
                logger.addHandler(self.gui_handler)
            
            # Handler per console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Formatter con prefisso modulo
            formatter = logging.Formatter(
                f'%(asctime)s - [{module_name.upper()}] %(message)s',
                datefmt='%H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            
            self.loggers[module_name] = logger
        
        return self.loggers[module_name]
    
    def setup_gui_handler(self, log_queue: queue.Queue):
        """
        Configura l'handler per la GUI.
        
        Args:
            log_queue: Coda per i log della GUI
        """
        self.gui_handler = GUILogHandler(log_queue)
        
        # Aggiungi handler a tutti i logger esistenti
        for logger in self.loggers.values():
            logger.addHandler(self.gui_handler)
    
    def log_system(self, message: str, level: str = "INFO"):
        """
        Logga un messaggio di sistema.
        
        Args:
            message: Messaggio da loggare
            level: Livello del log (INFO, WARNING, ERROR)
        """
        logger = self.get_logger("system")
        
        if level == "INFO":
            logger.info(message)
        elif level == "WARNING":
            logger.warning(message)
        elif level == "ERROR":
            logger.error(message)
    
    def log_module_start(self, module_name: str):
        """
        Logga l'inizio di un modulo.
        
        Args:
            module_name: Nome del modulo
        """
        self.log_system(f"🚀 Avvio modulo: {module_name.upper()}")
    
    def log_module_complete(self, module_name: str, success: bool = True):
        """
        Logga il completamento di un modulo.
        
        Args:
            module_name: Nome del modulo
            success: Se l'operazione è riuscita
        """
        status = "✅ Completato" if success else "❌ Fallito"
        self.log_system(f"{status} modulo: {module_name.upper()}")
    
    def log_progress(self, module_name: str, current: int, total: int):
        """
        Logga il progresso di un modulo.
        
        Args:
            module_name: Nome del modulo
            current: Step corrente
            total: Totale step
        """
        progress = (current / total) * 100 if total > 0 else 0
        self.log_system(f"📊 {module_name.upper()}: {current}/{total} ({progress:.1f}%)")
    
    def get_all_logs(self) -> List[Dict]:
        """
        Ottiene tutti i log dalla coda.
        
        Returns:
            Lista di log
        """
        logs = []
        while not self.log_queue.empty():
            try:
                log_entry = self.log_queue.get_nowait()
                logs.append(log_entry)
            except queue.Empty:
                break
        return logs


class GUILogHandler(logging.Handler):
    """
    Handler per inviare i log alla GUI.
    """
    
    def __init__(self, log_queue: queue.Queue):
        """
        Inizializza l'handler GUI.
        
        Args:
            log_queue: Coda per i log
        """
        super().__init__()
        self.log_queue = log_queue
    
    def emit(self, record):
        """
        Invia il record di log alla coda GUI.
        
        Args:
            record: Record di log da processare
        """
        try:
            msg = self.format(record)
            
            # Estrai il nome del modulo dal logger name
            module_name = record.name.upper()
            
            # Determina il colore basato sul livello
            if record.levelno >= logging.ERROR:
                color = "red"
            elif record.levelno >= logging.WARNING:
                color = "orange"
            else:
                color = "white"
            
            log_entry = {
                'module': module_name,
                'message': msg,
                'level': record.levelname,
                'color': color,
                'timestamp': time.strftime('%H:%M:%S')
            }
            
            self.log_queue.put(log_entry)
        except Exception:
            self.handleError(record)


# Istanza globale del logger centralizzato
central_logger = CentralizedLogger() 