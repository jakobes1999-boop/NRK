"""Steg 15: Effektiv marginalpris for husholdninger med strømstøtte, og modellvarianter.

Bakgrunn (kritikk pkt. B, ARBEIDSLOGG.md 05.09.2026): ingen av NRKs eller våre egne modeller til nå
bruker prisen husholdningene faktisk møtte på marginen – de bruker spotprisen før strømstøtte.
Strømstøtten dekker en andel av spotprisen over en terskel (månedsbasis t.o.m. aug. 2023, timebasis
fra sep. 2023); Norgespris-kunder (fra okt. 2025) betaler i stedet en fast pris uavhengig av spot.
Parametre og kilder: kilder/stromstotte_parametre.md (regjeringen.no, lovdata.no, hvakosterstrommen.no).

p_eff (eks. mva) for husholdning UTEN Norgespris, per prisområde × måned:
  månedsbasis (t.o.m. 2023-08): p_eff = p_snitt - andel * max(p_snitt - terskel, 0)
  timebasis    (fra 2023-09):   p_eff_time_t = p_t - andel * max(p_t - terskel, 0), deretter månedssnitt
Norgespris: p_np = 40 øre/kWh eks. mva fra 2025-10 (husholdning, tak 5000 kWh/mnd, ikke strømstøtte
samtidig på samme målepunkt – se kilder-fil).

Modellene i del 2 gjenbruker fit-mønsteret fra s07 (PanelOLS, kommune-FE, Driscoll-Kraay for
tidsdummyer) og s10 (statsmodels-formel, kommune×kalendermåned-FE, egd×kommune) direkte via import –
ingen kode dupliseres, og s07/s10 sine egne output-filer berøres ikke (deres main() kjøres ikke).
"""
import numpy as np
import pandas as pd
from config import PROC, OUT, RAW, NORGESPRIS_START

import s07_estimate_fe as s07
import s10_forbedret_modell as s10

AREAS = ["NO1", "NO2", "NO5"]
MVA = 1.25
NORGESPRIS_ORE_EKS_MVA = 40.0
POST = NORGESPRIS_START[:7]

# Strømstøtteparametre – kilde og verifisering: kilder/stromstotte_parametre.md
# (fra_maned, til_maned_inkl, dekningsgrad, terskel_ore_kwh_eks_mva, basis)
PARAMS = [
    ("2021-12", "2021-12", 0.55, 70.0, "maned"),
    ("2022-01", "2022-08", 0.80, 70.0, "maned"),
    ("2022-09", "2023-03", 0.90, 70.0, "maned"),
    ("2023-04", "2023-05", 0.80, 70.0, "maned"),
    ("2023-06", "2023-08", 0.90, 70.0, "maned"),
    ("2023-09", "2023-12", 0.90, 70.0, "time"),
    ("2024-01", "2024-12", 0.90, 73.0, "time"),
    ("2025-01", "2025-12", 0.90, 75.0, "time"),
    ("2026-01", "2026-12", 0.90, 77.0, "time"),
]


def params_for_maned(m):
    for fra, til, andel, terskel, basis in PARAMS:
        if fra <= m <= til:
            return andel, terskel, basis
    return np.nan, np.nan, None


