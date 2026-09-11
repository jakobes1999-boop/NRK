"""Steg 18: Systematisk spesifikasjonssøk mot NRKs fire koeffisienter.

NRKs metodeboks (kilder/nrk_prisen_for_billig_strom.md, linje 251-285) oppgir en
kommune-FE-regresjon for husholdningenes månedlige strømforbruk i NO1/NO2/NO5,
2021-juni 2026:

    energigradtall            0,0019***
    månedlig spotpris        -0,0005***
    innføring av Norgespris   0,0822***
    medianinntekt             0,0024***
    R2                       93,76 %

Venstresidens form, koding av Norgespris, tids-FE, vekting, enheter på spot og
inntekt, gradtallsdefinisjon, R2-type og kommuneutvalg er ikke oppgitt. Skriptet
kjører et rutenett over disse dimensjonene på vårt panel og rangerer
spesifikasjonene etter avstand til NRKs tall.

Effektivisering: enhetsvalg på spot og inntekt er rene reskaleringer av en
lineær koeffisient. Kjernemodellene estimeres derfor én gang (spot i øre/kWh,
inntekt i 1 000 kr) og reskaleres analytisk etterpå. Log-inntekt er en egen
funksjonsform og estimeres separat.

Skriver:
    output/tab_nrk_spes_sok.csv   alle kjøringer (kjerne x enhetsvalg)
    output/tab_nrk_spes_sok.md    topp 15 + dimensjonstabell for post_np
    output/log_s18.txt            kjørelogg
"""
import io
import itertools
import time
import warnings

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

from config import PROC, RAW, OUT, GRADTALL_BASE_TEMP

warnings.simplefilter("ignore")

# NRKs oppgitte tall
NRK = {"egd": 0.0019, "spot": -0.0005, "np": 0.0822, "innt": 0.0024}
NRK_R2 = 0.9376

LOG = io.StringIO()


def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.write(s + "\n")
    print(s.encode("ascii", "replace").decode("ascii"), flush=True)


# ---------------------------------------------------------------- data

def egd_base18(months):
    """Energigradtall med basetemperatur 18 grader, samme stasjonsvalg som s04.

    Månedspanelet har bare månedsmiddeltemperatur, så basen kan ikke regnes om
    der. Rå døgnverdier fra Frost ligger i data/raw og gjør omregningen mulig.
    """
    f = RAW / "frost_daily_tmean.parquet"
    s = RAW / "frost_sources.parquet"
    if not (f.exists() and s.exists()):
        return None, None
    daily = pd.read_parquet(f).dropna(subset=["tmean"])
    daily["maned"] = daily["dato"].str[:7]
    daily["egd18"] = (18.0 - daily["tmean"]).clip(lower=0)
    src = pd.read_parquet(s).dropna(subset=["municipalityId"]).copy()
    src["knr"] = src.municipalityId.astype(int).astype(str).str.zfill(4)
    src["fylke"] = src.knr.str[:2]
    cnt = daily.groupby("source").size().rename("n").reset_index()
    src2 = src.merge(cnt, left_on="id", right_on="source", how="inner")
    best = src2.sort_values("n", ascending=False).drop_duplicates("knr")
    m = daily.merge(best[["id", "knr"]], left_on="source", right_on="id")
    k = (m.groupby(["knr", "maned"], as_index=False)
           .agg(egd18=("egd18", "sum"), n_dager=("egd18", "size")))
    k = k[k.n_dager >= 20].drop(columns="n_dager")
    m2 = daily.merge(src2[["id", "fylke"]], left_on="source", right_on="id")
    fy = (m2.groupby(["fylke", "source", "maned"], as_index=False)
            .agg(egd18=("egd18", "sum"), n=("egd18", "size")))
    fy = fy[fy.n >= 20].groupby(["fylke", "maned"], as_index=False).agg(egd18_f=("egd18", "mean"))
    return k, fy


