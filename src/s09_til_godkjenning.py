"""Steg 9 (kjøres sist): Samle alle tall fra output/ i én fil «TIL_GODKJENNING.md».

Ingenting føres inn i notatet før Jakob har godkjent tallene i denne filen.
Tallformat her er maskinnært (punktum); notatet får norsk format ved innføring.
"""
import pandas as pd
import numpy as np
from config import OUT, PROC

L = []
def h(t): L.append(f"\n## {t}\n")
def p(t=""): L.append(t)
def tab(df, floatfmt=3):
    L.append(df.round(floatfmt).to_markdown())

p("# Tall til godkjenning – etterprøving av NRK «Prisen for billig strøm»")
p(f"Generert {pd.Timestamp.now():%Y-%m-%d %H:%M}. Kilder og skript i src/. Ikke ført inn i notatet. Kritikk: notat/KRITIKK_2026-09-05.md.")

h("Tabell 1: Energiekvivalent (s05, NVE vannkraftdatabase, veid med MidProd_91_20)")
e = pd.read_csv(OUT / "tab_energiekvivalent.csv", index_col=0)
tab(e)
p(f"\nNRK: 1 429 l/kWh. Vårt NO1+NO2: {e.loc['NO1+NO2','liter_per_kwh']:.0f} l/kWh, avvik {e.loc['NO1+NO2','avvik_fra_nrk_pst']:+.1f} %.")
p("Dusj (vann_dusj.py): 1,4 kWh × 1 429 = 2 001 l. 6 min à 6 l/min ved 38 °C gir 1,4 kWh bare hvis inntaksvannet er 4,6 °C; ved 8 °C er det 1,26 kWh (6,7 min for 1,4 kWh); med virkningsgrad 0,9 på berederen gir 8 °C 1,4 kWh, så NRKs tall holder. Forhold kraftverksvann/dusjvann ≈ 50.")

h("Panelbeskrivelse (s06)")
pn = pd.read_parquet(PROC / "panel.parquet")
p(f"- Kommuner: {pn.knr.nunique()}; måneder: {pn.maned.nunique()} ({pn.maned.min()}–{pn.maned.max()}); rader: {len(pn)}")
p(f"- Per område: {pn.drop_duplicates('knr').prisomrade.value_counts().to_dict()}")
p(f"- Prisområde-kilde: {pn.drop_duplicates('knr').pa_kilde.value_counts().to_dict()} (overstyringer: output/tab_kommune_prisomrade.csv – TIL VERIFISERING mot Statnett/nettselskap)")
if "egd_kilde" in pn:
    k = pn.drop_duplicates("knr").egd_kilde.value_counts().to_dict()
    p(f"- Gradtall-kilde (kommuner): {k}")
post = pn[pn.post_np == 1]
if len(post):
    siste = pn[pn.maned == pn.maned.max()]
    a_hh = siste.groupby("prisomrade").apply(lambda x: np.average(x.np_andel_hh, weights=x.np_tot_hh), include_groups=False)
    a_pr = siste.groupby("prisomrade").apply(lambda x: np.average(x.np_andel, weights=x.np_tot), include_groups=False)
    p(f"- Andel husholdningsmålere med Norgespris, {pn.maned.max()}, målerveid: {a_hh.round(3).to_dict()}; Privat inkl. hytter: {a_pr.round(3).to_dict()}")
    p(f"- Kommune-måneder i post-perioden med np_andel = 0 (anonymisering < 100 målere): {int((post.np_andel == 0).sum())} av {len(post)}")

