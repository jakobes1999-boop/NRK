"""Steg 7: Faste-effekter-regresjoner – replikasjon av NRK og robusthet.

NRK (log husholdningsforbruk, kommune-FE):
  EGD 0,0019***   spotpris −0,0005***   Norgespris 0,0822***   medianinntekt 0,0024***   R² 93,8 %

Spesifikasjoner:
  M1  NRK-lik: kommune-FE, post-dummy for Norgespris, ingen tids-FE
  M2  M1 + kalendermåned-FE (sesong)            – post-dummy fortsatt identifisert
  M3  M1 + år×måned-FE                          – post-dummy IKKE identifisert (kollineær) →
      erstattes med andel målere på Norgespris (np_andel), som varierer mellom kommuner
  M4  M3 med Y = log kWh per målepunkt
  M5  Placebo: «Norgespris» satt til 2024-10 på data t.o.m. 2025-09 (M1-oppsett)
Klustrede standardfeil på kommune.
"""
import pandas as pd
import numpy as np
from linearmodels.panel import PanelOLS
from config import PROC, OUT, NORGESPRIS_START

STARS = lambda p: "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""


DK = []   # Driscoll-Kraay-standardfeil for rene tidsvariabler (post_np er lik for alle kommuner)


def fit(df, y, xs, time_fe=False, label="", mnd_fe=False):
    d = df.dropna(subset=[y] + xs).copy()
    d["t"] = pd.PeriodIndex(d.maned, freq="M").to_timestamp()
    d = d.set_index(["knr", "t"])
    X = d[xs]
    if not time_fe and mnd_fe:
        X = pd.concat([X, pd.get_dummies(d.mnd, prefix="m", drop_first=True).astype(float)], axis=1)
    mod = PanelOLS(d[y], X, entity_effects=True, time_effects=time_fe, drop_absorbed=True)
    res = mod.fit(cov_type="clustered", cluster_entity=True)
    tab = pd.DataFrame({"koef": res.params, "se": res.std_errors, "p": res.pvalues})
    tab["stjerner"] = tab.p.map(STARS)
    if "post_np" in xs:
        # Klustring på kommune er ugyldig for en variabel uten tverrsnittsvariasjon; Driscoll-Kraay (kernel) tar
        # hensyn til felles sjokk over tid. Rapporteres ved siden av.
        dk = mod.fit(cov_type="kernel", kernel="bartlett")
        DK.append({"modell": label, "koef": dk.params["post_np"], "se_kluster": res.std_errors["post_np"],
                   "se_driscoll_kraay": dk.std_errors["post_np"], "p_driscoll_kraay": dk.pvalues["post_np"]})
        print(f"   post_np: se kluster {res.std_errors['post_np']:.4f} vs Driscoll-Kraay {dk.std_errors['post_np']:.4f} (p={dk.pvalues['post_np']:.3f})")
    tab = tab.loc[[x for x in xs if x in tab.index]]
    tab["modell"] = label
    tab.attrs["r2_within"] = res.rsquared_within
    tab.attrs["r2_overall"] = res.rsquared_overall
    tab.attrs["n"] = res.nobs
    print(f"\n== {label} ==  N={res.nobs}  R²(within)={res.rsquared_within:.3f}  R²(overall)={res.rsquared_overall:.3f}")
    print(tab[["koef", "se", "p", "stjerner"]].round(5).to_string())
    return tab


def main():
    p = pd.read_parquet(PROC / "panel.parquet")
    p["innt_1000"] = p.median_innt_etter_skatt / 1000
    has_egd = "egd" in p.columns and p.egd.notna().mean() > 0.9
    weather = ["egd"] if has_egd else []
    if not has_egd:
        print("Ingen gradtall: M1 kjøres med kalendermåned-dummyer som værproxy")
    base = weather + ["spot_ore_kwh", "innt_1000", "snitt_bruksareal_m2"]
    tabs = []
    tabs.append(fit(p, "log_kwh", base + ["post_np"], label="M1 NRK-lik", mnd_fe=not has_egd))
    tabs.append(fit(p, "log_kwh_mp", base + ["post_np"], label="M1b NRK-lik, per målepunkt", mnd_fe=not has_egd))
    tabs.append(fit(p, "log_kwh", base + ["post_np"], label="M2 + kalendermåned", mnd_fe=True))
    tabs.append(fit(p, "log_kwh_mp", base + ["post_np"], label="M2b + kalendermåned, per målepunkt", mnd_fe=True))
    tabs.append(fit(p, "log_kwh", base + ["np_andel"], time_fe=True, label="M3 år×måned-FE, andel Norgespris (Privat)"))
    tabs.append(fit(p, "log_kwh_mp", base + ["np_andel"], time_fe=True, label="M4 som M3, per målepunkt"))
    tabs.append(fit(p, "log_kwh_mp", base + ["np_andel_hh"], time_fe=True, label="M4b som M4, husholdningsandel"))
    pre = p[p.maned < NORGESPRIS_START[:7]].copy()
    pre["post_np"] = (pre.maned >= "2024-10").astype(int)
    tabs.append(fit(pre, "log_kwh", base + ["post_np"], label="M5 placebo 2024-10 (data ≤ 2025-09)"))
    tabs.append(fit(pre, "log_kwh_mp", base + ["post_np"], label="M5b placebo, per målepunkt"))
    pd.DataFrame(DK).to_csv(OUT / "tab_fe_driscoll_kraay.csv", index=False)

    # Semi-elastisitet → prosent
    allt = pd.concat(tabs)
    allt["pst_effekt"] = np.where(allt.index.isin(["post_np", "np_andel", "np_andel_hh"]), (np.exp(allt.koef) - 1) * 100, np.nan)
    allt.to_csv(OUT / "tab_fe_resultater.csv")
    summ = pd.DataFrame([{"modell": t.modell.iloc[0], "N": t.attrs["n"],
                          "R2_within": t.attrs["r2_within"], "R2_overall": t.attrs["r2_overall"]} for t in tabs])
    summ.to_csv(OUT / "tab_fe_modellmaal.csv", index=False)
    print("\n", summ.round(3).to_string(index=False))

    # Event-study: effekt per måned etter oktober 2025 på np_andel × måned (M3-oppsett)
    ev = p.copy()
    post_m = sorted(ev.loc[ev.post_np == 1, "maned"].unique())
    cols = []
    for m in post_m:
        c = f"np_x_{m}"; ev[c] = ev.np_andel * (ev.maned == m); cols.append(c)
    t = fit(ev, "log_kwh", base + cols, time_fe=True, label="Event-study andel×måned")
    t.to_csv(OUT / "tab_event_study.csv")


if __name__ == "__main__":
    main()
