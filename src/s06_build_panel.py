"""Steg 6: Bygg kommune × måned-panelet.

Y   : forbruk i Elhub-gruppen «Privat» (husholdning + hytte) i kWh, og per målepunkt.
X   : energigradtall (EGD), månedlig spotpris i prisområdet, Norgespris
      (post-dummy og andel målere), medianinntekt (årlig, siste år framskrives),
      gjennomsnittlig bruksareal (årlig).
Utvalg: NO1, NO2, NO5 (som NRK).

Andel Norgespris beregnes fra Elhubs egen målerfil: ANTALL_NORGESPRIS / ANTALL,
summert over Husholdning + Hytter (samsvarer med «Privat»). Husholdning alene
lagres som np_andel_hh.
"""
import pandas as pd
import numpy as np
from config import PROC, PRICE_AREAS, NORGESPRIS_START
from geo import kommune_to_pa, kommune_to_fylke


def load_cons():
    c = pd.read_parquet(PROC / "elhub_cons_muni_month.parquet")
    c["knr"] = c["KOMMUNENUMMER"].astype(int).astype(str).str.zfill(4)
    c = c[c.knr != "0000"]
    grp = c["FORBRUKSGRUPPE"].str.lower()
    hh = c[grp.str.contains("privat|hushold")]
    if hh.empty:
        raise SystemExit(f"Fant ikke husholdningsgruppe. Grupper: {c.FORBRUKSGRUPPE.unique()}")
    hh = hh.groupby(["knr", "KOMMUNE", "maned"], as_index=False).agg(kwh=("kwh", "sum"), n_mp=("n_mp", "sum"))
    return hh.rename(columns={"KOMMUNE": "kommune"})


def load_norgespris():
    np_ = pd.read_parquet(PROC / "elhub_np_muni_daily.parquet")
    np_["knr"] = np_["KOMMUNENUMMER"].astype(int).astype(str).str.zfill(4)
    np_["maned"] = np_["DATO"].astype(str).str[:7]
    np_["hh"] = np_["FORBRUKSGRUPPE"].str.lower().str.contains("hushold")
    # dagsnitt per kommune × måned × gruppe, deretter sum over grupper
    d = np_.groupby(["knr", "maned", "hh"], as_index=False).agg(np_n=("ANTALL_NORGESPRIS", "mean"), tot=("ANTALL", "mean"))
    alle = d.groupby(["knr", "maned"], as_index=False).agg(np_malere=("np_n", "sum"), np_tot=("tot", "sum"))
    hh = d[d.hh].rename(columns={"np_n": "np_malere_hh", "tot": "np_tot_hh"}).drop(columns="hh")
    return alle.merge(hh, how="left")


def yearly_forward_fill(df, key, value_cols, months):
    """Årlige variabler → kommune × måned, siste tilgjengelige år framskrives."""
    yrs = sorted({int(m[:4]) for m in months})
    out = []
    for knr, g in df.groupby(key):
        g = g.set_index("aar").sort_index()
        for yr in yrs:
            avail = g.index[g.index <= yr]
            if len(avail) == 0:
                continue
            row = g.loc[avail.max(), value_cols].to_dict()
            row.update({key: knr, "aar": yr, "aar_kilde": int(avail.max())})
            out.append(row)
    return pd.DataFrame(out)