def bygg_effektiv_pris():
    """Time for time spotpris (eks. mva) -> p_eff per prisområde × måned."""
    df = pd.read_parquet(RAW / "spot_hourly.parquet")
    df = df[df.area.isin(AREAS)].copy()
    df["ore"] = df.NOK_per_kWh * 100.0                    # NOK/kWh -> øre/kWh, eks. mva
    df["maned"] = df.time_start.str[:7]
    df["time_lokal"] = df.time_start.str[11:13].astype(int)  # lokal time inkl. i offset i time_start
    df["vekt_kveld"] = np.where(df.time_lokal.between(17, 21), 2.0, 1.0)  # robusthet: kveld 17-21 vektet dobbelt

    par = df.maned.map(params_for_maned)
    df["andel"] = [t[0] for t in par]
    df["terskel"] = [t[1] for t in par]
    df["basis"] = [t[2] for t in par]
    før = len(df)
    df = df.dropna(subset=["andel"]).copy()
    if len(df) < før:
        print(f"  {før - len(df)} timer utenfor definerte strømstøtteperioder droppet (før des. 2021 / etter des. 2026)")

    df["p_eff_time"] = df.ore - df.andel * (df.ore - df.terskel).clip(lower=0)

    rows = []
    for (area, maned), g in df.groupby(["area", "maned"], observed=True):
        basis = g.basis.iloc[0]
        andel, terskel = g.andel.iloc[0], g.terskel.iloc[0]
        p_snitt = g.ore.mean()
        p_snitt_kveld = np.average(g.ore, weights=g.vekt_kveld)
        if basis == "maned":
            p_eff = p_snitt - andel * max(p_snitt - terskel, 0)
            p_eff_kveld = p_snitt_kveld - andel * max(p_snitt_kveld - terskel, 0)
        else:
            p_eff = g.p_eff_time.mean()
            p_eff_kveld = np.average(g.p_eff_time, weights=g.vekt_kveld)
        rows.append(dict(prisomrade=area, maned=maned, spot_ore_kwh=p_snitt, spot_ore_kwh_kveldsveid=p_snitt_kveld,
                          p_eff=p_eff, p_eff_kveldsveid=p_eff_kveld, andel=andel, terskel_ore=terskel,
                          basis=basis, n_timer=len(g)))
    tab = pd.DataFrame(rows).sort_values(["prisomrade", "maned"]).reset_index(drop=True)
    tab["p_eff_inkl_mva"] = tab.p_eff * MVA
    tab["p_eff_kveldsveid_inkl_mva"] = tab.p_eff_kveldsveid * MVA
    tab["p_np"] = np.where(tab.maned >= POST, NORGESPRIS_ORE_EKS_MVA, np.nan)
    tab["p_np_inkl_mva"] = tab.p_np * MVA
    tab["spot_minus_p_eff"] = tab.spot_ore_kwh - tab.p_eff
    return tab


def kontroll_mot_panel(tab):
    p = pd.read_parquet(PROC / "panel.parquet")
    ref = p.groupby(["prisomrade", "maned"], observed=True).apply(
        lambda x: np.average(x.spot_ore_kwh, weights=x.n_mp), include_groups=False).rename("spot_panel").reset_index()
    chk = tab.merge(ref, on=["prisomrade", "maned"], how="inner")
    chk["diff"] = chk.spot_ore_kwh - chk.spot_panel
    print(f"Kontroll mot panel.spot_ore_kwh: {len(chk)} område-måneder, snitt |diff| = {chk['diff'].abs().mean():.3f} øre/kWh, "
          f"maks |diff| = {chk['diff'].abs().max():.3f} øre/kWh")
    return chk


def vintertabell(tab):
    """Des-feb per vinter 2021/22 .. 2025/26, snitt over prisområder (enkelt snitt av områdene)."""
    vintre = {
        "2021/22": ["2021-12", "2022-01", "2022-02"],
        "2022/23": ["2022-12", "2023-01", "2023-02"],
        "2023/24": ["2023-12", "2024-01", "2024-02"],
        "2024/25": ["2024-12", "2025-01", "2025-02"],
        "2025/26": ["2025-12", "2026-01", "2026-02"],
    }
    rows = []
    for vinter, maneder in vintre.items():
        sub = tab[tab.maned.isin(maneder)]
        if sub.empty:
            continue
        rows.append(dict(vinter=vinter, spot=sub.spot_ore_kwh.mean(), p_eff=sub.p_eff.mean(),
                          diff=sub.spot_minus_p_eff.mean(),
                          diff_pst=100 * sub.spot_minus_p_eff.mean() / sub.spot_ore_kwh.mean(),
                          n_omrade_maneder=len(sub)))
    return pd.DataFrame(rows)


def merge_med_panel(tab):
    p = pd.read_parquet(PROC / "panel.parquet")
    m = p.merge(tab[["prisomrade", "maned", "p_eff", "p_eff_inkl_mva", "p_np"]], on=["prisomrade", "maned"], how="left")
    if m.p_eff.isna().any():
        manglende = sorted(m.loc[m.p_eff.isna(), "maned"].unique())
        print(f"  ADVARSEL: {m.p_eff.isna().sum()} panelrader uten p_eff (måneder: {manglende})")
    m["log_p_eff"] = np.log(m.p_eff)
    m["log_spot"] = np.log(m.spot_ore_kwh)
    return m


