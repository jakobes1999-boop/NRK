"""Steg 12: Beregninger utløst av kritikkrunde 2 (notat/KRITIKK2_2026-09-05.md).

  A  Gradtall per fyringssesong (okt–apr), uveid og målerveid                     (K1)
  B  D2 med gruppespesifikk sesongprofil: bestilt × kalendermåned × EAC-gruppe    (K6)
  C  Forbruksandel for bestillere (vekt for aggregering), per område og samlet    (V1)
  D  Dekomponering jan–apr 2024/2025/2026: forbruk per måler og gradtall          (V2)
  E  Spredning i oppslutning i F2- og F7-panelet (diagnose av F7s standardfeil)   (V4)
  F  Oppslutning i Norgespris-filen mot bestillingsstatus-uttrekket               (M6)
Skriver output/tab_kritikk2.md.
"""
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from config import PROC, OUT, NORGESPRIS_START

POST = NORGESPRIS_START[:7]
L = []
def p(t=""): L.append(t); print(t)
def tab(df, r=3): L.append(df.round(r).to_markdown()); print(df.round(r).to_string())

pn = pd.read_parquet(PROC / "panel.parquet")

# A – fyringssesong
p("## A Gradtall per fyringssesong (okt–apr), 197 kommuner")
pn["sesong"] = np.where(pn.mnd >= 10, pn.aar.astype(str) + "/" + (pn.aar + 1).astype(str).str[2:],
                        (pn.aar - 1).astype(str) + "/" + pn.aar.astype(str).str[2:])
fyr = pn[pn.mnd.isin([10, 11, 12, 1, 2, 3, 4])]
a = fyr.groupby(["sesong", "maned"]).apply(lambda x: pd.Series({"egd_uveid": x.egd.mean(), "egd_veid": np.average(x.egd, weights=x.n_mp)}), include_groups=False)
a = a.groupby("sesong").agg(egd_uveid=("egd_uveid", "sum"), egd_veid=("egd_veid", "sum"), mnd=("egd_uveid", "size"))
tab(a, 0)
jan = pn[pn.mnd == 1].groupby("aar").apply(lambda x: pd.Series({"egd_jan_uveid": x.egd.mean(), "egd_jan_veid": np.average(x.egd, weights=x.n_mp)}), include_groups=False)
tab(jan, 0)

# B – D2 med gruppespesifikk sesongprofil
p("\n## B DiD med sesongprofil per EAC-gruppe (bestilt × kalendermåned × EAC)")
m = pd.read_parquet(PROC / "did_month.parquet")
m["mnd"] = m.maned.str[5:]; m["bestilt_post"] = m.bestilt * m.post
m["tidlig_post"] = m.tidlig * m.post; m["sent_post"] = m.sent * m.post
rows = []
def wfit(df, f, terms, label):
    r = smf.wls(f, data=df, weights=df.n_mp).fit(cov_type="cluster", cov_kwds={"groups": df.g})
    for t in terms:
        rows.append({"modell": label, "term": t, "koef": r.params[t], "se": r.bse[t], "p": r.pvalues[t], "pst": 100 * (np.exp(r.params[t]) - 1), "N": int(r.nobs), "klustre": df.g.nunique()})
