# Sistema di Filtro Intelligente - Multi-Automation-System

## 🚦 Panoramica

Il sistema di filtro intelligente evita di riprocessare account già completati e gestisce correttamente gli stati di automazione per Outlook e PSN, ottimizzando l'efficienza del sistema.

## 🎯 Logica di Filtro

### **Automazione Singola**

#### **Outlook**
- **Processa solo:** Account con `outlook_status != 'success'`
- **Salta:** Account con `outlook_status = 'success'`

#### **PSN**
- **Processa solo:** Account con `psn_status != 'success'`
- **Salta:** Account con `psn_status = 'success'`

### **Automazione Combinata (Outlook + PSN)**

- **Processa:** Account se almeno uno dei due status non è `'success'`
- **Esegue solo:** L'automazione necessaria per il servizio non completato
- **Obiettivo finale:** Entrambe le colonne con stato `'success'`

## 🚨 Gestione Stati

### **Stati da Riprocessare**
```
pending, failed, error, timeout → Riprocessa
'' (vuoto), null, None → Riprocessa
Qualsiasi valore != 'success' → Riprocessa
```

### **Stati da Saltare**
```
'success' → Salta (già completato)
```

## 🎯 Comportamento per Automazione

### **Solo Outlook**
```bash
python main.py --outlook
```
- ✅ Salta account con `outlook_status = 'success'`
- 🔄 Processa account con `outlook_status != 'success'`
- 📊 Mostra riepilogo stati prima dell'esecuzione

### **Solo PSN**
```bash
python main.py --psn
```
- ✅ Salta account con `psn_status = 'success'`
- 🔄 Processa account con `psn_status != 'success'`
- 📊 Mostra riepilogo stati prima dell'esecuzione

### **Combinata**
```bash
python main.py --combined
```
- ✅ Salta account con entrambi `outlook_status = 'success'` E `psn_status = 'success'`
- 🔄 Processa account se almeno uno dei due servizi non è completato
- 🎯 Esegue solo i servizi necessari per ogni account
- 📊 Mostra riepilogo dettagliato degli stati

## 📊 Statistiche Dettagliate

### **Comando Statistiche**
```bash
python main.py --stats
```

### **Output Esempio**
```
📊 Statistiche Dettagliate Sistema:
==================================
📧 OUTLOOK:
   • Completati: 25
   • In attesa: 15
   • Falliti: 10

🎮 PSN:
   • Completati: 20
   • In attesa: 20
   • Falliti: 10

🔄 COMBINATO:
   • Entrambi completati: 15
   • Necessitano processing: 35
   • Totale account: 50

💡 SUGGERIMENTI:
   • Solo Outlook: 25 account da processare
   • Solo PSN: 30 account da processare
   • Combinato: 35 account da processare
```

## 🔧 Funzioni Principali

### **1. Filtro Intelligente**
```python
def _should_process_account(self, account: Dict[str, str], service_filter: str = None) -> bool:
    """
    Determina se un account deve essere processato.
    
    Args:
        account: Dati dell'account
        service_filter: 'outlook', 'psn', 'combined'
    
    Returns:
        True se l'account deve essere processato
    """
```

### **2. Caricamento Account Filtrati**
```python
def get_accounts_for_service(self, service: str) -> List[Dict[str, str]]:
    """
    Ottiene gli account che necessitano processing per un servizio.
    
    Args:
        service: 'outlook', 'psn', 'combined'
    
    Returns:
        Lista di account da processare
    """
```

### **3. Riepilogo Stati**
```python
def get_account_status_summary(self) -> Dict[str, int]:
    """
    Ottiene un riepilogo dettagliato degli stati degli account.
    
    Returns:
        Dizionario con conteggi degli stati
    """
```

## 📋 Esempi di Utilizzo

### **Scenario 1: Tutti gli account Outlook completati**
```bash
python main.py --outlook
```
**Output:**
```
📊 Riepilogo stati: 50 completati, 0 in attesa, 0 falliti
✅ Tutti gli account Outlook sono già completati!
```

### **Scenario 2: Alcuni account PSN da processare**
```bash
python main.py --psn
```
**Output:**
```
📊 Riepilogo stati: 20 completati, 25 in attesa, 5 falliti
📊 Processando 30 account PSN
🔄 Account 1/30: f900-fifa@outlook.com (stato: pending)
🔄 Account 2/30: f901-fifa@outlook.com (stato: failed)
```

### **Scenario 3: Automazione combinata intelligente**
```bash
python main.py --combined
```
**Output:**
```
📊 Riepilogo stati:
   • Outlook: 40 completati, 10 in attesa
   • PSN: 30 completati, 20 in attesa
   • Entrambi completati: 25
   • Necessitano processing: 25

📊 Processando 25 account
🔄 Account 1/25: f900-fifa@outlook.com
   • Outlook: success
   • PSN: pending
⏩ Outlook già completato, salto...
🎮 Avvio automazione PSN...
```

## 🛡️ Gestione Errori

### **Valori Null/None**
- ✅ Gestione sicura dei valori `None`
- ✅ Conversione automatica in stringa vuota
- ✅ Evita errori di tipo

### **Case Sensitivity**
- ✅ Normalizzazione automatica a lowercase
- ✅ Gestione di `'SUCCESS'`, `'Success'`, `'success'`

### **Whitespace**
- ✅ Rimozione automatica di spazi extra
- ✅ Gestione di `'  success  '` → `'success'`

## 🎯 Vantaggi del Sistema

### **1. Efficienza**
- ⚡ Evita riprocessamento inutile
- ⚡ Riduce tempo di esecuzione
- ⚡ Ottimizza risorse

### **2. Flessibilità**
- 🔄 Supporta automazione singola e combinata
- 🔄 Gestisce stati multipli
- 🔄 Adattabile a diversi scenari

### **3. Trasparenza**
- 📊 Statistiche dettagliate
- 📊 Logging informativo
- 📊 Suggerimenti intelligenti

### **4. Robustezza**
- 🛡️ Gestione errori completa
- 🛡️ Casi edge coperti
- 🛡️ Compatibilità con dati esistenti

## 🚀 Come Avviare

### **1. Verifica Stati**
```bash
python main.py --stats
```

### **2. Automazione Singola**
```bash
# Solo Outlook
python main.py --outlook

# Solo PSN
python main.py --psn
```

### **3. Automazione Combinata**
```bash
python main.py --combined
```

### **4. GUI**
```bash
python main.py --gui
```

## 📈 Monitoraggio Progresso

Il sistema fornisce feedback dettagliato durante l'esecuzione:

- 📊 **Riepilogo iniziale:** Stati prima dell'esecuzione
- 🔄 **Progresso account:** Account corrente e stato
- ⏩ **Account saltati:** Log degli account già completati
- ✅ **Completamento:** Riepilogo finale

## 🎯 Risultato Finale

Dopo l'esecuzione completa, tutti gli account processati avranno:

```
outlook_status: 'success'
psn_status: 'success'
```

Il sistema di filtro intelligente garantisce che:
- ✅ Nessun account venga riprocessato inutilmente
- ✅ Tutti gli account necessari vengano processati
- ✅ L'efficienza sia massimizzata
- ✅ Il progresso sia tracciabile 