def modeller(m):
    tabs = []
    has_egd = "egd" in m.columns and m.egd.notna().mean() > 0.9
    xs_eff = (["egd"] if has_egd else []) + ["log_p_eff", "log_innt", "post_np"]
    xs_spot = (["egd"] if has_egd else []) + ["log_spot", "log_innt", "post_np"]
    # Eksakt s07-M1-spesifikasjon (nivå-spot, inntekt i 1000 kr, boligareal) med p_eff i nivå (kritikk 4, V1)
    m["innt_1000"] = m.median_innt_etter_skatt / 1000
    xs_ex_spot = ["egd", "spot_ore_kwh", "innt_1000", "snitt_bruksareal_m2", "post_np"]
    xs_ex_eff = ["egd", "p_eff", "innt_1000", "snitt_bruksareal_m2", "post_np"]
    tabs.append(s07.fit(m, "log_kwh", xs_ex_spot, mnd_fe=False, label="M1 s07-spesifikasjon, spot i nivå"))
    tabs.append(s07.fit(m, "log_kwh", xs_ex_eff, mnd_fe=False, label="M1e s07-spesifikasjon, p_eff i nivå"))
    tabs.append(s07.fit(m, "log_kwh", xs_ex_spot, mnd_fe=True, label="M2 s07-spesifikasjon, spot i nivå"))
    tabs.append(s07.fit(m, "log_kwh", xs_ex_eff, mnd_fe=True, label="M2e s07-spesifikasjon, p_eff i nivå"))

    # Sammenligningsgrunnlag: samme spesifikasjon som M1e/M2e, men med log(spot) i stedet for log(p_eff)
    tabs.append(s07.fit(m, "log_kwh", xs_spot, mnd_fe=False, label="M1 sammenligning, log(spot)"))
    tabs.append(s07.fit(m, "log_kwh", xs_eff, mnd_fe=False, label="M1e NRK-lik med log(p_eff)"))
    tabs.append(s07.fit(m, "log_kwh", xs_spot, mnd_fe=True, label="M2 sammenligning, log(spot) + kalendermåned"))
    tabs.append(s07.fit(m, "log_kwh", xs_eff, mnd_fe=True, label="M2e + kalendermåned, log(p_eff)"))

    # F2e: som s10 sin F2 (egd × kommune, husholdningsandel), men med område×måned-prisen log(p_eff) lagt til.
    # OBS: log(p_eff) varierer kun over TRE prisområder × måned – identifiseres i praksis fra område×måned-
    # variasjon på toppen av C(maned)-FE, dvs. kun forskjeller MELLOM de tre områdene innad i hver måned.
    # Svak identifikasjon med bare tre områder; koeffisienten rapporteres, men tolkes med forsiktighet.
    p2, w2, mean_share2 = s10.prep(m)
    base = "C(knr) + C(maned)"
    r_f2e = s10.fit(p2, f"log_kwh_mp ~ {base} + egd:C(knr) + share_post + log_p_eff",
                     ["share_post", "log_p_eff"], "F2e + log(p_eff) [3 prisområder – svak identifikasjon, se merknad]", "knr")
    print("  F2e: log_p_eff identifiseres kun av variasjon MELLOM NO1/NO2/NO5 innen hver kalendermåned (3 grupper) – flagges.")

    # Prisgap-modell: for bestillere er marginalprisen 40 øre fra okt. 2025; for ikke-bestillere p_eff.
    # gap = log(p_eff) - log(40) i postperioden (0 i førperioden, hvor Norgespris ikke finnes).
    # np_andel_hh er den LØPENDE husholdningsandelen (ikke s10 sin faste "share") - i tråd med bestillingen.
    g = m.copy()
    er_post = g.maned >= POST
    g["gap"] = np.where(er_post, np.log(g.p_eff) - np.log(NORGESPRIS_ORE_EKS_MVA), 0.0)
    g["gap_x"] = g.np_andel_hh * g.gap
    r_gap = s10.fit(g, f"log_kwh_mp ~ {base} + egd:C(knr) + gap_x", ["gap_x"],
                     "Prisgap: np_andel_hh x (log p_eff - log 40)", "knr")
    elastisitet = -r_gap.params["gap_x"]   # gap > 0 og positiv koeffisient = forbruket øker når marginalprisen faller: egenpriselastisitet negativ
    r_gap.snitt_gap = float(g.loc[er_post & (g.np_andel_hh > 0), "gap"].mean()); r_gap.did_elast = -0.0299 / r_gap.snitt_gap
    print(f"  Prisgap-modell: implisert egenpriselastisitet (np_andel_hh=1) = {elastisitet:.4f}; snittgap post {r_gap.snitt_gap:.3f}; D7-implisert {r_gap.did_elast:.3f}")

    allt = pd.concat(tabs)
    allt["pst_effekt"] = np.where(allt.index.isin(["post_np"]), (np.exp(allt.koef) - 1) * 100, np.nan)
    allt.to_csv(OUT / "tab_effektiv_pris_modeller.csv")

    rows_extra = pd.DataFrame([
        {"modell": "F2e + log(p_eff)", "term": "share_post", "koef": r_f2e.params["share_post"], "se": r_f2e.bse["share_post"], "p": r_f2e.pvalues["share_post"], "N": int(r_f2e.nobs)},
        {"modell": "F2e + log(p_eff)", "term": "log_p_eff", "koef": r_f2e.params["log_p_eff"], "se": r_f2e.bse["log_p_eff"], "p": r_f2e.pvalues["log_p_eff"], "N": int(r_f2e.nobs)},
        {"modell": "Prisgap", "term": "gap_x", "koef": r_gap.params["gap_x"], "se": r_gap.bse["gap_x"], "p": r_gap.pvalues["gap_x"], "N": int(r_gap.nobs)},
    ])
    with open(OUT / "tab_effektiv_pris_modeller.csv", "a", encoding="utf-8") as f:
        f.write("\n# F2e og prisgap (statsmodels-formel, ikke PanelOLS-format over):\n")
        rows_extra.to_csv(f, index=False)

    return allt, r_f2e, r_gap, elastisitet


