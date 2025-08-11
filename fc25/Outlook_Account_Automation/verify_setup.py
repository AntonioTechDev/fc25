#!/usr/bin/env python3
"""
Multi Outlook Account Creator - Setup Verification
================================================

Script di verifica per controllare che tutto il setup sia corretto.
Esegue controlli su dipendenze, file, configurazione e funzionalità base.
"""

import importlib
import os
import sys
from pathlib import Path


def check_python_version():
    """Verifica versione Python."""
    print("🐍 Verifica versione Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Richiesto 3.8+")
        return False


def check_dependencies():
    """Verifica dipendenze Python."""
    print("\n📦 Verifica dipendenze Python...")
    dependencies = [
        ('cv2', 'opencv-python'),
        ('pyautogui', 'pyautogui'),
        ('numpy', 'numpy'),
        ('pynput', 'pynput'),
        ('tkinter', 'tkinter (built-in)')
    ]
    
    all_ok = True
    for module, package in dependencies:
        try:
            importlib.import_module(module)
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - MANCANTE")
            all_ok = False
    
    return all_ok


def check_system_dependencies():
    """Verifica dipendenze di sistema."""
    print("\n🖥️ Verifica dipendenze di sistema...")
    
    # Verifica spoof-mac
    spoof_mac_ok = False
    try:
        import subprocess
        result = subprocess.run(['which', 'spoof-mac'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ spoof-mac - Installato")
            spoof_mac_ok = True
        else:
            print("❌ spoof-mac - Non installato (brew install spoof-mac)")
    except Exception:
        print("❌ spoof-mac - Errore verifica")
    
    # Verifica sudo
    sudo_ok = False
    try:
        result = subprocess.run(['sudo', '-n', 'echo', 'test'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ sudo - Accesso disponibile")
            sudo_ok = True
        else:
            print("⚠️ sudo - Richiede autenticazione (sudo -v)")
    except Exception:
        print("❌ sudo - Errore verifica")
    
    return spoof_mac_ok and sudo_ok


def check_files():
    """Verifica presenza file necessari."""
    print("\n📁 Verifica file necessari...")
    
    base_dir = Path(__file__).parent.parent
    required_files = [
        'accounts.csv',
        'templates/'
    ]
    
    all_ok = True
    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path} - Presente")
        else:
            print(f"❌ {file_path} - MANCANTE")
            all_ok = False
    
    return all_ok


def check_templates():
    """Verifica template necessari."""
    print("\n🖼️ Verifica template immagini...")
    
    base_dir = Path(__file__).parent.parent
    templates_dir = base_dir / 'templates'
    
    if not templates_dir.exists():
        print("❌ Cartella templates/ non trovata")
        return False
    
    required_templates = [
        'email_input.png',
        'next_button.png',
        'password_input.png',
        'birth_day_dropdown.png',
        'birth_month_dropdown.png',
        'birth_year_input.png',
        'first_name_input.png',
        'last_name_input.png',
        'captcha_button.png'
    ]
    
    all_ok = True
    for template in required_templates:
        template_path = templates_dir / template
        if template_path.exists():
            print(f"✅ {template} - Presente")
        else:
            print(f"❌ {template} - MANCANTE")
            all_ok = False
    
    return all_ok


def check_csv_format():
    """Verifica formato CSV."""
    print("\n📊 Verifica formato CSV...")
    
    base_dir = Path(__file__).parent.parent
    csv_path = base_dir / 'accounts.csv'
    
    if not csv_path.exists():
        print("❌ accounts.csv non trovato")
        return False
    
    try:
        import csv
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames
            
            required_headers = ['email', 'password', 'first_name', 'last_name', 'birth_year']
            missing_headers = [h for h in required_headers if h not in headers]
            
            if missing_headers:
                print(f"❌ Headers mancanti: {missing_headers}")
                return False
            else:
                print("✅ Formato CSV - Corretto")
                return True
    except Exception as e:
        print(f"❌ Errore lettura CSV: {e}")
        return False


def test_imports():
    """Testa import dei moduli del progetto."""
    print("\n🔧 Test import moduli...")
    
    modules = [
<<<<<<<< HEAD:fc25/Outlook_Account_Automation/tests/verify_setup.py
        'Outlook_Account_Automation.backend.automation',
        'Outlook_Account_Automation.frontend.gui_logger',
        'Outlook_Account_Automation.backend.browser_utils',
        'Outlook_Account_Automation.backend.csv_utils',
        'Outlook_Account_Automation.backend.mac_utils'
========
        'multi_outlook_creator.automation',
        'multi_outlook_creator.gui_logger',
        'multi_outlook_creator.browser_utils',
        'multi_outlook_creator.csv_utils',
        'multi_outlook_creator.mac_utils'
>>>>>>>> parent of d1ee7da (Riorganizzazione codice, creazione cartella, documentazione etc):fc25/Outlook_Account_Automation/verify_setup.py
    ]
    
    all_ok = True
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module} - OK")
        except ImportError as e:
            print(f"❌ {module} - ERRORE: {e}")
            all_ok = False
    
    return all_ok


def main():
    """Funzione principale di verifica."""
    print("🔍 Outlook Account Automation - Setup Verification")
    print("=" * 60)
    
    checks = [
        ("Versione Python", check_python_version),
        ("Dipendenze Python", check_dependencies),
        ("Dipendenze Sistema", check_system_dependencies),
        ("File Necessari", check_files),
        ("Template Immagini", check_templates),
        ("Formato CSV", check_csv_format),
        ("Import Moduli", test_imports)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Errore durante {name}: {e}")
            results.append((name, False))
    
    # Riepilogo
    print("\n" + "=" * 60)
    print("📋 RIEPILOGO VERIFICA")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n🎯 Risultato: {passed}/{total} verifiche superate")
    
    if passed == total:
        print("🎉 Setup completato con successo! Puoi avviare l'automazione.")
        print("💡 Comando: python -m multi_outlook_creator.main")
        return True
    else:
        print("⚠️ Alcuni controlli sono falliti. Risolvi i problemi prima di procedere.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 