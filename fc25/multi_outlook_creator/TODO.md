# TODO - Multi Outlook Account Creator

- [ ] Abilitare spoof-mac senza password:
      Modificare il file sudoers per permettere l'esecuzione di spoof-mac senza richiesta password (vedi README o chiedi al maintainer per istruzioni precise).
      Esempio riga da aggiungere (sostituisci 'tuo_utente' con il tuo username):
      
      tuo_utente ALL=(ALL) NOPASSWD: /usr/local/bin/spoof-mac
      
      oppure (per Mac M1/M2):
      tuo_utente ALL=(ALL) NOPASSWD: /opt/homebrew/bin/spoof-mac