def main():
    print("== Bygger effektiv marginalpris per prisområde × måned ==")
    tab = bygg_effektiv_pris()
    kontroll_mot_panel(tab)
    tab.to_parquet(PROC / "effektiv_pris_pa_maned.parquet", index=False)
    tab.round(4).to_csv(OUT / "tab_effektiv_pris.csv", index=False,
                         columns=["prisomrade", "maned", "spot_ore_kwh", "p_eff", "p_eff_kveldsveid",
                                  "p_eff_inkl_mva", "p_np", "p_np_inkl_mva", "spot_minus_p_eff", "andel", "terskel_ore", "basis"])
    print(f"Skrevet {len(tab)} rader til data/processed/effektiv_pris_pa_maned.parquet og output/tab_effektiv_pris.csv")

    vinter = vintertabell(tab)
    print("\nVintermåneder (des-feb), snitt over NO1/NO2/NO5, øre/kWh eks. mva:")
    print(vinter.round(3).to_string(index=False))

    print("\n== Kobler p_eff på kommunepanelet og estimerer ==")
    m = merge_med_panel(tab)
    allt, r_f2e, r_gap, elastisitet = modeller(m)

    m1 = allt[allt.modell == "M1 sammenligning, log(spot)"].loc["post_np"]
    m1e = allt[allt.modell == "M1e NRK-lik med log(p_eff)"].loc["post_np"]
    m2 = allt[allt.modell == "M2 sammenligning, log(spot) + kalendermåned"].loc["post_np"]
    m2e = allt[allt.modell == "M2e + kalendermåned, log(p_eff)"].loc["post_np"]

    md = []
    md.append("# Effektiv marginalpris med strømstøtte – tabell og tolkning\n")
    md.append("Parametre og kilder: `kilder/stromstotte_parametre.md`. Tallformat: punktum som desimaltegn (som øvrige output-filer i prosjektet).\n")
    md.append("## Vintermåneder (des-feb), snitt over NO1/NO2/NO5, øre/kWh eks. mva\n")
    md.append(vinter.round(3).to_markdown(index=False))
    md.append("")
    md.append("`diff` = spot - p_eff (hvor mye strømstøtten trekker prisen ned i snitt over vintermånedene); `diff_pst` = diff i prosent av spotprisen.\n")

    md.append("## Modeller: post_np-koeffisient, spot vs. effektiv pris (log-log, samme spesifikasjon ellers)\n")
    md.append(f"- M1 (log spot): post_np = {m1.koef:.4f} (se {m1.se:.4f}, p {m1.p:.4f}) -> {(np.exp(m1.koef)-1)*100:.2f} prosent")
    md.append(f"- M1e (log p_eff): post_np = {m1e.koef:.4f} (se {m1e.se:.4f}, p {m1e.p:.4f}) -> {(np.exp(m1e.koef)-1)*100:.2f} prosent")
    md.append(f"- M2 (log spot, + kalendermåned): post_np = {m2.koef:.4f} (se {m2.se:.4f}, p {m2.p:.4f}) -> {(np.exp(m2.koef)-1)*100:.2f} prosent")
    md.append(f"- M2e (log p_eff, + kalendermåned): post_np = {m2e.koef:.4f} (se {m2e.se:.4f}, p {m2e.p:.4f}) -> {(np.exp(m2e.koef)-1)*100:.2f} prosent")
    md.append(f"- F2e: share_post = {r_f2e.params['share_post']:.4f} (p {r_f2e.pvalues['share_post']:.4f}); log_p_eff = {r_f2e.params['log_p_eff']:.4f} (p {r_f2e.pvalues['log_p_eff']:.4f}) - identifisert av kun tre prisområder, se merknad i loggen.")
    md.append(f"- Prisgap: koeffisient på np_andel_hh × (log p_eff − log 40) = {r_gap.params['gap_x']:.4f} (se {r_gap.bse['gap_x']:.4f}, p {r_gap.pvalues['gap_x']:.4f}); implisert egenpriselastisitet {elastisitet:.3f}. Identifisert av samme tverrsnittsvariasjon i oppslutning som F2, ikke av prisvariasjon. Snittgap i postperioden {r_gap.snitt_gap:.2f} logpoeng (marginalprisen om lag halveres); D7-estimatet 0,0299 delt på snittgapet gir {r_gap.did_elast:.3f}.")
    md.append("")

    diff_snitt = vinter["diff"].mean()
    diff_pst_snitt = vinter["diff_pst"].mean()
    topp = vinter.sort_values("diff", ascending=False).iloc[0]
    md.append("## Tolkning\n")
    md.append(
        f"Strømstøtten trekker vintermånedenes gjennomsnittlige spotpris ned med {diff_snitt:.1f} øre/kWh i snitt over de fem vintrene "
        f"({diff_pst_snitt:.1f} prosent av spotprisen), med størst nivåforskjell i vintrene med høyest spotpris "
        f"({topp['vinter']}: {topp['diff']:.1f} øre). "
        f"post_np-koeffisienten endres når effektiv pris (p_eff) erstatter spotpris i samme spesifikasjon: "
        f"M1 gir {m1.koef:.4f} med log(spot) mot {m1e.koef:.4f} med log(p_eff); M2 gir {m2.koef:.4f} mot {m2e.koef:.4f}. "
        f"Retningen er konsistent med at p_eff er en mindre volatil og lavere pris enn spot i høyprisperioder, slik at prisvariabelen "
        f"fanger opp noe mindre av forbruksvariasjonen og post_np-dummyen dermed kan ta opp noe av det spotprisen ellers ville forklart. "
        f"F2e-spesifikasjonen identifiserer log(p_eff) fra kun tre prisområder innad i hver kalendermåned, som er et svakt identifisert "
        f"grunnlag - koeffisienten rapporteres, men bør ikke tillegges selvstendig vekt. "
        f"Prisgap-modellen gir en implisert egenpriselastisitet på {elastisitet:.2f} (p {r_gap.pvalues['gap_x']:.2f}); den er identifisert av tverrsnittsvariasjon i oppslutning, ikke av prisvariasjon, og D7-estimatet tilsvarer {r_gap.did_elast:.2f}. Korttids husholdningselastisiteter i litteraturen ligger typisk i −0,05 til −0,2 ([fylles inn] referanse)."
    )

    with open(OUT / "tab_effektiv_pris.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print("\nSkrevet output/tab_effektiv_pris.md og output/tab_effektiv_pris_modeller.csv")


if __name__ == "__main__":
    main()
