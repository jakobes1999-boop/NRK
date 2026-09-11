"""Uavhengig revisjon av restringert wild cluster bootstrap (WCR)."""
from __future__ import annotations

import itertools

import numpy as np
import pandas as pd
import patsy
import scipy.linalg as sla

from felles import (
    DID_FORMEL_BASE, PROC, VERIF, forbered_did, json_skriv,
    prosent_fra_log,
)

FULL = DID_FORMEL_BASE + " + bestilt_post"


def design_fullrang(formel, data, term):
    y, xdf = patsy.dmatrices(formel, data, return_type="dataframe")
    navn = list(xdf.columns)
    behold = navn.index(term)
    rest = [j for j in range(xdf.shape[1]) if j != behold]
    r = xdf.iloc[:, rest].to_numpy()
    norm = np.linalg.norm(r, axis=0)
    norm[norm == 0] = 1.0
    _, qr_r, pivot = sla.qr(r / norm, mode="economic", pivoting=True)
    diag = np.abs(np.diag(qr_r))
    rang = int((diag > 1e-8 * max(diag.max(), 1.0)).sum())
    valgte = sorted(rest[j] for j in pivot[:rang]) + [behold]
    x = xdf.iloc[:, valgte].to_numpy()
    if np.linalg.matrix_rank(x) != x.shape[1]:
        raise ValueError("Testleddet er ikke identifisert.")
    return y.iloc[:, 0].to_numpy(), x, len(valgte) - 1


def forbered(formel, data, term, cluster):
    y, x, k = design_fullrang(formel, data, term)
    w = data["n_mp"].to_numpy(dtype=float)
    sw = np.sqrt(w)
    xt, yt = x * sw[:, None], y * sw
    grupper, gi = np.unique(data[cluster].astype(str), return_inverse=True)
    g = len(grupper)
    n, ant_k = xt.shape
    ai = np.linalg.pinv(xt.T @ xt)
    p = ai @ xt.T
    beta = p @ yt
    u = yt - xt @ beta
    h = xt @ ai[:, k]
    dmat = np.zeros((g, n))
    dmat[gi, np.arange(n)] = 1.0
    korr = g / (g - 1) * (n - 1) / (n - ant_k)
    score = dmat @ (h * u)
    se = float(np.sqrt(korr * (score @ score)))
    rest = [j for j in range(ant_k) if j != k]
    xr = xt[:, rest]
    xk = xt[:, k]
    fy = xr @ np.linalg.lstsq(xr, yt, rcond=None)[0]
    fk = xr @ np.linalg.lstsq(xr, xk, rcond=None)[0]
    return {
        "xt": xt, "yt": yt, "p": p, "h": h, "dmat": dmat,
        "fy": fy, "fk": fk, "xk": xk, "gi": gi,
        "beta": float(beta[k]), "se": se, "k": k, "G": g,
        "N": n, "K": ant_k, "korr": korr, "grupper": grupper,
    }


def rademacher_trekk(g, b, seed):
    rng = np.random.default_rng(seed)
    return rng.integers(0, 2, size=(g, b)) * 2.0 - 1.0


def rademacher_eksakt(g):
    return np.array(list(itertools.product([-1.0, 1.0], repeat=g))).T


def kurvegrunnlag(prep, trekk):
    v = trekk[prep["gi"]]
    a = prep["yt"] - prep["fy"]
    d = prep["xk"] - prep["fk"]
    ys0 = prep["fy"][:, None] + a[:, None] * v
    ys1 = d[:, None] * (1.0 - v)
    bh0 = prep["p"] @ ys0
    bh1 = prep["p"] @ ys1
    us0 = ys0 - prep["xt"] @ bh0
    us1 = ys1 - prep["xt"] @ bh1
    s0 = prep["dmat"] @ (prep["h"][:, None] * us0)
    s1 = prep["dmat"] @ (prep["h"][:, None] * us1)
    return {
        "num0": bh0[prep["k"]],
        "num1": bh1[prep["k"]] - 1.0,
        "var0": (s0 * s0).sum(axis=0),
        "var1": (s0 * s1).sum(axis=0),
        "var2": (s1 * s1).sum(axis=0),
        "B": trekk.shape[1],
    }


def pverdier(prep, grunn, nuller, eksakt=False):
    nuller = np.atleast_1d(nuller).astype(float)
    num = (
        grunn["num0"][None, :]
        + nuller[:, None] * grunn["num1"][None, :]
    )
    varians = prep["korr"] * (
        grunn["var0"][None, :]
        + 2.0 * nuller[:, None] * grunn["var1"][None, :]
        + nuller[:, None] ** 2 * grunn["var2"][None, :]
    )
    se_stjerne = np.sqrt(np.maximum(varians, 0.0))
    t_stjerne = num / se_stjerne
    t_obs = np.abs((prep["beta"] - nuller) / prep["se"])
    antall = (
        np.abs(t_stjerne) >= t_obs[:, None] - 1e-12
    ).sum(axis=1)
    if eksakt:
        return antall / grunn["B"]
    return (1.0 + antall) / (grunn["B"] + 1.0)