def load_panel():
    p = pd.read_parquet(PROC / "panel.parquet")
    p["innt_1000"] = p.median_innt_etter_skatt / 1000
    p["t"] = pd.PeriodIndex(p.maned, freq="M").to_timestamp()
    p["aar_s"] = p.maned.str[:4]
    # Norgespris-dummy fra september 2025 (bestillingen åpnet i august 2025)
    p["post_np_sep"] = (p.maned >= "2025-09").astype(int)
    p["egd17"] = p["egd"]
    k, fy = egd_base18(sorted(p.maned.unique()))
    if k is not None:
        p = p.merge(k, on=["knr", "maned"], how="left").merge(fy, on=["fylke", "maned"], how="left")
        p["egd18"] = p.egd18.fillna(p.egd18_f)
        p = p.drop(columns=["egd18_f"])
        log(f"egd18 bygget: {p.egd18.notna().mean():.3f} av radene har verdi; "
            f"korr(egd17, egd18) = {p[['egd17','egd18']].corr().iloc[0,1]:.4f}")
    else:
        p["egd18"] = np.nan
        log("ADVARSEL: rå Frost-data mangler, egd18 ikke bygget")
    return p


# ---------------------------------------------------------------- estimering

Y_VARS = {
    "log_kwh": "log_kwh",
    "log_kwh_per_maler": "log_kwh_mp",
    "kwh_nivaa": "kwh",
    "kwh_per_maler_nivaa": "kwh_per_mp",
}

NP_VARS = {
    "post_okt2025": "post_np",
    "post_sep2025": "post_np_sep",
    "andel_privat": "np_andel",
    "andel_husholdning": "np_andel_hh",
}
DUMMY_NP = {"post_okt2025", "post_sep2025"}

SAMPLES = {
    "alle": lambda d: d,
    "pa_entydig": lambda d: d[d.pa_kilde == "fylke=nve"],
    "egd_kommunestasjon": lambda d: d[d.egd_kilde == "kommune"],
}


def fit_one(df, yv, egdv, npv, areal, innt_form, tid_fe, vekt):
    xs = [egdv, "spot_ore_kwh", "innt_1000" if innt_form == "lineaer" else "log_innt"]
    if areal:
        xs.append("snitt_bruksareal_m2")
    xs.append(npv)
    need = [yv] + xs + (["n_mp"] if vekt else [])
    d = df.dropna(subset=need).copy()
    if d.empty or d[npv].std() == 0:
        return None
    d = d.set_index(["knr", "t"])
    X = d[xs].astype(float)
    if tid_fe == "mnd":
        X = pd.concat([X, pd.get_dummies(d.mnd, prefix="m", drop_first=True).astype(float)], axis=1)
    elif tid_fe == "aar":
        X = pd.concat([X, pd.get_dummies(d.aar_s, prefix="y", drop_first=True).astype(float)], axis=1)
    kw = dict(entity_effects=True, time_effects=(tid_fe == "aar_x_mnd"), drop_absorbed=True)
    if vekt:
        kw["weights"] = d["n_mp"].astype(float)
    try:
        res = PanelOLS(d[yv].astype(float), X, **kw).fit(cov_type="unadjusted")
    except Exception as e:                                    # kollinearitet o.l.
        log(f"  hopper over ({yv}, {npv}, {tid_fe}): {type(e).__name__}")
        return None
    par = res.params
    if npv not in par.index or egdv not in par.index:
        return None
    return {
        "b_egd": par[egdv], "b_spot": par["spot_ore_kwh"],
        "b_innt_1000": par.get("innt_1000", np.nan), "b_log_innt": par.get("log_innt", np.nan),
        "b_np": par[npv],
        "r2_within": res.rsquared_within, "r2_overall": res.rsquared_overall,
        "r2_ols_dummyer": res.rsquared_inclusive,
        "N": int(res.nobs), "n_kommuner": d.index.get_level_values(0).nunique(),
        "mean_y": float(d[yv].mean()),
    }


# Enhetsvalg. Kjernen er estimert med spot i øre/kWh og inntekt i 1 000 kr.
SPOT_ENHETER = {"ore_per_kwh": 1.0, "kr_per_mwh": 10.0, "kr_per_kwh": 0.01}
INNT_ENHETER = {"kr": 1 / 1000, "1000_kr": 1.0, "10000_kr": 10.0, "100000_kr": 100.0}


