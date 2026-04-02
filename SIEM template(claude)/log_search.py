"""
Modulis: log_search.py
Nodrošina meklēšanu žurnāla ierakstos pēc dažādiem parametriem:
IP adreses, lietotājvārda, notikuma tipa un laika perioda.
"""

from database import nolasit_datus, LOGS_FILE
from ui import (display_section_header, display_error, display_info,
                        display_warning, gaaidit_enter, DZELTENS, ATIESTATIT,
                        BOLD, ZILANS, GAISSZILS, SARKANS, ZALS)
from log_viewer import drukaat_log_tabulas_galveni, drukaat_log_ierakstu
from validator import validet_ip, validet_nav_tukss


def meklet_zurnaalfailos():
    """
    Funkcija meklet_zurnaalfailos nepieņem vērtības un atgriež None tipa vērtību rezultaats.
    Ļauj lietotājam meklēt žurnāla ierakstos pēc dažādiem parametriem.
    """
    display_section_header("MEKLĒŠANA ŽURNĀLFAILOS")

    logi = nolasit_datus(LOGS_FILE)
    if not logi:
        display_error("Nav ielādētu žurnāla ierakstu.")
        gaaidit_enter()
        return

    # Meklēšanas parametru izvēle
    print(f"  {GAISSZILS}Meklēšanas veidi:{ATIESTATIT}")
    print(f"  {DZELTENS}[1]{ATIESTATIT} Meklēt pēc IP adreses")
    print(f"  {DZELTENS}[2]{ATIESTATIT} Meklēt pēc lietotājvārda")
    print(f"  {DZELTENS}[3]{ATIESTATIT} Meklēt pēc notikuma tipa")
    print(f"  {DZELTENS}[4]{ATIESTATIT} Filtrēt pēc laika perioda")
    print(f"  {DZELTENS}[5]{ATIESTATIT} Kombinētā meklēšana")

    izvele = input(f"\n  {BOLD}Izvēlieties meklēšanas veidu [1-5]: {ATIESTATIT}").strip()

    if izvele == "1":
        rezultaati = meklet_pec_ip(logi)
    elif izvele == "2":
        rezultaati = meklet_pec_lietotaajvarda(logi)
    elif izvele == "3":
        rezultaati = meklet_pec_notikuma_tipa(logi)
    elif izvele == "4":
        rezultaati = filtret_pec_laika(logi)
    elif izvele == "5":
        rezultaati = kombineta_mekleesana(logi)
    else:
        display_error("Nepareiza izvēle!")
        gaaidit_enter()
        return

    # Meklēšanas rezultātu attēlošana
    atteelojamiie = atteelot_meklesanas_rezultaatus(rezultaati)
    gaaidit_enter()


def meklet_pec_ip(logi):
    """
    Funkcija meklet_pec_ip pieņem list tipa vērtību logi un atgriež list tipa vērtību rezultaati.
    Filtrē žurnāla ierakstus pēc norādītās IP adreses (pilna vai daļēja atbilstība).
    """
    ip_meklesana = input(f"  {DZELTENS}Ievadiet IP adresi (vai daļu, piem. 192.168): {ATIESTATIT}").strip()

    if not validet_nav_tukss(ip_meklesana):
        display_error("IP adrese nedrīkst būt tukša!")
        return []

    # Filtrē pēc daļējas atbilstības
    rezultaati = [
        log for log in logi
        if ip_meklesana.lower() in str(log.get("ip", "")).lower()
    ]
    return rezultaati


def meklet_pec_lietotaajvarda(logi):
    """
    Funkcija meklet_pec_lietotaajvarda pieņem list tipa vērtību logi un atgriež list tipa vērtību rezultaati.
    Filtrē žurnāla ierakstus pēc norādītā lietotājvārda (reģistrjutīga meklēšana).
    """
    lietotaajvards = input(f"  {DZELTENS}Ievadiet lietotājvārdu: {ATIESTATIT}").strip()

    if not validet_nav_tukss(lietotaajvards):
        display_error("Lietotājvārds nedrīkst būt tukšs!")
        return []

    rezultaati = [
        log for log in logi
        if lietotaajvards.lower() in str(log.get("user", "")).lower()
    ]
    return rezultaati


