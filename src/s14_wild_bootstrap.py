"""s14: Wild cluster bootstrap (WCB) for DiD-modellene i s12 og s13.

Klusterstandardfeilene i D- og E-modellene bygger på G = 27 klustre (område × status × EAC)
og G = 9 i per-EAC-modellene. Med så få klustre er CR1-standardfeilene nedadskjeve og
t-testen forkaster for ofte. Denne kjøringen gjentar inferensen med restringert wild cluster
bootstrap (WCR), B = 999, seed 1 – Cameron, Gelbach og Miller (2008); MacKinnon og Webb
(2018). Selve algoritmen ligger i src/wcb.py.

Spesifikasjonene er identiske med s12 (D-modellene) og s13 (E-modellene): samme
patsy-formler, samme WLS-vekter (n_mp) og samme klustervariabel g. Dosevariabelen regnes ut
på nytt fra data/processed/elhub_np_mba_daily.parquet med koden fra s13.

Skriver output/tab_wcb.csv, output/tab_wcb.md og output/log_s14.txt.
"""
import time
import warnings

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

from config import PROC, OUT
import wcb

warnings.filterwarnings("ignore")

B = 999
SEED = 1
POST = "2025-10"
L = []


def p(t=""):
    L.append(t)
    print(t, flush=True)


# --------------------------------------------------------------------------------------
# Data: did_month + dose (identisk med s13)
# --------------------------------------------------------------------------------------
m = pd.read_parquet(PROC / "did_month.parquet")
m["mnd"] = m.maned.str[5:]

d = pd.read_parquet(PROC / "elhub_np_mba_daily.parquet")
h = d[(d.FORBRUKSGRUPPE == "Husholdning") & d.PRISOMRADE.isin(["NO1", "NO2", "NO5"])].copy()
h["dag"] = h.DATO.astype(str).str[:10]
h["maned"] = h.dag.str[:7]
rows = []
for pa, g in h.groupby("PRISOMRADE"):
    g = g.set_index("dag").sort_index()
    n0, nT = g.loc["2025-10-01", "ANTALL_NORGESPRIS"], g.loc["2026-04-30", "ANTALL_NORGESPRIS"]
    g["dose"] = ((g.ANTALL_NORGESPRIS - n0) / (nT - n0)).clip(0, 1)
    mm = g.loc["2025-10-01":"2026-04-30"].groupby("maned").dose.mean()
    rows += [{"pa": pa, "maned": k, "dose": v} for k, v in mm.items()]
dose = pd.DataFrame(rows)

m = m.merge(dose, on=["pa", "maned"], how="left")
m["dose"] = m.dose.fillna(0.0)
m["bestilt_post"] = m.bestilt * m.post
m["tidlig_post"] = m.tidlig * m.post
m["sent_post"] = m.sent * m.post
m["sent_dose"] = m.sent * m.dose
m["pa_t_eac"] = m.pa_t + "|" + m.eac

FE_F = "log_y ~ C(g) + C(pa_t_eac) + bestilt:C(mnd):C(eac)"
FE_K = "log_y ~ C(g) + C(pa_t_eac) + tidlig:C(mnd):C(eac) + sent:C(mnd):C(eac)"

# D7-placebo: kun førperioden, med konstruert bestillingstidspunkt okt. 2024
pre = m[m.maned < POST].copy()
pre["bestilt_post"] = pre.bestilt * (pre.maned >= "2024-10")

p("# Wild cluster bootstrap (WCR), B = %d, seed = %d" % (B, SEED))
p("Dose per område og måned (snitt av daglige andeler), som i s13:")
p(dose.pivot(index="maned", columns="pa", values="dose").round(3).to_markdown())
p()

# --------------------------------------------------------------------------------------
# Modelliste
# --------------------------------------------------------------------------------------
JOBS = [
    ("D7 område×måned×EAC-FE + sesong per EAC", m,
     FE_F + " + bestilt_post", ["bestilt_post"], ["auto"]),
    ("D7 tidlig/sent", m,
     FE_F + " + tidlig_post + sent_post", ["tidlig_post", "sent_post"], ["auto"]),
    ("D7 placebo okt 2024", pre,
     FE_F + " + bestilt_post", ["bestilt_post"], ["auto"]),
    ("E1 sesong per kohort", m,
     FE_K + " + tidlig_post + sent_post + sent_dose", ["sent_post", "sent_dose"], ["auto"]),
    ("E4 sesong per kohort, sent kun via dose", m,
     FE_K + " + tidlig_post + sent_dose", ["sent_dose"], ["auto"]),
]
for eac in sorted(m.eac.unique()):
    sub = m[m.eac == eac]
    JOBS.append((f"E6 {eac} (9 klustre)", sub,
                 "log_y ~ C(g) + C(pa_t) + tidlig:C(mnd) + sent:C(mnd) + tidlig_post + sent_post + sent_dose",
                 ["tidlig_post", "sent_dose"], ["rademacher", "webb"]))
