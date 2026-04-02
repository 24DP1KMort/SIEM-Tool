"""
Modulis: log_viewer.py
Nodrošina žurnālfailu ierakstu apskatīšanu strukturētā veidā terminālī.
"""

from database import nolasit_datus, LOGS_FILE
from ui import (display_section_header, display_error, display_info,
                        gaaidit_enter, DZELTENS, ATIESTATIT,
                        BOLD, ZILANS, SARKANS, ZALS, VIOLETS, GAISSZILS)


# Notikumu tipu krāsu karte vizualizācijai
EVENT_KRASAS = {
    "failed_login": SARKANS,
    "success_login": ZALS,
    "error": SARKANS,
    "access_denied": DZELTENS,
    "port_scan": VIOLETS,
    "brute_force": SARKANS,
    "anomaly": DZELTENS,
    "general": ATIESTATIT,
}

LAPPUSES_IZMERS = 20  # Ierakstu skaits uz vienu lapu


def apskatit_zurnaalfailus():
    """
    Funkcija apskatit_zurnaalfailus nepieņem vērtības un atgriež None tipa vērtību rezultaats.
    Attēlo visus ielādētos žurnāla ierakstus strukturētā tabulas veidā ar lapošanu.
    """
    display_section_header("ŽURNĀLFAILU SARAKSTS")

    logi = nolasit_datus(LOGS_FILE)

    if not logi:
        display_error("Nav ielādētu žurnāla ierakstu. Vispirms ielādējiet žurnālfailu (izvēle 1).")
        gaaidit_enter()
        return

    display_info(f"Kopā atrasti: {len(logi)} ieraksti")
    print()

    # Lapošanas loģika
    lappuse = 0
    kopskaits_lappuses = (len(logi) + LAPPUSES_IZMERS - 1) // LAPPUSES_IZMERS

    while True:
        sakums = lappuse * LAPPUSES_IZMERS
        beigas = min(sakums + LAPPUSES_IZMERS, len(logi))
        atteelojamiie = logi[sakums:beigas]

        # Tabulas galvene
        drukaat_log_tabulas_galveni()

        # Ierakstu attēlošana
        for ieraksts in atteelojamiie:
            drukaat_log_ierakstu(ieraksts)

        print(f"{ZILANS}  {'─' * 80}{ATIESTATIT}")
        print(f"  Lapa: {BOLD}{lappuse + 1}/{kopskaits_lappuses}{ATIESTATIT}  |  "
              f"Ieraksti: {sakums + 1}–{beigas} no {len(logi)}")
        print()

        # Navigācijas opcijas
        print(f"  {DZELTENS}[N]{ATIESTATIT} Nākamā lapa  "
              f"{DZELTENS}[P]{ATIESTATIT} Iepriekšējā lapa  "
              f"{DZELTENS}[Q]{ATIESTATIT} Atgriezties")

        izvele = input(f"  {BOLD}Ievadiet izvēli: {ATIESTATIT}").strip().upper()

        if izvele == "N" and lappuse < kopskaits_lappuses - 1:
            lappuse += 1
        elif izvele == "P" and lappuse > 0:
            lappuse -= 1
        elif izvele == "Q":
            break
        # Citu taustiņu gadījumā paliek pašreizējā lapā


def drukaat_log_tabulas_galveni():
    """
    Funkcija drukaat_log_tabulas_galveni nepieņem vērtības un atgriež None tipa vērtību rezultaats.
    Izdrukā tabulas galvenes rindu ar kolonnu nosaukumiem.
    """
    print(f"{BOLD}{GAISSZILS}", end="")
    print(f"  {'ID':<5} {'LAIKS':<22} {'IP ADRESE':<16} {'LIETOTĀJS':<15} {'NOTIKUMA TIPS':<18}")
    print(f"  {'─'*5} {'─'*22} {'─'*16} {'─'*15} {'─'*18}")
    print(f"{ATIESTATIT}", end="")


def drukaat_log_ierakstu(ieraksts):
    """
    Funkcija drukaat_log_ierakstu pieņem dict tipa vērtību ieraksts un atgriež None tipa vērtību rezultaats.
    Izdrukā vienu žurnāla ierakstu formatētā veidā ar krāsu kodēšanu pēc notikuma tipa.
    """
    notikuma_tips = ieraksts.get("event_type", "general")
    krasa = EVENT_KRASAS.get(notikuma_tips, ATIESTATIT)

    log_id = str(ieraksts.get("id", "?"))[:5]
    laiks = str(ieraksts.get("timestamp", "N/A"))[:22]
    ip = str(ieraksts.get("ip", "N/A"))[:16]
    lietotajs = str(ieraksts.get("user", "N/A"))[:15]
    tips = str(notikuma_tips)[:18]

    print(f"  {DZELTENS}{log_id:<5}{ATIESTATIT} "
          f"{laiks:<22} "
          f"{GAISSZILS}{ip:<16}{ATIESTATIT} "
          f"{lietotajs:<15} "
          f"{krasa}{tips:<18}{ATIESTATIT}")