h("Tabell 2: Faste-effekter-regresjoner, NRK-lik og varianter (s07)")
fe = pd.read_csv(OUT / "tab_fe_resultater.csv", index_col=0)
fe["koef_se"] = fe.apply(lambda r: f"{r.koef:.4f}{r.stjerner} ({r.se:.4f})", axis=1)
piv = fe.pivot_table(index=fe.index, columns="modell", values="koef_se", aggfunc="first")
order = ["egd", "spot_ore_kwh", "post_np", "np_andel", "np_andel_hh", "innt_1000", "snitt_bruksareal_m2"]
piv = piv.reindex([o for o in order if o in piv.index])
L.append(piv.to_markdown())
mm = pd.read_csv(OUT / "tab_fe_modellmaal.csv")
p(""); tab(mm)
p("\nProsenteffekt (exp(β)−1) for Norgespris-variablene:")
tab(fe.loc[fe.index.isin(["post_np", "np_andel", "np_andel_hh"]), ["modell", "koef", "se", "p", "pst_effekt"]], 4)
p("\nNRK: gradtall 0,0019***, spotpris −0,0005***, Norgespris 0,0822*** (8,6 %), medianinntekt 0,0024***, R² 0,9376.")
dk = OUT / "tab_fe_driscoll_kraay.csv"
if dk.exists():
    p("\nStandardfeil for post_np: kluster (kommune) mot Driscoll-Kraay. post_np er lik for alle kommuner, så kommune-klustring undervurderer usikkerheten:")
    tab(pd.read_csv(dk), 4)

ev = OUT / "tab_event_study.csv"
if ev.exists():
    h("Event-study kommunepanel: Privat-andel × måned (M3-oppsett, uten egd×kommune)")
    tab(pd.read_csv(ev, index_col=0)[["koef", "se", "p"]], 4)

h("Forbedrede modeller (s10): kommunepanel F1–F7 og DiD D1–D6")
fb = pd.read_csv(OUT / "tab_forbedret.csv")
tab(fb, 4)
p("\nshare-modeller: β er effekten av å gå fra 0 til 100 % oppslutning; pst_effekt er ved målerveid husholdningsandel. Hovedspesifikasjoner: F2 (kommunepanel) og D2/D3 (DiD).")
f5 = OUT / "tab_event_study_f5.csv"
if f5.exists():
    es = pd.read_csv(f5)
    pre = es[es.maned < "2025-10"]; po = es[es.maned >= "2025-10"]
    sig = int((pre.koef.abs() > 1.96 * pre.se).sum())
    p(f"\nF5 pre-trendtest: {len(pre)} pre-koeffisienter, snitt {pre.koef.mean():.4f}, sd {pre.koef.std():.4f}, spenn {pre.koef.min():.3f} til {pre.koef.max():.3f}, {sig} signifikante på 5 %. Post: snitt {po.koef.mean():.4f}, spenn {po.koef.min():.3f} til {po.koef.max():.3f}. Figur: output/fig_event_study_f5.png")
d2 = OUT / "tab_event_study_d2.csv"
if d2.exists():
    es = pd.read_csv(d2)
    p("\nDiD event-study, D2-stil (avvik fra egen sesongprofil), prosent per post-måned:")
    L.append(es.pivot(index="maned", columns="gruppe", values="pst").round(1).to_markdown())
    p("Figur: output/fig_event_study_d2.png")

h("Tabell 3: Forbruk per målepunkt før okt. 2025, kWh/måned (s08, husholdninger)")
tab(pd.read_csv(OUT / "tab_did_nivaa_foer.csv", index_col=0), 1)
p("\nInnen EAC-gruppe:")
tab(pd.read_csv(OUT / "tab_did_nivaa_foer_eac.csv", index_col=[0, 1]), 1)
p("\nMålepunkt per status, siste måned:")
tab(pd.read_csv(OUT / "tab_did_malepunkt.csv", index_col=0), 0)

h("Tabell 4: Diff-in-diff, ujustert (s08) – erstattes av D2/D3 i notatet")
tab(pd.read_csv(OUT / "tab_did.csv"), 4)
esd = pd.read_csv(OUT / "tab_event_study_did.csv")
pre = esd[esd.maned < "2025-10"]; po = esd[esd.maned >= "2025-10"]
p(f"\nUjustert event-study (ref. sep. 2025): pre snitt {pre.koef.mean():.4f} (sd {pre.koef.std():.4f}); des–feb før ordningen +{100*pre[pre.maned.str[5:].isin(['12','01','02'])].koef.mean():.1f} %, jun–aug {100*pre[pre.maned.str[5:].isin(['06','07','08'])].koef.mean():.1f} %. Post snitt {po.koef.mean():.4f}. Figur: output/fig_event_study_did.png")

