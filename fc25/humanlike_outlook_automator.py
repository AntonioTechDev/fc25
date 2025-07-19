#!/usr/bin/env python3
"""
Automazione human-like per la registrazione di account Outlook.
- Nessun uso di Selenium o browser automation riconoscibile
- Usa pyautogui, pynput, opencv, pygetwindow, Pillow
- Movimenti e digitazione umana, template matching, gestione captcha

ISTRUZIONI:
1. Installa le dipendenze:
   pip install pyautogui pynput opencv-python pygetwindow pillow numpy
2. Prepara la cartella 'templates/' e inserisci i PNG degli elementi da cliccare/compilare per ogni step.
   - Usa i nomi indicati in TEMPLATE_PATHS qui sotto.
   - Puoi crearli con screenshot e crop (Paint, Anteprima, ecc.)
3. Apri la pagina di registrazione Outlook in una finestra browser visibile e porta la finestra in primo piano.
4. Avvia lo script.
5. NON usare il mouse/tastiera durante l'automazione.
"""
import pyautogui
import pygetwindow as gw
import cv2
import numpy as np
import random
import time
import logging
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key
import os
import webbrowser
import datetime

# === DICHIARAZIONE TEMPLATE PER OGNI STEP ===
TEMPLATE_PATHS = {
    "email_input": "templates/email_input.png",                  # Campo email
    "next_button": "templates/next_button.png",                 # Bottone "Successivo" (usato in più step)
    "password_input": "templates/password_input.png",           # Campo password
    "birth_day_dropdown": "templates/birth_day_dropdown.png",   # Dropdown giorno
    "birth_day_option": "templates/birth_day_option.png",       # Opzione giorno
    "birth_month_dropdown": "templates/birth_month_dropdown.png", # Dropdown mese
    "birth_month_option": "templates/birth_month_option.png",   # Opzione mese
    "birth_year_input": "templates/birth_year_input.png",       # Campo anno
    "date_confirm": "templates/date-btn-confirm.png",           # Bottone conferma data
    "first_name_input": "templates/first_name_input.png",       # Campo nome
    "last_name_input": "templates/last_name_input.png",         # Campo cognome
    "captcha_button": "templates/captcha_button.png",           # Bottone captcha
}

# === CONFIGURAZIONE ===
CONFIG = {
    "move_duration_range": (0.8, 2.0),
    "click_offset": 5,
    "type_wpm": 40,
    "type_error_rate": 0.02,
    "captcha_hold_range": (9, 12),
    "template_threshold": 0.75,  # Soglia abbassata
    "window_title": "Outlook"  # Titolo (o parte) della finestra browser
}

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler()]
)

