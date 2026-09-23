"""Steg 22: Hva betyr hyttene for NRK-lik kommuneanalyse? Robust panelregresjon.

Spørsmål: Økte privatforbruket (husholdning + hytte, Elhubs gruppe «Privat») mer etter
oktober 2025 i kommuner med høy hytteandel, når man kontrollerer for mest mulig?

Behandling: post (fra 2025-10) × hytteandel, der hytteandel = hytter av private målere
i kommunen (Elhub målerfil, siste dag), i prosentpoeng. Tidsinvariant.

Spesifikasjoner (utfall log kWh Privat per kommune og måned, klustret på kommune):
  H1  kommune-FE + år×måned-FE
  H2  kommune-FE + prisområde×år×måned-FE        (spotpris, strømstøtte, felles sjokk per område)
  H3  H2 + kommune×kalendermåned-FE              (egen sesongprofil, f.eks. påske/vintersesong)
  H4  H3 + kommune-spesifikk temperaturrespons (gradtall × kommune)
  H5  H4 + post × kommunekjennetegn (oppslutning husholdninger, inntekt, boligareal,
          andel store boliger, log antall målere, normaltemperatur)
  H6  H5 + kommune-spesifikk lineær trend
  H7  H5 vektet med antall målere
Placebo: samme spesifikasjoner på data før 2025-10 med falsk start 2024-10.
Forløp: hytteandel × sesongår (okt–sep), referanse 2024/25, H4-oppsett.
Tolkning i NRK-modellen: M1 (NRKs oppsett) med post × hytteandel sentrert i 0 gir
NRK-lik effekt for en tenkt kommune uten hytter.
"""
import numpy as np
import pandas as pd
from linearmodels.iv.absorbing import AbsorbingLS, Interaction
from config import PROC, OUT, NORGESPRIS_START

START = NORGESPRIS_START[:7]


def hytteandel():
    n = pd.read_parquet(PROC / "elhub_np_muni_daily.parquet")
    n["knr"] = n.KOMMUNENUMMER.astype(int).astype(str).str.zfill(4)
    n["hytte"] = n.FORBRUKSGRUPPE.str.lower().str.contains("hytte|fritid")
    d = n[n.DATO.astype(str) == n.DATO.astype(str).max()].groupby(["knr", "hytte"]).ANTALL.sum().unstack(fill_value=0)
    return (100 * d[True] / (d[True] + d[False])).rename("hytte_pp"), str(n.DATO.max())[:10]


def panel():
    p = pd.read_parquet(PROC / "panel.parquet")
    ha, dato = hytteandel()
    p = p.merge(ha, left_on="knr", right_index=True, how="inner")
    p["t"] = pd.PeriodIndex(p.maned, freq="M").to_timestamp()
    p["tn"] = (p.t.dt.year - 2022) * 12 + p.t.dt.month
    p["ym"] = p.maned
    p["pa_ym"] = p.prisomrade + "_" + p.maned
    p["k_mnd"] = p.knr + "_" + p.mnd.astype(str)
    p["innt_1000"] = p.median_innt_etter_skatt / 1000
    # tidsinvariante kommunekjennetegn (for post × X)
    last = p[p.maned == p.maned.max()].set_index("knr")
    kj = pd.DataFrame({
        "oppsl_hh": last.np_andel_hh,
        "innt": p.groupby("knr").innt_1000.mean(),
        "areal": p.groupby("knr").snitt_bruksareal_m2.mean(),
        "stor": p.groupby("knr").andel_over_160m2.mean(),
        "logmp": np.log(p.groupby("knr").n_mp.mean()),
        "tnorm": p.groupby("knr").tmean.mean(),
    })
    kj = (kj - kj.mean()) / kj.std()
    p = p.merge(kj.add_prefix("z_"), left_on="knr", right_index=True)
    return p, dato


