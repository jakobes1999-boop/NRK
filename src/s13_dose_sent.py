"""s13: Dose-respons for «Bestilt sent». Versjon 2 etter kritikkrunde 3 (notat/KRITIKK3_2026-09-05.md).

Elhub-dokumentasjon (kilder/elhub_wiki_norgespris_status.txt): «Bestilt tidlig» = bestilt før eller på
2025-10-01; «Bestilt sent» = bestilt 2025-10-02 t.o.m. 2026-04-30. Norgespris gjelder fra bestillingsdagen.
Behandlingsandel (dose) per område og måned fra daglige Norgespris-tellinger (alle husholdningsmålere):
dose(t) = (N(t) - N(2025-10-01)) / (N(2026-04-30) - N(2025-10-01)), månedssnitt.

Modeller i D7-rammen (område×måned×EAC-FE). To sesongspesifikasjoner:
  felles:     bestilt:C(mnd):C(eac)                        (som D7)
  per kohort: tidlig:C(mnd):C(eac) + sent:C(mnd):C(eac)    (hovedspesifikasjon etter K1)
Termer: tidlig_post, sent_post (nivå), sent_dose (per fullt behandlet måler).
Nullverdier for nivå/dose-delingen er IKKE 0 og «tidlig»: med månedsvarierende per-enhets-effekt gir en
konstruert null (ingen seleksjon, samme per-enhets-effekt som tidlig) selv et positivt sent_post. Den
simulerte nullverdien rapporteres ved siden av estimatet (K2/K3).
"""
import numpy as np, pandas as pd, statsmodels.formula.api as smf
from config import PROC, OUT
POST = "2025-10"; PM = ["2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04"]
L = []
def p(t=""): L.append(t); print(t)
def tab(df, r=4): L.append(df.round(r).to_markdown()); print(df.round(r).to_string())

# ---------- dose ----------
d = pd.read_parquet(PROC / "elhub_np_mba_daily.parquet")
h = d[(d.FORBRUKSGRUPPE == "Husholdning") & d.PRISOMRADE.isin(["NO1", "NO2", "NO5"])].copy()
h["dag"] = h.DATO.astype(str).str[:10]; h["maned"] = h.dag.str[:7]
rows = []
for pa, g in h.groupby("PRISOMRADE"):
    g = g.set_index("dag").sort_index()
    n0, nT = g.loc["2025-10-01", "ANTALL_NORGESPRIS"], g.loc["2026-04-30", "ANTALL_NORGESPRIS"]
    g["dose"] = ((g.ANTALL_NORGESPRIS - n0) / (nT - n0)).clip(0, 1)
    mm = g.loc["2025-10-01":"2026-04-30"].groupby("maned").dose.mean()
    rows += [{"pa": pa, "maned": k, "dose": v} for k, v in mm.items()]
dose = pd.DataFrame(rows)
p("## Dose: andel av sent-gruppen med Norgespris, snitt per måned (daglige tellinger, alle husholdningsmålere)")
tab(dose.pivot(index="maned", columns="pa", values="dose"), 3)
tot = h.groupby("dag")[["ANTALL_NORGESPRIS", "ANTALL"]].sum()
p(f"Alle målere 01.10.2025: {tot.loc['2025-10-01', 'ANTALL']:.0f}, Norgespris {tot.loc['2025-10-01', 'ANTALL_NORGESPRIS']:.0f}; "
  f"30.04.2026 Norgespris {tot.loc['2026-04-30', 'ANTALL_NORGESPRIS']:.0f}. Statuskohorten: tidlig 493 315, sent 367 106 (43 prosent sene); "
  "målere utenfor kohorten: 55 prosent sene. Kohortens eget inntredelsesforløp er ikke observert (V1).")

m = pd.read_parquet(PROC / "did_month.parquet")
m["mnd"] = m.maned.str[5:]
m = m.merge(dose, on=["pa", "maned"], how="left"); m["dose"] = m.dose.fillna(0.0)
dw = m[(m.sent == 1) & (m.post == 1)].groupby("maned").apply(lambda x: np.average(x.dose, weights=x.n_mp), include_groups=False).rename("dose_v")
m["tidlig_post"] = m.tidlig * m.post; m["sent_post"] = m.sent * m.post
m["sent_dose"] = m.sent * m.dose; m["bestilt_post"] = m.bestilt * m.post
m["pa_t_eac"] = m.pa_t + "|" + m.eac
FE_F = "log_y ~ C(g) + C(pa_t_eac) + bestilt:C(mnd):C(eac)"
FE_K = "log_y ~ C(g) + C(pa_t_eac) + tidlig:C(mnd):C(eac) + sent:C(mnd):C(eac)"

def wfit(df, f, terms, label, y="log_y"):
    r = smf.wls(f.replace("log_y", y, 1), data=df, weights=df.n_mp).fit(cov_type="cluster", cov_kwds={"groups": df.g}, use_t=True)
    out = pd.DataFrame({"modell": label, "term": terms, "koef": [r.params[t] for t in terms], "se": [r.bse[t] for t in terms],
                        "p_t": [r.pvalues[t] for t in terms], "klustre": df.g.nunique(), "n": len(df)})
    out["pst"] = (np.exp(out.koef) - 1) * 100
    return out, r

