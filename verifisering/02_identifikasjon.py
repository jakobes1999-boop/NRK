"""Rang-, FWL-, vekt- og klusterkontroller for D7."""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import patsy
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.tools.sm_exceptions import SingularMatrixWarning

from felles import (
    DID_FORMEL_BASE, VERIF, fit_wls_cluster, forbered_did, json_skriv,
    prosent_fra_log,
)

warnings.filterwarnings("ignore", category=SingularMatrixWarning)
FULL = DID_FORMEL_BASE + " + bestilt_post"


def matrise(formel, data):
    y, x = patsy.dmatrices(formel, data, return_type="dataframe")
    return y.iloc[:, 0].to_numpy(), x


def rank_rad(navn, formel, data):
    _, x = matrise(formel, data)
    rang = int(np.linalg.matrix_rank(x.to_numpy()))
    return {
        "navn": navn, "rader": len(x), "kolonner": x.shape[1],
        "rang": rang, "nullitet": x.shape[1] - rang,
        "residual_df": len(x) - rang,
    }


def residualiser(a, z):
    return a - z @ np.linalg.lstsq(z, a, rcond=None)[0]


def hoved():
    m = forbered_did()
    former = [
        ("basis", "log_y ~ C(g) + C(pa_t_eac)"),
        ("basis_og_profil", DID_FORMEL_BASE),
        ("full_D7", FULL),
    ]
    rang = [rank_rad(n, f, m) for n, f in former]

    pre = m.loc[m["maned"] < "2025-10"].copy()
    pre["bestilt_post"] = (
        pre["bestilt"] * (pre["maned"] >= "2024-10").astype(int)
    )
    rang += [
        rank_rad("placebo_" + n, f, pre)
        for n, f in former
    ]

    y, xdf = matrise(FULL, m)
    j = xdf.columns.get_loc("bestilt_post")
    x = xdf.iloc[:, j].to_numpy()
    z = np.delete(xdf.to_numpy(), j, axis=1)
    sw = np.sqrt(m["n_mp"].to_numpy())
    yw, xw, zw = y * sw, x * sw, z * sw[:, None]
    xt = residualiser(xw, zw)
    yt = residualiser(yw, zw)
    nevner = float(xt @ xt)
    beta_fwl = float((xt @ yt) / nevner)
    d7 = fit_wls_cluster(FULL, m, use_t=True)
    beta_modell = float(d7.params["bestilt_post"])
    assert abs(beta_fwl - beta_modell) < 1e-10

    bidrag = pd.DataFrame({
        "maned": m["maned"], "post": m["post"],
        "informasjonsvekt": xt * xt / nevner,
        "beta_bidrag": xt * yt / nevner,
        "x_tilde_vektet": xt, "y_tilde_vektet": yt,
    })
    manedsbidrag = bidrag.groupby(
        ["maned", "post"], as_index=False
    ).agg({
        "informasjonsvekt": "sum", "beta_bidrag": "sum",
        "x_tilde_vektet": "sum", "y_tilde_vektet": "sum",
    })
    manedsbidrag.to_csv(VERIF / "fwl_manedsbidrag.csv", index=False)

    _, basis = matrise(former[0][1], m)
    _, med_profil = matrise(former[1][1], m)
    p = med_profil.iloc[:, basis.shape[1]:].to_numpy()
    bw = basis.to_numpy() * sw[:, None]
    pw = p * sw[:, None]
    pr = residualiser(pw, bw)
    u, s, _ = np.linalg.svd(pr, full_matrices=False)
    toleranse = np.finfo(float).eps * max(pr.shape) * s[0]
    profilrang = int((s > toleranse).sum())
    q = u[:, :profilrang]
    profil_leverage = (q * q).sum(axis=1)

    # Gjennomsiktig spesialtilfelle: status-minus-kontroll, fratrukket
    # samme status/område/klasse/kalendermåneds snitt i de to førårene.
    idx = ["pa", "eac", "maned"]
    kontroll = (
        m.loc[m["status"] == "Ikke bestilt", idx + ["log_y", "n_mp"]]
        .set_index(idx)
        .rename(columns={"log_y": "y_kontroll", "n_mp": "w_kontroll"})
    )
    par = (
        m.loc[m["bestilt"] == 1, idx + ["status", "log_y", "n_mp"]]
        .set_index(idx)
        .join(kontroll)
        .reset_index()
    )
    par["mnd"] = par["maned"].str[5:]
    par["gap"] = par["log_y"] - par["y_kontroll"]
    par["post"] = (par["maned"] >= "2025-10").astype(int)
    grunnlag = (
        par.loc[par["post"] == 0]
        .groupby(["pa", "eac", "status", "mnd"], as_index=False)
        .agg(gap_for=("gap", "mean"))
    )
    etter = par.loc[par["post"] == 1].merge(
        grunnlag, on=["pa", "eac", "status", "mnd"], validate="many_to_one"
    )
    etter["avvik_fra_eget_for"] = etter["gap"] - etter["gap_for"]
    etter["harmonisk_vekt"] = (
        etter["n_mp"] * etter["w_kontroll"]
        / (etter["n_mp"] + etter["w_kontroll"])
    )
    per_maned = etter.groupby("maned", as_index=False).apply(
        lambda d: pd.Series({
            "enkelt_snitt": d["avvik_fra_eget_for"].mean(),
            "n_mp_vektet": np.average(
                d["avvik_fra_eget_for"], weights=d["n_mp"]
            ),
            "harmonisk_vektet": np.average(
                d["avvik_fra_eget_for"], weights=d["harmonisk_vekt"]
            ),
            "antall_statuskontraster": len(d),
        }),
        include_groups=False,
    ).reset_index(drop=True)
    per_maned.to_csv(VERIF / "manuell_kontrast.csv", index=False)

    manuelt = {
        "enkelt_snitt": float(etter["avvik_fra_eget_for"].mean()),
        "n_mp_vektet": float(np.average(
            etter["avvik_fra_eget_for"], weights=etter["n_mp"]
        )),
        "harmonisk_vektet": float(np.average(
            etter["avvik_fra_eget_for"], weights=etter["harmonisk_vekt"]
        )),
    }

    modeller = []
    spesifikasjoner = [
        ("WLS_g", "wls", "g"),
        ("OLS_g", "ols", "g"),
        ("WLS_omraade_klasse", "wls", "ae"),
        ("WLS_omraade", "wls", "pa"),
    ]
    for navn, metode, cluster in spesifikasjoner:
        mod = (
            smf.wls(FULL, data=m, weights=m["n_mp"])
            if metode == "wls" else smf.ols(FULL, data=m)
        )
        res = mod.fit(
            cov_type="cluster",
            cov_kwds={"groups": m[cluster]},
            use_t=True,
        )
        g = int(m[cluster].nunique())
        b = float(res.params["bestilt_post"])
        se = float(res.bse["bestilt_post"])
        krit = float(stats.t.ppf(0.975, g - 1))
        modeller.append({
            "modell": navn, "koef": b, "se": se,
            "prosent": prosent_fra_log(b),
            "p_t": float(res.pvalues["bestilt_post"]),
            "klustre": g,
            "ki95_log_lav": b - krit * se,
            "ki95_log_hoy": b + krit * se,
            "ki95_prosent_lav": prosent_fra_log(b - krit * se),
            "ki95_prosent_hoy": prosent_fra_log(b + krit * se),
        })
    modtab = pd.DataFrame(modeller)
    modtab.to_csv(VERIF / "vekting_og_klustring.csv", index=False)

    profil_telling = (
        pre.groupby(["eac", "mnd"])["bestilt"].sum()
    )
    resultater = {
        "rang": rang,
        "rangtap_basis": rang[0]["nullitet"],
        "profilkolonner_rå": int(p.shape[1]),
        "profilrang_inkrementell": profilrang,
        "profilredundanser_utover_basis": int(p.shape[1] - profilrang),
        "profil_leverage_for": float(profil_leverage[m["post"] == 0].sum()),
        "profil_leverage_etter": float(
            profil_leverage[m["post"] == 1].sum()
        ),
        "profil_leverage_etter_andel": float(
            profil_leverage[m["post"] == 1].sum() / profil_leverage.sum()
        ),
        "fwl_beta": beta_fwl,
        "modell_beta": beta_modell,
        "fwl_avvik": beta_fwl - beta_modell,
        "fwl_nevner": nevner,
        "fwl_restvariasjon_andel": float(nevner / (xw @ xw)),
        "fwl_informasjonsvekt_for": float(
            bidrag.loc[bidrag["post"] == 0, "informasjonsvekt"].sum()
        ),
        "fwl_informasjonsvekt_etter": float(
            bidrag.loc[bidrag["post"] == 1, "informasjonsvekt"].sum()
        ),
        "manuelle_kontraster": manuelt,
        "enkelt_snitt_minus_OLS": (
            manuelt["enkelt_snitt"]
            - modtab.loc[modtab["modell"] == "OLS_g", "koef"].iloc[0]
        ),
        "enkelt_snitt_minus_WLS": manuelt["enkelt_snitt"] - beta_modell,
        "celler_pa_t_eac": int(m["pa_t_eac"].nunique()),
        "rader_per_celle_min": int(m.groupby("pa_t_eac").size().min()),
        "rader_per_celle_maks": int(m.groupby("pa_t_eac").size().max()),
        "forprofil_observasjoner_per_eac_mnd_min": int(
            profil_telling.min()
        ),
        "forprofil_observasjoner_per_eac_mnd_maks": int(
            profil_telling.max()
        ),
        "n_mp_min": float(m["n_mp"].min()),
        "n_mp_maks": float(m["n_mp"].max()),
        "n_mp_forhold_maks_min": float(m["n_mp"].max() / m["n_mp"].min()),
        "n_mp_cv": float(m["n_mp"].std() / m["n_mp"].mean()),
    }
    json_skriv(VERIF / "resultater_identifikasjon.json", resultater)
    pd.DataFrame(rang).to_csv(VERIF / "rang_d7.csv", index=False)

    print(pd.DataFrame(rang).to_string(index=False))
    print()
    print("FWL:", beta_fwl, "modell:", beta_modell,
          "avvik:", beta_fwl - beta_modell)
    print("Manuelle kontraster:", manuelt)
    print()
    print(modtab.to_string(index=False))
    print()
    print(resultater)


if __name__ == "__main__":
    hoved()