def prosjektintervall(prep, grunn, n_grid=41, span=4.0):
    grid = np.linspace(
        prep["beta"] - span * prep["se"],
        prep["beta"] + span * prep["se"],
        n_grid,
    )
    ps = pverdier(prep, grunn, grid)
    inne = ps >= 0.05
    if not inne.any():
        return np.nan, np.nan, grid, ps
    i0 = int(np.argmax(inne))
    i1 = int(len(inne) - 1 - np.argmax(inne[::-1]))

    def interp(ia, ib):
        pa, pb = ps[ia], ps[ib]
        if pb == pa:
            return grid[ib]
        return grid[ia] + (
            (0.05 - pa) * (grid[ib] - grid[ia]) / (pb - pa)
        )

    lav = grid[0] if i0 == 0 else interp(i0 - 1, i0)
    hoy = grid[-1] if i1 == len(grid) - 1 else interp(i1 + 1, i1)
    return float(lav), float(hoy), grid, ps


def komponenter(inne):
    start = np.flatnonzero(inne & ~np.r_[False, inne[:-1]])
    slutt = np.flatnonzero(inne & ~np.r_[inne[1:], False])
    return list(zip(start.tolist(), slutt.tolist()))


def finintervall(prep, grunn, eksakt=False, punkter=4001, span=5.0):
    grid = np.linspace(
        prep["beta"] - span * prep["se"],
        prep["beta"] + span * prep["se"],
        punkter,
    )
    ps = pverdier(prep, grunn, grid, eksakt=eksakt)
    kom = komponenter(ps >= 0.05)
    if not kom:
        return np.nan, np.nan, grid, ps, kom
    return grid[kom[0][0]], grid[kom[-1][1]], grid, ps, kom


def analyser(navn, data, formel, term, cluster, trekk, eksakt=False):
    prep = forbered(formel, data, term, cluster)
    grunn = kurvegrunnlag(prep, trekk)
    p0 = float(pverdier(prep, grunn, [0.0], eksakt=eksakt)[0])
    if eksakt:
        grov_lav = grov_hoy = np.nan
    else:
        grov_lav, grov_hoy, _, _ = prosjektintervall(prep, grunn)
    fin_lav, fin_hoy, grid, ps, kom = finintervall(
        prep, grunn, eksakt=eksakt
    )
    topp = int(np.argmax(ps))
    venstre_brudd = int((np.diff(ps[:topp + 1]) < 0).sum())
    hoyre_brudd = int((np.diff(ps[topp:]) > 0).sum())
    resultat = {
        "modell": navn,
        "term": term,
        "cluster": cluster,
        "G": prep["G"],
        "N": prep["N"],
        "K_rang": prep["K"],
        "beta": prep["beta"],
        "se_cr1_rang": prep["se"],
        "p_wcr": p0,
        "B": grunn["B"],
        "eksakt_enumerering": eksakt,
        "grov41_lav": grov_lav,
        "grov41_hoy": grov_hoy,
        "fin_lav": float(fin_lav),
        "fin_hoy": float(fin_hoy),
        "fin_lav_prosent": prosent_fra_log(fin_lav),
        "fin_hoy_prosent": prosent_fra_log(fin_hoy),
        "akseptkomponenter": len(kom),
        "monotonibrudd_venstre": venstre_brudd,
        "monotonibrudd_hoyre": hoyre_brudd,
        "p_min": float(ps.min()),
        "p_maks": float(ps.max()),
        "fin_grid_steg": float(grid[1] - grid[0]),
    }
    kurve = pd.DataFrame({
        "modell": navn, "nullverdi": grid, "p_wcr": ps,
        "akseptert_5pst": (ps >= 0.05).astype(int),
    })
    return resultat, kurve


def legg_til_dose(m):
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
    dose = pd.DataFrame(rader)
    x = m.merge(dose, on=["pa", "maned"], how="left")
    x["dose"] = x["dose"].fillna(0.0)
    x["sent_dose"] = x["sent"] * x["dose"]
    return x


