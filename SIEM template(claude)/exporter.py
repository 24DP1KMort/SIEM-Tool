"""
Modulis: exporter.py
Nodrošina analīzes rezultātu eksportēšanu TXT un JSON formātos.
"""

import json
import os
from datetime import datetime
from database import nolasit_datus, LOGS_FILE, ALERTS_FILE, INCIDENTS_FILE
from ui import (display_section_header, display_error, display_success,
                        display_info, gaaidit_enter, DZELTENS, ATIESTATIT,
                        BOLD, GAISSZILS, ZILANS)
from validator import validet_nav_tukss


def eksportet_analiezi():
    """
    Funkcija eksportet_analiezi nepieņem vērtības un atgriež None tipa vērtību rezultaats.
    Eksportē analīzes rezultātus (logus, brīdinājumus, incidentus) izvēlētajā formātā.
    """
    display_section_header("ANALĪZES EKSPORTS")

    logi = nolasit_datus(LOGS_FILE)
    bridinaajumi = nolasit_datus(ALERTS_FILE)
    incidenti = nolasit_datus(INCIDENTS_FILE)

    if not logi and not bridinaajumi:
        display_error("Nav datu eksportēšanai. Vispirms ielādējiet un analizējiet žurnālfailus.")
        gaaidit_enter()
        return

    # Eksporta formāta izvēle
    print(f"  {GAISSZILS}Eksporta formāti:{ATIESTATIT}")
    print(f"  {DZELTENS}[1]{ATIESTATIT} TXT  — Lasāms teksta fails")
    print(f"  {DZELTENS}[2]{ATIESTATIT} JSON — Strukturēts JSON fails")

    formata_izvele = input(f"\n  {BOLD}Izvēlieties formātu [1/2]: {ATIESTATIT}").strip()

    if formata_izvele not in ("1", "2"):
        display_error("Nepareiza izvēle!")
        gaaidit_enter()
        return

    # Izvades faila ceļa ievade
    noklusejuma_nosaukums = f"siem_eksports_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    faila_nosaukums = input(
        f"  {DZELTENS}Faila nosaukums (Enter priekš '{noklusejuma_nosaukums}'): {ATIESTATIT}"
    ).strip()

    if not validet_nav_tukss(faila_nosaukums):
        faila_nosaukums = noklusejuma_nosaukums

    # Pievieno paplašinājumu
    if formata_izvele == "1":
        if not faila_nosaukums.endswith(".txt"):
            faila_nosaukums += ".txt"
        veiksme = eksportet_txt(faila_nosaukums, logi, bridinaajumi, incidenti)
    else:
        if not faila_nosaukums.endswith(".json"):
            faila_nosaukums += ".json"
        veiksme = eksportet_json(faila_nosaukums, logi, bridinaajumi, incidenti)

    if veiksme:
        faila_izmers = os.path.getsize(faila_nosaukums)
        display_success(f"Fails saglabāts: {faila_nosaukums} ({faila_izmers} baiti)")
    else:
        display_error("Kļūda eksportējot datus!")

    gaaidit_enter()


def eksportet_txt(faila_cels, logi, bridinaajumi, incidenti):
    """
    Funkcija eksportet_txt pieņem str tipa vērtību faila_cels, list tipa vērtību logi,
    list tipa vērtību bridinaajumi un list tipa vērtību incidenti un atgriež bool tipa vērtību veiksme.
    Eksportē visus datus cilvēkam lasāmā TXT formātā ar sekcijām.
    """
    try:
        with open(faila_cels, "w", encoding="utf-8") as f:
            # Virsraksts
            f.write("=" * 65 + "\n")
            f.write("  SIEM RĪKS — ANALĪZES EKSPORTS\n")
            f.write(f"  Eksportēts: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 65 + "\n\n")

            # Kopsavilkums
            f.write("KOPSAVILKUMS\n")
            f.write("-" * 40 + "\n")
            f.write(f"Kopā žurnāla ieraksti:   {len(logi)}\n")
            f.write(f"Kopā brīdinājumi:        {len(bridinaajumi)}\n")
            f.write(f"  - Augsta riska:        {sum(1 for b in bridinaajumi if b.get('severity') == 'high')}\n")
            f.write(f"  - Vidēja riska:        {sum(1 for b in bridinaajumi if b.get('severity') == 'medium')}\n")
            f.write(f"  - Zema riska:          {sum(1 for b in bridinaajumi if b.get('severity') == 'low')}\n")
            f.write(f"Reģistrētie incidenti:   {len(incidenti)}\n\n")

            # Brīdinājumu sekcija
            f.write("DROŠĪBAS BRĪDINĀJUMI\n")
            f.write("-" * 40 + "\n")
            aktiiviie = [b for b in bridinaajumi if not b.get("ignorets", False)]
            for bridins in aktiiviie:
                f.write(f"[{bridins.get('severity', '?').upper()}] "
                        f"ID: {bridins.get('id', '?')} | "
                        f"Tips: {bridins.get('alert_type', '?')} | "
                        f"IP: {bridins.get('ip', '?')}\n")
                f.write(f"  Apraksts: {bridins.get('apraksts', 'Nav')}\n\n")

            # Žurnāla ierakstu sekcija (tikai pirmie 100)
            f.write("ŽURNĀLA IERAKSTI (maks. 100)\n")
            f.write("-" * 40 + "\n")
            for log in logi[:100]:
                f.write(f"{log.get('timestamp', 'N/A'):<22} "
                        f"{log.get('ip', 'N/A'):<16} "
                        f"{log.get('user', 'N/A'):<15} "
                        f"{log.get('event_type', 'N/A')}\n")

            # Incidentu sekcija
            if incidenti:
                f.write("\nREĢISTRĒTIE INCIDENTI\n")
                f.write("-" * 40 + "\n")
                for inc in incidenti:
                    f.write(f"Incidents #{inc.get('id')}: [{inc.get('status', '?').upper()}]\n")
                    f.write(f"  Apraksts: {inc.get('apraksts', 'Nav')}\n")
                    f.write(f"  Izveidots: {inc.get('izveidots', 'N/A')}\n\n")

        return True
    except Exception as e:
        return False


def eksportet_json(faila_cels, logi, bridinaajumi, incidenti):
    """
    Funkcija eksportet_json pieņem str tipa vērtību faila_cels, list tipa vērtību logi,
    list tipa vērtību bridinaajumi un list tipa vērtību incidenti un atgriež bool tipa vērtību veiksme.
    Eksportē visus datus strukturētā JSON formātā mašīnlasāmai apstrādei.
    """
    eksporta_dati = {
        "eksports_metadata": {
            "datums": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "versija": "1.0",
            "sistēma": "SIEM Rīks — RVT 2026"
        },
        "kopsavilkums": {
            "kopaa_logi": len(logi),
            "kopaa_bridinaajumi": len(bridinaajumi),
            "augsta_riska": sum(1 for b in bridinaajumi if b.get("severity") == "high"),
            "incidenti": len(incidenti)
        },
        "bridinaajumi": [b for b in bridinaajumi if not b.get("ignorets", False)],
        "logi": logi[:500],  # Eksportē max 500 ierakstus
        "incidenti": incidenti
    }

    try:
        with open(faila_cels, "w", encoding="utf-8") as f:
            json.dump(eksporta_dati, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        return False
