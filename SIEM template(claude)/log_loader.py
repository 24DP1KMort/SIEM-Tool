"""
Modulis: log_loader.py
Atbild par žurnālfailu ielādi un parsēšanu.
Atbalsta LOG, TXT un JSON failu formātus.
"""

import os
import re
import json
from datetime import datetime
from database import nolasit_datus, saglaabt_datus, nakamais_id, LOGS_FILE
from ui import (display_section_header, display_error, display_success,
                        display_info, gaaidit_enter, DZELTENS, ATIESTATIT,
                        GAISSZILS, BOLD, ZILANS)
from validator import validet_ip, validet_timestamp, validet_nav_tukss


def ielaadet_zurnaalfailu():
    """
    Funkcija ielaadet_zurnaalfailu nepieņem vērtības un atgriež None tipa vērtību rezultaats.
    Ielādē žurnālfailu no norādītā ceļa, parsē ierakstus un saglabā datubāzē.
    """
    display_section_header("ŽURNĀLFAILA IELĀDE")

    # Faila ceļa ievade un validācija
    fails_cels = input(f"  {DZELTENS}Ievadiet faila ceļu (piem. /var/log/auth.log): {ATIESTATIT}").strip()
    if not validet_nav_tukss(fails_cels):
        display_error("Faila ceļš nedrīkst būt tukšs!")
        gaaidit_enter()
        return

    # Pārbauda vai fails eksistē
    if not os.path.exists(fails_cels):
        display_error(f"Fails '{fails_cels}' netika atrasts! Pārbaudiet ceļu.")
        gaaidit_enter()
        return

    # Faila tipa izvēle
    print(f"\n  {GAISSZILS}Pieejamie failu tipi:{ATIESTATIT}")
    print(f"  {DZELTENS}[1]{ATIESTATIT} LOG  - Standarta žurnālfails")
    print(f"  {DZELTENS}[2]{ATIESTATIT} TXT  - Teksta fails")
    print(f"  {DZELTENS}[3]{ATIESTATIT} JSON - JSON formāta fails")

    tips_izvele = input(f"\n  {DZELTENS}Izvēlieties faila tipu [1-3]: {ATIESTATIT}").strip()

    tips_karte = {"1": "log", "2": "txt", "3": "json"}
    if tips_izvele not in tips_karte:
        display_error("Nepareiza faila tipa izvēle!")
        gaaidit_enter()
        return

    faila_tips = tips_karte[tips_izvele]
    display_info(f"Ielādē failu: {fails_cels} (tips: {faila_tips.upper()})")

    # Parsē failu atbilstoši tipa
    if faila_tips == "json":
        ieraksti = parseet_json_failu(fails_cels)
    else:
        ieraksti = parseet_log_failu(fails_cels)

    if not ieraksti:
        display_error("Failā netika atrasti derīgi ieraksti vai fails ir tukšs.")
        gaaidit_enter()
        return

    # Saglabā ierakstus datubāzē
    esosie_logi = nolasit_datus(LOGS_FILE)
    sakumais_id = nakamais_id(esosie_logi)

    # Piešķir ID katram jaunam ierakstam
    for i, ieraksts in enumerate(ieraksti):
        ieraksts["id"] = sakumais_id + i
        ieraksts["avota_fails"] = fails_cels

    esosie_logi.extend(ieraksti)
    if saglaabt_datus(LOGS_FILE, esosie_logi):
        display_success(f"Veiksmīgi ielādēti {len(ieraksti)} ieraksti no faila!")
    else:
        display_error("Kļūda saglabājot datus!")

    gaaidit_enter()