def fit(p, post_start, spec, weights=False):
    d = p.copy()
    d["post"] = (d.maned >= post_start).astype(float)
    d["post_x_hytte"] = d.post * d.hytte_pp
    x = ["post_x_hytte"]
    absorb = {"H1": ["knr", "ym"], "H2": ["knr", "pa_ym"]}.get(spec, ["knr", "pa_ym", "k_mnd"])
    inter = []
    if spec in ("H4", "H5", "H6", "H7"):
        inter.append(Interaction(cat=d[["knr"]].astype("category"), cont=d[["egd"]]))
    if spec in ("H5", "H6", "H7"):
        for c in ["z_oppsl_hh", "z_innt", "z_areal", "z_stor", "z_logmp", "z_tnorm"]:
            d[f"post_{c}"] = d.post * d[c]; x.append(f"post_{c}")
    if spec == "H6":
        inter.append(Interaction(cat=d[["knr"]].astype("category"), cont=d[["tn"]].astype(float)))
    if spec in ("H1", "H2"):
        x = x + ["egd"]
    elif spec == "H3":
        x = x + ["egd"]
    mod = AbsorbingLS(d.log_kwh, d[x], absorb=d[absorb].astype("category"),
                      interactions=inter or None, weights=d.n_mp if weights else None)
    r = mod.fit(cov_type="clustered", clusters=d.knr.astype("category").cat.codes)
    return r.params["post_x_hytte"], r.std_errors["post_x_hytte"], r.pvalues["post_x_hytte"], int(r.nobs)


def main():
    p, dato = panel()
    pre = p[p.maned < START]
    rows = []
    for spec in ["H1", "H2", "H3", "H4", "H5", "H6", "H7"]:
        w = spec == "H7"
        b, se, pv, n = fit(p, START, spec, w)
        bp, sep, pvp, npl = fit(pre, "2024-10", spec, w)
        rows.append({"spes": spec, "koef": b, "se": se, "p": pv, "n": n,
                     "placebo_koef": bp, "placebo_se": sep, "placebo_p": pvp, "placebo_n": npl})
        print(f"{spec}: {100*b:.3f} ({100*se:.3f}) p={pv:.3f} | placebo {100*bp:.3f} ({100*sep:.3f}) p={pvp:.3f}")
    res = pd.DataFrame(rows)
    res["pst_per_10pp_hytte"] = 100 * (np.exp(10 * res.koef) - 1)
    res["placebo_pst_per_10pp"] = 100 * (np.exp(10 * res.placebo_koef) - 1)
    res.to_csv(OUT / "tab_hytteandel_robust.csv", index=False)

    # Forløp: hytteandel × sesongår (okt–sep), ref 2024/25, H4-oppsett
    d = p.copy()
    sy = np.where(d.t.dt.month >= 10, d.t.dt.year, d.t.dt.year - 1)
    d["sesong"] = [f"{y}/{str(y+1)[2:]}" for y in sy]
    ev = []
    for s in sorted(d.sesong.unique()):
        if s == "2024/25":
            continue
        c = f"h_{s.replace('/', '_')}"; d[c] = d.hytte_pp * (d.sesong == s); ev.append(c)
    mod = AbsorbingLS(d.log_kwh, d[ev], absorb=d[["knr", "pa_ym", "k_mnd"]].astype("category"),
                      interactions=[Interaction(cat=d[["knr"]].astype("category"), cont=d[["egd"]])])
    r = mod.fit(cov_type="clustered", clusters=d.knr.astype("category").cat.codes)
    evt = pd.DataFrame({"koef": r.params[ev], "se": r.std_errors[ev], "p": r.pvalues[ev]})
    evt.index = [i[2:].replace("_", "/") for i in evt.index]
    evt.loc["2024/25"] = [0.0, 0.0, np.nan]
    evt = evt.sort_index(); evt["pst_per_10pp"] = 100 * (np.exp(10 * evt.koef) - 1)
    evt.to_csv(OUT / "tab_hytteandel_forlop.csv")
    print(evt.round(4))

    # NRK-lik M1 med post × hytteandel: effekt ved 0 hytter og ved snitt
    from linearmodels.panel import PanelOLS
    m = p.copy(); m["post"] = (m.maned >= START).astype(float); m["post_x_hytte"] = m.post * m.hytte_pp
    m = m.set_index(["knr", "t"])
    xs = ["egd", "spot_ore_kwh", "innt_1000", "snitt_bruksareal_m2", "post", "post_x_hytte"]
    rm = PanelOLS(m.log_kwh, m[xs], entity_effects=True).fit(cov_type="clustered", cluster_entity=True)
    mean_h = p.groupby("knr").hytte_pp.first().mean()
    nrk = {"M1_post_ved_0_hytter": rm.params["post"], "se": rm.std_errors["post"],
           "post_x_hytte": rm.params["post_x_hytte"], "snitt_hytteandel_pp": mean_h,
           "M1_post_ved_snitt": rm.params["post"] + mean_h * rm.params["post_x_hytte"],
           "hytteandel_dato": dato, "kommuner": p.knr.nunique()}
    pd.Series(nrk).to_csv(OUT / "tab_hytteandel_nrk_m1.csv", header=["verdi"])
    print(pd.Series(nrk))


if __name__ == "__main__":
    main()
