"""
🤖 Screen Automation con Template Matching

Questo script automatizza il click su elementi grafici usando il pattern matching.
Funziona catturando lo schermo, cercando un'immagine template e cliccandoci sopra.

IMPORTANTE: Su macOS Retina, le coordinate fisiche (screenshot) sono diverse
da quelle logiche (mouse), quindi convertiamo sempre le coordinate.

Dipendenze: pip install opencv-python pyautogui pillow numpy
"""

import cv2
import numpy as np
import pyautogui
import time
import logging
from pathlib import Path
from typing import Optional, Tuple

# Configurazione globale
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Sicurezza: muovi mouse nell'angolo per fermare l'esecuzione
pyautogui.FAILSAFE = True
# Pausa tra operazioni pyautogui per stabilità
pyautogui.PAUSE = 0.1


def capture_screen() -> np.ndarray:
    """
    Cattura tutto lo schermo corrente
    
    Returns:
        Screenshot in formato BGR (compatibile OpenCV)
    """
    screenshot = pyautogui.screenshot()  # Cattura in RGB
    screenshot_np = np.array(screenshot)
    # OpenCV usa BGR invece di RGB
    return cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)


def find_element(screenshot: np.ndarray, template_path: str, confidence: float = 0.8) -> Optional[Tuple[int, int]]:
    """
    Cerca un'immagine template dentro lo screenshot usando OpenCV
    
    Args:
        screenshot: Immagine dello schermo catturato
        template_path: Percorso dell'immagine da cercare (es. "icon.png")
        confidence: Soglia di similarità 0.0-1.0 (0.8 = 80% simile)
    
    Returns:
        Coordinate (x, y) del CENTRO dell'elemento trovato, None se non trovato
        ATTENZIONE: Restituisce coordinate fisiche (risoluzione screenshot)
    """
    # Verifica esistenza file template
    if not Path(template_path).exists():
        logger.error(f"Template non trovato: {template_path}")
        return None
    
    template = cv2.imread(template_path)
    if template is None:
        logger.error(f"Impossibile caricare: {template_path}")
        return None
    
    # Converte in scala di grigi per matching più robusto
    # (elimina variazioni di colore/luminosità)
    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    
    # Cerca template nello screenshot usando correlazione normalizzata
    result = cv2.matchTemplate(gray_screenshot, gray_template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    if max_val >= confidence:
        # max_loc è l'angolo top-left del match, calcoliamo il centro
        template_h, template_w = gray_template.shape
        center_x = max_loc[0] + template_w // 2
        center_y = max_loc[1] + template_h // 2
        
        logger.info(f"Elemento trovato: ({center_x}, {center_y}) - confidenza: {max_val:.2f}")
        return center_x, center_y
    
    logger.warning(f"Elemento non trovato - confidenza max: {max_val:.2f}")
    return None


def convert_to_logical_coordinates(physical_x: int, physical_y: int, screenshot_shape: Tuple[int, int]) -> Tuple[int, int]:
    """
    Converte coordinate fisiche (screenshot) in logiche (mouse)
    
    PROBLEMA: Su Retina displays, lo screenshot è 2x la risoluzione logica.
    Es. Screenshot 2880x1800, ma mouse funziona su 1440x900
    
    Args:
        physical_x, physical_y: Coordinate trovate nello screenshot
        screenshot_shape: Dimensioni dello screenshot (height, width, channels)
    
    Returns:
        Coordinate (x, y) per pyautogui.moveTo()
    """
    # Dimensioni logiche del desktop (quello che vede l'utente)
    logical_width, logical_height = pyautogui.size()
    # Dimensioni fisiche dello screenshot catturato
    physical_height, physical_width = screenshot_shape[:2]
    
    # Calcola fattori di scala
    scale_x = physical_width / logical_width
    scale_y = physical_height / logical_height
    
    # Converte dividendo per il fattore di scala
    logical_x = int(physical_x / scale_x)
    logical_y = int(physical_y / scale_y)
    
    logger.info(f"Fisiche: ({physical_x}, {physical_y}) → Logiche: ({logical_x}, {logical_y})")
    return logical_x, logical_y


def click_element(template_path: str, confidence: float = 0.8, max_retries: int = 3) -> bool:
    """
    🎯 FUNZIONE PRINCIPALE: Trova e clicca un elemento grafico
    
    Workflow:
    1. Cattura schermo
    2. Cerca template nell'immagine
    3. Converte coordinate fisiche → logiche
    4. Muove mouse e clicca
    5. Se fallisce, riprova fino a max_retries
    
    Args:
        template_path: Percorso dell'immagine da cercare (es. "./icons/button.png")
        confidence: Quanto deve essere simile 0.0-1.0 (consigliato: 0.7-0.9)
        max_retries: Quante volte riprovare se non trova l'elemento
        
    Returns:
        True se ha cliccato con successo, False altrimenti
        
    Esempio:
        success = click_element("./whatsapp_icon.png", confidence=0.8)
    """
    for attempt in range(max_retries):
        logger.info(f"Tentativo {attempt + 1}/{max_retries}")
        
        try:
            # Step 1: Cattura schermo corrente
            screenshot = capture_screen()
            
            # Step 2: Cerca elemento nell'immagine
            coordinates = find_element(screenshot, template_path, confidence)
            
            if coordinates:
                # Step 3: Converte coordinate per Retina displays
                logical_x, logical_y = convert_to_logical_coordinates(
                    coordinates[0], coordinates[1], screenshot.shape
                )
                
                # Step 4: Movimento fluido del mouse + click
                pyautogui.moveTo(logical_x, logical_y, duration=0.5)
                time.sleep(0.1)  # Piccola pausa per stabilità
                pyautogui.click()
                
                logger.info("✅ Click eseguito con successo!")
                return True
            
            # Se non trovato, aspetta prima di riprovare
            if attempt < max_retries - 1:
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"Errore: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
    
    logger.error("❌ Tutti i tentativi falliti")
    return False


def main():
    """Esempio di utilizzo"""
    template_path = "./fc25/templates/whatsapp_icon.png"
    
    try:
        success = click_element(template_path, confidence=0.8, max_retries=3)
        
        if success:
            print("🎯 Automazione completata!")
        else:
            print("💥 Elemento non trovato")
            
    except KeyboardInterrupt:
        print("\n🛑 Interrotto dall'utente")
    except Exception as e:
        print(f"❌ Errore: {e}")


if __name__ == "__main__":
    main()