"""Steg 11: Etterprøv NRKs øvrige tallpåstander i artikkelen.

  P1  «Strømforbruk sør i Norge, januar–juni» (Elhub-figur) og «økningen hittil i år tilsvarer
      en sammenhengende dusj i 20 000 år» – 6 min dusj = 1,4 kWh → 1 år = 122 640 kWh.
  P2  «Med norgespris koster dusjen 70 øre; med markedspris (ca. 150 øre) 2 kr 10 øre.»
  P3  «Jo høyere inntektene er i en kommune, desto flere har valgt norgespris.»
  P4  «Årets nettoeksport tilsvarer det økte forbruket blant husholdningene i Sør-Norge.»
      (Statnett-tall ikke lastet ned – rapporteres som [fylles inn]; vi oppgir forbruksøkningen i GWh.)
Kilde for P1/P4: Elhub forbruk per prisområde og gruppe (cons_mba), grupper Husholdning + Hytter.
"""
import pandas as pd
import numpy as np
from config import PROC, OUT

KWH_PER_SHOWER = 1.4           # NRK: 6 min, 6 l/min, 38 °C
KWH_PER_SHOWER_YEAR = KWH_PER_SHOWER * 10 * 24 * 365   # 10 dusjer à 6 min per time
L = []

mba = pd.read_parquet(PROC / "elhub_cons_mba_month.parquet")
mba = mba[mba.PRISOMRADE.isin(["NO1", "NO2", "NO5"])]
mba["aar"] = mba.maned.str[:4].astype(int); mba["mnd"] = mba.maned.str[5:].astype(int)
print("Grupper i mba-filen:", sorted(mba.FORBRUKSGRUPPE.unique()))
h1 = mba[mba.mnd <= 6]
def gwh(grp_mask, label):
    t = h1[grp_mask].groupby("aar").kwh.sum() / 1e6
    t.name = label
    return t
hush = h1.FORBRUKSGRUPPE.str.contains("Hushold")
hytte = h1.FORBRUKSGRUPPE.str.contains("Hytte")
tab = pd.concat([gwh(hush, "Husholdning"), gwh(hytte, "Hytter"), gwh(hush | hytte, "Hus+hytter")], axis=1)
tab["endring_hus_hytter_gwh"] = tab["Hus+hytter"].diff()
tab["endring_pst"] = tab["Hus+hytter"].pct_change() * 100
tab["dusj_aar"] = tab.endring_hus_hytter_gwh * 1e6 / KWH_PER_SHOWER_YEAR
tab["vann_mrd_liter_1429"] = tab.endring_hus_hytter_gwh * 1e6 * 1429 / 1e9
# mnd-dekning per år (jan–jun = 6)
tab["mnd_dekket"] = h1[hush].groupby("aar").maned.nunique()
print("\nP1 Forbruk jan–jun, NO1+NO2+NO5, GWh:\n", tab.round(1).to_string())
tab.round(2).to_csv(OUT / "tab_p1_forbruk_jan_jun.csv")
L.append("## P1 Forbruk januar–juni, NO1+NO2+NO5 (GWh)\n" + tab.round(1).to_markdown())
L.append(f"\n1 dusjår = {KWH_PER_SHOWER_YEAR:,.0f} kWh. NRK: økningen 2026 tilsvarer 20 000 dusjår = {20000*KWH_PER_SHOWER_YEAR/1e6:,.0f} GWh.")

# P2
for pris, navn in ((0.50, "Norgespris 40 øre + mva"), (1.50, "markedspris 150 øre")):
    L.append(f"- P2 {navn}: {KWH_PER_SHOWER} kWh × {pris:.2f} kr = {KWH_PER_SHOWER*pris:.2f} kr")
    print(f"P2 {navn}: {KWH_PER_SHOWER*pris:.2f} kr")

# P3 inntekt og oppslutning på kommunenivå (panelets siste måned)
p = pd.read_parquet(PROC / "panel.parquet")
last = p[p.maned == p.maned.max()].copy()
last["innt_1000"] = last.median_innt_etter_skatt / 1000
c_all = last[["np_andel", "np_andel_hh", "innt_1000", "snitt_bruksareal_m2", "andel_over_160m2", "kwh_per_mp"]].corr().loc["np_andel_hh"]
res = {"alle (197)": c_all.round(3).to_dict()}
for pa, g in last.groupby("prisomrade"):
    res[f"{pa} ({len(g)})"] = g[["np_andel", "np_andel_hh", "innt_1000", "snitt_bruksareal_m2", "andel_over_160m2", "kwh_per_mp"]].corr().loc["np_andel_hh"].round(3).to_dict()
p3 = pd.DataFrame(res).T
print("\nP3 Korrelasjon husholdningsandel Norgespris (apr. 2026) med kommunekjennetegn:\n", p3.to_string())
p3.to_csv(OUT / "tab_p3_inntekt_oppslutning.csv")
import statsmodels.formula.api as smf
r = smf.wls("np_andel_hh ~ innt_1000 + C(prisomrade)", data=last, weights=last.np_tot_hh).fit(cov_type="HC1")
r2 = smf.wls("np_andel_hh ~ innt_1000 + snitt_bruksareal_m2 + C(prisomrade)", data=last, weights=last.np_tot_hh).fit(cov_type="HC1")
L.append("\n## P3 Inntekt og oppslutning (kommunenivå, apr. 2026, husholdningsmålere)\n" + p3.to_markdown())
L.append(f"\nMålerveid regresjon andel ~ inntekt (1 000 kr) + område-FE: β = {r.params['innt_1000']:.5f} (se {r.bse['innt_1000']:.5f}, p = {r.pvalues['innt_1000']:.3f}); "
         f"med boligstørrelse: β_innt = {r2.params['innt_1000']:.5f} (p = {r2.pvalues['innt_1000']:.3f}), β_bolig = {r2.params['snitt_bruksareal_m2']:.5f} (p = {r2.pvalues['snitt_bruksareal_m2']:.3f}). "
         f"10 000 kr høyere medianinntekt ⇒ {r.params['innt_1000']*10*100:+.2f} prosentpoeng.")
print(f"\nP3 regresjon: β_innt = {r.params['innt_1000']:.5f} (p={r.pvalues['innt_1000']:.3f}); med bolig: β_innt = {r2.params['innt_1000']:.5f} (p={r2.pvalues['innt_1000']:.3f})")
# Områdesnitt
L.append("\nOppslutning per område (målerveid, husholdning): " + last.groupby("prisomrade").apply(lambda x: np.average(x.np_andel_hh, weights=x.np_tot_hh), include_groups=False).round(3).to_dict().__repr__())

(OUT / "tab_nrk_pastander.md").write_text("\n".join(L), encoding="utf-8")
print("\nSkrevet output/tab_nrk_pastander.md")
