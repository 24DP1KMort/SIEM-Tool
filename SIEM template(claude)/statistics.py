"""
Modulis: statistics.py
Aprēķina un attēlo statistiku par sistēmas notikumiem,
brīdinājumiem un drošības stāvokli.
"""

from collections import defaultdict, Counter
from database import nolasit_datus, LOGS_FILE, ALERTS_FILE, INCIDENTS_FILE
from ui import (display_section_header, display_error, display_info,
                        gaaidit_enter, DZELTENS, ATIESTATIT, BOLD, GAISSZILS,
                        SARKANS, ZALS, VIOLETS, ZILANS)


def skatit_statistiku():
    """
    Funkcija skatit_statistiku nepieņem vērtības un atgriež None tipa vērtību rezultaats.
    Aprēķina un attēlo visaptverošu statistiku par sistēmas drošības stāvokli.
    """
    display_section_header("SISTĒMAS STATISTIKA")

    logi = nolasit_datus(LOGS_FILE)
    bridinaajumi = nolasit_datus(ALERTS_FILE)
    incidenti = nolasit_datus(INCIDENTS_FILE)

    if not logi and not bridinaajumi:
        display_error("Nav datu statistikas aprēķinam. Ielādējiet žurnālfailus.")
        gaaidit_enter()
        return

    # === VISPĀRĪGĀ STATISTIKA ===
    print(f"{BOLD}{GAISSZILS}  ╔══════════════════════════════════╗")
    print(f"  ║      VISPĀRĪGĀ STATISTIKA        ║")
    print(f"  ╚══════════════════════════════════╝{ATIESTATIT}\n")

    kopejs_skaits = len(logi)
    neveiksmiigi = sum(1 for l in logi if l.get("event_type") == "failed_login")
    veiksmiigi = sum(1 for l in logi if l.get("event_type") == "success_login")
    unikalaas_ip = len(set(l.get("ip", "") for l in logi))
    kopejie_alerti = len(bridinaajumi)
    aktiiviie_alerti = sum(1 for b in bridinaajumi if not b.get("ignorets", False))
    augsta_riska = sum(1 for b in bridinaajumi if b.get("severity") == "high" and not b.get("ignorets"))

    # Vizuāls informācijas panelis
    print(f"  {DZELTENS}┌─────────────────────────────────────────────┐{ATIESTATIT}")
    print(f"  {DZELTENS}│{ATIESTATIT}  📊 Kopā žurnāla ieraksti:     {BOLD}{kopejs_skaits:>8}{ATIESTATIT}          {DZELTENS}│{ATIESTATIT}")
    print(f"  {DZELTENS}│{ATIESTATIT}  {SARKANS}✗{ATIESTATIT} Neveiksmīgie pieslēgumi:  {BOLD}{neveiksmiigi:>8}{ATIESTATIT}          {DZELTENS}│{ATIESTATIT}")
    print(f"  {DZELTENS}│{ATIESTATIT}  {ZALS}✓{ATIESTATIT} Veiksmīgie pieslēgumi:    {BOLD}{veiksmiigi:>8}{ATIESTATIT}          {DZELTENS}│{ATIESTATIT}")
    print(f"  {DZELTENS}│{ATIESTATIT}  🌐 Unikālās IP adreses:       {BOLD}{unikalaas_ip:>8}{ATIESTATIT}          {DZELTENS}│{ATIESTATIT}")
    print(f"  {DZELTENS}│{ATIESTATIT}  🚨 Kopā brīdinājumi:          {BOLD}{kopejie_alerti:>8}{ATIESTATIT}          {DZELTENS}│{ATIESTATIT}")
    print(f"  {DZELTENS}│{ATIESTATIT}  ⚠️  Aktīvie brīdinājumi:       {BOLD}{aktiiviie_alerti:>8}{ATIESTATIT}          {DZELTENS}│{ATIESTATIT}")
    print(f"  {DZELTENS}│{ATIESTATIT}  {SARKANS}🔴 Augsta riska brīdinājumi:{BOLD}{augsta_riska:>8}{ATIESTATIT}          {DZELTENS}│{ATIESTATIT}")
    print(f"  {DZELTENS}│{ATIESTATIT}  📝 Reģistrētie incidenti:     {BOLD}{len(incidenti):>8}{ATIESTATIT}          {DZELTENS}│{ATIESTATIT}")
    print(f"  {DZELTENS}└─────────────────────────────────────────────┘{ATIESTATIT}\n")

    if not logi:
        gaaidit_enter()
        return

    # === TOP IP ADRESES ===
    print(f"\n{BOLD}{GAISSZILS}  TOP 5 AKTĪVĀKĀS IP ADRESES{ATIESTATIT}")
    print(f"  {ZILANS}{'─' * 45}{ATIESTATIT}")

    ip_skaaitajs = aprekskinaat_ip_aktivitati(logi)
    for ip, skaits in ip_skaaitajs.most_common(5):
        # Progress bar vizualizācija
        max_skaits = ip_skaaitajs.most_common(1)[0][1]
        bar_garums = int((skaits / max_skaits) * 20) if max_skaits > 0 else 0
        bar = "█" * bar_garums + "░" * (20 - bar_garums)
        print(f"  {GAISSZILS}{ip:<18}{ATIESTATIT} {DZELTENS}{bar}{ATIESTATIT} {skaits}")

    # === NOTIKUMU TIPI ===
    print(f"\n{BOLD}{GAISSZILS}  NOTIKUMU SADALĪJUMS PĒC TIPA{ATIESTATIT}")
    print(f"  {ZILANS}{'─' * 45}{ATIESTATIT}")

    tipu_skaaitajs = Counter(l.get("event_type", "unknown") for l in logi)
    for tips, skaits in tipu_skaaitajs.most_common():
        print(f"  {DZELTENS}{tips:<25}{ATIESTATIT} {skaits:>6} ieraksti")

    # === DROŠĪBAS NOVĒRTĒJUMS ===
    print(f"\n{BOLD}{GAISSZILS}  DROŠĪBAS STĀVOKĻA NOVĒRTĒJUMS{ATIESTATIT}")
    print(f"  {ZILANS}{'─' * 45}{ATIESTATIT}")

    novertejums = noverteet_drosibas_staavokli(neveiksmiigi, augsta_riska, kopejs_skaits)
    print(f"  {novertejums}")

    gaaidit_enter()