class HumanLikeAutomator:
    def __init__(self, config=CONFIG):
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.config = config
        # Crea cartella debug_screens se non esiste
        if not os.path.exists('debug_screens'):
            os.makedirs('debug_screens')

    def bring_window_to_front(self):
        """
        Porta la finestra del browser in primo piano (compatibile Mac).
        Modifica browser_name se usi Safari invece di Chrome.
        """
        browser_name = "Google Chrome"  # Cambia in "Safari" se usi Safari
        import subprocess
        try:
            subprocess.run([
                "osascript", "-e",
                f'tell application "{browser_name}" to activate'
            ])
            time.sleep(1)
            logging.info(f"Finestra '{browser_name}' portata in primo piano.")
            return True
        except Exception as e:
            logging.error(f"Errore nel portare in primo piano {browser_name}: {e}")
            return False

    def screenshot(self, step_name=None):
        """Cattura screenshot dell'area visibile, salva in debug_screens e restituisce np.array."""
        img = pyautogui.screenshot()
        img_np = np.array(img)
        if step_name:
            ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            path = f'debug_screens/{ts}_{step_name}.png'
            img.save(path)
            logging.info(f"[DEBUG] Screenshot salvato: {path}")
        return img_np

    def find_element(self, template_path, threshold=None, region=None, step_name=None):
        """Trova un elemento tramite template matching in scala di grigi, salva screenshot per debug."""
        if not os.path.exists(template_path):
            logging.error(f"Template non trovato: {template_path}")
            return None
        img = self.screenshot(step_name=step_name) if region is None else np.array(pyautogui.screenshot(region=region))
        img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        # Salva anche la versione grigia per debug
        if step_name:
            ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            cv2.imwrite(f'debug_screens/{ts}_{step_name}_gray.png', img_gray)
        template = cv2.imread(template_path, 0)  # Carica già in grigio
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        logging.info(f"Matching '{template_path}': max_val={max_val:.3f}")
        if max_val >= (threshold or self.config["template_threshold"]):
            h, w = template.shape
            center = (max_loc[0] + w // 2, max_loc[1] + h // 2)
            logging.info(f"Elemento '{template_path}' trovato a {center}")
            return center
        else:
            logging.warning(f"Elemento '{template_path}' NON trovato.")
            return None

    def human_move(self, target_pos, duration=None):
        """Muove il mouse in modo umano (curva Bezier + jitter)."""
        start = pyautogui.position()
        end = (
            target_pos[0] + random.randint(-self.config["click_offset"], self.config["click_offset"]),
            target_pos[1] + random.randint(-self.config["click_offset"], self.config["click_offset"])
        )
        duration = duration or random.uniform(*self.config["move_duration_range"])
        steps = int(duration * 60)
        points = self._bezier_curve(start, end, steps)
        for point in points:
            pyautogui.moveTo(point[0], point[1], duration=0.01, _pause=False)
        time.sleep(random.uniform(0.05, 0.2))

    def _bezier_curve(self, start, end, steps):
        """Genera punti su una curva Bezier per movimento naturale."""
        cp = (
            (start[0] + end[0]) // 2 + random.randint(-100, 100),
            (start[1] + end[1]) // 2 + random.randint(-100, 100)
        )
        return [
            (
                int((1-t)**2 * start[0] + 2*(1-t)*t*cp[0] + t**2*end[0]),
                int((1-t)**2 * start[1] + 2*(1-t)*t*cp[1] + t**2*end[1])
            )
            for t in np.linspace(0, 1, steps)
        ]

    def human_click(self, pos):
        """Clicca con jitter umano."""
        self.human_move(pos)
        pyautogui.click()
        logging.info(f"Click umano a {pos}")

    def human_type(self, text, wpm=None, error_rate=None):
        """Digita testo con errori e correzioni casuali."""
        wpm = wpm or self.config["type_wpm"]
        error_rate = error_rate or self.config["type_error_rate"]
        delay = 60 / (wpm * 5)
        for char in text:
            if random.random() < error_rate:
                wrong = random.choice('abcdefghijklmnopqrstuvwxyz')
                self.keyboard.type(wrong)
                time.sleep(delay)
                self.keyboard.press(Key.backspace)
                self.keyboard.release(Key.backspace)
                logging.info(f"Errore simulato: '{wrong}' cancellato")
            self.keyboard.type(char)
            time.sleep(delay + random.uniform(-0.03, 0.07))
        logging.info(f"Testo digitato: {text}")

    def wait_random(self, min_s=0.7, max_s=2.0):
        t = random.uniform(min_s, max_s)
        time.sleep(t)
        logging.info(f"Attesa random: {t:.2f}s")

class OutlookAutomator(HumanLikeAutomator):
    def __init__(self, config=CONFIG):
        super().__init__(config)

    def run_automation_flow(self):
        if not self.bring_window_to_front():
            return
        # Parametri retry
        max_wait = 30  # secondi massimo per ogni step
        retry_interval = 1.5  # secondi tra un tentativo e l'altro

        def wait_and_click(step_key, type_text=None):
            """Aspetta che il template sia visibile, poi clicca e (opzionale) scrive."""
            start = time.time()
            while True:
                pos = self.find_element(TEMPLATE_PATHS[step_key], step_name=step_key)
                if pos:
                    self.human_click(pos)
                    self.wait_random()
                    if type_text:
                        self.human_type(type_text)
                    return True
                if time.time() - start > max_wait:
                    logging.error(f"Timeout step: {step_key}")
                    return False
                time.sleep(retry_interval)

        # Step 1: Inserisci email
        wait_and_click("email_input", type_text="testaccount123@outlook.com")
        # Step 2: Clicca "Successivo" dopo email
        wait_and_click("next_button")
        # Step 3: Inserisci password
        wait_and_click("password_input", type_text="PasswordSicura123!")
        # Step 4: Clicca "Successivo" dopo password
        wait_and_click("next_button")
        # Step 5: Compila data di nascita
        wait_and_click("birth_day_dropdown")
        wait_and_click("birth_day_option")
        wait_and_click("birth_month_dropdown")
        wait_and_click("birth_month_option")
        wait_and_click("birth_year_input", type_text="1990")
        # Step 6: Conferma data
        wait_and_click("date_confirm")
        # Step 7: Inserisci nome e cognome
        wait_and_click("first_name_input", type_text="NomeTest")
        wait_and_click("last_name_input", type_text="CognomeTest")
        # Step 8: Clicca "Successivo" dopo nome/cognome
        wait_and_click("next_button")
        # Step 9: Gestione captcha
        self.solve_captcha()
        # ... altri step se necessario ...

    def solve_captcha(self):
        """Strategia avanzata per il captcha press-and-hold"""
        if (pos := self.find_element(TEMPLATE_PATHS['captcha_button'], step_name="captcha_button")):
            self.human_move(pos)
            pyautogui.mouseDown()
            logging.info("Hold captcha: mouseDown")
            # Movimento casuale durante il hold
            hold_time = random.uniform(*self.config["captcha_hold_range"])
            t0 = time.time()
            while time.time() - t0 < hold_time:
                jitter = (
                    pos[0] + random.randint(-3, 3),
                    pos[1] + random.randint(-3, 3)
                )
                pyautogui.moveTo(jitter[0], jitter[1], duration=0.05, _pause=False)
                time.sleep(random.uniform(0.1, 0.3))
            pyautogui.mouseUp()
            logging.info(f"Hold captcha: mouseUp dopo {hold_time:.2f}s")
            self.wait_random(1, 2)
        else:
            logging.error("Captcha button non trovato!")

if __name__ == "__main__":
    # Apertura automatica della pagina di registrazione Outlook
    OUTLOOK_SIGNUP_URL = "https://signup.live.com/"
    webbrowser.open(OUTLOOK_SIGNUP_URL)
    print("[INFO] Attendi che la pagina di registrazione Outlook sia caricata...")
    time.sleep(5)  # Attendi che il browser apra la pagina
    automator = OutlookAutomator()
    automator.run_automation_flow() 