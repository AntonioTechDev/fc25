#!/usr/bin/env python3
"""
Script di automazione per test su ambiente locale.
SOLO PER USO SU SITI E AMBIENTI DI SVILUPPO PROPRI.
"""

import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# =====================
# Costanti di configurazione
# =====================
CSV_PATH = "test_accounts.csv"
DEFAULT_PASSWORD = "Sdser34df"
TEST_SITE_URL = "https://signup.live.com/"

# Selettori usati nel form
SELECTORS = {
    'email_input': "floatingLabelInput5",
    'password_input': "floatingLabelInput14",
    'birth_day_dropdown': "BirthDayDropdown",
    'birth_month_dropdown': "BirthMonthDropdown",
    'birth_year_input': "floatingLabelInput24",
    'first_name_input': "firstNameInput",
    'last_name_input': "lastNameInput",
    'next_button': "//button[contains(., 'Successivo')]",
    'submit_input': "//input[@type='submit']",
    'create_account_btn': "//span[text()='Crea un account']",
    'birth_day_option': "//div[@role='option' and text()='1']",
    'birth_month_option': "//div[@role='option' and contains(., 'gennaio')]",
}

# =====================
# Funzioni di utilità
# =====================
def log(msg):
    """Stampa un messaggio di log standardizzato."""
    print(f"[LOG] {msg}")

def log_error(msg):
    """Stampa un messaggio di errore standardizzato."""
    print(f"[ERROR] {msg}")

def take_screenshot(driver, prefix="test_result"):
    """Salva screenshot per debug."""
    try:
        timestamp = int(time.time())
        screenshot_name = f"{prefix}_{timestamp}.png"
        driver.save_screenshot(screenshot_name)
        log(f"Screenshot salvato: {screenshot_name}")
    except Exception:
        pass

# =====================
# Selenium helpers
# =====================
def wait_and_click(driver, selector, by_type=By.XPATH, timeout=10):
    """Attende e clicca un elemento."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by_type, selector))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", element)
        return True
    except TimeoutException:
        log_error(f"Timeout: elemento non trovato: {selector}")
        return False
    except Exception as e:
        log_error(f"Errore click: {e}")
        return False

def wait_and_type(driver, selector, text, by_type=By.ID, timeout=10):
    """Attende e scrive in un campo di input."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((by_type, selector))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        element.clear()
        time.sleep(0.5)
        element.send_keys(text)
        return True
    except TimeoutException:
        log_error(f"Timeout: campo non trovato: {selector}")
        return False
    except Exception as e:
        log_error(f"Errore scrittura: {e}")
        return False

# =====================
# Step di automazione form
# =====================
def open_signup_page(driver):
    """Apre la pagina di signup e gestisce eventuale bottone 'Crea un account'."""
    log(f"Navigazione a: {TEST_SITE_URL}")
    driver.get(TEST_SITE_URL)
    time.sleep(5)  # Attesa caricamento pagina
    try:
        create_btn = driver.find_element(By.XPATH, SELECTORS['create_account_btn'])
        if create_btn.is_displayed():
            log("Clic su 'Crea un account'")
            driver.execute_script("arguments[0].click();", create_btn)
            time.sleep(3)
    except NoSuchElementException:
        log("Bottone 'Crea account' non necessario o già nella pagina giusta")


def fill_email(driver, email):
    """Compila il campo email e clicca su Successivo."""
    log(f"Inserimento email: {email}")
    if not wait_and_type(driver, SELECTORS['email_input'], email):
        return False
    log("Clic Successivo (email)")
    if not wait_and_click(driver, SELECTORS['email_btn']):
        # Prova selettore alternativo
        if not wait_and_click(driver, SELECTORS['submit_input']):
            return False
    time.sleep(3)
    return True

def fill_password(driver, password):
    """Compila il campo password e clicca su Successivo."""
    log("Inserimento password")
    if not wait_and_type(driver, SELECTORS['password_input'], password):
        return False
    log("Clic Successivo (password)")
    if not wait_and_click(driver, SELECTORS['email_btn']):
        return False
    time.sleep(3)
    return True

def fill_birthdate(driver, year="1990"):
    """Compila la data di nascita (giorno, mese, anno) e clicca su Successivo."""
    log("Selezione giorno")
    if not wait_and_click(driver, SELECTORS['birth_day_dropdown'], By.ID):
        return False
    if not wait_and_click(driver, SELECTORS['birth_day_option']):
        return False
    log("Selezione mese")
    if not wait_and_click(driver, SELECTORS['birth_month_dropdown'], By.ID):
        return False
    if not wait_and_click(driver, SELECTORS['birth_month_option']):
        return False
    log("Inserimento anno")
    if not wait_and_type(driver, SELECTORS['birth_year_input'], year):
        return False
    log("Clic Successivo (data)")
    if not wait_and_click(driver, SELECTORS['email_btn']):
        return False
    time.sleep(3)
    return True

def fill_name_surname(driver, name, surname="Cognome Test"):
    """Compila nome e cognome e clicca su Successivo."""
    log("Inserimento nome e cognome")
    if not wait_and_type(driver, SELECTORS['first_name_input'], name):
        return False
    if not wait_and_type(driver, SELECTORS['last_name_input'], surname):
        return False
    log("Clic Successivo (nome)")
    if not wait_and_click(driver, SELECTORS['email_btn']):
        return False
    time.sleep(5)
    return True

