"""Kommune → prisområde og kommune → fylke.

Det finnes ingen offisiell tabell kommune→prisområde. Vi bruker:
  1. fylkesbasert standard (kommuneinndeling 2024),
  2. NVEs vannkraftdatabase: kraftverkenes ElspotomraadeNummer per (fylkesnr, kommunenavn).
     Når alle kraftverk i kommunen ligger i ett område og det avviker fra fylkesregelen,
     overstyrer NVE. NB: NVE-feltet `KommuneNr` er en intern ID (1–80), IKKE kommunenummer;
     koblingen går derfor på navn.
  3. manuelle unntak for kommuner uten kraftverk der fylkesregelen er kjent feil.
Kolonnen `pa_kilde` sier hvor koblingen kommer fra. Listen over overstyringer skrives
til output/tab_kommune_prisomrade.csv til godkjenning.
"""
import re
import pandas as pd
from config import RAW, OUT

FYLKE_TO_PA = {
    "03": "NO1", "31": "NO1", "32": "NO1", "33": "NO1", "34": "NO1",
    "39": "NO2", "40": "NO2", "42": "NO2", "11": "NO2",
    "46": "NO5",
    "15": "NO3", "50": "NO3",
    "18": "NO4", "55": "NO4", "56": "NO4",
}

# Kommuner uten (entydige) kraftverk der fylkesregelen er kjent feil. TIL GODKJENNING.
EXCEPTIONS = {
    "4613": "NO2",  # Bømlo – Sunnhordland ligger i NO2 (som Stord, Fitjar, Tysnes, Etne iflg. NVE)
    "4612": "NO2",  # Sveio – Sunnhordland
}


def _norm(s: pd.Series) -> pd.Series:
    s = s.astype(str).str.strip().str.lower()
    s = s.str.replace(r"\s+[–-]\s+.*$", "", regex=True)      # «Raarvikhe – Røyrvik» → «raarvikhe»; krever mellomrom rundt streken, så «Nord-Aurdal» beholdes
    s = s.str.replace(r"\s*\(.*\)$", "", regex=True)          # «Våler (Innlandet)» → «våler»
    return s


def kommune_to_fylke(knr: pd.Series) -> pd.Series:
    return knr.astype(str).str.zfill(4).str[:2]


def nve_area_by_name() -> pd.DataFrame:
    """(fylkesnr, normalisert navn) → prisområde når entydig, ellers 'flere'."""
    p = pd.read_json(RAW / "nve_kraftverk.json").dropna(subset=["ElspotomraadeNummer", "Kommune", "FylkesNr"])
    p["fylke"] = p.FylkesNr.astype(int).astype(str).str.zfill(2)
    p["navn"] = _norm(p.Kommune)
    # samisk/norsk dobbeltnavn: også siste ledd
    p2 = p.copy(); p2["navn"] = p.Kommune.astype(str).str.split(r"\s+[–-]\s+").str[-1].str.strip().str.lower()
    p = pd.concat([p, p2]).drop_duplicates(["Navn", "navn"])
    g = p.groupby(["fylke", "navn"]).ElspotomraadeNummer.agg(lambda s: sorted(set(s.astype(int))))
    out = g.reset_index()
    out["pa_nve"] = out.ElspotomraadeNummer.map(lambda l: f"NO{l[0]}" if len(l) == 1 else "flere")
    out["n_omrader"] = out.ElspotomraadeNummer.map(len)
    return out[["fylke", "navn", "pa_nve", "n_omrader"]]


def kommune_to_pa(knr: pd.Series, navn: pd.Series | None = None, use_nve: bool = True) -> pd.DataFrame:
    k = knr.astype(str).str.zfill(4)
    df = pd.DataFrame({"knr": k.values, "kommune": (navn.values if navn is not None else k.values)})
    df["fylke"] = kommune_to_fylke(df.knr)
    df["prisomrade"] = df.fylke.map(FYLKE_TO_PA)
    df["pa_kilde"] = "fylke"
    if use_nve and navn is not None and (RAW / "nve_kraftverk.json").exists():
        nve = nve_area_by_name()
        df["navn"] = _norm(df.kommune)
        df = df.merge(nve, on=["fylke", "navn"], how="left")
        ent = df.pa_nve.notna() & (df.pa_nve != "flere")
        diff = ent & (df.pa_nve != df.prisomrade)
        df.loc[diff, "prisomrade"] = df.loc[diff, "pa_nve"]
        df.loc[diff, "pa_kilde"] = "nve"
        df.loc[ent & ~diff, "pa_kilde"] = "fylke=nve"
        print(f"Prisområde: {ent.sum()} kommuner bekreftet/overstyrt av NVE, {diff.sum()} overstyrt: "
              f"{df.loc[diff, ['kommune', 'pa_nve']].apply(lambda r: f'{r.kommune}→{r.pa_nve}', axis=1).tolist()}")
        df = df.drop(columns=["navn"])
    exc = df.knr.map(EXCEPTIONS)
    df.loc[exc.notna(), "prisomrade"] = exc[exc.notna()]
    df.loc[exc.notna(), "pa_kilde"] = "unntak"
    if use_nve:
        df.to_csv(OUT / "tab_kommune_prisomrade.csv", index=False)
    return df
