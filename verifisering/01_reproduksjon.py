"""Uavhengig reproduksjon. Kjør: py -3 verifisering/01_reproduksjon.py"""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from statsmodels.tools.sm_exceptions import SingularMatrixWarning

from felles import (
    DID_FORMEL_BASE, PROC, ROOT, VERIF, fit_panel_m1, fit_wls_cluster,
    forbered_did, json_skriv, numeriske_summer, prosent_fra_log,
    sha256_fil,
)

warnings.filterwarnings("ignore", category=SingularMatrixWarning)

MAAL = {
    ("D7", "bestilt_post"): (0.02988, 0.00284),
    ("D7 tidlig/sent", "tidlig_post"): (0.03094, 0.00299),
    ("D7 tidlig/sent", "sent_post"): (0.02861, 0.00320),
    ("D7 placebo", "bestilt_post"): (-0.00190, 0.00124),
    ("M1", "post_np"): (0.0950, 0.0069),
    ("M5", "post_np"): (0.0509, 0.0023),
}


def resultat_rad(modell, term, koef, se, n, g):
    maal_koef, maal_se = MAAL[(modell, term)]
    return {
        "modell": modell,
        "term": term,
        "koef": float(koef),
        "se": float(se),
        "prosent": prosent_fra_log(koef),
        "n": int(n),
        "klustre": np.nan if g is None else int(g),
        "maal_koef_til_godkjenning": maal_koef,
        "maal_se_til_godkjenning": maal_se,
        "avvik_koef": float(koef - maal_koef),
        "avvik_se": float(se - maal_se),
    }


def manifest():
    filer = [
        PROC / "did_month.parquet",
        PROC / "panel.parquet",
        PROC / "elhub_np_mba_daily.parquet",
        ROOT / "output" / "TIL_GODKJENNING.md",
    ]
    rader = []
    for path in filer:
        rad = {
            "relativ_sti": path.relative_to(ROOT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_fil(path),
        }
        if path.suffix == ".parquet":
            d = pd.read_parquet(path)
            rad["rader"] = len(d)
            rad["kolonner"] = len(d.columns)
            datokol = "maned" if "maned" in d.columns else "DATO"
            rad["dato_min"] = str(d[datokol].min())
            rad["dato_maks"] = str(d[datokol].max())
        rader.append(rad)
    return pd.DataFrame(rader)


def hoved():
    m = forbered_did()
    assert len(m) == 837
    assert m["g"].nunique() == 27
    assert m[["g", "maned"]].duplicated().sum() == 0
    assert set(m.groupby("g").size()) == {31}
    assert int(m.isna().sum().sum()) == 0
    resultater = []

    d7 = fit_wls_cluster(DID_FORMEL_BASE + " + bestilt_post", m)
    resultater.append(resultat_rad(
        "D7", "bestilt_post", d7.params["bestilt_post"],
        d7.bse["bestilt_post"], d7.nobs, m["g"].nunique()
    ))

    ts = fit_wls_cluster(
        DID_FORMEL_BASE + " + tidlig_post + sent_post", m
    )
    for term in ["tidlig_post", "sent_post"]:
        resultater.append(resultat_rad(
            "D7 tidlig/sent", term, ts.params[term], ts.bse[term],
            ts.nobs, m["g"].nunique()
        ))

    pre = m.loc[m["maned"] < "2025-10"].copy()
    pre["bestilt_post"] = (
        pre["bestilt"] * (pre["maned"] >= "2024-10").astype(int)
    )
    assert len(pre) == 648
    placebo = fit_wls_cluster(DID_FORMEL_BASE + " + bestilt_post", pre)
    resultater.append(resultat_rad(
        "D7 placebo", "bestilt_post", placebo.params["bestilt_post"],
        placebo.bse["bestilt_post"], placebo.nobs, pre["g"].nunique()
    ))

    panel = pd.read_parquet(PROC / "panel.parquet")
    assert len(panel) == 10047
    assert panel[["knr", "maned"]].duplicated().sum() == 0
    assert int(panel.isna().sum().sum()) == 0
    m1 = fit_panel_m1(panel)
    resultater.append(resultat_rad(
        "M1", "post_np", m1.params["post_np"],
        m1.std_errors["post_np"], m1.nobs, panel["knr"].nunique()
    ))

    panel_pre = panel.loc[panel["maned"] < "2025-10"].copy()
    panel_pre["post_np"] = (panel_pre["maned"] >= "2024-10").astype(int)
    assert len(panel_pre) == 8668
    m5 = fit_panel_m1(panel_pre)
    resultater.append(resultat_rad(
        "M5", "post_np", m5.params["post_np"],
        m5.std_errors["post_np"], m5.nobs,
        panel_pre["knr"].nunique()
    ))

    r = pd.DataFrame(resultater)
    r.to_csv(VERIF / "resultater_reproduksjon.csv", index=False)
    man = manifest()
    man.to_csv(VERIF / "input_manifest.csv", index=False)

    summer = {
        "did": {
            "rader": len(m),
            "grupper": int(m["g"].nunique()),
            "maaneder": int(m["maned"].nunique()),
            **numeriske_summer(m, ["kwh", "n_mp", "timer", "log_y"]),
        },
        "did_placebo": {
            "rader": len(pre),
            **numeriske_summer(pre, ["kwh", "n_mp", "timer", "log_y"]),
        },
        "panel": {
            "rader": len(panel),
            "kommuner": int(panel["knr"].nunique()),
            "maaneder": int(panel["maned"].nunique()),
            **numeriske_summer(
                panel, ["kwh", "n_mp", "egd", "spot_ore_kwh", "log_kwh"]
            ),
        },
        "panel_placebo": {
            "rader": len(panel_pre),
            **numeriske_summer(
                panel_pre,
                ["kwh", "n_mp", "egd", "spot_ore_kwh", "log_kwh"],
            ),
        },
        "maks_abs_avvik_koef_mot_avrundet_maal":
            float(r["avvik_koef"].abs().max()),
        "maks_abs_avvik_se_mot_avrundet_maal":
            float(r["avvik_se"].abs().max()),
    }
    json_skriv(VERIF / "kontrollsummer_reproduksjon.json", summer)

    pd.set_option("display.max_columns", None)
    print(r.to_string(index=False))
    print()
    print(man.to_string(index=False))
    print()
    print("Kontrollsummer:", summer)


if __name__ == "__main__":
    hoved()
