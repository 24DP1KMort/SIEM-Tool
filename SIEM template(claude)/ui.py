"""
Modulis: ui.py
Nodrošina lietotāja saskarnes funkcijas termināļa vidē (TUI).
Atbild par teksta formatēšanu, izvēļņu attēlošanu un kļūdu paziņojumiem.
"""

import os


# Krāsu kodi termināļa izvadei
SARKANS = "\033[91m"
ZALS = "\033[92m"
DZELTENS = "\033[93m"
ZILANS = "\033[94m"
VIOLETS = "\033[95m"
GAISSZILS = "\033[96m"
BALTS = "\033[97m"
BOLD = "\033[1m"
ATIESTATIT = "\033[0m"


def notirit_ekranu():
    """
    Funkcija notirit_ekranu nepieņem vērtības un atgriež None tipa vērtību rezultaats.
    Notīra termināļa ekrānu atkarībā no operētājsistēmas.
    """
    os.system("cls" if os.name == "nt" else "clear")


def display_header():
    """
    Funkcija display_header nepieņem vērtības un atgriež None tipa vērtību rezultaats.
    Attēlo programmas galveni ar nosaukumu un autoru informāciju.
    """
    notirit_ekranu()
    print(f"{GAISSZILS}{BOLD}")
    print("=" * 65)
    print("   ██████╗ ██╗███████╗███╗   ███╗    ██████╗ ██╗██╗  ██╗███████╗")
    print("   ██╔════╝██║██╔════╝████╗ ████║    ██╔══██╗██║██║ ██╔╝██╔════╝")
    print("   ███████╗██║█████╗  ██╔████╔██║    ██████╔╝██║█████╔╝ ███████╗")
    print("   ╚════██║██║██╔══╝  ██║╚██╔╝██║    ██╔══██╗██║██╔═██╗ ╚════██║")
    print("   ███████║██║███████╗██║ ╚═╝ ██║    ██║  ██║██║██║  ██╗███████║")
    print("   ╚══════╝╚═╝╚══════╝╚═╝     ╚═╝    ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚══════╝")
    print("=" * 65)
    print(f"   Drošības Notikumu un Žurnālu Analīzes Rīks")
    print(f"   Rīgas Valsts Tehnikums | Datorikas nodaļa | 2026")
    print("=" * 65)
    print(f"{ATIESTATIT}")


def display_menu():
    """
    Funkcija display_menu nepieņem vērtības un atgriež str tipa vērtību izvele.
    Attēlo galveno izvēlni un pieprasa lietotāja ievadi.
    """
    print(f"{BOLD}{GAISSZILS}  GALVENĀ IZVĒLNE{ATIESTATIT}")
    print(f"{ZILANS}  {'─' * 40}{ATIESTATIT}")
    print(f"  {DZELTENS}[1]{ATIESTATIT} 📂  Ielādēt žurnālfailu")
    print(f"  {DZELTENS}[2]{ATIESTATIT} 📋  Apskatīt žurnālfailus")
    print(f"  {DZELTENS}[3]{ATIESTATIT} 🔍  Meklēt žurnālfailos")
    print(f"  {DZELTENS}[4]{ATIESTATIT} 🧠  Analizēt žurnālfailus")
    print(f"  {DZELTENS}[5]{ATIESTATIT} 🚨  Apskatīt brīdinājumus")
    print(f"  {DZELTENS}[6]{ATIESTATIT} 📊  Skatīt statistiku")
    print(f"  {DZELTENS}[7]{ATIESTATIT} 📝  Reģistrēt incidentu")
    print(f"  {DZELTENS}[8]{ATIESTATIT} 💾  Eksportēt analīzi")
    print(f"  {SARKANS}[0]{ATIESTATIT} ❌  Iziet")
    print(f"{ZILANS}  {'─' * 40}{ATIESTATIT}")
    return input(f"  {BOLD}Ievadiet izvēli: {ATIESTATIT}").strip()


def display_error(ziņojums):
    """
    Funkcija display_error pieņem str tipa vērtību zinojums un atgriež None tipa vērtību rezultaats.
    Attēlo kļūdas paziņojumu sarkanā krāsā.
    """
    print(f"\n  {SARKANS}[KĻŪDA]{ATIESTATIT} {ziņojums}\n")


def display_success(ziņojums):
    """
    Funkcija display_success pieņem str tipa vērtību zinojums un atgriež None tipa vērtību rezultaats.
    Attēlo veiksmīgas darbības paziņojumu zaļā krāsā.
    """
    print(f"\n  {ZALS}[VEIKSMĪGI]{ATIESTATIT} {ziņojums}\n")


def display_info(ziņojums):
    """
    Funkcija display_info pieņem str tipa vērtību zinojums un atgriež None tipa vērtību rezultaats.
    Attēlo informatīvo paziņojumu zilā krāsā.
    """
    print(f"  {GAISSZILS}[INFO]{ATIESTATIT} {ziņojums}")


def display_warning(ziņojums):
    """
    Funkcija display_warning pieņem str tipa vērtību zinojums un atgriež None tipa vērtību rezultaats.
    Attēlo brīdinājuma paziņojumu dzeltenā krāsā.
    """
    print(f"  {DZELTENS}[BRĪDINĀJUMS]{ATIESTATIT} {ziņojums}")


def display_section_header(nosaukums):
    """
    Funkcija display_section_header pieņem str tipa vērtību nosaukums un atgriež None tipa vērtību rezultaats.
    Attēlo sadaļas virsrakstu ar dekoratīvu apmali.
    """
    print(f"\n{BOLD}{GAISSZILS}  ╔{'═' * (len(nosaukums) + 4)}╗")
    print(f"  ║  {nosaukums}  ║")
    print(f"  ╚{'═' * (len(nosaukums) + 4)}╝{ATIESTATIT}\n")


def gaaidit_enter():
    """
    Funkcija gaaidit_enter nepieņem vērtības un atgriež None tipa vērtību rezultaats.
    Gaida, kamēr lietotājs nospiež Enter, pirms turpināt.
    """
    input(f"\n  {DZELTENS}Nospiediet Enter, lai turpinātu...{ATIESTATIT}")
    display_header()