h("NRKs øvrige tallpåstander (s11)")
L.append((OUT / "tab_nrk_pastander.md").read_text(encoding="utf-8"))

k2 = OUT / "tab_kritikk2.md"
if k2.exists():
    h("Beregninger fra kritikkrunde 2 (s12): fyringssesong, D7, forbruksandel, dekomponering, F7-diagnose")
    L.append(k2.read_text(encoding="utf-8"))

k3 = OUT / "tab_dose_sent.md"
if k3.exists():
    h("Dose-respons for «Bestilt sent» (s13): skjæringsdato 1./2. oktober 2025 fra Elhubs dokumentasjon, behandlingsandel per måned fra daglige tellinger; versjon 2 etter KRITIKK3: begge sesongspesifikasjoner, nullverdi, bootstrap")
    L.append(k3.read_text(encoding="utf-8"))

k4 = OUT / "tab_dose_robusthet.md"
if k4.exists():
    h("Robusthet for dose-responsen (s13b): dosegrenser for kohorten, gradtall per kohort, leads")
    L.append(k4.read_text(encoding="utf-8"))

for fn, tittel in (("tab_wcb.md", "Wild cluster bootstrap (s14): p-verdier og KI som tåler 27 og 9 klustre"),
                   ("tab_effektiv_pris.md", "Effektiv marginalpris med strømstøtte (s15) og NRK-like modeller på effektiv pris"),
                   ("tab_prisomrade_verifisering.md", "Verifisering av kommune→prisområde (s16, sekundærkilde VG)"),
                   ("tab_nettoeksport.md", "Nettoeksport fra SSB elektrisitetsbalanse (s17), NRK P4")):
    f = OUT / fn
    if f.exists():
        h(tittel); L.append(f.read_text(encoding="utf-8"))

h("Åpne punkter før tallene kan brukes")
p("- Skjæringsdato tidlig/sent: LØST (Elhub-wiki: tidlig = bestilt t.o.m. 01.10.2025, sent = 02.10.2025–30.04.2026; Norgespris gjelder fra bestillingsdagen). Dose-respons i s13; forenlig med behandlingseffekt, ikke avgjort (KRITIKK3). Gjenstår: kohortens inntredelsesforløp fra Elhub.")
p("- Prisområde: 28 av 29 overstyrte kommuner bekreftet mot VG (sekundærkilde); Sel ikke slått opp; ingen offisiell liste funnet. Delte kommuner ikke utelukket.")
p("- Effektiv marginalpris: gjort (s15). Parameter april–mai 2023 (80 prosent) svakere belagt, se kilder/stromstotte_parametre.md.")
p("- Wild cluster bootstrap: gjort (s14). E6 Lav sent_dose overlever ikke (p 0,08–0,09); øvrige hovedtermer overlever.")
p("- Nettoeksport: gjort (s17, SSB 14091, hele landet). Fall 10 168 GWh mot forbruksøkning 2 323 GWh i Sør-Norge; produksjonsfall 6 379 GWh.")
p("- Må bestilles eksternt: kohortens inntredelsesforløp og døgnstart 1. oktober (Elhub), NRKs spesifikasjon (NRK). Se notat/SPORSMAL_ELHUB_NRK.md.")
p("- Panelet mangler 2021 (Elhubs kommunefil starter feb. 2022) og slutter apr. 2026 (NRK: juni 2026).")

(OUT / "TIL_GODKJENNING.md").write_text("\n".join(L), encoding="utf-8")
print("Skrevet", OUT / "TIL_GODKJENNING.md")