def nipunktskontroller(m):
    maal = {
        ("Husholdning Høy", "E6", "tidlig_post"): 0.033,
        ("Husholdning Høy", "E6", "sent_dose"): 0.398,
        ("Husholdning Lav", "E6", "tidlig_post"): 0.022,
        ("Husholdning Lav", "E6", "sent_dose"): 0.082,
        ("Husholdning Medium", "E6", "tidlig_post"): 0.003,
        ("Husholdning Medium", "E6", "sent_dose"): 0.115,
        ("Husholdning Høy", "D6", "bestilt_post"): 0.025,
        ("Husholdning Lav", "D6", "bestilt_post"): 0.001,
        ("Husholdning Medium", "D6", "bestilt_post"): 0.001,
    }
    m = legg_til_dose(m)
    rader = []
    for eac, sub in m.groupby("eac"):
        jobber = [
            (
                "E6",
                "log_y ~ C(g) + C(pa_t) + tidlig:C(mnd) + "
                "sent:C(mnd) + tidlig_post + sent_post + sent_dose",
                ["tidlig_post", "sent_dose"],
            ),
            (
                "D6",
                "log_y ~ C(g) + C(pa_t) + "
                "bestilt:C(mnd) + bestilt_post",
                ["bestilt_post"],
            ),
        ]
        for modell, formel, termer in jobber:
            for term in termer:
                prep = forbered(formel, sub, term, "g")
                mc = kurvegrunnlag(
                    prep, rademacher_trekk(prep["G"], 999, 1)
                )
                ex = kurvegrunnlag(prep, rademacher_eksakt(prep["G"]))
                p_mc = float(pverdier(prep, mc, [0.0])[0])
                p_ex = float(
                    pverdier(prep, ex, [0.0], eksakt=True)[0]
                )
                target = maal[(eac, modell, term)]
                rader.append({
                    "eac": eac, "modell": modell, "term": term,
                    "beta": prep["beta"], "se_cr1_rang": prep["se"],
                    "G": prep["G"], "K_rang": prep["K"],
                    "p_mc_B999_seed1": p_mc,
                    "p_til_godkjenning": target,
                    "avvik_p_mc": p_mc - target,
                    "p_eksakt_512": p_ex,
                    "eksakt_teller": int(round(p_ex * 512)),
                })
    return pd.DataFrame(rader)


def hoved():
    m = forbered_did()
    pre = m.loc[m["maned"] < "2025-10"].copy()
    pre["bestilt_post"] = (
        pre["bestilt"] * (pre["maned"] >= "2024-10").astype(int)
    )

    d7_prep_g = forbered(FULL, m, "bestilt_post", "g")
    trekk_g = rademacher_trekk(d7_prep_g["G"], 999, 1)
    d7, kurve_d7 = analyser(
        "D7_g_B999", m, FULL, "bestilt_post", "g", trekk_g
    )
    placebo, kurve_pl = analyser(
        "D7_placebo_g_B999", pre, FULL, "bestilt_post", "g", trekk_g
    )

    d7_prep_ae = forbered(FULL, m, "bestilt_post", "ae")
    trekk_ae = rademacher_eksakt(d7_prep_ae["G"])
    ae, kurve_ae = analyser(
        "D7_omraade_klasse_eksakt", m, FULL, "bestilt_post",
        "ae", trekk_ae, eksakt=True
    )
    hovedresultater = [d7, placebo, ae]
    pd.concat(
        [kurve_d7, kurve_pl, kurve_ae], ignore_index=True
    ).to_csv(VERIF / "wcb_pkurve.csv", index=False)

    ni = nipunktskontroller(m)
    ni.to_csv(VERIF / "wcb_ni_klustre_eksakt.csv", index=False)

    webb = np.array([
        -np.sqrt(1.5), -1.0, -np.sqrt(0.5),
        np.sqrt(0.5), 1.0, np.sqrt(1.5),
    ])
    kontroll = {
        "hovedresultater": hovedresultater,
        "d7_grov41_avvik_lav_mot_til_godkjenning":
            d7["grov41_lav"] - 0.024227021763099318,
        "d7_grov41_avvik_hoy_mot_til_godkjenning":
            d7["grov41_hoy"] - 0.036596749319697454,
        "d7_se_cr1_rang_avvik_mot_output":
            d7["se_cr1_rang"] - 0.00280861593142299,
        "placebo_grov41_avvik_lav_mot_til_godkjenning":
            placebo["grov41_lav"] - (-0.00416),
        "placebo_grov41_avvik_hoy_mot_til_godkjenning":
            placebo["grov41_hoy"] - 0.00104,
        "monte_carlo_p_opplosning_B999": 1.0 / 1000.0,
        "feil_i_prosjekttekst_som_sier_1_over_999": (
            1.0 / 999.0 - 1.0 / 1000.0
        ),
        "rademacher_27_mulige_monstre": 2 ** 27,
        "rademacher_9_mulige_monstre": 2 ** 9,
        "webb_gjennomsnitt": float(webb.mean()),
        "webb_varians": float(np.mean(webb ** 2)),
        "ni_klustre_maks_abs_avvik_mc_p_mot_avrundet_output":
            float(ni["avvik_p_mc"].abs().max()),
        "wcb_ki_publisert_log": [
            0.024227021763099318, 0.036596749319697454
        ],
        "wcb_ki_publisert_prosent": [
            prosent_fra_log(0.024227021763099318),
            prosent_fra_log(0.036596749319697454),
        ],
    }
    json_skriv(VERIF / "wcb_revisjon.json", kontroll)
    print(pd.DataFrame(hovedresultater).to_string(index=False))
    print()
    print(ni.to_string(index=False))
    print()
    print(kontroll)


if __name__ == "__main__":
    hoved()
