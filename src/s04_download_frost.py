"""Steg 4: Energigradtall per kommune og måned fra MET Frost.

Energigradtall (EGD) per døgn = max(17 − døgnmiddeltemperatur, 0); summeres per måned.
Krever FROST_CLIENT_ID (lastes fra .env via config).

Stasjonsvalg: kun stasjoner i fylkene som ligger i NO1/NO2/NO5. For hver kommune
velges stasjonen med flest døgnverdier i perioden. Kommuner uten egen stasjon
får fylkessnitt (flagges i steg 6). Ett API-kall per stasjon for hele perioden;
mellomlagres fortløpende slik at kjøringen kan gjenopptas.
"""
import sys
import time
import requests
import pandas as pd
from config import RAW, PROC, FROST_BASE, FROST_CLIENT_ID, START, END, GRADTALL_BASE_TEMP, SOUTH_COUNTIES

if not FROST_CLIENT_ID:
    sys.exit("FROST_CLIENT_ID mangler i .env")

S = requests.Session()
S.auth = (FROST_CLIENT_ID, "")
REF = f"{START}/{pd.Timestamp(END) + pd.Timedelta(days=1):%Y-%m-%d}"


def sources() -> pd.DataFrame:
    cache = RAW / "frost_sources.parquet"
    if cache.exists():
        df = pd.read_parquet(cache)
    else:
        r = S.get(f"{FROST_BASE}/sources/v0.jsonld",
                  params={"types": "SensorSystem", "country": "NO",
                          "fields": "id,name,municipality,municipalityId,county,countyId,validFrom,validTo"},
                  timeout=120)
        r.raise_for_status()
        df = pd.DataFrame(r.json()["data"])
        df.to_parquet(cache, index=False)
    df = df.dropna(subset=["municipalityId"]).copy()
    df["knr"] = df.municipalityId.astype(int).astype(str).str.zfill(4)
    df["fylke"] = df.knr.str[:2]
    return df[df.fylke.isin(SOUTH_COUNTIES)]


def daily_mean_temp(source_id: str) -> pd.DataFrame:
    for attempt in range(3):
        r = S.get(f"{FROST_BASE}/observations/v0.jsonld",
                  params={"sources": source_id, "referencetime": REF,
                          "elements": "mean(air_temperature P1D)",
                          "timeoffsets": "PT0H", "levels": "default"},
                  timeout=180)
        if r.status_code in (412, 404):      # ingen data for elementet
            return pd.DataFrame()
        if r.status_code == 429:
            time.sleep(10 * (attempt + 1)); continue
        r.raise_for_status()
        return pd.DataFrame([{"source": source_id, "dato": row["referenceTime"][:10],
                              "tmean": row["observations"][0]["value"]} for row in r.json().get("data", [])])
    return pd.DataFrame()


def main():
    src = sources()
    print(f"{len(src)} stasjoner i NO1/NO2/NO5-fylker")
    cache = RAW / "frost_daily_tmean.parquet"
    done_file = RAW / "frost_done_sources.txt"
    daily = pd.read_parquet(cache) if cache.exists() else pd.DataFrame(columns=["source", "dato", "tmean"])
    done = set(done_file.read_text().split()) if done_file.exists() else set()
    parts = [daily] if len(daily) else []
    todo = [s for s in src.id.unique() if s not in done]
    for i, sid in enumerate(todo, 1):
        d = daily_mean_temp(sid)
        if len(d):
            parts.append(d)
        done.add(sid)
        if i % 25 == 0 or i == len(todo):
            pd.concat(parts).to_parquet(cache, index=False)
            done_file.write_text("\n".join(sorted(done)))
            print(f"  {i}/{len(todo)} stasjoner hentet", flush=True)
    daily = pd.concat(parts) if parts else daily
    daily = daily.dropna(subset=["tmean"])
    daily["egd"] = (GRADTALL_BASE_TEMP - daily["tmean"]).clip(lower=0)
    daily["maned"] = daily["dato"].str[:7]

    # velg beste stasjon per kommune (flest døgnverdier)
    cnt = daily.groupby("source").size().rename("n").reset_index()
    src2 = src.merge(cnt, left_on="id", right_on="source", how="inner")
    best = src2.sort_values("n", ascending=False).drop_duplicates("knr")
    m = daily.merge(best[["id", "knr"]], left_on="source", right_on="id")
    egd_k = (m.groupby(["knr", "maned"], as_index=False)
               .agg(egd=("egd", "sum"), tmean=("tmean", "mean"), n_dager=("egd", "size")))
    egd_k = egd_k[egd_k.n_dager >= 20]          # krev nesten full måned
    egd_k["egd_kilde"] = "kommune"

    # fylkessnitt (snitt over alle stasjoner i fylket) for kommuner uten stasjon
    m2 = daily.merge(src2[["id", "fylke"]], left_on="source", right_on="id")
    egd_f = (m2.groupby(["fylke", "source", "maned"], as_index=False)
               .agg(egd=("egd", "sum"), tmean=("tmean", "mean"), n=("egd", "size")))
    egd_f = egd_f[egd_f.n >= 20].groupby(["fylke", "maned"], as_index=False).agg(egd=("egd", "mean"), tmean=("tmean", "mean"))
    egd_k.to_parquet(PROC / "egd_kommune_maned.parquet", index=False)
    egd_f.to_parquet(PROC / "egd_fylke_maned.parquet", index=False)
    print(f"EGD for {egd_k.knr.nunique()} kommuner, {egd_f.fylke.nunique()} fylker, "
          f"{egd_k.maned.min()}–{egd_k.maned.max()}")


if __name__ == "__main__":
    main()
