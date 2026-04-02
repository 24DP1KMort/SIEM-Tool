"""
Modulis: incident_manager.py
Nodrošina drošības incidentu reģistrāciju, pārvaldību un statusu atjaunināšanu.
"""

from datetime import datetime
from database import (nolasit_datus, saglaabt_datus,
                               nakamais_id, INCIDENTS_FILE, ALERTS_FILE)
from ui import (display_section_header, display_error, display_success,
                        display_info, gaaidit_enter, DZELTENS, ATIESTATIT,
                        BOLD, GAISSZILS, SARKANS, ZALS, ZILANS)
from validator import validet_nav_tukss, validet_status


def registret_incidentu():
    """
    Funkcija registret_incidentu nepieņem vērtības un atgriež None tipa vērtību rezultaats.
    Ļauj lietotājam reģistrēt jaunu drošības incidentu, saistot to ar esošu brīdinājumu.
    """
    display_section_header("INCIDENTA REĢISTRĀCIJA")

    bridinaajumi = nolasit_datus(ALERTS_FILE)
    incidenti = nolasit_datus(INCIDENTS_FILE)

    # Attēlo aktīvos brīdinājumus, lai lietotājs var izvēlēties saistāmo
    aktiiviie = [b for b in bridinaajumi if not b.get("ignorets", False)]

    if aktiiviie:
        print(f"  {GAISSZILS}Pieejamie brīdinājumi incidenta saistīšanai:{ATIESTATIT}")
        for b in aktiiviie[:10]:  # Rāda maksimāli 10
            riska_krasa = SARKANS if b.get("severity") == "high" else DZELTENS
            print(f"  {riska_krasa}[{b.get('id')}]{ATIESTATIT} {b.get('apraksts', '')[:55]}")
        print()

    # Brīdinājuma ID (neobligāts)
    alert_id_str = input(f"  {DZELTENS}Saistītā brīdinājuma ID (Enter, lai izlaistu): {ATIESTATIT}").strip()
    alert_id = None
    if alert_id_str:
        if not alert_id_str.isdigit():
            display_error("Brīdinājuma ID jābūt skaitlim!")
            gaaidit_enter()
            return
        alert_id = int(alert_id_str)

    # Incidenta apraksts
    apraksts = input(f"  {DZELTENS}Incidenta apraksts (max 255 rakstzīmes): {ATIESTATIT}").strip()
    if not validet_nav_tukss(apraksts):
        display_error("Incidenta apraksts nedrīkst būt tukšs!")
        gaaidit_enter()
        return

    # Apgriež aprakstu līdz 255 rakstzīmēm
    apraksts = apraksts[:255]

    # Statusa izvēle
    print(f"\n  {GAISSZILS}Incidenta sākotnējais statuss:{ATIESTATIT}")
    print(f"  {DZELTENS}[1]{ATIESTATIT} open   — Atvērts (aktīvs incidents)")
    print(f"  {ZALS}[2]{ATIESTATIT} closed — Slēgts (atrisināts incidents)")

    status_izvele = input(f"  {BOLD}Izvēlieties statusu [1/2]: {ATIESTATIT}").strip()
    status = "open" if status_izvele != "2" else "closed"

    # Izveido jauno incidenta ierakstu
    jaunais_incidents = {
        "id": nakamais_id(incidenti),
        "alert_id": alert_id,
        "apraksts": apraksts,
        "status": status,
        "izveidots": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "atjauninats": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    incidenti.append(jaunais_incidents)

    if saglaabt_datus(INCIDENTS_FILE, incidenti):
        display_success(f"Incidents #{jaunais_incidents['id']} veiksmīgi reģistrēts!")
        print(f"  Status: {ZALS if status == 'closed' else SARKANS}{status.upper()}{ATIESTATIT}")
    else:
        display_error("Kļūda saglabājot incidentu!")

    gaaidit_enter()