def ekspander(kjerne):
    """Én kjernemodell -> rader for hver kombinasjon av spot- og inntektsenhet."""
    ut = []
    if kjerne["innt_form"] == "log":
        innt_valg = [("log", kjerne["b_log_innt"])]
    else:
        innt_valg = [(navn, kjerne["b_innt_1000"] * f) for navn, f in INNT_ENHETER.items()]
    for (s_navn, s_f), (i_navn, b_innt) in itertools.product(SPOT_ENHETER.items(), innt_valg):
        r = dict(kjerne)
        r["spot_enhet"] = s_navn
        r["innt_enhet"] = i_navn
        r["b_spot_enhet"] = kjerne["b_spot"] / s_f
        r["b_innt_enhet"] = b_innt
        ut.append(r)
    return ut


def avstand(r):
    """Relativt avvik per koeffisient + beste R2-variant."""
    d_egd = abs(r["b_egd"] - NRK["egd"]) / abs(NRK["egd"])
    d_spot = abs(r["b_spot_enhet"] - NRK["spot"]) / abs(NRK["spot"])
    d_np = abs(r["b_np"] - NRK["np"]) / abs(NRK["np"])
    d_innt = abs(r["b_innt_enhet"] - NRK["innt"]) / abs(NRK["innt"])
    r2navn = ["r2_within", "r2_overall", "r2_ols_dummyer"]
    d_r2 = [abs(r[k] - NRK_R2) / NRK_R2 for k in r2navn]
    j = int(np.argmin(d_r2))
    r.update({"avvik_egd": d_egd, "avvik_spot": d_spot, "avvik_np": d_np,
              "avvik_innt": d_innt, "avvik_r2": d_r2[j], "r2_variant": r2navn[j],
              "avvik_koef_sum": d_egd + d_spot + d_np + d_innt,
              "avstand": d_egd + d_spot + d_np + d_innt + d_r2[j]})
    return r


# ---------------------------------------------------------------- rutenett

def np_tid_kombinasjoner():
    """År x måned-FE gjør 0/1-dummyen kollineær; kjøres bare for andelsvariantene."""
    for npn in NP_VARS:
        fes = ["ingen", "mnd", "aar"] + ([] if npn in DUMMY_NP else ["aar_x_mnd"])
        for fe in fes:
            yield npn, fe


