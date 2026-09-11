"""s13b: Robusthet for dose-responsen (KRITIKK3 V1, V3, V6).

1. Dosegrenser for kohorten: statuskohorten (sent 367 106 målere) er en delmengde av alle husholdningsmålere.
   Kohortens eget inntredelsesforløp er ikke observert. Tre varianter per område:
     identisk: dose = (N(t) - N0) / (N(T) - N0)                       (som s13)
     kohort først: dose_U = min(1, (N(t) - N0) / S_pa)                (kohortens sene bestillere først)
     kohort sist:  dose_L = max(0, (N(t) - N0 - (N(T) - N0 - S_pa)) / S_pa)
   der S_pa = antall «Bestilt sent» i kohorten i området.
2. Gradtall per kohort: egd (målerveid per område × måned) interagert med tidlig og sent i FE_K-rammen.
3. Leads: (a) sent × dose i neste måned (dose_lead) ved siden av sent_dose; (b) sent-spesifikke månedsdummyer
   apr–sep 2025 (før noen i sent-gruppen hadde bestilt) mot tidlig-gruppen, i FE_K-rammen.
"""
import numpy as np, pandas as pd, statsmodels.formula.api as smf
from config import PROC, OUT
POST = "2025-10"; PM = ["2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04"]
L = []
def p(t=""): L.append(t); print(t)
def tab(df, r=4): L.append(df.round(r).to_markdown()); print(df.round(r).to_string())

m = pd.read_parquet(PROC / "did_month.parquet"); m["mnd"] = m.maned.str[5:]
m["pa_t_eac"] = m.pa_t + "|" + m.eac
S = m[(m.sent == 1) & (m.maned == "2026-04")].groupby("pa").n_mp.sum()   # kohortens sene per område

d = pd.read_parquet(PROC / "elhub_np_mba_daily.parquet")
h = d[(d.FORBRUKSGRUPPE == "Husholdning") & d.PRISOMRADE.isin(["NO1", "NO2", "NO5"])].copy()
h["dag"] = h.DATO.astype(str).str[:10]; h["maned"] = h.dag.str[:7]
rows = []
for pa, g in h.groupby("PRISOMRADE"):
    g = g.set_index("dag").sort_index()
    n0, nT = g.loc["2025-10-01", "ANTALL_NORGESPRIS"], g.loc["2026-04-30", "ANTALL_NORGESPRIS"]
    cum = g.ANTALL_NORGESPRIS - n0; late = nT - n0; s_pa = S[pa]
    g["dose"] = (cum / late).clip(0, 1)
    g["dose_U"] = (cum / s_pa).clip(0, 1)
    g["dose_L"] = ((cum - (late - s_pa)) / s_pa).clip(0, 1)
    mm = g.loc["2025-10-01":"2026-04-30"].groupby("maned")[["dose", "dose_U", "dose_L"]].mean()
    for k, r in mm.iterrows(): rows.append({"pa": pa, "maned": k, **r.to_dict()})
    p(f"{pa}: sene bestillere totalt {late:.0f}, i kohorten {s_pa:.0f} ({s_pa / late:.2f})")
dose = pd.DataFrame(rows)
p("\n## Dosegrenser per måned (snitt over områder)")
tab(dose.groupby("maned")[["dose_L", "dose", "dose_U"]].mean(), 3)
dose.to_csv(OUT / "tab_dose_grenser.csv", index=False)

m = m.merge(dose, on=["pa", "maned"], how="left")
for c in ["dose", "dose_U", "dose_L"]: m[c] = m[c].fillna(0.0)
# gradtall per område × måned: målerveid snitt av kommunenes gradtall (vekt = alle målere i kommunen, ikke bare
# husholdningskohorten; kohortens fordeling over kommuner er ikke observert)
pan = pd.read_parquet(PROC / "panel.parquet")
egd = pan.groupby(["prisomrade", "maned"]).apply(lambda x: pd.Series({"egd_pa": np.average(x.egd, weights=x.n_mp)}), include_groups=False).reset_index().rename(columns={"prisomrade": "pa"})
egd.to_parquet(PROC / "egd_pa_maned.parquet", index=False)
m = m.merge(egd, on=["pa", "maned"], how="left"); m["egd100"] = m.egd_pa / 100
m["tidlig_post"] = m.tidlig * m.post; m["sent_post"] = m.sent * m.post
m["tidlig_egd"] = m.tidlig * m.egd100; m["sent_egd"] = m.sent * m.egd100
# lead: dose neste måned (april -> 1)
nxt = dose.assign(maned=dose.maned.shift(-1).where(dose.pa == dose.pa.shift(-1)))
lead = dose.copy(); lead["dose_lead"] = dose.groupby("pa").dose.shift(-1).fillna(1.0)
m = m.merge(lead[["pa", "maned", "dose_lead"]], on=["pa", "maned"], how="left"); m["dose_lead"] = m.dose_lead.fillna(0.0)
# september 2025: lead = oktoberdosen
sep = dose[dose.maned == "2025-10"][["pa", "dose"]].rename(columns={"dose": "d_okt"})
m = m.merge(sep, on="pa", how="left"); m.loc[m.maned == "2025-09", "dose_lead"] = m.loc[m.maned == "2025-09", "d_okt"]
m["sent_dose_lead"] = m.sent * m.dose_lead
FE_K = "log_y ~ C(g) + C(pa_t_eac) + tidlig:C(mnd):C(eac) + sent:C(mnd):C(eac)"