def solve_captcha_press_hold(driver, hold_seconds=10):
    """
    Hack: entra nell'iframe, clicca su px-captcha, tiene premuto ENTER per hold_seconds secondi.
    """
    try:
        log("Cerco iframe del captcha...")
        iframe = driver.find_element(By.XPATH, "//iframe[contains(@title, 'Sfida di verifica')]")
        driver.switch_to.frame(iframe)
        log("Entrato nell'iframe captcha.")
        captcha_area = driver.find_element(By.ID, "px-captcha")
        time.sleep(1)
        log("Clicco sull'area captcha per attivare il focus...")
        captcha_area.click()
        time.sleep(1)
        log(f"Tengo premuto ENTER per {hold_seconds} secondi...")
        actions = ActionChains(driver)
        actions.key_down(Keys.ENTER).perform()
        time.sleep(hold_seconds)
        actions.key_up(Keys.ENTER).perform()
        log("ENTER rilasciato.")
        time.sleep(2)
        log("Attendo che la pagina aggiorni lo stato del captcha...")
        time.sleep(3)
        driver.switch_to.default_content()
        return True
    except Exception as e:
        log_error(f"Errore durante hack captcha: {e}")
        try:
            driver.switch_to.default_content()
        except Exception:
            pass
        return False

# =====================
# Automazione principale del form
# =====================
def automate_signup_form(driver, account_data):
    """Esegue tutti gli step di automazione del form di registrazione."""
    try:
        open_signup_page(driver)
        if not fill_email(driver, account_data['email']):
            log_error("Impossibile inserire email")
            return False
        if not fill_password(driver, DEFAULT_PASSWORD):
            log_error("Impossibile inserire password")
            return False
        if not fill_birthdate(driver):
            log_error("Impossibile inserire data di nascita")
            return False
        if not fill_name_surname(driver, account_data.get('name', 'Nome Test')):
            log_error("Impossibile inserire nome/cognome")
            return False
        # === Risoluzione captcha ===
        log("Provo a risolvere il captcha se presente...")
        solve_captcha_press_hold(driver)
        log("Gestione passaggi finali (eventuali step aggiuntivi non implementati)")
        return True
    except WebDriverException as e:
        log_error(f"WebDriver: {str(e)}")
        return False
    except Exception as e:
        log_error(f"Errore durante automazione: {str(e)}")
        return False
    finally:
        take_screenshot(driver)

# =====================
# Setup browser
# =====================
def setup_browser():
    """
    Configura e restituisce un'istanza di Chrome il più simile possibile a un utente reale.
    Rimuove incognito e opzioni anti-automation.
    """
    options = webdriver.ChromeOptions()
    # NON usare modalità incognito
    # NON usare opzioni anti-automation
    # User agent standard (opzionale, puoi anche non settarlo)
    # options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    # Opzioni solo per stabilità
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    # Puoi commentare la riga sotto se vuoi sembrare ancora più "umano"
    # options.add_argument("--disable-extensions")
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(1280, 720)
        return driver
    except Exception as e:
        log_error(f"Errore inizializzazione browser: {e}")
        log("Verifica che ChromeDriver sia installato e aggiornato")
        return None

# =====================
# Main
# =====================
def main():
    """Funzione principale: gestisce il ciclo di test e aggiorna il CSV."""
    print("\n==============================")
    print("🧪 Script di Automazione Form Semplificato")
    print("==============================\n")
    # Carica dati di test
    try:
        df = pd.read_csv(CSV_PATH)
        df['status'] = df['status'].astype('object')
        log(f"Caricati {len(df)} account di test")
    except Exception as e:
        log_error(f"Errore lettura CSV: {e}")
        return
    # Trova primo account non testato
    untested = df[(df['status'].isna()) | (df['status'] == '')]
    if untested.empty:
        log("Tutti gli account sono già stati testati")
        print("💡 Svuota la colonna 'status' nel CSV per ripetere i test")
        return
    account = untested.iloc[0]
    log(f"Testing account: {account['email']}")
    # Setup browser
    log("Avvio browser con impostazioni ottimizzate...")
    driver = setup_browser()
    if not driver:
        log_error("Impossibile avviare il browser")
        return
    try:
        log("Inizio automazione form...")
        success = automate_signup_form(driver, account.to_dict())
        # Aggiorna stato nel CSV
        status = 'success' if success else 'failed'
        df.loc[df['email'] == account['email'], 'status'] = status
        df.to_csv(CSV_PATH, index=False)
        log(f"Stato aggiornato nel CSV: {status}")
        if success:
            print("🎉 Automazione completata con successo!")
        else:
            print("⚠️ Automazione fallita - controlla gli screenshot per debug")
    except Exception as e:
        log_error(f"Errore generale: {str(e)}")
        try:
            df.loc[df['email'] == account['email'], 'status'] = 'error'
            df.to_csv(CSV_PATH, index=False)
        except Exception:
            pass
    finally:
        log("Chiusura browser...")
        try:
            driver.quit()
        except Exception:
            pass
        print("✅ Script completato")

if __name__ == "__main__":
    main()