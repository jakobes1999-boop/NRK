"""Strengere førtest, E5-placebo og leave-one-cluster-out."""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import patsy
import scipy.linalg as sla
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.tools.sm_exceptions import SingularMatrixWarning

from felles import DID_FORMEL_BASE, PROC, VERIF, forbered_did, json_skriv

warnings.filterwarnings("ignore", category=SingularMatrixWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
FULL = DID_FORMEL_BASE + " + bestilt_post"


def fit(formel, data):
    return smf.wls(formel, data=data, weights=data["n_mp"]).fit(
        cov_type="cluster", cov_kwds={"groups": data["g"]}, use_t=True
    )


def fullrang_design(formel, data, behold):
    y, x = patsy.dmatrices(formel, data, return_type="dataframe")
    navn = list(x.columns)
    k0 = navn.index(behold)
    rest = [j for j in range(x.shape[1]) if j != k0]
    r = x.iloc[:, rest].to_numpy()
    norm = np.linalg.norm(r, axis=0)
    norm[norm == 0] = 1.0
    _, qr_r, pivot = sla.qr(r / norm, mode="economic", pivoting=True)
    diag = np.abs(np.diag(qr_r))
    rang = int((diag > 1e-10 * max(diag.max(), 1.0)).sum())
    valgte = sorted(rest[j] for j in pivot[:rang]) + [k0]
    return (
        y.iloc[:, 0].to_numpy(),
        x.iloc[:, valgte].to_numpy(),
        valgte.index(k0),
    )


def loco_lineaer(formel, data, modellnavn, full_koef):
    y, x, k = fullrang_design(formel, data, "bestilt_post")
    rader = []
    for utelatt in sorted(data["g"].unique()):
        maske = (data["g"].to_numpy() != utelatt)
        w = data.loc[maske, "n_mp"].to_numpy()
        xt = x[maske] * np.sqrt(w)[:, None]
        yt = y[maske] * np.sqrt(w)
        a = xt.T @ xt
        lam, v = np.linalg.eigh(a)
        bruk = lam > 1e-10 * max(lam.max(), 1.0)
        rang = int(bruk.sum())
        ai = (v[:, bruk] / lam[bruk]) @ v[:, bruk].T
        beta = ai @ (xt.T @ yt)
        u = yt - xt @ beta
        h = xt @ ai[:, k]
        grupper = data.loc[maske, "g"].to_numpy()
        _, gi = np.unique(grupper, return_inverse=True)
        g = int(gi.max() + 1)
        score = np.bincount(gi, weights=h * u, minlength=g)
        korr = g / (g - 1) * (len(yt) - 1) / (len(yt) - rang)
        se = float(np.sqrt(korr * (score @ score)))
        b = float(beta[k])
        p = float(2 * stats.t.sf(abs(b / se), g - 1))
        rader.append({
            "modell": modellnavn, "utelatt_g": utelatt,
            "utelatt_status": utelatt.split("|")[1],
            "koef": b, "se": se, "p_t": p,
            "full_koef": full_koef,
            "avvik_fra_full": b - full_koef,
            "n": len(yt), "klustre": g, "matriserang": rang,
        })
    return rader


def bygg_dose():
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
        mm = g.loc["2025-10-01":"2026-04-30"].groupby("maned")["dose"].mean()
        rader.extend(
            {"pa": pa, "maned": maned, "dose": float(verdi)}
            for maned, verdi in mm.items()
        )
    return pd.DataFrame(rader)


def hoved():
    m = forbered_did()
    pre = m.loc[m["maned"] < "2025-10"].copy()

    andre_aar = sorted(
        pre.loc[pre["maned"] >= "2024-10", "maned"].unique()
    )
    event_termer = []
    for maned in andre_aar:
        term = "evt_" + maned.replace("-", "")
        pre[term] = pre["bestilt"] * (pre["maned"] == maned).astype(int)
        event_termer.append(term)
    event_formel = DID_FORMEL_BASE + " + " + " + ".join(event_termer)
    event = fit(event_formel, pre)
    restriksjon = np.zeros((len(event_termer), len(event.params)))
    for i, term in enumerate(event_termer):
        restriksjon[i, event.params.index.get_loc(term)] = 1.0
    wald = event.wald_test(restriksjon, use_f=True, scalar=True)
    krit = stats.t.ppf(0.975, pre["g"].nunique() - 1)
    event_rader = []
    for maned, term in zip(andre_aar, event_termer):
        b, se = float(event.params[term]), float(event.bse[term])
        event_rader.append({
            "maned": maned, "term": term, "koef": b, "se": se,
            "prosent": 100.0 * np.expm1(b),
            "p_t26": float(event.pvalues[term]),
            "ki95_log_lav": b - krit * se,
            "ki95_log_hoy": b + krit * se,
        })
    event_df = pd.DataFrame(event_rader)
    event_df.to_csv(VERIF / "pre_event_study.csv", index=False)

    # E5: syvmåneders dose/placebo, flyttet nøyaktig ett år tilbake.
    dose = bygg_dose()
    dose["maned"] = (
        (dose["maned"].str[:4].astype(int) - 1).astype(str)
        + dose["maned"].str[4:]
    )
    e5 = pre.merge(
        dose, on=["pa", "maned"], how="left", validate="many_to_one"
    )
    e5["dose"] = e5["dose"].fillna(0.0)
    e5["post_pl"] = e5["maned"].between("2024-10", "2025-04").astype(int)
    e5["tidlig_post"] = e5["tidlig"] * e5["post_pl"]
    e5["sent_post"] = e5["sent"] * e5["post_pl"]
    e5["sent_dose"] = e5["sent"] * e5["dose"]
    fe_f = DID_FORMEL_BASE
    fe_k = (
        "log_y ~ C(g) + C(pa_t_eac) + "
        "tidlig:C(mnd):C(eac) + sent:C(mnd):C(eac)"
    )
    e5_rader = []
    for navn, formel in [
        ("E5_felles", fe_f),
        ("E5_sesong_per_kohort", fe_k),
    ]:
        res = fit(
            formel + " + tidlig_post + sent_post + sent_dose", e5
        )
        for term in ["tidlig_post", "sent_post", "sent_dose"]:
            e5_rader.append({
                "modell": navn, "term": term,
                "koef": float(res.params[term]),
                "se": float(res.bse[term]),
                "p_t26": float(res.pvalues[term]),
                "prosent": float(100.0 * np.expm1(res.params[term])),
            })
    e5_df = pd.DataFrame(e5_rader)
    e5_df.to_csv(VERIF / "e5_placebo.csv", index=False)

    # D7 og gjennomsnittsplacebo med ett g-kluster utelatt om gangen.
    pre_loco = pre.copy()
    pre_loco["bestilt_post"] = (
        pre_loco["bestilt"]
        * (pre_loco["maned"] >= "2024-10").astype(int)
    )
    full_d7 = fit(FULL, m)
    full_pl = fit(FULL, pre_loco)
    loco = loco_lineaer(
        FULL, m, "D7", float(full_d7.params["bestilt_post"])
    )
    loco += loco_lineaer(
        FULL, pre_loco, "D7_placebo",
        float(full_pl.params["bestilt_post"]),
    )
    loco_df = pd.DataFrame(loco)
    loco_df.to_csv(VERIF / "loco_d7.csv", index=False)

    oppsummering = {
        "event_antall_termer": len(event_termer),
        "event_rang": int(np.linalg.matrix_rank(event.model.exog)),
        "event_kolonner": int(event.model.exog.shape[1]),
        "event_residual_df": int(event.df_resid),
        "event_felles_F": float(wald.statistic),
        "event_felles_p": float(wald.pvalue),
        "event_felles_df_num": int(wald.df_num),
        "event_felles_df_denom": int(wald.df_denom),
        "event_koef_snitt": float(event_df["koef"].mean()),
        "event_prosent_min": float(event_df["prosent"].min()),
        "event_prosent_maks": float(event_df["prosent"].max()),
        "event_antall_p_under_005":
            int((event_df["p_t26"] < 0.05).sum()),
        "d7_loco_koef_min": float(
            loco_df.loc[loco_df["modell"] == "D7", "koef"].min()
        ),
        "d7_loco_koef_maks": float(
            loco_df.loc[loco_df["modell"] == "D7", "koef"].max()
        ),
        "d7_loco_maks_abs_avvik": float(
            loco_df.loc[
                loco_df["modell"] == "D7", "avvik_fra_full"
            ].abs().max()
        ),
        "placebo_loco_koef_min": float(
            loco_df.loc[loco_df["modell"] == "D7_placebo", "koef"].min()
        ),
        "placebo_loco_koef_maks": float(
            loco_df.loc[loco_df["modell"] == "D7_placebo", "koef"].max()
        ),
        "placebo_loco_maks_abs_avvik": float(
            loco_df.loc[
                loco_df["modell"] == "D7_placebo", "avvik_fra_full"
            ].abs().max()
        ),
        "placebo_loco_antall_p_under_005": int(
            (
                loco_df.loc[
                    loco_df["modell"] == "D7_placebo", "p_t"
                ] < 0.05
            ).sum()
        ),
    }
    json_skriv(VERIF / "placebo_robusthet.json", oppsummering)
    print(event_df.to_string(index=False))
    print()
    print(e5_df.to_string(index=False))
    print()
    print(loco_df.groupby("modell")[
        ["koef", "se", "avvik_fra_full"]
    ].agg(["min", "max"]).to_string())
    print()
    print(oppsummering)


if __name__ == "__main__":
    hoved()
