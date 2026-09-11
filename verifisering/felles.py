"""Felles hjelpefunksjoner; importerer med hensikt ingenting fra src/."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from linearmodels.panel import PanelOLS

ROOT = Path(__file__).resolve().parents[1]
VERIF = ROOT / "verifisering"
PROC = ROOT / "data" / "processed"
DID_FORMEL_BASE = "log_y ~ C(g) + C(pa_t_eac) + bestilt:C(mnd):C(eac)"


def sha256_fil(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for blokk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(blokk)
    return h.hexdigest()


def forbered_did(df: pd.DataFrame | None = None) -> pd.DataFrame:
    if df is None:
        df = pd.read_parquet(PROC / "did_month.parquet")
    m = df.copy()
    m["mnd"] = m["maned"].str[5:]
    m["pa_t_eac"] = m["pa_t"] + "|" + m["eac"]
    m["ae"] = m["pa"] + "|" + m["eac"]
    m["bestilt_post"] = m["bestilt"] * m["post"]
    m["tidlig_post"] = m["tidlig"] * m["post"]
    m["sent_post"] = m["sent"] * m["post"]
    return m


def fit_wls_cluster(formel: str, df: pd.DataFrame, cluster: str = "g",
                    use_t: bool = False):
    return smf.wls(formel, data=df, weights=df["n_mp"]).fit(
        cov_type="cluster", cov_kwds={"groups": df[cluster]}, use_t=use_t
    )


def fit_panel_m1(df: pd.DataFrame):
    d = df.copy()
    d["innt_1000"] = d["median_innt_etter_skatt"] / 1000.0
    d["t"] = pd.PeriodIndex(d["maned"], freq="M").to_timestamp()
    d = d.set_index(["knr", "t"])
    xs = ["egd", "spot_ore_kwh", "innt_1000",
          "snitt_bruksareal_m2", "post_np"]
    modell = PanelOLS(d["log_kwh"], d[xs], entity_effects=True,
                      drop_absorbed=True)
    return modell.fit(cov_type="clustered", cluster_entity=True)


def prosent_fra_log(beta: float) -> float:
    return 100.0 * np.expm1(float(beta))


def json_skriv(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2,
                               sort_keys=True), encoding="utf-8")


def numeriske_summer(df: pd.DataFrame,
                     kolonner: Iterable[str]) -> dict[str, float]:
    return {f"sum_{kol}": float(df[kol].sum())
            for kol in kolonner if kol in df.columns}
