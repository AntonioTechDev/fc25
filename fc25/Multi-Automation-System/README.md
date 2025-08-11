# Multi-Automation System

**Autore:** Antonio De Biase  
**Versione:** 2.0.0  
**Data:** 2025-07-27

## 📋 Descrizione

Sistema di automazione professionale modulare per la creazione automatica di account Outlook e PSN con GUI di monitoraggio log in tempo reale. Utilizza riconoscimento immagini per navigare attraverso i processi di registrazione.

## ✨ Caratteristiche Principali

- 🤖 **Automazione completa** del processo di registrazione Outlook e PSN
- 🔍 **GUI di monitoraggio log** sempre visibile in tempo reale
- 🎯 **Riconoscimento immagini** per navigazione precisa
- 🔄 **Cambio MAC address** automatico per ogni account
- 📊 **Gestione CSV** degli account con tracking status
- 🌐 **Supporto browser** Chrome/Firefox in modalità incognito
- 🎨 **Colori differenziati** per livelli log (INFO, WARNING, ERROR)
- ⚡ **Thread separati** per GUI e automazione
- 🏗️ **Architettura modulare** scalabile e mantenibile
- 🖥️ **Supporto multi-monitor** con spostamento automatico finestra

## 🚀 Quick Start

### 1. Installazione Dipendenze

```bash
# Dipendenze Python
pip install -r requirements.txt

# Spoof-mac per cambio MAC address (macOS)
brew install spoof-mac

# Estendi timestamp sudo
sudo -v
```

### 2. Configurazione Sudo per Spoof-Mac

```bash
# Configura sudoers per spoof-mac (una sola volta)
echo "$(whoami) ALL=(ALL) NOPASSWD: /opt/homebrew/bin/spoof-mac" | sudo tee /etc/sudoers.d/spoof-mac

# Verifica configurazione
sudo -n /opt/homebrew/bin/spoof-mac randomize en0
```

### 3. Preparazione File

```bash
# Struttura progetto
Multi-Automation-System/
├── data/accounts.csv          # File con i dati degli account
├── templates/                 # Cartella con le immagini template
│   ├── outlook_images/        # Template Outlook
│   └── psn_images/           # Template PSN
├── modules/                   # Moduli di automazione
├── core/                      # Funzioni core condivise
├── gui/                       # Interfaccia grafica
└── main.py                    # Punto di ingresso
```

### 4. Formato CSV

```csv
email,password,first_name,last_name,birth_year,status,psn_id,psn_email,psn_psw,data_creazione_psn,status_psn
user1@outlook.com,password123,Mario,Rossi,1990,,mariorossi517,user1@outlook.com,Psn2024!,,,
user2@outlook.com,password456,Giulia,Bianchi,1985,,giuliabianchi123,user2@outlook.com,Psn2024!,,,
```

### 5. Esecuzione

```bash
# Modalità CLI
python main.py --outlook      # Solo automazione Outlook
python main.py --psn          # Solo automazione PSN
python main.py --combined     # Outlook + PSN sequenziale
python main.py --gui          # GUI per selezione moduli
python main.py --stats        # Visualizzazione statistiche

# Modalità GUI
python main.py --gui
```

## 🏗️ Architettura Modulare

### Struttura Directory

```
Multi-Automation-System/
├── README.md                  # 📖 Documentazione completa
├── requirements.txt           # 📦 Dipendenze Python
├── main.py                    # Entry point principale
├── gui/
│   ├── __init__.py
│   └── main_gui.py           # GUI condivisa
├── modules/
│   ├── __init__.py
│   ├── outlook_automation.py # Modulo Outlook
│   └── psn_automation.py     # Modulo PSN
├── core/
│   ├── __init__.py
│   ├── base_automator.py     # Classe base per automator
│   ├── common_functions.py   # Funzioni condivise
│   ├── csv_handler.py        # Gestione CSV unificata
│   └── logger.py             # Sistema logging condiviso
├── templates/
│   ├── outlook_images/       # Immagini Outlook
│   └── psn_images/          # Immagini PSN
├── data/
│   └── accounts.csv         # File dati condiviso
└── tests/
    └── test_architecture.py # Test architettura
```

### Componenti Core

#### **core/base_automator.py**
- **Classe base astratta** per tutti gli automator
- **Interfaccia comune** e funzionalità condivise
- **Template matching** unificato
- **Gestione progresso** standardizzata

#### **core/common_functions.py**
- **Coordinate detection** e click/scroll operations
- **Data generation utilities** (PSN ID, password)
- **Image matching functions** condivise
- **Browser management** unificato
- **Multi-monitor support** integrato

#### **core/csv_handler.py**
- **Unified CSV operations** per tutti i moduli
- **Dynamic column management** automatico
- **Data validation/completion** intelligente
- **Backup automatico** con versioning

#### **core/logger.py**
- **Centralized logging system** per tutti i moduli
- **GUI integration hooks** per log in tempo reale
- **Module-specific log formatting** con colori
- **Thread-safe logging** per GUI