# ---------- sesongprofil per kohort i førperioden (K1) ----------
pre = m[m.maned < POST].copy()
r0 = smf.wls("log_y ~ C(g) + C(pa_t_eac) + bestilt:C(mnd):C(eac) + sent:C(mnd)", data=pre, weights=pre.n_mp).fit(cov_type="cluster", cov_kwds={"groups": pre.g}, use_t=True)
prof = pd.Series({k[-3:-1]: v for k, v in r0.params.items() if k.startswith("sent:C(mnd)")}).sort_index()
prof = prof - prof["10"]   # referanse oktober; nivået er absorbert i C(g)
p("\n## Sent-gruppens sesongprofil ut over tidlig-gruppens i FØRPERIODEN (okt 2023–sep 2025), prosentpoeng relativt til oktober")
tab((prof * 100).rename("pp").to_frame().T, 2)
p("Profilen er ikke flat: kohortene har ulik sesongprofil også uten reform. Sesongprofil per kohort er derfor hovedspesifikasjon under.")

# ---------- hovedestimater ----------
res = []
for tag, FE in (("felles sesong", FE_F), ("sesong per kohort", FE_K)):
    res.append(wfit(m, FE + " + tidlig_post + sent_post", ["tidlig_post", "sent_post"], f"E0 {tag}")[0])
    res.append(wfit(m, FE + " + tidlig_post + sent_post + sent_dose", ["tidlig_post", "sent_post", "sent_dose"], f"E1 {tag}")[0])
    res.append(wfit(m, FE + " + tidlig_post + sent_dose", ["tidlig_post", "sent_dose"], f"E4 {tag}, sent kun via dose")[0])
ms = m[m.status != "Bestilt tidlig"]
res.append(wfit(ms, FE_F + " + sent_post + sent_dose", ["sent_post", "sent_dose"], "E2 kun sent vs ikke bestilt (sesong implisitt sent-spesifikk)")[0])
mt = m[m.status != "Bestilt sent"]
res.append(wfit(mt, FE_F + " + tidlig_post", ["tidlig_post"], "E3 kun tidlig vs ikke bestilt")[0])
# placebo med matchende vindu okt 2024–apr 2025 (V4)
pl = m[m.maned < POST].copy()
dl = dose.copy(); dl["maned"] = (dl.maned.str[:4].astype(int) - 1).astype(str) + dl.maned.str[4:]
pl = pl.drop(columns="dose").merge(dl, on=["pa", "maned"], how="left"); pl["dose"] = pl.dose.fillna(0.0)
pl["post_pl"] = pl.maned.isin([f"{int(k[:4]) - 1}{k[4:]}" for k in PM]).astype(int)
pl["tidlig_post"] = pl.tidlig * pl.post_pl; pl["sent_post"] = pl.sent * pl.post_pl; pl["sent_dose"] = pl.sent * pl.dose
for tag, FE in (("felles sesong", FE_F), ("sesong per kohort", FE_K)):
    res.append(wfit(pl, FE + " + tidlig_post + sent_post + sent_dose", ["tidlig_post", "sent_post", "sent_dose"], f"E5 placebo okt 2024–apr 2025, {tag}")[0])
for eac, sub in m.groupby("eac"):
    res.append(wfit(sub, "log_y ~ C(g) + C(pa_t) + tidlig:C(mnd) + sent:C(mnd) + tidlig_post + sent_post + sent_dose",
                    ["tidlig_post", "sent_post", "sent_dose"], f"E6 {eac} (9 klustre)")[0])
R = pd.concat(res, ignore_index=True)
R["ki95_lav"] = R.koef - 2.056 * R.se; R["ki95_hoy"] = R.koef + 2.056 * R.se
p("\n## Estimater (p fra t(G-1); 95-prosentintervall med t(26); for E6 med 9 klustre er intervallet for smalt)")
tab(R.set_index(["modell", "term"])[["koef", "se", "p_t", "ki95_lav", "ki95_hoy", "pst", "klustre", "n"]])

# ---------- event-study begge sesongspesifikasjoner ----------
def event(df, FE):
    ev = df.copy()
    for k in PM:
        ev[f"t_{k[:4]}{k[5:]}"] = ev.tidlig * (ev.maned == k); ev[f"s_{k[:4]}{k[5:]}"] = ev.sent * (ev.maned == k)
    terms = [c for c in ev.columns if c.startswith(("t_20", "s_20"))]
    r = smf.wls(FE + " + " + " + ".join(terms), data=ev, weights=ev.n_mp).fit(cov_type="cluster", cov_kwds={"groups": ev.g}, use_t=True)
    E = pd.DataFrame({"term": terms, "koef": [r.params[t] for t in terms], "se": [r.bse[t] for t in terms]})
    E["gruppe"] = np.where(E.term.str.startswith("t_"), "tidlig", "sent"); E["maned"] = E.term.str[2:6] + "-" + E.term.str[6:8]
    return E, r, ev, terms