def main():
    t0 = time.time()
    p = load_panel()
    log(f"Panel: {p.knr.nunique()} kommuner, {p.maned.min()}-{p.maned.max()}, {len(p)} rader")
    log("pa_kilde:", p.drop_duplicates('knr').pa_kilde.value_counts().to_dict())

    kjerner = []

    def kjor(yn, egd_navn, npn, areal, innt_form, fe, vekt, utvalg):
        d = SAMPLES[utvalg](p)
        egdv = {"base17": "egd17", "base18": "egd18"}[egd_navn]
        r = fit_one(d, Y_VARS[yn], egdv, NP_VARS[npn], areal, innt_form, fe, vekt)
        if r is None:
            return
        r.update({"y": yn, "gradtall": egd_navn, "np_variabel": npn,
                  "bruksareal": "med" if areal else "uten", "innt_form": innt_form,
                  "tids_fe": fe, "vekting": "n_mp" if vekt else "uvektet", "utvalg": utvalg})
        kjerner.append(r)

    # (1) Hovedrutenett: log-venstresider, alle np/tids-FE-kombinasjoner
    for yn in ["log_kwh", "log_kwh_per_maler"]:
        for npn, fe in np_tid_kombinasjoner():
            for areal in (True, False):
                for innt_form in ("lineaer", "log"):
                    for vekt in (False, True):
                        for utvalg in SAMPLES:
                            kjor(yn, "base17", npn, areal, innt_form, fe, vekt, utvalg)
    log(f"Hovedrutenett: {len(kjerner)} kjernemodeller ({time.time()-t0:.0f} s)")

    # (2) Nivå-venstresider (redusert: koeffisientene har en annen tolkning)
    n0 = len(kjerner)
    for yn in ["kwh_nivaa", "kwh_per_maler_nivaa"]:
        for npn, fe in np_tid_kombinasjoner():
            for areal in (True, False):
                kjor(yn, "base17", npn, areal, "lineaer", fe, False, "alle")
    log(f"Nivåmodeller: {len(kjerner)-n0}")

    # (3) Gradtall med base 18 grader (redusert rutenett)
    n0 = len(kjerner)
    if p.egd18.notna().any():
        for npn, fe in np_tid_kombinasjoner():
            for areal in (True, False):
                for vekt in (False, True):
                    kjor("log_kwh", "base18", npn, areal, "lineaer", fe, vekt, "alle")
    log(f"Base 18-modeller: {len(kjerner)-n0}")

    rader = [avstand(r) for k in kjerner for r in ekspander(k)]
    df = pd.DataFrame(rader)
    kols = ["y", "np_variabel", "tids_fe", "bruksareal", "innt_form", "innt_enhet",
            "spot_enhet", "gradtall", "vekting", "utvalg", "N", "n_kommuner",
            "b_egd", "b_spot_enhet", "b_np", "b_innt_enhet",
            "r2_within", "r2_overall", "r2_ols_dummyer", "mean_y",
            "avvik_egd", "avvik_spot", "avvik_np", "avvik_innt", "avvik_r2",
            "r2_variant", "avvik_koef_sum", "avstand"]
    df = df[kols].sort_values("avstand").reset_index(drop=True)
    df.to_csv(OUT / "tab_nrk_spes_sok.csv", index=False, encoding="utf-8")
    log(f"{len(kjerner)} kjernemodeller -> {len(df)} rader i tab_nrk_spes_sok.csv")

    # ---------- dimensjonstabell: hva gjør hver dimensjon med post_np isolert
    basis = dict(yn="log_kwh", egd_navn="base17", npn="post_okt2025", areal=True,
                 innt_form="lineaer", fe="ingen", vekt=False, utvalg="alle")

    def hent(**endring):
        s = dict(basis); s.update(endring)
        d = SAMPLES[s["utvalg"]](p)
        egdv = {"base17": "egd17", "base18": "egd18"}[s["egd_navn"]]
        return fit_one(d, Y_VARS[s["yn"]], egdv, NP_VARS[s["npn"]], s["areal"],
                       s["innt_form"], s["fe"], s["vekt"])

    dim = []
    b0 = hent()
    dim.append({"dimensjon": "(basislinje)", "verdi": "log kWh, 0/1 fra okt 2025, med bruksareal, "
                "inntekt lineær, ingen tids-FE, uvektet, alle kommuner",
                "b_np": b0["b_np"], "r2_within": b0["r2_within"], "r2_ols_dummyer": b0["r2_ols_dummyer"]})
    varianter = (
        [("Venstreside", v, {"yn": v}) for v in Y_VARS if v != "log_kwh"] +
        [("Norgespris-variabel", v, {"npn": v}) for v in NP_VARS if v != "post_okt2025"] +
        [("Tids-FE", v, {"fe": v}) for v in ["mnd", "aar"]] +
        [("Tids-FE (andel)", "aar_x_mnd + andel_privat", {"fe": "aar_x_mnd", "npn": "andel_privat"})] +
        [("Bruksareal", "uten", {"areal": False})] +
        [("Inntektsform", "log", {"innt_form": "log"})] +
        [("Vekting", "n_mp", {"vekt": True})] +
        [("Utvalg", v, {"utvalg": v}) for v in SAMPLES if v != "alle"] +
        [("Gradtall", "base18", {"egd_navn": "base18"})]
    )
    for navn, verdi, endring in varianter:
        r = hent(**endring)
        if r is None:
            continue
        dim.append({"dimensjon": navn, "verdi": verdi, "b_np": r["b_np"],
                    "r2_within": r["r2_within"], "r2_ols_dummyer": r["r2_ols_dummyer"]})
    dimdf = pd.DataFrame(dim)
    dimdf["endring_vs_basis"] = dimdf.b_np - b0["b_np"]
    dimdf.to_csv(OUT / "tab_nrk_spes_sok_dimensjoner.csv", index=False, encoding="utf-8")

    # ---------- markdown
    topp = df.head(15)
    md = ["# Spesifikasjonssøk mot NRKs koeffisienter", "",
          "Alle tall er **til godkjenning**. Kilde for målene: NRKs metodeboks "
          "(`kilder/nrk_prisen_for_billig_strom.md`, linje 251–285): "
          "energigradtall 0,0019, spotpris −0,0005, Norgespris 0,0822, medianinntekt 0,0024, R² 93,76 prosent.",
          "",
          f"Panel: {p.knr.nunique()} kommuner, {p.maned.min()}–{p.maned.max()}. "
          f"{len(kjerner)} kjernemodeller × enhetsvalg = {len(df)} kjøringer.",
          "",
          "Avstand = sum av relative avvik på de fire koeffisientene + relativt avvik i beste R²-variant.",
          "", "## Topp 15 nærmeste spesifikasjoner", "",
          "| # | y | Norgespris | tids-FE | areal | inntekt | spot | vekting | utvalg | egd | spot | np | innt | R² (variant) | avstand |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]

    def nf(x, n=5):
        """Norsk tallformat: desimalkomma og ekte minustegn (U+2212)."""
        if x is None or (isinstance(x, float) and np.isnan(x)):
            return "absorbert"
        return f"{x:.{n}f}".replace(".", ",").replace("-", "−")

    for i, r in topp.iterrows():
        md.append(f"| {i+1} | {r.y} | {r.np_variabel} | {r.tids_fe} | {r.bruksareal} | "
                  f"{r.innt_form}/{r.innt_enhet} | {r.spot_enhet} | {r.vekting} | {r.utvalg} | "
                  f"{nf(r.b_egd)} | {nf(r.b_spot_enhet)} | {nf(r.b_np, 4)} | {nf(r.b_innt_enhet)} | "
                  f"{nf(r[r.r2_variant], 4)} ({r.r2_variant}) | {nf(r.avstand, 3)} |")

    md += ["", "## Beste treff per koeffisient (uansett øvrig spesifikasjon)", "",
           "| Koeffisient | NRK | beste verdi | avvik | spesifikasjon |", "|---|---|---|---|---|"]
    for navn, kol, avk, mal in [("energigradtall", "b_egd", "avvik_egd", NRK["egd"]),
                                ("spotpris", "b_spot_enhet", "avvik_spot", NRK["spot"]),
                                ("Norgespris", "b_np", "avvik_np", NRK["np"]),
                                ("medianinntekt", "b_innt_enhet", "avvik_innt", NRK["innt"])]:
        b = df.loc[df[avk].idxmin()]
        md.append(f"| {navn} | {nf(mal)} | {nf(b[kol])} | {nf(b[avk]*100, 1)} prosent | "
                  f"{b.y}, {b.np_variabel}, tids-FE {b.tids_fe}, areal {b.bruksareal}, "
                  f"inntekt {b.innt_form}/{b.innt_enhet}, spot {b.spot_enhet}, {b.vekting}, {b.utvalg}, {b.gradtall} |")

    md += ["", "## Hva hver dimensjon gjør med Norgespris-koeffisienten isolert", "",
           "Basislinjen er M1-oppsettet; én dimensjon endres om gangen.", "",
           "| Dimensjon | Verdi | koeffisient | endring vs. basis | R² within | R² OLS m/dummyer |",
           "|---|---|---|---|---|---|"]
    for _, r in dimdf.iterrows():
        md.append(f"| {r.dimensjon} | {r.verdi} | {nf(r.b_np, 4)} | {nf(r.endring_vs_basis, 4)} | "
                  f"{nf(r.r2_within, 4)} | {nf(r.r2_ols_dummyer, 4)} |")

    md += ["", "## Koeffisientspenn per tids-FE (log-venstresider, spot i øre/kWh)", "",
           "Viser hvilke tids-FE-valg som i det hele tatt kan gi NRKs nivåer.", "",
           "| Tids-FE | egd | spot | Norgespris | R² within |", "|---|---|---|---|---|"]
    sub = df[(df.spot_enhet == "ore_per_kwh") & (df.y.str.startswith("log"))
             & (df.innt_enhet.isin(["1000_kr", "log"]))]
    for fe, g in sub.groupby("tids_fe"):
        md.append(f"| {fe} | {nf(g.b_egd.min())} til {nf(g.b_egd.max())} | "
                  f"{nf(g.b_spot_enhet.min())} til {nf(g.b_spot_enhet.max())} | "
                  f"{nf(g.b_np.min(), 4)} til {nf(g.b_np.max(), 4)} | "
                  f"{nf(g.r2_within.min(), 4)} til {nf(g.r2_within.max(), 4)} |")
    md.append("")
    md.append(f"NRKs verdier: egd 0,0019, spot −0,0005, Norgespris 0,0822, R² 0,9376.")

    # ---------- periodefølsomhet (NRK har 2021 og mai-juni 2026, vi har ikke)
    per = []
    for lbl, lo, hi in [("hele panelet", "2022-02", "2026-04"),
                        ("2022-02–2024-12 (før Norgespris, ingen framskrevet inntekt)", "2022-02", "2024-12"),
                        ("2023-01–2026-04", "2023-01", "2026-04"),
                        ("2024-01–2026-04", "2024-01", "2026-04"),
                        ("2022-02–2025-09 (før Norgespris)", "2022-02", "2025-09")]:
        d = p[(p.maned >= lo) & (p.maned <= hi)]
        npn = "post_okt2025" if d.post_np.std() > 0 else None
        if npn is None:
            xs = ["egd17", "spot_ore_kwh", "innt_1000", "snitt_bruksareal_m2"]
            dd = d.dropna(subset=["log_kwh"] + xs).set_index(["knr", "t"])
            res = PanelOLS(dd["log_kwh"].astype(float), dd[xs].astype(float),
                           entity_effects=True, drop_absorbed=True).fit(cov_type="unadjusted")
            r = {"b_egd": res.params["egd17"], "b_spot": res.params["spot_ore_kwh"],
                 "b_innt_1000": res.params["innt_1000"], "b_np": np.nan,
                 "r2_within": res.rsquared_within, "N": int(res.nobs)}
        else:
            r = fit_one(d, "log_kwh", "egd17", "post_np", True, "lineaer", "ingen", False)
        r["periode"] = lbl
        per.append(r)
    perdf = pd.DataFrame(per)[["periode", "N", "b_egd", "b_spot", "b_innt_1000", "b_np", "r2_within"]]
    perdf.to_csv(OUT / "tab_nrk_spes_sok_periode.csv", index=False, encoding="utf-8")
    md += ["", "## Periodefølsomhet (M1-oppsettet, ulike delperioder)", "",
           "NRK har 2021 og mai–juni 2026 i sitt datasett; vi har ikke kommunetall for disse månedene.",
           "", "| Periode | N | egd | spot | inntekt (1 000 kr) | Norgespris | R² within |",
           "|---|---|---|---|---|---|---|"]
    for _, r in perdf.iterrows():
        npv = "ikke identifisert" if pd.isna(r.b_np) else nf(r.b_np, 4)
        md.append(f"| {r.periode} | {r.N} | {nf(r.b_egd)} | {nf(r.b_spot)} | {nf(r.b_innt_1000)} | "
                  f"{npv} | {nf(r.r2_within, 4)} |")

    md += ["", "## Datadekning", "",
           f"- Elhubs kommunefil dekker {p.maned.min()}–{p.maned.max()}. NRK oppgir 2021–juni 2026.",
           "- Rådataene i `data/raw/` inneholder ikke kommunetall for 2021 eller mai–juni 2026, "
           "så perioden kan ikke utvides uten et nytt uttrekk.", ""]
    (OUT / "tab_nrk_spes_sok.md").write_text("\n".join(md), encoding="utf-8")
    log(f"Ferdig på {time.time()-t0:.0f} s. Topp 5:")
    log(topp.head(5)[["y", "np_variabel", "tids_fe", "innt_enhet", "spot_enhet", "vekting",
                      "b_egd", "b_spot_enhet", "b_np", "b_innt_enhet", "r2_variant", "avstand"]].to_string())
    (OUT / "log_s18.txt").write_text(LOG.getvalue(), encoding="utf-8")


if __name__ == "__main__":
    main()