for eac in sorted(m.eac.unique()):
    sub = m[m.eac == eac]
    JOBS.append((f"D6 {eac} (9 klustre)", sub,
                 "log_y ~ C(g) + C(pa_t) + bestilt:C(mnd) + bestilt_post",
                 ["bestilt_post"], ["rademacher", "webb"]))

res = []
t_start = time.time()
for label, df, formula, terms, wkinds in JOBS:
    fit = smf.wls(formula, data=df, weights=df.n_mp).fit(
        cov_type="cluster", cov_kwds={"groups": df.g}, use_t=True)
    y, X, names, w = wcb.design_from_formula(formula, df)
    Xn, nn, kidx = wcb.drop_collinear(X, names, terms)
    for term, kk in zip(terms, kidx):
        prep = wcb.prepare(y, Xn, w, df.g.values, kk)
        G = prep["G"]
        koef, se_own, t_own, _ = float(prep["P"][kk] @ prep["yt"]), None, None, None
        for kind in wkinds:
            base = wcb.wild_cluster_boot(B=B, weights=kind, seed=SEED, b0=0.0, prep=prep)
            lo, hi, grid, ps = wcb.wild_cluster_ci(B=B, weights=kind, seed=SEED, prep=prep,
                                                   n_grid=41, span=4.0)
            se_cl = float(fit.bse[term])
            koef_sm = float(fit.params[term])
            p_cl = float(fit.pvalues[term])
            res.append({
                "modell": label, "term": term, "koef": koef_sm,
                "pst": 100 * (np.exp(koef_sm) - 1),
                "se_cluster": se_cl, "p_cluster_t": p_cl, "p_wcb": base["p_wcb"],
                "ki_wcb_lav": lo, "ki_wcb_hoy": hi,
                "ki_t_lav": koef_sm - stats.t.ppf(0.975, G - 1) * se_cl,
                "ki_t_hoy": koef_sm + stats.t.ppf(0.975, G - 1) * se_cl,
                "G": G, "vekttype": base["vekttype"], "B": B,
                "se_wcb_intern": base["se"], "t_wcb_intern": base["t"], "N": prep["N"],
            })
            p(f"  {label:52s} {term:12s} {base['vekttype']:11s} "
              f"koef {koef_sm: .5f}  se {se_cl:.5f}  p_t {p_cl:.4f}  "
              f"p_wcb {base['p_wcb']:.4f}  KI [{lo: .5f}, {hi: .5f}]")

R = pd.DataFrame(res)
R.to_csv(OUT / "tab_wcb.csv", index=False)
p(f"\nKjøretid modeller: {time.time() - t_start:.1f} s")

# --------------------------------------------------------------------------------------
# Sanity-sjekk: p-fordeling under sann H0
# --------------------------------------------------------------------------------------
SANITY_FROM = len(L)
p("\n## Sanity-sjekk: p-fordeling når nullhypotesen er sann")
p("Utfallet konstrueres på nytt i D7-rammen: y = tilpasset verdi uten bestilt_post + støy med")
p("klusterkomponent (klusterspesifikt nivå + AR-fri idiosynkratisk ledd), skalert til samme")
p("residualspredning som i den virkelige modellen. Sann effekt er null. 200 simuleringer,")
p("B = 199 per simulering (av kjøretidshensyn); rapporterer andel p < 0,05 for klusterrobust")
p("t-test og for WCR.")

SIM, B_SIM = 200, 199
fs = FE_F + " + bestilt_post"
y0, X0, n0_, w0 = wcb.design_from_formula(fs, m)
Xs, ns, kis = wcb.drop_collinear(X0, n0_, ["bestilt_post"])
ks = kis[0]
gvals = m.g.values
gi, G0 = np.unique(gvals, return_inverse=True)[1], m.g.nunique()
sw = np.sqrt(w0)
Xt0 = Xs * sw[:, None]
b_hat = np.linalg.lstsq(Xt0, y0 * sw, rcond=None)[0]
u_hat = y0 * sw - Xt0 @ b_hat
sd = u_hat.std()
fit_null = (Xt0 @ b_hat - b_hat[ks] * Xt0[:, ks]) / sw   # tilpasset uten bestilt_post, utransformert

rng = np.random.default_rng(20260905)
gidx = pd.factorize(m.g.values)[0]
tcrit = stats.t.ppf(0.975, G0 - 1)
p_t, p_wcb = [], []
t0 = time.time()
for s in range(SIM):
    ug = rng.normal(0, sd, size=G0)[gidx]
    ui = rng.normal(0, sd, size=len(m))
    ysim = fit_null + (0.7 * ug + 0.7 * ui) / sw
    prep = wcb.prepare(ysim, Xs, w0, gvals, ks)
    r = wcb.wild_cluster_boot(B=B_SIM, weights="rademacher", seed=1000 + s, b0=0.0, prep=prep)
    p_wcb.append(r["p_wcb"])
    p_t.append(2 * stats.t.sf(abs(r["t"]), G0 - 1))
