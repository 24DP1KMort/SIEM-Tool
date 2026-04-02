"""
Modulis: log_analyzer.py
Galvenais analīzes modulis — draudu noteikšana un korelācija.
Izmanto definētus drošības noteikumus aizdomīgu darbību identificēšanai.
"""

from collections import defaultdict
from database import (nolasit_datus, saglaabt_datus,
                               nakamais_id, LOGS_FILE, ALERTS_FILE)
from ui import (display_section_header, display_error, display_success,
                        display_info, display_warning, gaaidit_enter,
                        DZELTENS, ATIESTATIT, BOLD, GAISSZILS, SARKANS,
                        ZALS, VIOLETS, ZILANS)

# Drošības noteikumu sliekšņvērtības
BRUTEFORCE_SLIEKSNIS = 5      # Neveiksmīgi mēģinājumi vienā IP
PORTSCANAS_SLIEKSNIS = 10     # Dažādi notikumi vienā IP īsā laikā
NEPARASTA_STUNDA_NO = 22      # Neparasta darbība pēc 22:00
NEPARASTA_STUNDA_LIDZ = 6     # Neparasta darbība pirms 06:00


def analizet_zurnaalfailus():
    """
    Funkcija analizet_zurnaalfailus nepieņem vērtības un atgriež None tipa vērtību rezultaats.
    Veic visaptverošu žurnāla ierakstu analīzi, izmantojot drošības noteikumus,
    un saglabā ģenerētos brīdinājumus datubāzē.
    """
    display_section_header("ŽURNĀLFAILU ANALĪZE")

    logi = nolasit_datus(LOGS_FILE)
    if not logi:
        display_error("Nav ielādētu žurnāla ierakstu analīzei.")
        gaaidit_enter()
        return

    display_info(f"Analizē {len(logi)} ierakstus...")
    print()

    jaunie_bridinaajumi = []

    # === NOTEIKUMS 1: Brute Force noteikšana ===
    display_info("Pārbauda brute force uzbrukumus...")
    bf_bridinaajumi = noteikt_bruteforce(logi)
    jaunie_bridinaajumi.extend(bf_bridinaajumi)
    print(f"  {ZALS}✓{ATIESTATIT} Brute force analīze pabeigta — atrasti {len(bf_bridinaajumi)} draudi")

    # === NOTEIKUMS 2: Port scan noteikšana ===
    display_info("Pārbauda port scanning aktivitāti...")
    ps_bridinaajumi = noteikt_portskanu(logi)
    jaunie_bridinaajumi.extend(ps_bridinaajumi)
    print(f"  {ZALS}✓{ATIESTATIT} Port scan analīze pabeigta — atrasti {len(ps_bridinaajumi)} draudi")

    # === NOTEIKUMS 3: Neparasta laika aktivitāte ===
    display_info("Pārbauda neparastu laika aktivitāti...")
    laika_bridinaajumi = noteikt_neparastu_laiku(logi)
    jaunie_bridinaajumi.extend(laika_bridinaajumi)
    print(f"  {ZALS}✓{ATIESTATIT} Laika analīze pabeigta — atrasti {len(laika_bridinaajumi)} draudi")

    # === NOTEIKUMS 4: Aizdomīgi lietotājvārdi ===
    display_info("Pārbauda aizdomīgus lietotājvārdus...")
    user_bridinaajumi = noteikt_aizdomiigus_lietotaajus(logi)
    jaunie_bridinaajumi.extend(user_bridinaajumi)
    print(f"  {ZALS}✓{ATIESTATIT} Lietotāju analīze pabeigta — atrasti {len(user_bridinaajumi)} draudi")

    # Saglabā brīdinājumus datubāzē
    if jaunie_bridinaajumi:
        esosie_bridinaajumi = nolasit_datus(ALERTS_FILE)
        sakumais_id = nakamais_id(esosie_bridinaajumi)

        for i, bridins in enumerate(jaunie_bridinaajumi):
            bridins["id"] = sakumais_id + i

        esosie_bridinaajumi.extend(jaunie_bridinaajumi)
        saglaabt_datus(ALERTS_FILE, esosie_bridinaajumi)

        print()
        display_success(f"Analīze pabeigta! Ģenerēti {len(jaunie_bridinaajumi)} jauni brīdinājumi.")
        print(f"  ℹ️  Skatiet brīdinājumus, izvēloties opciju 5 galvenajā izvēlnē.")
    else:
        print()
        display_success("Analīze pabeigta! Aizdomīgas darbības netika atklātas.")

    gaaidit_enter()