### Moduli di Automazione

#### **modules/outlook_automation.py**
- **Classe OutlookAutomator** ereditata da BaseAutomator
- **Logica specifica Outlook** completamente isolata
- **26 template** per riconoscimento elementi
- **21 step** di automazione

#### **modules/psn_automation.py**
- **Classe PSNAutomator** ereditata da BaseAutomator
- **Logica specifica PSN** completamente isolata
- **23 template** per riconoscimento elementi
- **23 step** di automazione

## ⚙️ Configurazione

### File e Path
- `TEMPLATES_DIR`: Cartella con le immagini template
- `CSV_FILE_PATH`: Path al file CSV degli account

### Browser
- `BROWSER`: Browser da utilizzare ('chrome', 'firefox')
- `INCOGNITO_MODE`: Modalità incognito/privata
- `MOVE_BROWSER_TO_PRIMARY`: Sposta browser sul primo schermo (utile per multi-monitor)

### Automazione
- `ENABLE_PSN_AUTOMATION`: Abilita automazione PSN dopo Outlook
- `MATCH_CONFIDENCE`: Soglia matching immagini (0.4)
- `MAX_RETRIES`: Tentativi per template (3)

### Timing e Delay
- `PAGE_LOAD_DELAY`: Attesa dopo apertura browser (15s)
- `CLICK_DELAY`: Attesa tra ogni azione (8s)
- `ACCOUNT_DELAY`: Attesa tra account (30s)
- `MAC_WAIT_SECONDS`: Attesa dopo cambio MAC (10s)

## 🖥️ Supporto Multi-Monitor

### Rilevamento Automatico
- **Rilevamento multi-monitor**: Il sistema rileva automaticamente se ci sono più monitor
- **Spostamento intelligente**: La finestra del browser viene spostata sul primo schermo solo se necessario
- **Configurazione opzionale**: Può essere disabilitata impostando `MOVE_BROWSER_TO_PRIMARY = False`

### Come Funziona
1. **Rilevamento**: All'avvio, il sistema rileva il numero di monitor
2. **Apertura browser**: Il browser si apre normalmente
3. **Spostamento**: Se multi-monitor rilevato, la finestra viene spostata sul primo schermo
4. **Screenshot**: Gli screenshot vengono presi dal primo schermo dove ora si trova il browser

## 🖥️ GUI di Monitoraggio

La GUI si apre automaticamente nell'angolo basso-destra dello schermo:

- **Sempre in primo piano** (stay on top)
- **Auto-scroll** dei log in tempo reale
- **Colori per livelli log**:
  - 🔵 INFO: Bianco
  - 🟡 WARNING: Arancione  
  - 🔴 ERROR: Rosso
- **Bottone Clear** per pulire i log
- **Contatore log** in tempo reale
- **Buffer limitato** a 1000 righe per performance

### Layout Modulare
```
┌─────────────────────────────────────┐
│ [▶️ Outlook] [▶️ PSN] [▶️ Combined]   │
├─────────────────────────────────────┤
│ 📊 Progress: [████░░░] 60%          │
├─────────────────────────────────────┤
│ 📝 Logs (Unified):                 │
│ [OUTLOOK] Email created...          │
│ [PSN] Account registration...       │
│ [SYSTEM] CSV updated...             │
└─────────────────────────────────────┘
```

## 🎮 Automazione PSN

L'automazione include la creazione automatica di account PSN utilizzando le email Outlook appena create.

### Caratteristiche
- **🔄 Integrazione automatica** dopo creazione email Outlook
- **🖥️ Sessione browser mantenuta** per verifica email futura
- **📊 Aggiornamento CSV** con dati PSN completi
- **🎮 Generazione intelligente** PSN ID e password
- **📋 Template matching** per tutti i step PSN

### Flusso Operativo
1. **✅ Email Outlook creata** con successo
2. **🆕 Nuova tab PSN** aperta automaticamente
3. **📝 Form PSN compilato** con dati correlati
4. **🎮 Account PSN creato** con ID e password generati
5. **📊 CSV aggiornato** con tutti i dati PSN

### Dati PSN Generati
- **PSN ID**: Basato su nome/cognome + numeri casuali
- **PSN Email**: Stessa email Outlook
- **PSN Password**: Derivata dalla password Outlook
- **Data Creazione**: Timestamp automatico
- **Status**: SUCCESS/FAILED/PENDING_VERIFICATION

## 🧪 Test e Verifica

### Test Completati
```bash
python tests/test_modular_architecture.py
```

### Risultati Test
- ✅ **Core Logger**: Funzionante con moduli multipli
- ✅ **CSV Handler**: Gestione unificata con 51 account
- ✅ **Base Automator**: Classe base funzionante
- ✅ **Outlook Automator**: 26 template, 21 step
- ✅ **PSN Automator**: 23 template, 23 step
- ✅ **Struttura Directory**: Tutte le directory create
- ✅ **File Principali**: Tutti i file implementati
- ✅ **Integrazione**: Sistema modulare funzionante

