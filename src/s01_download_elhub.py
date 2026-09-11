"""Steg 1: Last ned Elhub-datasettene og aggreger til måned.

Filene er verifisert 05.09.2026: fire av fem er gzip bak .csv-URL, alle med ';'
og desimalkomma. Kommunefilen er 534 MB komprimert og leses i biter.

Utdata (data/processed):
  elhub_cons_muni_month.parquet   kommune × måned × gruppe: kwh, n_mp (snitt målepunkt/time)
  elhub_cons_mba_month.parquet    prisområde × måned × gruppe
  elhub_np_muni_daily.parquet     Norgespris-målere og totalt antall per kommune, gruppe, dag
  elhub_np_mba_daily.parquet      samme per prisområde
  elhub_np_status_hour.parquet    forbruk etter bestillingsstatus (rått, timesnivå)
"""
import sys
import requests
import pandas as pd
from config import RAW, PROC, ELHUB_DL, ELHUB_FILES, ELHUB_CSV_KW

CHUNK = 3_000_000


def raw_path(dataset: str, gz: bool):
    return RAW / (f"{dataset}.csv.gz" if gz else f"{dataset}.csv")


def download(dataset: str, gz: bool):
    dest = raw_path(dataset, gz)
    if dest.exists() and dest.stat().st_size > 1000:
        print(f"  finnes: {dest.name} ({dest.stat().st_size/1e6:.1f} MB)")
        return dest
    url = f"{ELHUB_DL}/{dataset}/{dataset}-all-no-0000-00-00.csv"
    print(f"  laster ned {url}")
    with requests.get(url, stream=True, timeout=600) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    return dest


def norm_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Elhub bruker STORE BOKSTAVER med Å/Ø/Æ; normaliser til ASCII."""
    return df.rename(columns={c: c.strip().upper().replace("Å", "A").replace("Ø", "O").replace("Æ", "AE")
                              for c in df.columns})


def read_elhub(path, gz: bool, **kw):
    return pd.read_csv(path, compression="gzip" if gz else None, **ELHUB_CSV_KW, **kw)


HOURLY_DTYPES = {"STARTTID": "string", "SLUTTID": "string", "KOMMUNE": "category", "KOMMUNENUMMER": "int32",
                 "FORBRUKSGRUPPE": "category", "VOLUM_KWH": "float64", "ANTALL_MÅLEPUNKT": "int64", "PRISOMRÅDE": "category"}


def aggregate_hourly_to_month(path, gz, key_cols, vol_col="VOLUM_KWH"):
    """Les stor times-CSV i biter og summer volum til måned (Oslo-tid)."""
    parts = []
    for i, ch in enumerate(read_elhub(path, gz, chunksize=CHUNK, dtype=HOURLY_DTYPES, usecols=lambda c: c != "SLUTTID")):
        ch = norm_cols(ch)
        # STARTTID er lokal tid (Europe/Oslo) med offset, f.eks. 2022-02-01T00:00:00+01:00 → måned = de 7 første tegnene
        ch["maned"] = ch["STARTTID"].str[:7]
        g = (ch.groupby(key_cols + ["maned"], as_index=False)
               .agg(kwh=(vol_col, "sum"),
                    n_mp_sum=("ANTALL_MALEPUNKT", "sum"),
                    n_rows=(vol_col, "size")))
        parts.append(g)
        print(f"    bit {i+1}: {len(ch):,} rader, t.o.m. {ch['maned'].max()}", flush=True)
    df = (pd.concat(parts).groupby(key_cols + ["maned"], as_index=False)
            .agg(kwh=("kwh", "sum"), n_mp_sum=("n_mp_sum", "sum"), n_rows=("n_rows", "sum")))
    df["n_mp"] = df["n_mp_sum"] / df["n_rows"]   # snitt antall målepunkt per time i måneden
    return df.drop(columns=["n_mp_sum"])


def main(only=None):
    todo = [k for k in ELHUB_FILES if only is None or k in only]

    if "cons_muni" in todo:
        print("Forbruk per kommune")
        ds, gz = ELHUB_FILES["cons_muni"]
        df = aggregate_hourly_to_month(download(ds, gz), gz, ["KOMMUNENUMMER", "KOMMUNE", "FORBRUKSGRUPPE"])
        df.to_parquet(PROC / "elhub_cons_muni_month.parquet", index=False)
        print(f"  {len(df)} rader, {df.KOMMUNENUMMER.nunique()} kommuner, {df.maned.min()}–{df.maned.max()}")

    if "cons_mba" in todo:
        print("Forbruk per prisområde")
        ds, gz = ELHUB_FILES["cons_mba"]
        df = aggregate_hourly_to_month(download(ds, gz), gz, ["PRISOMRADE", "FORBRUKSGRUPPE"])
        df.to_parquet(PROC / "elhub_cons_mba_month.parquet", index=False)
        print(f"  {len(df)} rader, {df.maned.min()}–{df.maned.max()}")

    for key, out in (("np_muni", "elhub_np_muni_daily.parquet"), ("np_mba", "elhub_np_mba_daily.parquet")):
        if key in todo:
            print(f"Norgespris-målere ({key})")
            ds, gz = ELHUB_FILES[key]
            df = norm_cols(read_elhub(download(ds, gz), gz))
            df.to_parquet(PROC / out, index=False)
            print(f"  {len(df)} rader, {df.DATO.min()}–{df.DATO.max()}, grupper {sorted(df.FORBRUKSGRUPPE.unique())}")

    if "np_status" in todo:
        print("Forbruk etter Norgespris-bestillingsstatus")
        ds, gz = ELHUB_FILES["np_status"]
        df = norm_cols(read_elhub(download(ds, gz), gz))
        df.to_parquet(PROC / "elhub_np_status_hour.parquet", index=False)
        print(f"  {len(df)} rader; status {sorted(df.NORGESPRIS_BESTILLING_STATUS.unique())}; "
              f"grupper {sorted(df.ESTIMERT_ARLIG_FORBRUK_GRUPPE.unique())}")


if __name__ == "__main__":
    main(sys.argv[1:] or None)
