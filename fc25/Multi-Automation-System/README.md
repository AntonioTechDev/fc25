# 🎯 Multi-Automation System

Sistema di automazione modulare professionale per la creazione automatica di account Outlook e PSN con GUI di monitoraggio in tempo reale.

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

## 🏗️ Architettura Modulare

Il sistema è stato completamente ristrutturato in un'architettura modulare che supporta:

- **📧 Automazione Outlook**: Creazione account email con 26 template e 21 step
- **🎮 Automazione PSN**: Creazione account PlayStation Network con 23 template e 23 step
- **🖥️ GUI Unificata**: Interfaccia grafica per tutti i moduli
- **📊 Gestione CSV**: Sistema unificato per i dati con backup automatico
- **🔧 Estensibilità**: Framework per nuovi moduli con auto-discovery

## 📁 Struttura Progetto

```
Multi-Automation-System/
├── main.py                      # Entry point principale
├── gui/                         # Interfaccia grafica
│   └── main_gui.py             # GUI condivisa per tutti i moduli
├── modules/                     # Moduli di automazione
│   ├── outlook_automation.py   # Modulo Outlook
│   └── psn_automation.py       # Modulo PSN
├── core/                        # Componenti core condivisi
│   ├── base_automator.py       # Classe base per automator
│   ├── common_functions.py     # Funzioni condivise
│   ├── csv_handler.py          # Gestione CSV unificata
│   └── logger.py               # Sistema logging condiviso
├── templates/                   # Template immagini per automazione
│   ├── outlook_images/         # 26 template Outlook
│   └── psn_images/            # 23 template PSN
├── data/                        # Dati e configurazione
│   └── accounts.csv            # File dati condiviso
├── tests/                       # Test e verifiche
│   └── test_architecture.py   # Test architettura modulare
└── docs/                        # Documentazione completa
    ├── README.md               # Documentazione dettagliata
    └── requirements.txt        # Dipendenze Python
```

## 🚀 Quick Start

### 1. Installazione Dipendenze

```bash
# Dipendenze Python
pip install -r docs/requirements.txt

# Spoof-mac per cambio MAC address (macOS)
brew install spoof-mac

# Configurazione sudo per spoof-mac (una sola volta)
echo "$(whoami) ALL=(ALL) NOPASSWD: /opt/homebrew/bin/spoof-mac" | sudo tee /etc/sudoers.d/spoof-mac
```

### 2. Preparazione File

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

### 3. Formato CSV

```csv
email,password,first_name,last_name,birth_year,status,psn_id,psn_email,psn_psw,data_creazione_psn,status_psn
user1@outlook.com,password123,Mario,Rossi,1990,,mariorossi517,user1@outlook.com,Psn2024!,,,
user2@outlook.com,password456,Giulia,Bianchi,1985,,giuliabianchi123,user2@outlook.com,Psn2024!,,,
```

## 🎮 Utilizzo

### Modalità CLI
```bash
# Solo automazione Outlook
python main.py --outlook

# Solo automazione PSN
python main.py --psn

# Outlook + PSN sequenziale
python main.py --combined

# Visualizzazione statistiche
python main.py --stats

# GUI per selezione moduli
python main.py --gui
```

### Modalità GUI
```bash
python main.py --gui
```

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

## 🎯 Funzionalità Avanzate

### 🖥️ Supporto Multi-Monitor
- **Rilevamento automatico** del numero di monitor
- **Spostamento intelligente** della finestra browser sul primo schermo
- **Screenshot corretti** dal primo schermo per riconoscimento elementi

### 🎮 Automazione PSN
- **Integrazione automatica** dopo creazione email Outlook
- **Sessione browser mantenuta** per verifica email futura
- **Generazione intelligente** PSN ID e password
- **Template matching** per tutti i 23 step PSN

### 🔧 Estensibilità
- **Plugin system** con auto-discovery di nuovi moduli
- **Classe base** per creare nuovi automator
- **Interfaccia standardizzata** per tutti i moduli
- **Integrazione automatica** con GUI e CSV

## 🧪 Test e Verifica

```bash
# Test architettura modulare
python tests/test_architecture.py

# Verifica setup
python -c "from core.logger import Logger; print('✅ Setup verificato')"
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

## 📦 Dipendenze

### Python
- `opencv-python>=4.8.0` - Riconoscimento immagini
- `pyautogui>=0.9.54` - Automazione mouse/tastiera
- `pynput>=1.7.6` - Digitazione avanzata
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

# Configura sudoers per spoof-mac
echo "$(whoami) ALL=(ALL) NOPASSWD: /opt/homebrew/bin/spoof-mac" | sudo tee /etc/sudoers.d/spoof-mac

# Test senza password
sudo -n /opt/homebrew/bin/spoof-mac randomize en0
```

### Template Non Trovati
- Verifica che le immagini siano nella cartella `templates/`
- Controlla i nomi file nella sequenza di automazione
- Assicurati che le immagini siano in formato PNG

## 📚 Documentazione Completa

Per informazioni dettagliate su configurazione, architettura, troubleshooting e sviluppo, consulta la [documentazione completa](docs/README.md).

## 🔮 Roadmap

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
3. La [documentazione completa](docs/README.md) 