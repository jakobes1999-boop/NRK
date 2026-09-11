"""Steg 2: Kontrollvariabler fra SSB (PxWebApi v2, JSON-stat2).

  06944  Inntekt etter skatt, median, alle husholdninger, per kommune (årlig, t.o.m. 2024).
         Region-dimensjonen inneholder også delområder; vi beholder 4-sifrede kommunekoder.
  06513  Boliger etter bygningstype og bruksareal per kommune (årlig, 1.1.).
         Region-koder har formen «K-3101»; vi summerer over bygningstype.

Begge følger gjeldende kommuneinndeling (2024), som Elhubs kommunenummer.
Boligstørrelse beregnes som gjennomsnittlig bruksareal ved klassemidtpunkt.
"""
import json
import itertools
import requests
import pandas as pd
from config import RAW, PROC, SSB_V2, SSB_INCOME_TABLE, SSB_DWELLING_TABLE

AREA_MID = {  # klassemidtpunkt, m² (kode → midtpunkt); 99 = ukjent utelates
    "1": 25, "2": 35, "3": 45, "4": 55, "5": 70, "6": 90, "50": 110, "51": 130,
    "52": 150, "53": 180, "54": 225, "55": 275, "56": 325, "57": 400,
}


def fetch_jsonstat(table: str, selection: dict, name: str) -> dict:
    dest = RAW / f"ssb_{name}.json"
    if dest.exists():
        return json.loads(dest.read_text(encoding="utf-8"))
    params = {"lang": "no", "outputFormat": "json-stat2"}
    params.update({f"valueCodes[{k}]": v for k, v in selection.items()})
    r = requests.get(SSB_V2.format(tab=table), params=params, timeout=300)
    r.raise_for_status()
    dest.write_text(r.text, encoding="utf-8")
    return r.json()


def jsonstat_to_long(js: dict) -> pd.DataFrame:
    """JSON-stat2 → lang tabell med én kolonne per dimensjon (kode) + 'verdi'."""
    dims = js["id"]
    codes = [list(js["dimension"][d]["category"]["index"]) for d in dims]
    rows = list(itertools.product(*codes))
    df = pd.DataFrame(rows, columns=dims)
    df["verdi"] = js["value"]
    return df


def recode_to_2024(knr: pd.Series, aar: pd.Series) -> pd.Series:
    """Gamle kommunenummer → 2024-nummer via Klass 131. Splitter (1507 Ålesund→1508/1580) hoppes over."""
    dest = RAW / "klass_131_changes_2020_2024.json"
    if not dest.exists():
        r = requests.get("https://data.ssb.no/api/klass/v1/classifications/131/changes",
                         params={"from": "2020-01-01", "to": "2024-01-02"}, headers={"Accept": "application/json"}, timeout=60)
        r.raise_for_status(); dest.write_text(r.text, encoding="utf-8")
    ch = pd.DataFrame(json.loads(dest.read_text(encoding="utf-8"))["codeChanges"])
    ch = ch[ch.oldCode != ch.newCode]
    splits = ch.groupby("oldCode").newCode.nunique()
    ch = ch[~ch.oldCode.isin(splits[splits > 1].index)]
    mp = dict(zip(ch.oldCode, ch.newCode))
    out = knr.where(aar >= 2024, knr.map(mp).fillna(knr))
    print(f"  omkodet {int(((out != knr)).sum())} rader med gamle kommunenummer")
    return out


def income():
    js = fetch_jsonstat(SSB_INCOME_TABLE,
                        {"Region": "*", "HusholdType": "0000",
                         "ContentsCode": "InntSkatt,SamletInntekt,AntallHushold", "Tid": "from(2020)"},
                        "06944_inntekt")
    lab = js["dimension"]["Region"]["category"]["label"]
    df = jsonstat_to_long(js)
    df = df[df.Region.str.fullmatch(r"\d{4}") & (df.Region != "9999")].copy()
    # 06944 er IKKE omkodet til gjeldende inndeling: 2020–2023 bruker gamle kommunenummer
    # (f.eks. 3001 Halden), 2024 nye (3101). Omkod med SSB Klass 131 (endringer 2020→2024).
    df["Region"] = recode_to_2024(df.Region, df.Tid.astype(int))
    df["kommune"] = df.Region.map(lab)
    wide = df.pivot_table(index=["Region", "kommune", "Tid"], columns="ContentsCode", values="verdi").reset_index()
    wide = wide.rename(columns={"Region": "knr", "Tid": "aar", "InntSkatt": "median_innt_etter_skatt",
                                "SamletInntekt": "median_samlet_innt", "AntallHushold": "n_hushold"})
    wide["aar"] = wide.aar.astype(int)
    wide = wide.dropna(subset=["median_innt_etter_skatt"])
    wide.to_parquet(PROC / "ssb_inntekt_kommune_aar.parquet", index=False)
    print(f"Inntekt: {wide.knr.nunique()} kommuner, år {wide.aar.min()}–{wide.aar.max()}, {len(wide)} rader")
    return wide


def dwellings():
    parts, lab = [], {}
    for yr in range(2021, 2027):   # ett kall per år: hele perioden i ett kall gir 400 (for mange celler)
        js = fetch_jsonstat(SSB_DWELLING_TABLE,
                            {"Region": "*", "BygnType": "*", "BruksAreal": "*", "ContentsCode": "Boliger5", "Tid": str(yr)},
                            f"06513_boliger_{yr}")
        lab.update(js["dimension"]["Region"]["category"]["label"])
        parts.append(jsonstat_to_long(js))
    df = pd.concat(parts)
    df = df[df.Region.str.fullmatch(r"\d{4}") & (df.Region != "9999")].copy()
    df["verdi"] = df.verdi.fillna(0)
    df = df[df.verdi > 0]                       # gamle/nye koder ligger side om side med nuller
    df["knr"] = recode_to_2024(df.Region, df.Tid.astype(int))
    df["kommune"] = df.knr.map(lab)
    tot = df.groupby(["knr", "kommune", "Tid", "BruksAreal"], as_index=False).verdi.sum()  # over bygningstype
    tot["mid"] = tot.BruksAreal.map(AREA_MID)
    known = tot.dropna(subset=["mid"]).copy()
    known["nm"] = known.verdi * known.mid
    known["stor"] = known.verdi * (known.mid >= 180)
    g = known.groupby(["knr", "kommune", "Tid"], as_index=False).agg(nm=("nm", "sum"), n=("verdi", "sum"), stor=("stor", "sum"))
    g["snitt_bruksareal_m2"] = g.nm / g.n
    g["andel_over_160m2"] = g.stor / g.n
    g = g.rename(columns={"Tid": "aar", "n": "n_boliger_kjent_areal"}).drop(columns=["nm", "stor"])
    g["aar"] = g.aar.astype(int)
    g.to_parquet(PROC / "ssb_bolig_kommune_aar.parquet", index=False)
    print(f"Boliger: {g.knr.nunique()} kommuner, år {g.aar.min()}–{g.aar.max()}, {len(g)} rader")
    return g


if __name__ == "__main__":
    income()
    dwellings()
