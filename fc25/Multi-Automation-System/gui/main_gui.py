"""
Main GUI
========

Interfaccia grafica condivisa per tutti i moduli di automazione.
"""

import logging
import queue
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Dict, List, Optional

from core.logger import central_logger


class MainGUI:
    """
    GUI principale per tutti i moduli di automazione.
    """
    
    def __init__(self):
        """Inizializza la GUI principale."""
        self.root = tk.Tk()
        self.root.title("🎯 Multi-Automation System")
        self.root.geometry("800x600")
        
        # Coda per i log
        self.log_queue = queue.Queue()
        central_logger.setup_gui_handler(self.log_queue)
        
        # Stato dei moduli
        self.modules_status = {
            'outlook': {'enabled': True, 'running': False, 'progress': 0},
            'psn': {'enabled': True, 'running': False, 'progress': 0}
        }
        
        # Thread per l'aggiornamento log
        self.log_thread = None
        self.is_running = False
        
        self._setup_ui()
        self._start_log_thread()
    
    def _setup_ui(self):
        """Configura l'interfaccia utente."""
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurazione griglia
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Titolo
        title_label = ttk.Label(main_frame, text="🎯 Multi-Automation System", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Frame controlli moduli
        controls_frame = ttk.LabelFrame(main_frame, text="🎛️ Controlli Moduli", padding="10")
        controls_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Checkbox moduli
        self.outlook_var = tk.BooleanVar(value=True)
        self.psn_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(controls_frame, text="📧 Outlook Automation", 
                       variable=self.outlook_var).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(controls_frame, text="🎮 PSN Automation", 
                       variable=self.psn_var).grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        # Pulsanti controllo
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        self.start_button = ttk.Button(buttons_frame, text="▶️ Avvia", 
                                      command=self._start_automation)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(buttons_frame, text="⏹️ Ferma", 
                                     command=self._stop_automation, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="📊 Statistiche", 
                  command=self._show_statistics).grid(row=0, column=2)
        
        # Frame progresso
        progress_frame = ttk.LabelFrame(main_frame, text="📊 Progresso", padding="10")
        progress_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Progress bar generale
        ttk.Label(progress_frame, text="Progresso Generale:").grid(row=0, column=0, sticky=tk.W)
        self.general_progress = ttk.Progressbar(progress_frame, length=300, mode='determinate')
        self.general_progress.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        progress_frame.columnconfigure(1, weight=1)
        
        # Progress bar moduli
        ttk.Label(progress_frame, text="Outlook:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.outlook_progress = ttk.Progressbar(progress_frame, length=300, mode='determinate')
        self.outlook_progress.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(10, 0))
        
        ttk.Label(progress_frame, text="PSN:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.psn_progress = ttk.Progressbar(progress_frame, length=300, mode='determinate')
        self.psn_progress.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(10, 0))
        
        # Frame log
        log_frame = ttk.LabelFrame(main_frame, text="📝 Log", padding="10")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Controlli log
        log_controls_frame = ttk.Frame(log_frame)
        log_controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(log_controls_frame, text="Filtro:").pack(side=tk.LEFT)
        
        self.log_filter_var = tk.StringVar(value="all")
        filter_combo = ttk.Combobox(log_controls_frame, textvariable=self.log_filter_var, 
                                   values=["all", "outlook", "psn", "system"], 
                                   state="readonly", width=10)
        filter_combo.pack(side=tk.LEFT, padx=(5, 0))
        filter_combo.bind('<<ComboboxSelected>>', self._filter_logs)
        
        ttk.Button(log_controls_frame, text="🗑️ Pulisci", 
                  command=self._clear_logs).pack(side=tk.RIGHT)
        
        # Area log
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurazione tag per colori
        self.log_text.tag_configure("outlook", foreground="blue")
        self.log_text.tag_configure("psn", foreground="green")
        self.log_text.tag_configure("system", foreground="black")
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("warning", foreground="orange")
    
    def _start_log_thread(self):
        """Avvia il thread per l'aggiornamento dei log."""
        self.is_running = True
        self.log_thread = threading.Thread(target=self._update_logs, daemon=True)
        self.log_thread.start()
    
    def _update_logs(self):
        """Aggiorna i log dalla coda."""
        while self.is_running:
            try:
                # Controlla la coda ogni 100ms
                log_entry = self.log_queue.get(timeout=0.1)
                self._add_log_entry(log_entry)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Errore aggiornamento log: {e}")
    
    def _add_log_entry(self, log_entry: Dict):
        """Aggiunge un entry di log alla GUI."""
        try:
            # Determina il tag basato sul modulo e livello
            module = log_entry.get('module', 'SYSTEM').lower()
            level = log_entry.get('level', 'INFO')
            
            if level == 'ERROR':
                tag = 'error'
            elif level == 'WARNING':
                tag = 'warning'
            elif module == 'outlook':
                tag = 'outlook'
            elif module == 'psn':
                tag = 'psn'
            else:
                tag = 'system'
            
            # Formatta il messaggio
            timestamp = log_entry.get('timestamp', '')
            message = log_entry.get('message', '')
            
            # Aggiungi alla GUI (thread-safe)
            self.root.after(0, self._insert_log, f"[{timestamp}] {message}\n", tag)
            
        except Exception as e:
            print(f"Errore aggiunta log: {e}")
    
    def _insert_log(self, text: str, tag: str):
        """Inserisce testo nel log (thread-safe)."""
        try:
            self.log_text.insert(tk.END, text, tag)
            self.log_text.see(tk.END)
            
            # Limita il numero di righe
            lines = int(self.log_text.index('end-1c').split('.')[0])
            if lines > 1000:
                self.log_text.delete('1.0', '100.0')
                
        except Exception as e:
            print(f"Errore inserimento log: {e}")
    
    def _filter_logs(self, event=None):
        """Filtra i log in base al modulo selezionato."""
        filter_value = self.log_filter_var.get()
        
        # Mostra/nascondi tag in base al filtro
        for tag in ['outlook', 'psn', 'system']:
            if filter_value == 'all' or filter_value == tag:
                self.log_text.tag_config(tag, elide=False)
            else:
                self.log_text.tag_config(tag, elide=True)
    
    def _clear_logs(self):
        """Pulisce l'area log."""
        self.log_text.delete('1.0', tk.END)
    
    def _start_automation(self):
        """Avvia l'automazione."""
        try:
            # Aggiorna stato moduli
            self.modules_status['outlook']['enabled'] = self.outlook_var.get()
            self.modules_status['psn']['enabled'] = self.psn_var.get()
            
            # Verifica che almeno un modulo sia abilitato
            if not any(module['enabled'] for module in self.modules_status.values()):
                messagebox.showwarning("Attenzione", "Seleziona almeno un modulo da eseguire!")
                return
            
            # Aggiorna UI
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            # Log avvio
            central_logger.log_system("🚀 Avvio automazione...")
            
            # TODO: Implementare avvio automazione
            # Per ora, simula l'avvio
            self._simulate_automation()
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore avvio automazione: {e}")
            self._reset_ui()
    
    def _stop_automation(self):
        """Ferma l'automazione."""
        try:
            central_logger.log_system("⏹️ Fermata automazione...")
            self._reset_ui()
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore fermata automazione: {e}")
    
    def _reset_ui(self):
        """Ripristina l'UI allo stato iniziale."""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        # Reset progress bar
        self.general_progress['value'] = 0
        self.outlook_progress['value'] = 0
        self.psn_progress['value'] = 0
        
        # Reset stato moduli
        for module in self.modules_status.values():
            module['running'] = False
            module['progress'] = 0
    
    def _simulate_automation(self):
        """Simula l'automazione per test."""
        def simulate():
            import time
            
            # Simula progresso Outlook
            if self.modules_status['outlook']['enabled']:
                central_logger.log_module_start("outlook")
                for i in range(10):
                    if not self.is_running:
                        break
                    self.modules_status['outlook']['progress'] = (i + 1) * 10
                    self.outlook_progress['value'] = self.modules_status['outlook']['progress']
                    central_logger.log_progress("outlook", i + 1, 10)
                    time.sleep(1)
                central_logger.log_module_complete("outlook")
            
            # Simula progresso PSN
            if self.modules_status['psn']['enabled']:
                central_logger.log_module_start("psn")
                for i in range(8):
                    if not self.is_running:
                        break
                    self.modules_status['psn']['progress'] = (i + 1) * 12.5
                    self.psn_progress['value'] = self.modules_status['psn']['progress']
                    central_logger.log_progress("psn", i + 1, 8)
                    time.sleep(1)
                central_logger.log_module_complete("psn")
            
            # Aggiorna progresso generale
            total_progress = sum(module['progress'] for module in self.modules_status.values())
            enabled_modules = sum(1 for module in self.modules_status.values() if module['enabled'])
            if enabled_modules > 0:
                self.general_progress['value'] = total_progress / enabled_modules
            
            central_logger.log_system("✅ Automazione completata!")
            self._reset_ui()
        
        # Avvia simulazione in thread separato
        simulation_thread = threading.Thread(target=simulate, daemon=True)
        simulation_thread.start()
    
    def _show_statistics(self):
        """Mostra le statistiche."""
        try:
            # TODO: Implementare statistiche reali
            stats_text = """
📊 Statistiche Sistema:
=====================
• Account totali: 50
• Outlook completati: 23
• PSN completati: 18
• Entrambi completati: 15
• In attesa: 35
            """
            
            messagebox.showinfo("Statistiche", stats_text)
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore caricamento statistiche: {e}")
    
    def run(self):
        """Avvia la GUI."""
        try:
            central_logger.log_system("🎯 GUI Multi-Automation avviata")
            self.root.mainloop()
        except Exception as e:
            print(f"Errore GUI: {e}")
        finally:
            self.is_running = False 