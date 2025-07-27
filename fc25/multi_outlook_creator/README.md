# Multi Outlook Account Creator

**Autore:** Antonio De Biase  
**Versione:** 2.0.0  
**Data:** 2025-07-27

## 📋 Descrizione

Script di automazione per la creazione automatica di account Outlook con GUI di monitoraggio log in tempo reale. Utilizza riconoscimento immagini per navigare attraverso il processo di registrazione.

## ✨ Caratteristiche

- 🤖 **Automazione completa** del processo di registrazione Outlook
- 🔍 **GUI di monitoraggio log** sempre visibile in tempo reale
- 🎯 **Riconoscimento immagini** per navigazione precisa
- 🔄 **Cambio MAC address** automatico per ogni account
- 📊 **Gestione CSV** degli account con tracking status
- 🌐 **Supporto browser** Chrome/Firefox in modalità incognito
- 🎨 **Colori differenziati** per livelli log (INFO, WARNING, ERROR)
- ⚡ **Thread separati** per GUI e automazione

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

### 2. Preparazione File

```bash
# Struttura progetto
fc25/
├── accounts.csv          # File con i dati degli account
├── templates/            # Cartella con le immagini template
└── multi_outlook_creator/
    ├── main.py           # Punto di ingresso
    └── ...
```

### 3. Formato CSV

```csv
email,password,first_name,last_name,birth_year,status
user1@outlook.com,password123,Mario,Rossi,1990,
user2@outlook.com,password456,Giulia,Bianchi,1985,
```

### 4. Esecuzione

```bash
python -m multi_outlook_creator.main
```

## ⚙️ Configurazione

Tutte le variabili di configurazione sono nel file `automation.py`:

### File e Path
- `TEMPLATES_DIR`: Cartella con le immagini template
- `CSV_FILE_PATH`: Path al file CSV degli account

### Browser
- `BROWSER`: Browser da utilizzare ('chrome', 'firefox')
- `INCOGNITO_MODE`: Modalità incognito/privata
- `CHROME_OPEN_INDEX`: Step in cui aprire Chrome

### Timing e Delay
- `PAGE_LOAD_DELAY`: Attesa dopo apertura browser (15s)
- `CLICK_DELAY`: Attesa tra ogni azione (8s)
- `ACCOUNT_DELAY`: Attesa tra account (30s)
- `MAC_WAIT_SECONDS`: Attesa dopo cambio MAC (10s)

### Automazione
- `MATCH_CONFIDENCE`: Soglia matching immagini (0.4)
- `MAX_RETRIES`: Tentativi per template (3)
- `MOUSE_SPEED`: Velocità movimento mouse (0.5s)

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

## 📁 Struttura Progetto

```
multi_outlook_creator/
├── __init__.py           # Informazioni modulo
├── main.py              # Punto di ingresso principale
├── automation.py        # Motore di automazione
├── gui_logger.py        # GUI di monitoraggio log
├── browser_utils.py     # Gestione browser
├── csv_utils.py         # Gestione file CSV
├── mac_utils.py         # Gestione MAC address
├── requirements.txt     # Dipendenze Python
└── README.md           # Documentazione
```

## 🔧 Dipendenze

### Python
- `opencv-python>=4.8.0` - Riconoscimento immagini
- `pyautogui>=0.9.54` - Automazione mouse/tastiera
- `pynput>=1.7.6` - Digitazione avanzata (opzionale)
- `numpy>=1.24.0` - Elaborazione array

### Sistema (macOS)
- `spoof-mac` - Cambio MAC address
- `sudo` - Permessi amministrativi

## 🎯 Funzionalità Principali

### Automazione
1. **Caricamento account** dal CSV
2. **Cambio MAC address** per ogni account
3. **Apertura browser** in modalità incognito
4. **Navigazione automatica** tramite template matching
5. **Compilazione form** con dati account
6. **Gestione captcha** e step successivi
7. **Aggiornamento status** nel CSV

### GUI Monitoraggio
1. **Intercettazione log** dal sistema di logging
2. **Visualizzazione tempo reale** con colori
3. **Auto-scroll** ai nuovi log
4. **Gestione buffer** per performance
5. **Thread separato** per non bloccare automazione

## 🛠️ Troubleshooting

### Cambio MAC Address Fallisce
```bash
# Verifica installazione spoof-mac
which spoof-mac

# Estendi timestamp sudo
sudo -v

# Reinstalla se necessario
brew install spoof-mac
```

### Template Non Trovati
- Verifica che le immagini siano nella cartella `templates/`
- Controlla i nomi file nella sequenza `AUTOMATION_SEQUENCE`
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

## 📄 Licenza

Progetto privato per uso personale.

## 🤝 Supporto

Per problemi o domande, controlla:
1. La sezione Troubleshooting
2. I log nella GUI di monitoraggio
3. La configurazione nel file `automation.py` 