def parseet_log_failu(fails_cels):
    """
    Funkcija parseet_log_failu pieņem str tipa vērtību fails_cels un atgriež list tipa vērtību ieraksti.
    Parsē standarta LOG/TXT failu un izvelk strukturētus ierakstus.
    Atbalsta SSH auth.log un vispārīgus syslog formātus.
    """
    ieraksti = []

    # Regulārā izteiksme SSH pieteikšanās kļūmēm (piemēram, auth.log)
    ssh_kludas_reg = re.compile(
        r"(\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+\S+\s+sshd.*?Failed password for (\S+) from ([\d.]+)"
    )
    # Regulārā izteiksme veiksmīgai pieteikšanās
    ssh_veiksme_reg = re.compile(
        r"(\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+\S+\s+sshd.*?Accepted password for (\S+) from ([\d.]+)"
    )
    # Vispārīgs formāts: timestamp ip user event
    visp_reg = re.compile(
        r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+([\d.]+)\s+(\S+)\s+(.*)"
    )

    try:
        with open(fails_cels, "r", encoding="utf-8", errors="ignore") as f:
            for rinда in f:
                rinda = rinда.strip()
                if not rinda:
                    continue

                ieraksts = None

                # Mēģina SSH kļūdu formātu
                atbilsme = ssh_kludas_reg.search(rinda)
                if atbilsme:
                    ieraksts = {
                        "timestamp": atbilsme.group(1),
                        "ip": atbilsme.group(3),
                        "user": atbilsme.group(2),
                        "event_type": "failed_login",
                        "raw": rinda
                    }

                # Mēģina SSH veiksmīgas pieteikšanās formātu
                if not ieraksts:
                    atbilsme = ssh_veiksme_reg.search(rinda)
                    if atbilsme:
                        ieraksts = {
                            "timestamp": atbilsme.group(1),
                            "ip": atbilsme.group(3),
                            "user": atbilsme.group(2),
                            "event_type": "success_login",
                            "raw": rinda
                        }

                # Mēģina vispārīgo formātu
                if not ieraksts:
                    atbilsme = visp_reg.search(rinda)
                    if atbilsme:
                        ieraksts = {
                            "timestamp": atbilsme.group(1),
                            "ip": atbilsme.group(2),
                            "user": atbilsme.group(3),
                            "event_type": atbilsme.group(4)[:30],
                            "raw": rinda
                        }

                # Ja neviens formāts neatbilst, glabā kā vispārīgu notikumu
                if not ieraksts:
                    ieraksts = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "ip": "0.0.0.0",
                        "user": "nezināms",
                        "event_type": "general",
                        "raw": rinda[:200]
                    }

                ieraksti.append(ieraksts)

    except PermissionError:
        display_error("Nav atļaujas lasīt šo failu!")
        return []
    except Exception as e:
        display_error(f"Kļūda lasot failu: {e}")
        return []

    return ieraksti


def parseet_json_failu(fails_cels):
    """
    Funkcija parseet_json_failu pieņem str tipa vērtību fails_cels un atgriež list tipa vērtību ieraksti.
    Parsē JSON formāta žurnālfailu un validē katru ierakstu.
    """
    try:
        with open(fails_cels, "r", encoding="utf-8") as f:
            dati = json.load(f)

        if not isinstance(dati, list):
            display_error("JSON failam jābūt ierakstu masīvam (sarakstam)!")
            return []

        apstraadati = []
        for ieraksts in dati:
            # Pārbauda obligātos laukus
            apstraadats = {
                "timestamp": str(ieraksts.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))[:20],
                "ip": str(ieraksts.get("ip", "0.0.0.0"))[:15],
                "user": str(ieraksts.get("user", "nezināms"))[:50],
                "event_type": str(ieraksts.get("event_type", "general"))[:30],
                "raw": str(ieraksts.get("raw", json.dumps(ieraksts)))[:500]
            }
            apstraadati.append(apstraadats)

        return apstraadati

    except json.JSONDecodeError:
        display_error("Nepareizs JSON faila formāts!")
        return []
    except Exception as e:
        display_error(f"Kļūda apstrādājot JSON failu: {e}")
        return []