wfit(m, "log_y ~ C(g) + C(pa_t) + bestilt:C(mnd) + bestilt_post", ["bestilt_post"], "D2 felles sesongprofil")
wfit(m, "log_y ~ C(g) + C(pa_t) + bestilt:C(mnd):C(eac) + bestilt_post", ["bestilt_post"], "D2e sesongprofil per EAC")
wfit(m, "log_y ~ C(g) + C(pa_t) + bestilt:C(mnd):C(eac):C(pa) + bestilt_post", ["bestilt_post"], "D2ep sesongprofil per EAC × område")
wfit(m, "log_y ~ C(g) + C(pa_t) + bestilt:C(mnd):C(eac) + tidlig_post + sent_post", ["tidlig_post", "sent_post"], "D2e tidlig/sent")
m["pa_t_eac"] = m.pa_t + "|" + m.eac
wfit(m, "log_y ~ C(g) + C(pa_t_eac) + bestilt:C(mnd):C(eac) + bestilt_post", ["bestilt_post"], "D7 område×måned×EAC-FE + sesong per EAC")
wfit(m, "log_y ~ C(g) + C(pa_t_eac) + bestilt:C(mnd):C(eac) + tidlig_post + sent_post", ["tidlig_post", "sent_post"], "D7 tidlig/sent")
pre7 = m[m.maned < POST].copy(); pre7["bestilt_post"] = pre7.bestilt * (pre7.maned >= "2024-10")
wfit(pre7, "log_y ~ C(g) + C(pa_t_eac) + bestilt:C(mnd):C(eac) + bestilt_post", ["bestilt_post"], "D7 placebo okt 2024")
pre = m[m.maned < POST].copy(); pre["bestilt_post"] = pre.bestilt * (pre.maned >= "2024-10")
wfit(pre, "log_y ~ C(g) + C(pa_t) + bestilt:C(mnd):C(eac) + bestilt_post", ["bestilt_post"], "D2e placebo okt 2024")
# per EAC-gruppe med egen profil (identisk med D6, referanse)
for eac in sorted(m.eac.unique()):
    sub = m[m.eac == eac]
    wfit(sub, "log_y ~ C(g) + C(pa_t) + bestilt:C(mnd) + bestilt_post", ["bestilt_post"], f"D6 kun {eac}")
B = pd.DataFrame(rows); tab(B, 4)
B.to_csv(OUT / "tab_did_eac_sesong.csv", index=False)
# forbruksveid snitt av D6
post = m[m.post == 1]
wts = post[post.bestilt == 1].groupby("eac").kwh.sum()
d6 = B[B.modell.str.startswith("D6")].set_index(B[B.modell.str.startswith("D6")].modell.str[7:])
fv = np.average(d6.koef, weights=wts.reindex(d6.index))
p(f"\nForbruksveid snitt av D6-koeffisientene: {fv:.4f} → {100*(np.exp(fv)-1):.2f} % (vekter: {wts.div(wts.sum()).round(3).to_dict()})")

# C – forbruksandel bestillere
p("\n## C Bestillernes andel av husholdningsforbruket (post-periode, bestillingsstatus-uttrekket)")
c = post.groupby(["pa", "bestilt"]).kwh.sum().unstack()
c["forbruksandel_bestilt"] = c[1] / (c[0] + c[1])
n = post[post.maned == post.maned.max()].groupby(["pa", "bestilt"]).n_mp.sum().unstack()
c["malerandel_bestilt"] = n[1] / (n[0] + n[1])
c.loc["Sum"] = [c[0].sum(), c[1].sum(), c[1].sum() / (c[0].sum() + c[1].sum()), n[1].sum() / (n[0].sum() + n[1].sum())]
tab(c, 3)
fa = c.loc["Sum", "forbruksandel_bestilt"]; ma = c.loc["Sum", "malerandel_bestilt"]
for lab, b in (("D2 0.0433", 0.0433), ("D2e", B.loc[B.modell == "D2e sesongprofil per EAC", "koef"].iloc[0]), ("D6 forbruksveid", fv)):
    eff = 100 * (np.exp(b) - 1)
    p(f"  {lab}: bestillereffekt {eff:.2f} % → aggregert med forbruksandel {fa:.3f}: {eff*fa:.2f} %; med målerandel {ma:.3f}: {eff*ma:.2f} %")