## 🔧 Dipendenze

### Python
- `opencv-python>=4.8.0` - Riconoscimento immagini
- `pyautogui>=0.9.54` - Automazione mouse/tastiera
- `pynput>=1.7.6` - Digitazione avanzata (opzionale)
- `numpy>=1.24.0` - Elaborazione array

### Sistema (macOS)
- `spoof-mac` - Cambio MAC address
- `sudo` - Permessi amministrativi

## 🛠️ Troubleshooting

### Cambio MAC Address Fallisce
```bash
# Verifica installazione spoof-mac
which spoof-mac

# Se non installato
brew install spoof-mac

# Configura sudoers per spoof-mac (una sola volta)
echo "$(whoami) ALL=(ALL) NOPASSWD: /opt/homebrew/bin/spoof-mac" | sudo tee /etc/sudoers.d/spoof-mac

# Test senza password
sudo -n /opt/homebrew/bin/spoof-mac randomize en0
```

### Template Non Trovati
- Verifica che le immagini siano nella cartella `templates/`
- Controlla i nomi file nella sequenza di automazione
- Assicurati che le immagini siano in formato PNG

### Browser Non Si Apre
- Verifica che Chrome/Firefox sia installato
- Controlla i permessi di esecuzione
- Prova a cambiare `BROWSER` in configurazione

## 📝 Log e Debug

I log vengono mostrati sia nel terminale che nella GUI:

- **INFO**: Operazioni normali
- **WARNING**: Problemi non critici
- **ERROR**: Errori che bloccano l'operazione

### Esempi Log
```
2025-07-27 12:10:39 - 🇮🇹 Script multi-outlook-account avviato
2025-07-27 12:10:39 - 🔍 GUI di monitoraggio log attiva
2025-07-27 12:10:39 - 🚀 Avvio automazione multi-account
2025-07-27 12:10:39 - 🔄 Cambio MAC address su en0...
2025-07-27 12:10:39 - ✅ MAC address cambiato con successo
```

## 🔒 Sicurezza

- **Dati sensibili** vengono mascherati nei log
- **Modalità incognito** per ogni sessione
- **Cambio MAC address** per evitare tracking
- **Gestione errori** robusta

## 🚀 Estensibilità

### Aggiungere Nuovi Moduli
```python
# modules/new_service_automation.py
class NewServiceAutomator(BaseAutomator):
    def __init__(self):
        super().__init__(
            service_name="new_service",
            image_folder="new_service_images"
        )
    
    def run_automation(self):
        # Implementation
        pass
```

### Plugin System
- **Auto-discovery**: Scan modules/ per automazioni
- **Dynamic loading**: Import runtime moduli
- **Consistent interface**: BaseAutomator class
- **Easy integration**: Hook standard per GUI/CSV/Log

## 📊 Vantaggi dell'Architettura Modulare

### ✅ **Modularità**
- **Separazione responsabilità**: Ogni modulo è indipendente
- **Riutilizzabilità**: Componenti condivisi tra moduli
- **Manutenibilità**: Modifiche isolate per modulo
- **Testabilità**: Test unitari per ogni modulo

### ✅ **Scalabilità**
- **Framework estendibile**: Nuovi moduli facilmente aggiungibili
- **Plugin system**: Auto-discovery di nuovi servizi
- **Configurazione flessibile**: Ogni modulo configurabile
- **Architettura evolutiva**: Preparata per future estensioni

### ✅ **Robustezza**
- **Gestione errori**: Centralizzata e modulare
- **Logging avanzato**: Tracciamento completo delle operazioni
- **Backup automatico**: Protezione dati con versioning
- **Validazione dati**: Controlli di consistenza integrati

### ✅ **Usabilità**
- **GUI unificata**: Interfaccia per tutti i moduli
- **CLI flessibile**: Opzioni multiple per esecuzione
- **Monitoraggio real-time**: Progress e log in tempo reale
- **Statistiche avanzate**: Metriche complete del sistema

## 🔮 Roadmap Futura

### v2.1.0 - Miglioramenti Imminenti
- [ ] Configurazione GUI per modificare parametri runtime
- [ ] Pausa/Riprendi automazione dalla GUI
- [ ] Statistiche account processati
- [ ] Export log in file
- [ ] Tema scuro/chiaro

### v3.0.0 - Funzionalità Avanzate
- [ ] Supporto Windows e Linux completo
- [ ] API REST per controllo remoto
- [ ] Integrazione con database
- [ ] Plugin system avanzato
- [ ] Machine learning per riconoscimento

## 📄 Licenza

Progetto privato per uso personale.

## 🤝 Supporto

Per problemi o domande, controlla:
1. La sezione Troubleshooting
2. I log nella GUI di monitoraggio
3. La configurazione nei file dei moduli 