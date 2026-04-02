"""
SIEM rīks drošības notikumu un žurnālu analīzei
Autori: Rodrigo Šaudiņš, Kristers Mortuzāns, Roberts Savčenko
Rīgas Valsts Tehnikums, 2026
"""

import os
import sys

# Nodrošina, ka Python atrod 'modules' mapi neatkarīgi no tā,
# no kuras direktorijas programma tiek palaista
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import log_loader, log_viewer, log_search, log_analyzer
import alert_manager, statistics, incident_manager, exporter
from database import initialize_database
from ui import display_menu, display_header, display_error, display_success


def main():
    """
    Funkcija main nepieņem vērtības un atgriež None tipa vērtību exit_code.
    Galvenā programmas ieejas funkcija — inicializē datubāzi un palaiž galveno izvēlni.
    """
    initialize_database()
    display_header()

    while True:
        izvele = display_menu()

        if izvele == "1":
            log_loader.ielaadet_zurnaalfailu()
        elif izvele == "2":
            log_viewer.apskatit_zurnaalfailus()
        elif izvele == "3":
            log_search.meklet_zurnaalfailos()
        elif izvele == "4":
            log_analyzer.analizet_zurnaalfailus()
        elif izvele == "5":
            alert_manager.apskatit_bridinajumus()
        elif izvele == "6":
            statistics.skatit_statistiku()
        elif izvele == "7":
            incident_manager.registret_incidentu()
        elif izvele == "8":
            exporter.eksportet_analiezi()
        elif izvele == "0":
            display_success("Programma tiek aizvērta. Uz redzēšanos!")
            sys.exit(0)
        else:
            display_error("Nepareiza izvēle! Lūdzu, ievadiet skaitli no 0 līdz 8.")


if __name__ == "__main__":
    main()