# D – dekomponering jan–apr
p("\n## D Jan–apr: forbruk per måler (Privat, 197 kommuner) og målerveid gradtall")
ja = pn[pn.mnd <= 4].groupby("aar").apply(lambda x: pd.Series({"kwh_per_mp": x.kwh.sum() / x.groupby("maned").n_mp.sum().mean(), "kwh_gwh": x.kwh.sum() / 1e6,
                                                                 "egd_veid": x.groupby("maned").apply(lambda y: np.average(y.egd, weights=y.n_mp), include_groups=False).sum(),
                                                                 "spot_snitt": x.groupby("maned").apply(lambda y: np.average(y.spot_ore_kwh, weights=y.n_mp), include_groups=False).mean()}), include_groups=False)
ja["d_kwh_mp_pst"] = ja.kwh_per_mp.pct_change() * 100
ja["d_egd"] = ja.egd_veid.diff() / 4      # endring i gradtall per måned (snitt over jan–apr); koeffisientene gjelder månedlig EGD
for lab, beta in (("M1 0.0019", 0.0019), ("M2 0.0011", 0.0011), ("egd×kommune snitt", None)):
    if beta is None:
        # kommunespesifikke helninger fra F2-oppsettet: bruk enkel FE-regresjon per kommune på pre-data
        pre_p = pn[pn.maned < POST]
        sl = pre_p.groupby("knr").apply(lambda x: np.polyfit(x.egd, x.log_kwh_mp, 1)[0], include_groups=False)
        beta = np.average(sl, weights=pn.drop_duplicates("knr").set_index("knr").n_mp.reindex(sl.index))
        lab = f"egd×kommune, målerveid snitt {beta:.5f}"
    ja[f"vaerforklart_pst [{lab}]"] = (np.exp(beta * ja.d_egd) - 1) * 100
tab(ja, 2)
p("Lesning: 2026 mot 2025 og 2026 mot 2024. Differansen mellom d_kwh_mp_pst og vaerforklart er det været ikke forklarer, gitt valgt gradtallshelning.")

# E – F7-diagnose
p("\n## E Spredning i husholdningsoppslutning: F2-panel (NVE-kobling) mot F7-panel (fylkesregel)")
pf = pd.read_parquet(PROC / "panel_fylkeregel.parquet")
def spread(df, navn):
    last = df[df.maned == df.maned.max()]
    return pd.Series({"kommuner": len(last), "snitt": last.np_andel_hh.mean(), "sd": last.np_andel_hh.std(), "min": last.np_andel_hh.min(), "p10": last.np_andel_hh.quantile(.1), "maks": last.np_andel_hh.max()}, name=navn)
E = pd.concat([spread(pn, "F2 NVE-kobling"), spread(pf, "F7 fylkesregel")], axis=1).T
tab(E, 3)
ekstra = set(pf.knr) - set(pn.knr)
lastf = pf[(pf.maned == pf.maned.max()) & pf.knr.isin(ekstra)]
p(f"Kommuner bare i F7 ({len(ekstra)}): " + ", ".join(f"{r.kommune} ({r.prisomrade}, andel {r.np_andel_hh:.2f})" for r in lastf.itertuples()))

# F – to Elhub-uttrekk om oppslutning
p("\n## F Oppslutning husholdning apr. 2026: Norgespris-filen (kommune) mot bestillingsstatus-uttrekket")
last = pn[pn.maned == pn.maned.max()]
f1 = last.groupby("prisomrade").apply(lambda x: x.np_malere_hh.sum() / x.np_tot_hh.sum(), include_groups=False).rename("norgespris_fil")
f2 = (n[1] / (n[0] + n[1])).rename("status_uttrekk")
F = pd.concat([f1, f2], axis=1); F["diff_pp"] = (F.status_uttrekk - F.norgespris_fil) * 100
tab(F, 3)
p("Forskjellen kan skyldes at status-uttrekket teller målere per april 2026 med status «bestilt» uansett når, mens Norgespris-filen teller aktive avtaler den enkelte dag, og at kommuner med < 100 målere er nullet i Norgespris-filen.")

(OUT / "tab_kritikk2.md").write_text("\n".join(L), encoding="utf-8")
print("\nSkrevet output/tab_kritikk2.md")