def meklet_pec_notikuma_tipa(logi):
    """
    Funkcija meklet_pec_notikuma_tipa pieņem list tipa vērtību logi un atgriež list tipa vērtību rezultaati.
    Filtrē žurnāla ierakstus pēc izvēlētā notikuma tipa.
    """
    print(f"\n  {GAISSZILS}Pieejamie notikumu tipi:{ATIESTATIT}")
    notikumu_tipi = ["failed_login", "success_login", "error",
                     "access_denied", "port_scan", "brute_force", "anomaly", "general"]

    for i, tips in enumerate(notikumu_tipi, 1):
        print(f"  {DZELTENS}[{i}]{ATIESTATIT} {tips}")

    izvele = input(f"\n  {BOLD}Izvēlieties tipu [1-{len(notikumu_tipi)}] vai ievadiet pats: {ATIESTATIT}").strip()

    # Atļauj ievadīt gan numuru, gan tekstu
    if izvele.isdigit() and 1 <= int(izvele) <= len(notikumu_tipi):
        meklejamais_tips = notikumu_tipi[int(izvele) - 1]
    else:
        meklejamais_tips = izvele

    rezultaati = [
        log for log in logi
        if meklejamais_tips.lower() in str(log.get("event_type", "")).lower()
    ]
    return rezultaati


def filtret_pec_laika(logi):
    """
    Funkcija filtret_pec_laika pieņem list tipa vērtību logi un atgriež list tipa vērtību rezultaati.
    Filtrē žurnāla ierakstus pēc norādītā laika perioda (datuma prefikss).
    """
    print(f"\n  {GAISSZILS}Laika filtra formāts:{ATIESTATIT}")
    print(f"  Piemēri: '2026-03' (marts), '2026-03-30' (konkrēta diena), '2026' (gads)")
    laika_filtrs = input(f"  {DZELTENS}Ievadiet laika periodu: {ATIESTATIT}").strip()

    if not validet_nav_tukss(laika_filtrs):
        display_error("Laika filtrs nedrīkst būt tukšs!")
        return []

    rezultaati = [
        log for log in logi
        if str(log.get("timestamp", "")).startswith(laika_filtrs)
    ]
    return rezultaati


def kombineta_mekleesana(logi):
    """
    Funkcija kombineta_mekleesana pieņem list tipa vērtību logi un atgriež list tipa vērtību rezultaati.
    Ļauj meklēt pēc vairākiem parametriem vienlaicīgi (AND loģika).
    Tukši lauki tiek ignorēti.
    """
    print(f"\n  {GAISSZILS}Kombinētā meklēšana (tukšus laukus atstājiet tukšus):{ATIESTATIT}")

    ip_filtrs = input(f"  {DZELTENS}IP adrese: {ATIESTATIT}").strip()
    lietotajs_filtrs = input(f"  {DZELTENS}Lietotājvārds: {ATIESTATIT}").strip()
    tips_filtrs = input(f"  {DZELTENS}Notikuma tips: {ATIESTATIT}").strip()

    rezultaati = logi

    # Pakāpeniski piemēro filtrus (AND loģika)
    if validet_nav_tukss(ip_filtrs):
        rezultaati = [l for l in rezultaati if ip_filtrs.lower() in str(l.get("ip", "")).lower()]

    if validet_nav_tukss(lietotajs_filtrs):
        rezultaati = [l for l in rezultaati if lietotajs_filtrs.lower() in str(l.get("user", "")).lower()]

    if validet_nav_tukss(tips_filtrs):
        rezultaati = [l for l in rezultaati if tips_filtrs.lower() in str(l.get("event_type", "")).lower()]

    return rezultaati


def atteelot_meklesanas_rezultaatus(rezultaati):
    """
    Funkcija atteelot_meklesanas_rezultaatus pieņem list tipa vērtību rezultaati un atgriež int tipa vērtību atrasto_skaits.
    Attēlo meklēšanas rezultātus strukturētā tabulas veidā.
    """
    print()
    if not rezultaati:
        display_error("Netika atrasts neviens ieraksts, kas atbilstu meklēšanas kritērijiem.")
        return 0

    display_info(f"Atrasti {len(rezultaati)} ieraksti:")
    print()

    drukaat_log_tabulas_galveni()
    for ieraksts in rezultaati[:50]:  # Rāda maksimāli 50 rezultātus
        drukaat_log_ierakstu(ieraksts)

    if len(rezultaati) > 50:
        display_info(f"Rādīti 50 no {len(rezultaati)} rezultātiem. Izmantojiet precīzākus filtrus.")

    return len(rezultaati)
