"""
Modulis: validator.py
Nodrošina datu validācijas funkcijas visam projektam.
Pārbauda datu formātu, tukšas vērtības un datu pareizību.
"""

import re
from datetime import datetime


def validet_nav_tukss(vertiba):
    """
    Funkcija validet_nav_tukss pieņem str tipa vērtību vertiba un atgriež bool tipa vērtību ir_deriga.
    Pārbauda, vai ievadītā vērtība nav tukša virkne vai atstarpes.
    """
    return bool(vertiba and vertiba.strip())


def validet_ip(ip_adrese):
    """
    Funkcija validet_ip pieņem str tipa vērtību ip_adrese un atgriež bool tipa vērtību ir_deriga.
    Pārbauda, vai IP adrese atbilst IPv4 formātam (piem., 192.168.1.1).
    """
    if not ip_adrese:
        return False
    # IPv4 regulārā izteiksme
    ipv4_reg = re.compile(
        r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$"
    )
    atbilsme = ipv4_reg.match(ip_adrese.strip())
    if not atbilsme:
        return False
    # Pārbauda, ka katrs oktets ir 0-255
    return all(0 <= int(g) <= 255 for g in atbilsme.groups())


def validet_timestamp(laika_zīmogs):
    """
    Funkcija validet_timestamp pieņem str tipa vērtību laika_zimogs un atgriež bool tipa vērtību ir_deriga.
    Pārbauda, vai laika zīmogs atbilst formātam YYYY-MM-DD HH:MM:SS.
    """
    if not laika_zīmogs:
        return False
    try:
        datetime.strptime(laika_zīmogs.strip(), "%Y-%m-%d %H:%M:%S")
        return True
    except ValueError:
        return False


def validet_lietotajvards(lietotajvards):
    """
    Funkcija validet_lietotajvards pieņem str tipa vērtību lietotajvards un atgriež bool tipa vērtību ir_deriga.
    Pārbauda, vai lietotājvārds nav tukšs un nepārsniedz 50 rakstzīmes.
    """
    if not validet_nav_tukss(lietotajvards):
        return False
    return len(lietotajvards.strip()) <= 50


def validet_notikuma_tips(notikuma_tips):
    """
    Funkcija validet_notikuma_tips pieņem str tipa vērtību notikuma_tips un atgriež bool tipa vērtību ir_deriga.
    Pārbauda, vai notikuma tips ir viens no atļautajiem tipiem vai nav tukšs.
    """
    atlauti_tipi = {
        "failed_login", "success_login", "general", "error",
        "access_denied", "port_scan", "brute_force", "anomaly"
    }
    if not validet_nav_tukss(notikuma_tips):
        return False
    # Pieļauj gan standarta, gan pielāgotus tipus, bet pārbauda garumu
    return len(notikuma_tips.strip()) <= 30


def validet_severity(severity):
    """
    Funkcija validet_severity pieņem str tipa vērtību severity un atgriež bool tipa vērtību ir_deriga.
    Pārbauda, vai riska līmenis ir "low", "medium" vai "high".
    """
    return severity.lower() in {"low", "medium", "high"}


def validet_status(status):
    """
    Funkcija validet_status pieņem str tipa vērtību status un atgriež bool tipa vērtību ir_deriga.
    Pārbauda, vai incidenta statuss ir "open" vai "closed".
    """
    return status.lower() in {"open", "closed"}