def noteikt_bruteforce(logi):
    """
    Funkcija noteikt_bruteforce pieņem list tipa vērtību logi un atgriež list tipa vērtību bridinaajumi.
    Atklāj brute force uzbrukumus — atkārtotus neveiksmīgus pieslēgšanās mēģinājumus
    no vienas IP adreses (slieksnis: 5+ mēģinājumi).
    """
    bridinaajumi = []
    # Skaita neveiksmīgos mēģinājumus katrai IP adresei
    ip_kludas = defaultdict(list)

    for log in logi:
        if log.get("event_type") == "failed_login":
            ip = log.get("ip", "0.0.0.0")
            ip_kludas[ip].append(log)

    # Ģenerē brīdinājumu, ja pārsniegts slieksnis
    for ip, neveiksmigi in ip_kludas.items():
        if len(neveiksmigi) >= BRUTEFORCE_SLIEKSNIS:
            # Nosaka riska līmeni pēc mēģinājumu skaita
            if len(neveiksmigi) >= 20:
                severity = "high"
            elif len(neveiksmigi) >= 10:
                severity = "medium"
            else:
                severity = "low"

            bridins = {
                "log_id": neveiksmigi[0].get("id"),
                "alert_type": "brute_force",
                "ip": ip,
                "notikumu_skaits": len(neveiksmigi),
                "severity": severity,
                "apraksts": f"Brute force uzbrukums no {ip}: {len(neveiksmigi)} neveiksmīgi mēģinājumi"
            }
            bridinaajumi.append(bridins)

    return bridinaajumi


def noteikt_portskanu(logi):
    """
    Funkcija noteikt_portskanu pieņem list tipa vērtību logi un atgriež list tipa vērtību bridinaajumi.
    Atklāj iespējamus port scanning mēģinājumus — lielu dažādu notikumu skaitu
    no vienas IP adreses (slieksnis: 10+ unikāli notikumi).
    """
    bridinaajumi = []
    # Skaita unikālos notikumus katrai IP
    ip_notikumi = defaultdict(set)

    for log in logi:
        ip = log.get("ip", "0.0.0.0")
        tips = log.get("event_type", "general")
        ip_notikumi[ip].add(tips)

    for ip, notikumu_tipi in ip_notikumi.items():
        if len(notikumu_tipi) >= PORTSCANAS_SLIEKSNIS:
            bridins = {
                "log_id": None,
                "alert_type": "port_scan",
                "ip": ip,
                "notikumu_skaits": len(notikumu_tipi),
                "severity": "medium",
                "apraksts": f"Iespējams port scan no {ip}: {len(notikumu_tipi)} dažādi notikumu tipi"
            }
            bridinaajumi.append(bridins)

    return bridinaajumi


def noteikt_neparastu_laiku(logi):
    """
    Funkcija noteikt_neparastu_laiku pieņem list tipa vērtību logi un atgriež list tipa vērtību bridinaajumi.
    Identificē pieslēgšanās mēģinājumus naktī (22:00–06:00), kas var liecināt
    par nesankcionētu piekļuvi.
    """
    bridinaajumi = []

    for log in logi:
        laiks_str = str(log.get("timestamp", ""))
        # Izvelk stundu no laika zīmoga
        try:
            # Atbalsta formātus: "2026-03-30 23:15:00" vai "Mar 30 23:15:00"
            if " " in laiks_str:
                laika_dala = laiks_str.split(" ")[-1]
                stunda = int(laika_dala.split(":")[0])
            else:
                continue

            # Pārbauda vai stunda ir neparastajā diapazonā
            ir_neparasta = (stunda >= NEPARASTA_STUNDA_NO or stunda < NEPARASTA_STUNDA_LIDZ)
            notikums_ir_pieklusana = log.get("event_type") in ("failed_login", "success_login")

            if ir_neparasta and notikums_ir_pieklusana:
                bridins = {
                    "log_id": log.get("id"),
                    "alert_type": "anomaly",
                    "ip": log.get("ip", "N/A"),
                    "notikumu_skaits": 1,
                    "severity": "low",
                    "apraksts": (f"Neparasta laika aktivitāte: pieslēgšanās plkst. {stunda:02d}:xx "
                                 f"no {log.get('ip')} (lietotājs: {log.get('user')})")
                }
                bridinaajumi.append(bridins)

        except (ValueError, IndexError):
            # Ignorē ierakstus ar neparsējamu laiku
            continue

    return bridinaajumi


def noteikt_aizdomiigus_lietotaajus(logi):
    """
    Funkcija noteikt_aizdomiigus_lietotaajus pieņem list tipa vērtību logi un atgriež list tipa vērtību bridinaajumi.
    Identificē mēģinājumus pieslēgties ar sistēmas lietotājvārdiem
    (root, admin, administrator), kas ir augsta riska mērķi.
    """
    bridinaajumi = []
    AIZDOMIIGI_LIETOTAAJI = {"root", "admin", "administrator", "guest", "test", "user", "oracle", "postgres"}

    for log in logi:
        lietotajs = str(log.get("user", "")).lower()
        if (lietotajs in AIZDOMIIGI_LIETOTAAJI and
                log.get("event_type") == "failed_login"):
            bridins = {
                "log_id": log.get("id"),
                "alert_type": "suspicious_user",
                "ip": log.get("ip", "N/A"),
                "notikumu_skaits": 1,
                "severity": "medium",
                "apraksts": (f"Mēģinājums pieslēgties ar sistēmas kontu '{log.get('user')}' "
                             f"no {log.get('ip')}")
            }
            bridinaajumi.append(bridins)

    return bridinaajumi