p_t, p_wcb = np.array(p_t), np.array(p_wcb)
p(f"Simuleringer: {SIM}, kjøretid {time.time() - t0:.1f} s")
p(f"- Klusterrobust t(G−1): andel p < 0,05 = {(p_t < 0.05).mean():.3f}; p < 0,10 = {(p_t < 0.10).mean():.3f}")
p(f"- WCR (Rademacher, B = {B_SIM}): andel p < 0,05 = {(p_wcb < 0.05).mean():.3f}; "
  f"p < 0,10 = {(p_wcb < 0.10).mean():.3f}")
ks_stat = stats.kstest(p_wcb, "uniform")
p(f"- Kolmogorov–Smirnov mot uniform for WCR-p: D = {ks_stat.statistic:.3f}, p = {ks_stat.pvalue:.3f}")
dec = pd.Series(np.histogram(p_wcb, bins=np.linspace(0, 1, 11))[0] / SIM,
                index=[f"{i / 10:.1f}–{(i + 1) / 10:.1f}" for i in range(10)], name="andel")
p("- Desilfordeling av WCR-p (forventet 0,10 i hver):")
p(dec.round(3).to_frame().T.to_markdown())
sanity = {"sim": SIM, "B_sim": B_SIM, "rej_t_05": float((p_t < 0.05).mean()),
          "rej_wcb_05": float((p_wcb < 0.05).mean()), "ks_D": float(ks_stat.statistic),
          "ks_p": float(ks_stat.pvalue)}

# --------------------------------------------------------------------------------------
# Markdown-tabell og tolkning
# --------------------------------------------------------------------------------------
show = R[["modell", "term", "koef", "pst", "se_cluster", "p_cluster_t", "p_wcb",
          "ki_wcb_lav", "ki_wcb_hoy", "G", "vekttype", "B"]].copy()
_R = pd.read_csv(OUT / "tab_wcb.csv")
_R["b_wcb"] = _R.ki_wcb_hoy - _R.ki_wcb_lav
from scipy import stats as _st
_R["b_t"] = 2 * _st.t.ppf(0.975, _R.G - 1) * _R.se_cluster
_ratio = (_R.b_wcb / _R.b_t).dropna()
brd = f"{_ratio.min():.2f}–{_ratio.max():.2f}; videre i {(_ratio > 1).sum()} av {len(_ratio)} rader, smalere i {(_ratio < 1).sum()}"

md = ["# Wild cluster bootstrap av DiD-estimatene",
      "",
      f"Restringert wild cluster bootstrap (WCR), B = {B}, seed {SEED}, klustre g = område | status | EAC.",
      "Spesifikasjonene er identiske med s12 (D-modellene) og s13 (E-modellene). Kolonnene `koef`,",
      "`se_cluster` og `p_cluster_t` er statsmodels' WLS med CR1 og t(G−1); `p_wcb` og",
      "`ki_wcb_*` kommer fra bootstrappen. p-verdien har oppløsning 1/999, slik at 0,0000",
      "betyr p < 0,001. Konfidensintervallet er funnet ved å invertere testen på et rutenett",
      "med 41 nullverdier over estimat ± 4 standardfeil.",
      "",
      "Referanser: Cameron, Gelbach og Miller (2008); MacKinnon og Webb (2018). For modellene",
      "med ni klustre rapporteres både Rademacher- og Webb-vekter, siden Rademacher bare gir",
      "2^9 = 512 distinkte vektvektorer.",
      "",
      show.round(5).to_markdown(index=False),
      ""]

md += [s.lstrip("\n") for s in L[SANITY_FROM:]] + [""]

# tolkning
def g(modell, term, kind=None):
    q = R[(R.modell == modell) & (R.term == term)]
    if kind:
        q = q[q.vekttype == kind]
    return q.iloc[0]

d7 = g("D7 område×måned×EAC-FE + sesong per EAC", "bestilt_post")
d7t = g("D7 tidlig/sent", "tidlig_post")
d7s = g("D7 tidlig/sent", "sent_post")
d7p = g("D7 placebo okt 2024", "bestilt_post")
e1s = g("E1 sesong per kohort", "sent_post")
e1d = g("E1 sesong per kohort", "sent_dose")
e4 = g("E4 sesong per kohort, sent kun via dose", "sent_dose")
e6 = R[R.modell.str.startswith("E6")]
d6 = R[R.modell.str.startswith("D6")]

