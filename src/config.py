"""Felles konfigurasjon for etterprøvingen av NRKs «Prisen for billig strøm»."""
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
OUT = ROOT / "output"
for p in (RAW, PROC, OUT):
    p.mkdir(parents=True, exist_ok=True)

# .env i prosjektroten (FROST_CLIENT_ID). Leses uten å skrive verdien noe sted.
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

# Analyseperiode (NRK: 2021 – juni 2026). Elhubs kommunefil starter feb. 2022,
# spotpriser fra hvakosterstrommen.no starter des. 2021 → panelet blir feb. 2022–jun. 2026.
START = "2021-01-01"
END = "2026-06-30"
NORGESPRIS_START = "2025-10-01"

# Prisområder i analysen (NRK utelater NO3/NO4)
PRICE_AREAS = ["NO1", "NO2", "NO5"]
# Fylker (kommunenummerets to første sifre, 2024-inndeling) som ligger i NO1/NO2/NO5
SOUTH_COUNTIES = ["03", "31", "32", "33", "34", "39", "40", "42", "11", "46"]

# Elhub – åpne data, CC BY 4.0. Verifisert 05.09.2026: fire av fem filer leveres
# gzip-komprimert bak .csv-URL, alle med ';' som skilletegn og desimalkomma.
ELHUB_DL = "https://data.elhub.no/download"
ELHUB_FILES = {
    # STARTTID;SLUTTID;KOMMUNE;KOMMUNENUMMER;FORBRUKSGRUPPE;VOLUM_KWH;ANTALL_MÅLEPUNKT  (gz, fra 2022-02)
    "cons_muni": ("consumption_per_group_municipality_hour", True),
    # STARTTID;SLUTTID;PRISOMRÅDE;FORBRUKSGRUPPE;VOLUM_KWH;ANTALL_MÅLEPUNKT  (gz, fra 2021-01)
    "cons_mba": ("consumption_per_group_mba_hour", True),
    # DATO;KOMMUNENUMMER;KOMMUNE;FORBRUKSGRUPPE;ANTALL_NORGESPRIS;ANTALL  (gz, daglig fra 2025-10-01)
    "np_muni": ("norgespris_count_per_municipality_consumption_group", True),
    # DATO;PRISOMRÅDE;FORBRUKSGRUPPE;ANTALL_NORGESPRIS;ANTALL  (gz)
    "np_mba": ("norgespris_count_per_mba_consumption_group", True),
    # STARTTID;SLUTTID;PRISOMRÅDE;ESTIMERT_ÅRLIG_FORBRUK_GRUPPE;NORGESPRIS_BESTILLING_STATUS;FORBRUK;ANTALL_MÅLEPUNKT (ren csv)
    "np_status": ("consumption_per_norgespris_order_status_eac_group_mba_hour_20231001_20260430", False),
}
ELHUB_CSV_KW = dict(sep=";", decimal=",", encoding="utf-8")

# SSB PxWebApi v2 – JSON-stat2. Metadata verifisert 05.09.2026.
SSB_V2 = "https://data.ssb.no/api/pxwebapi/v2/tables/{tab}/data"
SSB_INCOME_TABLE = "06944"     # Inntekt for husholdninger, median; Region inkl. delområder → filtrer 4-sifret
SSB_DWELLING_TABLE = "06513"   # Boliger etter bygningstype og bruksareal; Region-koder "K-xxxx"

# Spotpriser (NOK/kWh eks. mva) – hvakosterstrommen.no, data fra 2021-12-01
HKS_URL = "https://www.hvakosterstrommen.no/api/v1/prices/{y}/{m:02d}-{d:02d}_{area}.json"

# MET Frost – klient-ID fra .env
FROST_CLIENT_ID = os.environ.get("FROST_CLIENT_ID", "")
FROST_BASE = "https://frost.met.no"
GRADTALL_BASE_TEMP = 17.0  # Enova/MET-standard for energigradtall

# NVE vannkraftdatabase (felt verifisert: EnEkv, MidProd_91_20, ElspotomraadeNummer, KommuneNr)
NVE_PLANTS_URL = "https://api.nve.no/web/Powerplant/GetHydroPowerPlantsInOperation"