def main(fylkeregel: bool = False):
    """fylkeregel=True: robusthetsvariant uten NVE-overstyring → panel_fylkeregel.parquet"""
    hh = load_cons()
    hh["aar"] = hh.maned.str[:4].astype(int)
    months = sorted(hh.maned.unique())
    kk = hh.drop_duplicates("knr")
    pa = kommune_to_pa(kk.knr, kk.kommune, use_nve=not fylkeregel).set_index("knr")
    hh["prisomrade"] = hh.knr.map(pa.prisomrade)
    hh["pa_kilde"] = hh.knr.map(pa.pa_kilde)
    hh["fylke"] = kommune_to_fylke(hh.knr)
    n0 = hh.knr.nunique()
    hh = hh[hh.prisomrade.isin(PRICE_AREAS)]
    print(f"Kommuner totalt {n0}, i NO1/NO2/NO5: {hh.knr.nunique()}; pa_kilde: {hh.drop_duplicates('knr').pa_kilde.value_counts().to_dict()}")

    spot = pd.read_parquet(PROC / "spot_month.parquet").rename(columns={"area": "prisomrade"})
    hh = hh.merge(spot[["prisomrade", "maned", "spot_ore_kwh", "spot_p90"]], how="left")

    p_egd = PROC / "egd_kommune_maned.parquet"
    if p_egd.exists():
        egd = pd.read_parquet(p_egd)
        hh = hh.merge(egd[["knr", "maned", "egd", "tmean"]], how="left")
        egf = pd.read_parquet(PROC / "egd_fylke_maned.parquet").rename(columns={"egd": "egd_f", "tmean": "tmean_f"})
        hh = hh.merge(egf[["fylke", "maned", "egd_f", "tmean_f"]], how="left")
        hh["egd_kilde"] = np.where(hh.egd.notna(), "kommune", "fylke")
        hh["egd"] = hh.egd.fillna(hh.egd_f); hh["tmean"] = hh.tmean.fillna(hh.tmean_f)
        hh = hh.drop(columns=["egd_f", "tmean_f"])
        print("EGD-kilde:", hh.egd_kilde.value_counts().to_dict())
    else:
        print("ADVARSEL: ingen gradtall – modellen kjøres med måneds-FE som værproxy")

    inc = pd.read_parquet(PROC / "ssb_inntekt_kommune_aar.parquet")
    inc_m = yearly_forward_fill(inc, "knr", ["median_innt_etter_skatt", "n_hushold"], months)
    hh = hh.merge(inc_m.rename(columns={"aar_kilde": "innt_aar"}), how="left")

    bol = pd.read_parquet(PROC / "ssb_bolig_kommune_aar.parquet")
    bol_m = yearly_forward_fill(bol, "knr", ["snitt_bruksareal_m2", "andel_over_160m2"], months)
    hh = hh.merge(bol_m.drop(columns="aar_kilde"), how="left")

    npm = load_norgespris()
    hh = hh.merge(npm, how="left")
    for c in ["np_malere", "np_tot", "np_malere_hh", "np_tot_hh"]:
        hh[c] = hh[c].fillna(0)
    hh["np_andel"] = np.where(hh.np_tot > 0, hh.np_malere / hh.np_tot, 0.0)
    hh["np_andel_hh"] = np.where(hh.np_tot_hh > 0, hh.np_malere_hh / hh.np_tot_hh, 0.0)
    hh["post_np"] = (hh.maned >= NORGESPRIS_START[:7]).astype(int)

    hh["kwh_per_mp"] = hh.kwh / hh.n_mp
    hh["log_kwh"] = np.log(hh.kwh)
    hh["log_kwh_mp"] = np.log(hh.kwh_per_mp)
    hh["log_innt"] = np.log(hh.median_innt_etter_skatt)
    hh["mnd"] = hh.maned.str[5:].astype(int)

    hh.to_parquet(PROC / ("panel_fylkeregel.parquet" if fylkeregel else "panel.parquet"), index=False)
    print(hh.describe().T[["count", "mean", "min", "max"]].to_string())
    print(f"\nPanel: {hh.knr.nunique()} kommuner × {hh.maned.nunique()} måneder = {len(hh)} rader, {hh.maned.min()}–{hh.maned.max()}")
    print("Manglende:", hh.isna().sum()[hh.isna().sum() > 0].to_dict())
    post = hh[hh.post_np == 1]
    print("Andel Norgespris (Privat) per område, snitt over post-måneder:",
          post.groupby("prisomrade").apply(lambda x: np.average(x.np_andel, weights=x.np_tot)).round(3).to_dict())


if __name__ == "__main__":
    import sys
    main(fylkeregel="--fylke" in sys.argv)