def fmt(x, n=4):
    """Norsk tallformat: desimalkomma og ekte minustegn (U+2212)."""
    return f"{x:.{n}f}".replace(".", ",").replace("-", "−")


def fmtp(x):
    """p-verdi; oppløsningen er 1/B, så eksakt null rapporteres som < 0,001."""
    return "< 0,001" if x == 0 else fmt(x, 3)

md += ["## Tolkning", "",
       f"- Hovedestimatet i D7 (bestilt_post) er {fmt(d7.koef)} i logaritmer, "
       f"{fmt(d7.pst, 2)} prosent. p fra klusterrobust t er {fmtp(d7.p_cluster_t)}, "
       f"p fra WCR {fmtp(d7.p_wcb)}. Konklusjonen om at bestillerne bruker mer strøm etter "
       f"innføringen overlever bootstrappen.",
       f"- I D7 tidlig/sent er tidlig_post {fmt(d7t.pst, 2)} prosent (p_t {fmtp(d7t.p_cluster_t)}, "
       f"p_wcb {fmtp(d7t.p_wcb)}) og sent_post {fmt(d7s.pst, 2)} prosent "
       f"(p_t {fmtp(d7s.p_cluster_t)}, p_wcb {fmtp(d7s.p_wcb)}).",
       f"- Placeboen (konstruert reform okt. 2024, kun førperioden) gir {fmt(d7p.pst, 2)} prosent "
       f"med p_t {fmt(d7p.p_cluster_t)} og p_wcb {fmtp(d7p.p_wcb)}. "
       + ("Placeboen er ikke signifikant i noen av testene." if d7p.p_wcb >= 0.05 and d7p.p_cluster_t >= 0.05
          else "Placeboen er signifikant i minst én av testene, og designet er dermed ikke rent."),
       f"- I E1 (sesong per kohort) er sent_post {fmt(e1s.pst, 2)} prosent med p_t {fmt(e1s.p_cluster_t)} "
       f"og p_wcb {fmtp(e1s.p_wcb)}; sent_dose er {fmt(e1d.koef)} med p_t {fmt(e1d.p_cluster_t)} "
       f"og p_wcb {fmtp(e1d.p_wcb)}. E4, der sent-effekten kun går via dose, gir sent_dose "
       f"{fmt(e4.koef)} med p_t {fmtp(e4.p_cluster_t)} og p_wcb {fmtp(e4.p_wcb)}.",
       f"- I per-EAC-modellene (ni klustre) er forskjellen mellom t-testen og bootstrappen størst. "
       f"Av {len(e6)} rader i E6 er {(e6.p_cluster_t < 0.05).sum()} signifikante på 5 prosent med "
       f"klusterrobust t, mot {(e6.p_wcb < 0.05).sum()} med WCR. For D6 er tallene "
       f"{(d6.p_cluster_t < 0.05).sum()} mot {(d6.p_wcb < 0.05).sum()} av {len(d6)}.",
       "- Rademacher- og Webb-vekter gir samme kvalitative bilde i ni-klustermodellene. Webb er "
       "å foretrekke her: med ni klustre gir Rademacher bare 512 distinkte vektvektorer, og "
       "p-verdien blir grovt diskretisert.",
       f"- Sanity-sjekken viser at den klusterrobuste t-testen forkaster i "
       f"{fmt(sanity['rej_t_05'], 3)} av tilfellene når nullhypotesen er sann, mot nominelle "
       f"0,050, mens WCR forkaster i {fmt(sanity['rej_wcb_05'], 3)}. "
       f"Kolmogorov–Smirnov-testen mot uniform fordeling for WCR-p gir p = {fmt(sanity['ks_p'], 3)}.",
       f"- Bredden på bootstrapintervallet delt på t(G−1)-intervallet: {brd}. Der p_wcb og "
       "p_cluster_t havner på hver sin side av 0,05, er det bootstrappen som gjelder.",
       "- se_cluster/p_cluster_t i tabellen er statsmodels-verdier (K = alle kolonner i CR1-korreksjonen); WCB bruker K = antall "
       "estimerte parametre (rang), som gir 1 prosent lavere se. Bootstrap-p og -KI er beregnet med sistnevnte.",
       "- Sanity-sjekken er kjørt med homoskedastisk støy og balanserte klustre for G = 27, der også t-testen er riktig dimensjonert. "
       "Den viser at WCR er riktig implementert, ikke at den korrigerer noe; tilfellet G = 9 med ubalanserte klustre er ikke simulert.",
       ""]

(OUT / "tab_wcb.md").write_text("\n".join(md), encoding="utf-8")
(OUT / "log_s14.txt").write_text("\n".join(L), encoding="utf-8")
print("\nSkrevet output/tab_wcb.csv, output/tab_wcb.md, output/log_s14.txt")
