"""
Modulis: database.py
Atbild par datubāzes inicializāciju un pamata darbībām ar JSON failiem.
Datubāze sastāv no 3 failiem: logs.json, alerts.json, incidents.json
"""

import json
import os

DB_DIR = "data"
LOGS_FILE = os.path.join(DB_DIR, "logs.json")
ALERTS_FILE = os.path.join(DB_DIR, "alerts.json")
INCIDENTS_FILE = os.path.join(DB_DIR, "incidents.json")


def initialize_database():
    """
    Funkcija initialize_database nepieņem vērtības un atgriež None tipa vērtību rezultaats.
    Izveido datu mapi un tukšus JSON failus, ja tie neeksistē.
    """
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)

    for fails in [LOGS_FILE, ALERTS_FILE, INCIDENTS_FILE]:
        if not os.path.exists(fails):
            saglaabt_datus(fails, [])


def nolasit_datus(fails_cels):
    """
    Funkcija nolasit_datus pieņem str tipa vērtību fails_cels un atgriež list tipa vērtību dati.
    Nolasa un atgriež datus no norādītā JSON faila.
    """
    try:
        with open(fails_cels, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def saglaabt_datus(fails_cels, dati):
    """
    Funkcija saglaabt_datus pieņem str tipa vērtību fails_cels un list tipa vērtību dati un atgriež bool tipa vērtību veiksme.
    Saglabā datus norādītajā JSON failā. Atgriež True, ja veiksmīgi.
    """
    try:
        with open(fails_cels, "w", encoding="utf-8") as f:
            json.dump(dati, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        return False


def nakamais_id(dati):
    """
    Funkcija nakamais_id pieņem list tipa vērtību dati un atgriež int tipa vērtību nakamais_id.
    Aprēķina nākamo pieejamo ID, pamatojoties uz esošajiem ierakstiem.
    """
    if not dati:
        return 1
    # Atrod maksimālo ID un palielina par 1
    return max(ieraksts.get("id", 0) for ieraksts in dati) + 1
