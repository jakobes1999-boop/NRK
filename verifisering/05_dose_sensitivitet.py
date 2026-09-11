"""Dose-, seleksjons-, spillover- og prisestimand-sensitiviteter."""
from __future__ import annotations

import numpy as np
import pandas as pd

from felles import PROC, VERIF, forbered_did, json_skriv, prosent_fra_log

BETA_D7 = 0.029880493831513134
BETA_TIDLIG = 0.03094415044645852
BETA_SENT = 0.028610176711826203


def dose_tabell():
    d = pd.read_parquet(PROC / "elhub_np_mba_daily.parquet")
    h = d.loc[
        (d["FORBRUKSGRUPPE"] == "Husholdning")
        & d["PRISOMRADE"].isin(["NO1", "NO2", "NO5"])
    ].copy()
    h["dag"] = h["DATO"].str[:10]
    h["maned"] = h["dag"].str[:7]
    rader = []
    for pa, gruppe in h.groupby("PRISOMRADE"):
        g = gruppe.set_index("dag").sort_index()
        n0 = g.loc["2025-10-01", "ANTALL_NORGESPRIS"]
        n1 = g.loc["2026-04-30", "ANTALL_NORGESPRIS"]
        g["dose"] = ((g["ANTALL_NORGESPRIS"] - n0) / (n1 - n0)).clip(0, 1)
        mm = (
            g.loc["2025-10-01":"2026-04-30"]
            .groupby("maned")["dose"].mean()
        )
        rader.extend(
            {"pa": pa, "maned": maned, "dose": float(verdi)}
            for maned, verdi in mm.items()
        )
    return pd.DataFrame(rader)


