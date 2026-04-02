"""
Modulis: alert_manager.py
Pārvalda drošības brīdinājumus: attēlošana, ignorēšana un eksportēšana.
"""

from database import nolasit_datus, saglaabt_datus, ALERTS_FILE
from ui import (display_section_header, display_error, display_success,
                        display_info, display_warning, gaaidit_enter,
                        DZELTENS, ATIESTATIT, BOLD, GAISSZILS, SARKANS,
                        ZALS, VIOLETS, ZILANS)

# Riska līmeņu krāsu karte
SEVERITY_KRASAS = {
    "high":   SARKANS,
    "medium": DZELTENS,
    "low":    ZALS,
}

# Riska līmeņu latviskie nosaukumi
SEVERITY_LV = {
    "high":   "AUGSTS",
    "medium": "VIDĒJS",
    "low":    "ZEMS",
}

# Brīdinājumu tipu latviskie nosaukumi
ALERT_TIPI_LV = {
    "brute_force":     "Brute Force uzbrukums",
    "port_scan":       "Port Scan",
    "anomaly":         "Laika anomālija",
    "suspicious_user": "Aizdomīgs lietotājvārds",
}


def apskatit_bridinajumus():
    """
    Funkcija apskatit_bridinajumus nepieņem vērtības un atgriež None tipa vērtību rezultaats.
    Attēlo visus aktīvos drošības brīdinājumus ar filtrēšanas iespēju pēc riska līmeņa.
    """
    display_section_header("DROŠĪBAS BRĪDINĀJUMI")

    bridinaajumi = nolasit_datus(ALERTS_FILE)

    if not bridinaajumi:
        display_error("Nav ģenerētu brīdinājumu. Vispirms veiciet analīzi (izvēle 4).")
        gaaidit_enter()
        return

    # Aktīvie (neignorētie) brīdinājumi
    aktiiviie = [b for b in bridinaajumi if not b.get("ignorets", False)]
    ignoretie = [b for b in bridinaajumi if b.get("ignorets", False)]

    display_info(f"Kopā brīdinājumi: {len(bridinaajumi)}  |  "
                 f"Aktīvie: {len(aktiiviie)}  |  Ignorētie: {len(ignoretie)}")

    # Filtrēšana pēc riska līmeņa
    print(f"\n  {GAISSZILS}Filtrēt pēc riska līmeņa:{ATIESTATIT}")
    print(f"  {DZELTENS}[1]{ATIESTATIT} Visi brīdinājumi")
    print(f"  {SARKANS}[2]{ATIESTATIT} Tikai augsta riska (HIGH)")
    print(f"  {DZELTENS}[3]{ATIESTATIT} Tikai vidēja riska (MEDIUM)")
    print(f"  {ZALS}[4]{ATIESTATIT} Tikai zema riska (LOW)")
    print(f"  {DZELTENS}[5]{ATIESTATIT} Ignorēt brīdinājumu")

    izvele = input(f"\n  {BOLD}Ievadiet izvēli: {ATIESTATIT}").strip()

    if izvele == "1":
        rādāmie = aktiiviie
    elif izvele == "2":
        rādāmie = [b for b in aktiiviie if b.get("severity") == "high"]
    elif izvele == "3":
        rādāmie = [b for b in aktiiviie if b.get("severity") == "medium"]
    elif izvele == "4":
        rādāmie = [b for b in aktiiviie if b.get("severity") == "low"]
    elif izvele == "5":
        ignoret_bridinajumu(bridinaajumi)
        gaaidit_enter()
        return
    else:
        display_error("Nepareiza izvēle!")
        gaaidit_enter()
        return

    print()
    drukaat_bridinaajumus(rādāmie)
    gaaidit_enter()


def drukaat_bridinaajumus(bridinaajumi):
    """
    Funkcija drukaat_bridinaajumus pieņem list tipa vērtību bridinaajumi un atgriež None tipa vērtību rezultaats.
    Attēlo brīdinājumu sarakstu formatētā veidā ar krāsu kodēšanu pēc riska līmeņa.
    """
    if not bridinaajumi:
        display_info("Nav brīdinājumu, kas atbilstu izvēlētajam filtram.")
        return

    print(f"{BOLD}{GAISSZILS}  BRĪDINĀJUMI ({len(bridinaajumi)} ieraksti){ATIESTATIT}")
    print(f"{ZILANS}  {'═' * 75}{ATIESTATIT}\n")

    for bridins in bridinaajumi:
        severity = bridins.get("severity", "low")
        krasa = SEVERITY_KRASAS.get(severity, ZALS)
        severity_lv = SEVERITY_LV.get(severity, severity.upper())
        tips_lv = ALERT_TIPI_LV.get(bridins.get("alert_type", ""), bridins.get("alert_type", "Nezināms"))

        print(f"  {krasa}{'▓' * 3} ID: {bridins.get('id', '?')} | "
              f"RISKS: {severity_lv:6} | "
              f"TIPS: {tips_lv}{ATIESTATIT}")
        print(f"  {GAISSZILS}  IP: {bridins.get('ip', 'N/A'):20}{ATIESTATIT}"
              f"Notikumi: {bridins.get('notikumu_skaits', '?')}")
        print(f"    📋 {bridins.get('apraksts', 'Nav apraksta')}")
        print(f"{ZILANS}  {'─' * 75}{ATIESTATIT}")


def ignoret_bridinajumu(bridinaajumi):
    """
    Funkcija ignoret_bridinajumu pieņem list tipa vērtību bridinaajumi un atgriež None tipa vērtību rezultaats.
    Atzīmē norādīto brīdinājumu kā ignorētu, lai to izslēgtu no aktīvā saraksta.
    """
    # Drukā aktīvos brīdinājumus, lai lietotājs var izvēlēties
    aktiiviie = [b for b in bridinaajumi if not b.get("ignorets", False)]
    if not aktiiviie:
        display_info("Nav aktīvu brīdinājumu, ko ignorēt.")
        return

    print(f"\n  {GAISSZILS}Aktīvie brīdinājumi:{ATIESTATIT}")
    for b in aktiiviie:
        print(f"  {DZELTENS}[{b.get('id')}]{ATIESTATIT} {b.get('apraksts', '')[:60]}")

    bridinajuma_id = input(f"\n  {BOLD}Ievadiet ignorējamā brīdinājuma ID: {ATIESTATIT}").strip()

    if not bridinajuma_id.isdigit():
        display_error("ID jābūt skaitlim!")
        return

    bridinajuma_id = int(bridinajuma_id)

    # Atrod un atzīmē brīdinājumu kā ignorētu
    atrasts = False
    for bridins in bridinaajumi:
        if bridins.get("id") == bridinajuma_id:
            bridins["ignorets"] = True
            atrasts = True
            break

    if atrasts:
        saglaabt_datus(ALERTS_FILE, bridinaajumi)
        display_success(f"Brīdinājums #{bridinajuma_id} tika atzīmēts kā ignorēts.")
    else:
        display_error(f"Brīdinājums ar ID {bridinajuma_id} netika atrasts.")
