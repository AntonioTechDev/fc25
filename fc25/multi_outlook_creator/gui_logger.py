"""
Multi Outlook Account Creator - GUI Logger
=========================================

Autore: Antonio De Biase
Versione: 2.0.0
Data: 2025-07-27

Descrizione:
GUI di monitoraggio log in tempo reale per l'automazione multi-account Outlook.
Mostra tutti i log dell'automazione in una finestra sempre visibile.

Caratteristiche:
- Finestra sempre in primo piano
- Posizione angolo basso-destra
- Auto-scroll dei log
- Colori per livelli log
- Bottone Clear
- Thread separato per non bloccare l'automazione
"""

import logging
import queue
import threading
import time
import tkinter as tk
from tkinter import scrolledtext, ttk


# =============================================================================
# CONFIGURAZIONE GUI
# =============================================================================

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 300
MAX_LOG_LINES = 1000
POLLING_INTERVAL = 100  # millisecondi


class LogHandler(logging.Handler):
    """
    Handler personalizzato per inviare i log alla GUI.
    """
    
    def __init__(self, queue):
        super().__init__()
        self.queue = queue
    
    def emit(self, record):
        """
        Invia il record di log alla coda GUI.
        
        Args:
            record: Record di log da processare
        """
        try:
            msg = self.format(record)
            self.queue.put((record.levelname, msg))
        except Exception:
            self.handleError(record)


class LogGUI:
    """
    GUI per il monitoraggio dei log in tempo reale.
    """
    
    def __init__(self):
        """Inizializza la GUI di monitoraggio log."""
        self.root = None
        self.log_queue = queue.Queue()
        self.max_lines = MAX_LOG_LINES
        self.gui_thread = None
        self.is_running = False
        
    def create_gui(self):
        """Crea e configura la finestra GUI."""
        self.root = tk.Tk()
        self.root.title("🔍 Monitor Log - Multi Outlook Creator")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        
        # Posiziona la finestra nell'angolo basso-destra
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - WINDOW_WIDTH - 20
        y = screen_height - WINDOW_HEIGHT - 40
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
        
        # Mantieni la finestra sempre in primo piano
        self.root.attributes('-topmost', True)
        
        # Configura il layout
        self.setup_layout()
        
        # Imposta il flag di esecuzione
        self.is_running = True
        
        # Gestisci la chiusura della finestra
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_layout(self):
        """Configura il layout della GUI."""
        # Frame principale
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Titolo
        title_label = ttk.Label(main_frame, text="📊 Log Monitor", 
                               font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 5))
        
        # Area di testo per i log
        self.log_text = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="black",
            fg="white",
            insertbackground="white",
            selectbackground="gray",
            height=15
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Frame per i controlli
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X)
        
        # Bottone Clear
        clear_button = ttk.Button(
            control_frame,
            text="🗑️ Clear Logs",
            command=self.clear_logs
        )
        clear_button.pack(side=tk.LEFT)
        
        # Label per il contatore
        self.counter_label = ttk.Label(control_frame, text="Log: 0")
        self.counter_label.pack(side=tk.RIGHT)
        
        # Configura i tag per i colori
        self.log_text.tag_configure("INFO", foreground="white")
        self.log_text.tag_configure("WARNING", foreground="orange")
        self.log_text.tag_configure("ERROR", foreground="red")
        self.log_text.tag_configure("CRITICAL", foreground="red", 
                                   font=("Consolas", 9, "bold"))
        
    def get_level_color(self, level):
        """
        Restituisce il tag colore per il livello di log.
        
        Args:
            level: Livello di log (INFO, WARNING, ERROR, CRITICAL)
            
        Returns:
            Nome del tag colore
        """
        level = level.upper()
        if level == "WARNING":
            return "WARNING"
        elif level in ["ERROR", "CRITICAL"]:
            return "CRITICAL"
        else:
            return "INFO"
    
    def add_log(self, level, message):
        """
        Aggiunge un log alla GUI.
        
        Args:
            level: Livello di log
            message: Messaggio da aggiungere
        """
        try:
            # Inserisci il nuovo log
            self.log_text.insert(tk.END, message + "\n")
            
            # Applica il colore
            tag = self.get_level_color(level)
            start_line = self.log_text.index("end-2c linestart")
            end_line = self.log_text.index("end-1c")
            self.log_text.tag_add(tag, start_line, end_line)
            
            # Mantieni solo le ultime max_lines righe
            lines = int(self.log_text.index("end-1c").split('.')[0])
            if lines > self.max_lines:
                excess = lines - self.max_lines
                self.log_text.delete("1.0", f"{excess + 1}.0")
            
            # Auto-scroll alla fine
            self.log_text.see(tk.END)
            
            # Aggiorna il contatore
            current_lines = int(self.log_text.index("end-1c").split('.')[0])
            self.counter_label.config(text=f"Log: {current_lines}")
            
        except Exception as e:
            print(f"Errore nell'aggiunta del log: {e}")
    
    def clear_logs(self):
        """Pulisce tutti i log dalla GUI."""
        self.log_text.delete(1.0, tk.END)
        self.counter_label.config(text="Log: 0")
    
    def on_closing(self):
        """Gestisce la chiusura della finestra."""
        self.is_running = False
        if self.root:
            self.root.destroy()
    
    def start(self):
        """Avvia la GUI nel thread principale."""
        self.create_gui()
        
        # Avvia il polling dei log in un thread separato
        def poll_thread():
            while self.is_running:
                try:
                    # Controlla se ci sono nuovi log
                    while True:
                        try:
                            level, message = self.log_queue.get_nowait()
                            # Usa after() per aggiornare la GUI dal thread principale
                            self.root.after(0, self.add_log, level, message)
                        except queue.Empty:
                            break
                except Exception as e:
                    print(f"Errore nel polling dei log: {e}")
                time.sleep(0.1)
        
        self.poll_thread = threading.Thread(target=poll_thread, daemon=True)
        self.poll_thread.start()
    
    def stop(self):
        """Ferma la GUI."""
        self.is_running = False
        if self.root:
            self.root.quit()


def setup_gui_logging():
    """
    Configura il sistema di logging per inviare i log alla GUI.
    
    Returns:
        Istanza della GUI logger
    """
    # Crea l'istanza della GUI
    gui_logger = LogGUI()
    
    # Avvia la GUI
    gui_logger.start()
    
    # Crea l'handler personalizzato
    gui_handler = LogHandler(gui_logger.log_queue)
    gui_handler.setLevel(logging.INFO)
    
    # Formatter per la GUI
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    gui_handler.setFormatter(formatter)
    
    # Aggiungi l'handler al logger root
    root_logger = logging.getLogger()
    root_logger.addHandler(gui_handler)
    
    return gui_logger 