p("\n## Månedsvise effekter (prosent), målerveid dose og forhold sent/tidlig")
EV = {}
for tag, FE in (("felles", FE_F), ("kohort", FE_K)):
    E, r, ev, terms = event(m, FE); E["pst"] = (np.exp(E.koef) - 1) * 100
    W = E.pivot(index="maned", columns="gruppe", values="pst").join(dw)
    W["forhold"] = W.sent / W.tidlig
    p(f"\n### Sesong {tag}"); tab(W, 2)
    E["sesong"] = tag; EV[tag] = (E, r, ev, terms)
pd.concat([EV[k][0] for k in EV]).to_csv(OUT / "tab_event_study_dose.csv", index=False)

# ---------- simulert nullverdi (K2) ----------
p("\n## Nivå/dose-deling mot simulert nullverdi (K2): utfall konstruert med null seleksjon og samme per-enhets-effekt som tidlig")
null_rows = []
for tag, FE, key in (("felles sesong", FE_F, "felles"), ("sesong per kohort", FE_K, "kohort")):
    E, r, ev, terms = EV[key]
    t_eff = E[E.gruppe == "tidlig"].set_index("maned").koef
    base = r.fittedvalues - sum(r.params[t] * ev[t] for t in terms)
    y0 = base + ev.tidlig * ev.maned.map(t_eff).fillna(0) + ev.sent * ev.dose * ev.maned.map(t_eff).fillna(0)
    ev = ev.assign(y_null=y0.values)
    o, _ = wfit(ev, FE + " + tidlig_post + sent_post + sent_dose", ["tidlig_post", "sent_post", "sent_dose"], f"E1 {tag}", y="y_null")
    null_rows.append(o.assign(hva="nullverdi"))
    e1 = R[R.modell == f"E1 {tag}"].set_index("term").koef; o0 = o.set_index("term").koef
    p(f"- {tag}: sent_post estimert {e1['sent_post'] * 100:.2f} pp, nullverdi {o0['sent_post'] * 100:.2f} pp (merutslag {(e1['sent_post'] - o0['sent_post']) * 100:.2f}); "
      f"sent_dose estimert {e1['sent_dose'] * 100:.2f}, nullverdi {o0['sent_dose'] * 100:.2f}; tidlig_post {e1['tidlig_post'] * 100:.2f}.")
pd.concat(null_rows).to_csv(OUT / "tab_dose_sent_nullverdi.csv", index=False)

# ---------- 7-punkts med parametrisk bootstrap (V5) ----------
p("\n## 7-punktstilpasning sent_m = a + b × (dose_m × tidlig_m); nullverdier a = 0, b = 1. Parametrisk bootstrap fra klusterkovariansen, 20 000 trekk")
rng = np.random.default_rng(1)
for tag in ("felles", "kohort"):
    E, r, ev, terms = EV[tag]
    idx = [list(r.params.index).index(t) for t in terms]
    mu = r.params.iloc[idx].values; V = r.cov_params().values[np.ix_(idx, idx)]
    tl = np.array([terms.index(f"t_{k[:4]}{k[5:]}") for k in PM]); sl = np.array([terms.index(f"s_{k[:4]}{k[5:]}") for k in PM])
    dv = dw.loc[PM].values
    def fit(v):
        b = np.polyfit(dv * v[tl], v[sl], 1); return b[0], b[1]
    b, a = fit(mu)
    draws = rng.multivariate_normal(mu, V, 20000); bs = np.array([fit(v) for v in draws])
    lo, hi = np.percentile(bs[:, 0], [2.5, 97.5]); alo, ahi = np.percentile(bs[:, 1], [2.5, 97.5])
    p(f"- Sesong {tag}: a = {a * 100:.2f} pp [{alo * 100:.2f}, {ahi * 100:.2f}], b = {b:.2f} [{lo:.2f}, {hi:.2f}]")

# ---------- figur ----------
try:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
    for ax, tag in zip(axes, ("felles", "kohort")):
        E = EV[tag][0].merge(dw, on="maned")
        for grp, mk in (("tidlig", "o"), ("sent", "s")):
            q = E[E.gruppe == grp]; ax.errorbar(q.dose_v, q.pst, yerr=2.056 * q.se * 100, fmt=mk, capsize=3, label=grp)
        ax.axhline(0, color="grey", lw=0.8); ax.set_title(f"Sesongprofil {tag}"); ax.set_xlabel("Andel av sent-gruppen med Norgespris i måneden")
    axes[0].set_ylabel("Effekt, prosent (D7-ramme, KI t(26))"); axes[0].legend(); fig.tight_layout(); fig.savefig(OUT / "fig_dose_sent.png", dpi=150)
except Exception as e:
    p(f"fig feilet: {e}")

R.to_csv(OUT / "tab_dose_sent.csv", index=False)
(OUT / "tab_dose_sent.md").write_text("\n".join(L), encoding="utf-8")