def hoved():
    dose = dose_tabell()
    assert len(dose) == 21
    dose.to_csv(VERIF / "dose_per_maned.csv", index=False)

    m = forbered_did().merge(
        dose, on=["pa", "maned"], how="left", validate="many_to_one"
    )
    m["dose"] = m["dose"].fillna(0.0)
    sent = m.loc[(m["sent"] == 1) & (m["post"] == 1)]
    best = m.loc[(m["bestilt"] == 1) & (m["post"] == 1)]
    alle_post = m.loc[m["post"] == 1]

    dose_enkel = float(dose["dose"].mean())
    dose_nmp = float(np.average(sent["dose"], weights=sent["n_mp"]))
    dose_kwh = float(np.average(sent["dose"], weights=sent["kwh"]))
    maaned_nmp = (
        sent.groupby("maned")
        .apply(lambda x: np.average(x["dose"], weights=x["n_mp"]),
               include_groups=False)
        .rename("dose_n_mp")
        .reset_index()
    )
    maaned_nmp.to_csv(VERIF / "dose_maaned_vektet.csv", index=False)

    forbruksvekt = (
        best.groupby("status")["kwh"].sum() / best["kwh"].sum()
    )
    andel_bestilt = float(
        alle_post.loc[alle_post["bestilt"] == 1, "kwh"].sum()
        / alle_post["kwh"].sum()
    )
    beta_sent_full = BETA_SENT / dose_nmp
    effekt_full_best = float(
        forbruksvekt["Bestilt tidlig"] * prosent_fra_log(BETA_TIDLIG)
        + forbruksvekt["Bestilt sent"] * prosent_fra_log(beta_sent_full)
    )

    seleksjon = []
    for sjokk_pst in [0.0, 1.0, 2.0, 3.0, prosent_fra_log(BETA_D7), 4.0]:
        beta_kausal = BETA_D7 - np.log1p(sjokk_pst / 100.0)
        seleksjon.append({
            "seleksjonssjokk_prosent": sjokk_pst,
            "gjenstaende_beta_log": beta_kausal,
            "gjenstaende_effekt_prosent": prosent_fra_log(beta_kausal),
        })
    seleksjon_df = pd.DataFrame(seleksjon)
    seleksjon_df.to_csv(VERIF / "seleksjon_sensitivitet.csv", index=False)

    kontrast_pst = prosent_fra_log(BETA_D7)
    sutva = []
    for effekt_kontroll in [-3.0, -1.0, 0.0, 1.0, 3.0]:
        sutva.append({
            "effekt_kontroll_prosentpoeng": effekt_kontroll,
            "direkte_effekt_bestiller_omtrent":
                kontrast_pst + effekt_kontroll,
            "samlet_effekt_omtrent":
                andel_bestilt * kontrast_pst + effekt_kontroll,
        })
    sutva_df = pd.DataFrame(sutva)
    sutva_df.to_csv(VERIF / "sutva_sensitivitet.csv", index=False)

    pris = pd.read_parquet(
        PROC / "effektiv_pris_pa_maned.parquet"
    ).rename(columns={"prisomrade": "pa"})
    prisgrunnlag = best.merge(
        pris, on=["pa", "maned"], validate="many_to_one"
    )
    prisgrunnlag["gap_stotte"] = np.log(
        prisgrunnlag["p_eff"] / prisgrunnlag["p_np"]
    )
    prisgrunnlag["gap_spot"] = np.log(
        prisgrunnlag["spot_ore_kwh"] / prisgrunnlag["p_np"]
    )
    gap_stotte = float(np.average(
        prisgrunnlag["gap_stotte"], weights=prisgrunnlag["n_mp"]
    ))
    gap_spot = float(np.average(
        prisgrunnlag["gap_spot"], weights=prisgrunnlag["n_mp"]
    ))
    elastisitet_mekanisk = -BETA_D7 / gap_stotte
    beta_mot_spot_mekanisk = -elastisitet_mekanisk * gap_spot

    behandlet_observert_andel = (
        andel_bestilt * (1.0 - np.exp(-BETA_D7))
    )
    samlet_eksakt_mot_kontrafaktisk = (
        100.0 * behandlet_observert_andel
        / (1.0 - behandlet_observert_andel)
    )

    resultater = {
        "dose_enkelt_snitt_21_omraademaaneder": dose_enkel,
        "dose_sent_n_mp_vektet": dose_nmp,
        "dose_sent_kwh_vektet": dose_kwh,
        "sent_observert_prosent": prosent_fra_log(BETA_SENT),
        "sent_full_dose_beta_log_mekanisk": beta_sent_full,
        "sent_full_dose_prosent_mekanisk": prosent_fra_log(beta_sent_full),
        "forbruksvekt_tidlig_blant_bestillere":
            float(forbruksvekt["Bestilt tidlig"]),
        "forbruksvekt_sent_blant_bestillere":
            float(forbruksvekt["Bestilt sent"]),
        "bestillereffekt_full_dose_prosent_mekanisk": effekt_full_best,
        "andel_bestilt_av_postforbruk": andel_bestilt,
        "aggregert_full_dose_prosent_mekanisk":
            effekt_full_best * andel_bestilt,
        "aggregert_prosjektapproksimasjon_prosent":
            kontrast_pst * andel_bestilt,
        "aggregert_eksakt_prosent_mot_kontrafaktisk":
            samlet_eksakt_mot_kontrafaktisk,
        "prisgap_stotte_log_n_mp_vektet": gap_stotte,
        "prisgap_spot_log_n_mp_vektet": gap_spot,
        "mekanisk_elastisitet": elastisitet_mekanisk,
        "effekt_mot_spot_beta_log_mekanisk": beta_mot_spot_mekanisk,
        "effekt_mot_spot_prosent_mekanisk":
            prosent_fra_log(beta_mot_spot_mekanisk),
    }
    json_skriv(VERIF / "dose_sensitivitet.json", resultater)
    print(dose.to_string(index=False))
    print()
    print(resultater)
    print()
    print(seleksjon_df.to_string(index=False))
    print()
    print(sutva_df.to_string(index=False))


if __name__ == "__main__":
    hoved()