def aprekskinaat_ip_aktivitati(logi):
    """
    Funkcija aprekskinaat_ip_aktivitati pieņem list tipa vērtību logi un atgriež Counter tipa vērtību ip_skaaitajs.
    Saskaita kopējo notikumu skaitu katrai IP adresei.
    """
    return Counter(log.get("ip", "unknown") for log in logi)


def noverteet_drosibas_staavokli(neveiksmiigi, augsta_riska, kopejais):
    """
    Funkcija noverteet_drosibas_staavokli pieņem int tipa vērtību neveiksmiigi, int tipa vērtību augsta_riska
    un int tipa vērtību kopejais un atgriež str tipa vērtību novertejuma_teksts.
    Aprēķina drošības riska līmeni pēc neveiksmīgo pieslēgumu proporcijas un augsta riska brīdinājumiem.
    """
    if kopejais == 0:
        return f"  {GAISSZILS}📊 Nepietiekami dati novērtējumam.{ATIESTATIT}"

    kludainas_proporcija = neveiksmiigi / kopejais if kopejais > 0 else 0

    if augsta_riska > 5 or kludainas_proporcija > 0.7:
        return (f"  {SARKANS}🔴 KRITISKI — Konstatēts augsts draudu līmenis!\n"
                f"     Nekavējoties pārskatiet augsta riska brīdinājumus!{ATIESTATIT}")
    elif augsta_riska > 0 or kludainas_proporcija > 0.3:
        return (f"  {DZELTENS}🟡 UZMANĪBU — Konstatētas aizdomīgas darbības.\n"
                f"     Ieteicams pārskatīt brīdinājumus un veikt izmeklēšanu.{ATIESTATIT}")
    else:
        return (f"  {ZALS}🟢 LABI — Sistēmas drošības stāvoklis ir apmierinošs.\n"
                f"     Turpiniet regulāru uzraudzību.{ATIESTATIT}")
