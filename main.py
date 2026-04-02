import json
import os
import csv
from datetime import datetime

# ==================== DATU IELĀDE UN SAGLABĀŠANA ====================

def ieladet_failus(faila_vards):
    if os.path.exists(faila_vards):
        with open(faila_vards, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"logs": [], "alerts": []}


def saglabat_datus(dati, faila_vards="siem_dati.json"):
    with open(faila_vards, 'w', encoding='utf-8') as f:
        json.dump(dati, f, indent=4, ensure_ascii=False)


def saglabat_csv(dati, faila_vards="siem_events.csv"):
    if not dati.get("logs"):
        print("Nav datu, ko saglabāt CSV.")
        return

    fieldnames = ["timestamp", "source", "event_type", "description", "severity", "user", "ip"]

    with open(faila_vards, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for entry in dati["logs"]:
            row = {
                "timestamp": entry.get("timestamp", datetime.now().isoformat()),
                "source": entry.get("source", "unknown"),
                "event_type": entry.get("event_type", "unknown"),
                "description": entry.get("description", ""),
                "severity": entry.get("severity", "INFO"),
                "user": entry.get("user", ""),
                "ip": entry.get("ip", "")
            }
            writer.writerow(row)
    print(f"Dati saglabāti CSV failā: {faila_vards}")


def saglabat_txt_log(dati, faila_vards="siem_log.txt"):
    with open(faila_vards, 'w', encoding='utf-8') as f:
        f.write(f"=== SIEM Žurnāls — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")
        for entry in dati.get("logs", []):
            f.write(f"[{entry.get('timestamp', '')[:19]}] ")
            f.write(f"{entry.get('severity', 'INFO'):8} ")
            f.write(f"{entry.get('source', 'SYSTEM'):12} ")
            f.write(f"{entry.get('event_type', '')} - ")
            f.write(f"{entry.get('description', '')}\n")
    print(f"Dati saglabāti TXT failā: {faila_vards}")


# ==================== FUNKCIJAS ====================

def saglabat_datubaze(dati):
    print("\nSaglabāju datus...")
    saglabat_csv(dati)
    saglabat_txt_log(dati)
    saglabat_datus(dati)
    print("Dati veiksmīgi saglabāti!")


def ieladet_zurnala_failus(dati):
    print("Ielādēju žurnālfailus (demo)...")
    
    jauni_ieraksti = [
        {
            "timestamp": datetime.now().isoformat(),
            "source": "Firewall",
            "event_type": "connection_attempt",
            "description": "Neautorizēta piekļuve no ārējā IP",
            "severity": "HIGH",
            "user": "unknown",
            "ip": "185.220.101.45"
        },
        {
            "timestamp": datetime.now().isoformat(),
            "source": "Windows-Server",
            "event_type": "login_success",
            "description": "Lietotājs admin pieslēdzās",
            "severity": "INFO",
            "user": "admin",
            "ip": "192.168.1.50"
        }
    ]
    
    dati["logs"].extend(jauni_ieraksti)
    print(f"Pievienoti {len(jauni_ieraksti)} jauni žurnāla ieraksti.")
    return dati


def apskatit_visus_ierakstus(dati):
    print(f"\n=== VISI ŽURNĀLA IERAKSTI ({len(dati.get('logs', []))}) ===")
    for i, entry in enumerate(dati.get("logs", []), 1):
        print(f"{i:2}. [{entry.get('timestamp','')[:19]}] {entry.get('severity','INFO'):8} {entry.get('description','')}")


def meklet_informaciju(dati):
    print("Meklēšana žurnālos vēl nav realizēta.")


def analizet_datus(dati):
    print("Datu analīze vēl nav realizēta.")
    return dati


def atzimet_aizdomigas_darbibas(dati):
    print("Aizdomīgu darbību atzīmēšana vēl nav realizēta.")
    return dati


def generet_bridinajumus(dati):
    print("Brīdinājumu ģenerēšana vēl nav realizēta.")
    return dati


def apskatit_bridinajumus(dati):
    print("Brīdinājumu apskate vēl nav realizēta.")


def analizet_statistiku(dati):
    print(f"\nStatistika:")
    print(f"Kopā žurnāla ieraksti: {len(dati.get('logs', []))}")
    print(f"Brīdinājumi: {len(dati.get('alerts', []))}")


# ==================== GALVENĀ IZVĒLNE ====================

def galvena_izvelne():
    """Funkcija parāda galveno izvēlni un apstrādā lietotāja izvēles."""
    faila_vards = "siem_dati.json"
    dati = ieladet_failus(faila_vards)
    
    while True:
        print("\n=== SIEM Rīks ===")
        print("1. Ielādēt žurnālfailus")
        print("2. Apskatīt visus žurnāla ierakstus")
        print("3. Meklēt informāciju žurnālos")
        print("4. Analizēt žurnāla datus")
        print("5. Atzīmēt aizdomīgas darbības")
        print("6. Ģenerēt brīdinājumus")
        print("7. Apskatīt brīdinājumu sarakstu")
        print("8. Analizēt statistiku")
        print("9. Saglabāt datus datubāzē")
        print("0. Iziet")
        
        izvele = input("Izvēlieties darbību (0-9): ").strip()
        
        if izvele == "1":
            dati = ieladet_zurnala_failus(dati)
        elif izvele == "2":
            apskatit_visus_ierakstus(dati)
        elif izvele == "3":
            meklet_informaciju(dati)
        elif izvele == "4":
            dati = analizet_datus(dati)
        elif izvele == "5":
            dati = atzimet_aizdomigas_darbibas(dati)
        elif izvele == "6":
            dati = generet_bridinajumus(dati)
        elif izvele == "7":
            apskatit_bridinajumus(dati)
        elif izvele == "8":
            analizet_statistiku(dati)
        elif izvele == "9":
            saglabat_datubaze(dati)
        elif izvele == "0":
            saglabat_datus(dati, faila_vards)
            print("Programma beidzas. Dati saglabāti.")
            break
        else:
            print("Nepareiza izvēle. Lūdzu, mēģiniet vēlreiz.")


# ==================== PROGRAMMAS SĀKUMS ====================

if __name__ == "__main__":
    galvena_izvelne()