def wfit(df, f, terms, label):
    r = smf.wls(f, data=df, weights=df.n_mp).fit(cov_type="cluster", cov_kwds={"groups": df.g}, use_t=True)
    out = pd.DataFrame({"modell": label, "term": terms, "koef": [r.params[t] for t in terms], "se": [r.bse[t] for t in terms],
                        "p_t": [r.pvalues[t] for t in terms], "klustre": df.g.nunique(), "n": len(df)})
    out["pst"] = (np.exp(out.koef) - 1) * 100
    return out

res = []
p("\n## 1. Dosegrenser (FE_K)")
for v, tag in (("dose_L", "kohort sist"), ("dose", "identisk"), ("dose_U", "kohort først")):
    m["sent_dose"] = m.sent * m[v]
    res.append(wfit(m, FE_K + " + tidlig_post + sent_post + sent_dose", ["tidlig_post", "sent_post", "sent_dose"], f"E1 K, dose {tag}"))
    res.append(wfit(m, FE_K + " + tidlig_post + sent_dose", ["tidlig_post", "sent_dose"], f"E4 K, dose {tag}"))
m["sent_dose"] = m.sent * m.dose
p("\n## 2. Gradtall per kohort (FE_K + tidlig×egd + sent×egd; egd i hundre gradtall)")
res.append(wfit(m, FE_K + " + tidlig_egd + sent_egd + tidlig_post + sent_post", ["tidlig_egd", "sent_egd", "tidlig_post", "sent_post"], "E0 K + egd per kohort"))
res.append(wfit(m, FE_K + " + tidlig_egd + sent_egd + tidlig_post + sent_post + sent_dose", ["tidlig_egd", "sent_egd", "tidlig_post", "sent_post", "sent_dose"], "E1 K + egd per kohort"))
res.append(wfit(m, FE_K + " + tidlig_egd + sent_egd + tidlig_post + sent_dose", ["tidlig_egd", "sent_egd", "tidlig_post", "sent_dose"], "E4 K + egd per kohort"))
# felles bestilt×egd (som D3) for sammenlikning
m["bestilt_egd"] = m.bestilt * m.egd100
res.append(wfit(m, FE_K + " + bestilt_egd + tidlig_post + sent_post + sent_dose", ["bestilt_egd", "tidlig_post", "sent_post", "sent_dose"], "E1 K + bestilt×egd"))
p("\n## 3a. Lead: sent × dose neste måned ved siden av sent × dose")
res.append(wfit(m, FE_K + " + tidlig_post + sent_post + sent_dose + sent_dose_lead", ["tidlig_post", "sent_post", "sent_dose", "sent_dose_lead"], "E1 K + dose_lead"))
res.append(wfit(m, FE_K + " + tidlig_post + sent_dose + sent_dose_lead", ["tidlig_post", "sent_dose", "sent_dose_lead"], "E4 K + dose_lead"))
# kun lead i september 2025 (ingen hadde bestilt): responderer sent-gruppen før noen er inne?
m["sent_sep25"] = m.sent * (m.maned == "2025-09"); m["tidlig_sep25"] = m.tidlig * (m.maned == "2025-09")
res.append(wfit(m, FE_K + " + tidlig_post + sent_post + sent_dose + tidlig_sep25 + sent_sep25", ["tidlig_sep25", "sent_sep25"], "E1 K + sep 2025 per kohort"))
R = pd.concat(res, ignore_index=True)
R["ki95_lav"] = R.koef - 2.056 * R.se; R["ki95_hoy"] = R.koef + 2.056 * R.se
tab(R.set_index(["modell", "term"])[["koef", "se", "p_t", "ki95_lav", "ki95_hoy", "pst"]])
R.to_csv(OUT / "tab_dose_robusthet.csv", index=False)

p("\n## 3b. Sent-gruppens avvik fra tidlig-gruppen månedene før ordningen (apr–sep 2025) og etter, FE_K-ramme, prosent")
ev = m.copy(); terms = []
for k in ["2025-04", "2025-05", "2025-06", "2025-07", "2025-08", "2025-09"] + PM:
    c = f"s_{k[:4]}{k[5:]}"; ev[c] = ev.sent * (ev.maned == k); terms.append(c)
    c2 = f"t_{k[:4]}{k[5:]}"; ev[c2] = ev.tidlig * (ev.maned == k); terms.append(c2)
r = smf.wls(FE_K + " + " + " + ".join(terms), data=ev, weights=ev.n_mp).fit(cov_type="cluster", cov_kwds={"groups": ev.g}, use_t=True)
E = pd.DataFrame({"term": terms, "koef": [r.params[t] for t in terms], "se": [r.bse[t] for t in terms]})
E["gruppe"] = np.where(E.term.str.startswith("s_"), "sent", "tidlig"); E["maned"] = E.term.str[2:6] + "-" + E.term.str[6:8]
E["pst"] = (np.exp(E.koef) - 1) * 100
W = E.pivot(index="maned", columns="gruppe", values="pst"); W["diff_sent_tidlig"] = W.sent - W.tidlig
tab(W, 2); E.to_csv(OUT / "tab_event_study_pre_kohort.csv", index=False)
pre = E[(E.gruppe == "sent") & (E.maned < POST)]
p(f"Sent apr–sep 2025: snitt {pre.pst.mean():.2f} prosent, maks |t| {np.max(np.abs(pre.koef / pre.se)):.2f}")
(OUT / "tab_dose_robusthet.md").write_text("\n".join(L), encoding="utf-8")
