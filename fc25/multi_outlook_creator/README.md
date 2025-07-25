# Multi Outlook Account Creator

Automazione completa per la creazione multipla di account Microsoft Outlook tramite browser, con cambio MAC address, gestione CSV, e riconoscimento immagini.

## 📁 Struttura del progetto

```
multi_outlook_creator/
│   main.py                # Punto di ingresso
│   automation.py          # Logica principale e orchestrazione
│   mac_utils.py           # Funzioni cambio MAC address
│   browser_utils.py       # Funzioni gestione browser
│   csv_utils.py           # Funzioni gestione CSV
│   requirements.txt       # Dipendenze Python
│   README.md              # Questo file
│   __init__.py            # Package marker
../templates/              # Template immagini per il riconoscimento
../accounts.csv            # File CSV con dati account
```

## ⚙️ Dipendenze
- Python 3.8+
- [pyautogui](https://pypi.org/project/PyAutoGUI/)
- [opencv-python](https://pypi.org/project/opencv-python/)
- [numpy](https://pypi.org/project/numpy/)
- [pynput](https://pypi.org/project/pynput/)
- [spoof-mac](https://github.com/feross/SpoofMAC) (via Homebrew)

### Installazione Python (consigliato: requirements.txt)

Per installare tutte le dipendenze Python necessarie:
```bash
pip install -r requirements.txt
```

Oppure, manualmente:
```bash
pip install pyautogui opencv-python numpy pynput
```

### Installazione spoof-mac (macOS)
```bash
brew install spoof-mac
```

## 🚀 Utilizzo
1. **Prepara il CSV**: inserisci gli account in `accounts.csv` (vedi esempio sotto).
2. **Prepara i template**: assicurati che la cartella `templates/` contenga tutte le immagini necessarie.
3. **Lancia lo script**:
   ```bash
   cd multi_outlook_creator
   python main.py
   ```

## 📄 Formato accounts.csv
```
email,password,first_name,last_name,birth_year,status
mario.rossi@outlook.com,Password123!,Mario,Rossi,1990,
...
```
- La colonna `status` viene aggiornata automaticamente dallo script (`success` o `denied`).

## 🖼️ Template immagini
Metti tutte le immagini di input (campi, bottoni, ecc.) nella cartella `templates/` a fianco della root del progetto.

## 🛠️ Troubleshooting
- **Permessi sudo**: per cambiare MAC address, lo script richiede la password di amministratore.
- **Errore cambio MAC**: assicurati che il Wi-Fi sia attivo e che l'adattatore sia corretto (`en0` di default).
- **Template non trovato**: verifica i path e la presenza delle immagini in `templates/`.
- **Browser non si apre**: assicurati che Chrome sia installato e accessibile.

## ✨ Personalizzazioni
- Modifica la sequenza di automazione in `automation.py` (`AUTOMATION_SEQUENCE`).
- Cambia l'adattatore di rete in `mac_utils.py` se necessario.
- Puoi aggiungere nuove funzioni modulari nei rispettivi file.

## 📧 Supporto
Per problemi o richieste, apri una issue o contatta lo sviluppatore. 