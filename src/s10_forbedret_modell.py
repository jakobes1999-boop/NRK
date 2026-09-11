"""Steg 10: Modeller som tar høyde for svakhetene i NRKs design.

NRKs M1 (kommune-FE, post-dummy) har tre problemer som resultatene i s07 bekrefter:
  (a) ingen tids-FE → dummyen fanger alt som skjedde etter okt. 2025 (placebo M5 gir +5 %),
  (b) ingen heterogen temperaturfølsomhet → kommuner med høy oppslutning (enebolig/elvarme)
      reagerer sterkere på kulde, og vinteren 2025/26 var den kaldeste i panelet,
  (c) andel Norgespris målt løpende varierer nesten bare mekanisk innen post-perioden,
  (d) standardfeil klustret på kommune er ugyldige for en ren tidsdummy (se s07, Driscoll-Kraay).

Kommunepanel, kontinuerlig DiD. Primær behandlingsvariabel er HUSHOLDNINGSANDEL (share_hh_k =
andel husholdningsmålere med Norgespris i apr. 2026); Privat-andel (inkl. hytter) er robusthet.
  F1  to-veis FE (kommune, år×måned) + share×post
  F2  F1 + kommunespesifikk EGD-helning (egd × kommune)             fjerner (b)   ← hovedspesifikasjon
  F3  F2 + share × spotpris                                          robusthet
  F4  placebo: F2 på data ≤ sep. 2025 med falsk post fra okt. 2024
  F5  event-study: share × måned (ref. sep. 2025) med F2-kontroller  pre-trendtest
  F6  F2 med Privat-andel (husholdning + hytte)                      robusthet
  F7  F2 på panel med ren fylkesregel for prisområde                 robusthet (geo-kobling)
Y = log kWh per målepunkt (primær) og log kWh. Klustret på kommune.

DiD på bestillingsstatus-uttrekket (s08), husholdninger:
  D1  gruppe-FE + område×måned-FE (som s08)
  D2  D1 + bestilt × kalendermåned (bestillernes egen sesongprofil)   ← hovedspesifikasjon
  D3  D1 + bestilt × EGD_område (ulik temperaturfølsomhet)
  D4  placebo på D3: data ≤ sep. 2025, falsk post fra okt. 2024
  D5  D3, tidlig/sent separat
  D6  D2 per EAC-gruppe
  Event-study i D2-stil for post-månedene, samlet og for tidlig/sent separat.
"""
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from config import PROC, OUT, NORGESPRIS_START

POST = NORGESPRIS_START[:7]
rows = []


def fit(df, formula, terms, label, cluster, weights=None):
    if weights is None:
        r = smf.ols(formula, data=df).fit(cov_type="cluster", cov_kwds={"groups": df[cluster]})
    else:
        r = smf.wls(formula, data=df, weights=df[weights]).fit(cov_type="cluster", cov_kwds={"groups": df[cluster]})
    for t in terms:
        b, se, p = r.params[t], r.bse[t], r.pvalues[t]
        rows.append({"modell": label, "term": t, "koef": b, "se": se, "p": p, "N": int(r.nobs), "r2": r.rsquared})
        print(f"  {label:52s} {t:16s} β={b:8.4f} (se {se:.4f}, p={p:.4f})")
    return r


def prep(p):
    last = p[p.maned == p.maned.max()].set_index("knr")
    p = p.copy()
    p["innt_1000"] = p.median_innt_etter_skatt / 1000
    p["share"] = p.knr.map(last.np_andel_hh)        # primær: husholdningsandel, fast per kommune
    p["share_priv"] = p.knr.map(last.np_andel)      # robusthet: Privat inkl. hytter
    p["share_post"] = p.share * p.post_np
    p["share_priv_post"] = p.share_priv * p.post_np
    p["share_spot"] = p.share * p.spot_ore_kwh
    w = last.reset_index()
    mean_share = np.average(w.np_andel_hh, weights=w.np_tot_hh)
    return p, w, mean_share


def kommunepanel():
    print("\n===== KOMMUNEPANEL =====")
    p, w, mean_share = prep(pd.read_parquet(PROC / "panel.parquet"))
    print(f"share_hh_k: snitt {w.np_andel_hh.mean():.3f}, målerveid {mean_share:.3f}, min {w.np_andel_hh.min():.3f}, maks {w.np_andel_hh.max():.3f}")
    w["innt_1000"] = w.median_innt_etter_skatt / 1000
    print("Korrelasjon share_hh_k med kommunekjennetegn:",
          w[["np_andel_hh", "np_andel", "snitt_bruksareal_m2", "andel_over_160m2", "innt_1000", "kwh_per_mp"]].corr().loc["np_andel_hh"].round(2).to_dict())

    base = "C(knr) + C(maned)"
    for y in ["log_kwh_mp", "log_kwh"]:
        print(f"\n-- Y = {y}")
        fit(p, f"{y} ~ {base} + egd + spot_ore_kwh + innt_1000 + snitt_bruksareal_m2 + share_post", ["share_post"], f"F1 to-veis FE, share×post [{y}]", "knr")
        fit(p, f"{y} ~ {base} + egd:C(knr) + share_post", ["share_post"], f"F2 + egd×kommune [{y}]", "knr")
        fit(p, f"{y} ~ {base} + egd:C(knr) + share_spot + share_post", ["share_post", "share_spot"], f"F3 + share×spot [{y}]", "knr")
        pre = p[p.maned < POST].copy()
        pre["share_post"] = pre.share * (pre.maned >= "2024-10")
        fit(pre, f"{y} ~ {base} + egd:C(knr) + share_post", ["share_post"], f"F4 placebo okt. 2024 (≤ sep. 2025) [{y}]", "knr")
        fit(p, f"{y} ~ {base} + egd:C(knr) + share_priv_post", ["share_priv_post"], f"F6 Privat-andel inkl. hytter [{y}]", "knr")

    pf = PROC / "panel_fylkeregel.parquet"
    if pf.exists():
        p2, _, _ = prep(pd.read_parquet(pf))
        print(f"\n-- F7 ren fylkesregel: {p2.knr.nunique()} kommuner")
        fit(p2, f"log_kwh_mp ~ {base} + egd:C(knr) + share_post", ["share_post"], "F7 F2 på fylkesregel-panel [log_kwh_mp]", "knr")

    # F5 event-study (Y = log kWh per målepunkt), ref. sep. 2025, alle måneder
    print("\n-- F5 event-study share × måned (ref. 2025-09), egd×kommune")
    ev = p.copy(); cols = []
    for m in sorted(ev.maned.unique()):
        if m == "2025-09":
            continue
        c = "ev_" + m.replace("-", "_"); ev[c] = ev.share * (ev.maned == m); cols.append(c)
    r = smf.ols(f"log_kwh_mp ~ {base} + egd:C(knr) + " + " + ".join(cols), data=ev).fit(cov_type="cluster", cov_kwds={"groups": ev.knr})
    es = pd.DataFrame([{"maned": c[3:].replace("_", "-"), "koef": r.params[c], "se": r.bse[c]} for c in cols])
    es = pd.concat([es, pd.DataFrame([{"maned": "2025-09", "koef": 0.0, "se": 0.0}])]).sort_values("maned")
    es["effekt_pst_ved_snittandel"] = (np.exp(es.koef * mean_share) - 1) * 100
    es.to_csv(OUT / "tab_event_study_f5.csv", index=False)
    pre_es = es[es.maned < POST]
    print(f"  pre: snitt {pre_es.koef.mean():.4f} (sd {pre_es.koef.std():.4f}, {int((pre_es.p if 'p' in pre_es else (pre_es.koef.abs() > 1.96*pre_es.se)).sum())} av {len(pre_es)} signifikante); "
          f"post: snitt {es[es.maned >= POST].koef.mean():.4f}")
    print(es.round(4).to_string(index=False))
    _plot(es, mean_share, OUT / "fig_event_study_f5.png",
          f"Kommunepanel: husholdningsandel×måned, egd×kommune, ref. sep. 2025 (effekt ved målerveid andel {mean_share:.2f})")
    return mean_share


def did():
    print("\n===== DIFF-IN-DIFF, BESTILLINGSSTATUS =====")
    m = pd.read_parquet(PROC / "did_month.parquet")
    p = pd.read_parquet(PROC / "panel.parquet")
    egd_pa = p.groupby(["prisomrade", "maned"]).apply(lambda x: np.average(x.egd, weights=x.n_mp), include_groups=False).rename("egd_pa").reset_index()
    m = m.merge(egd_pa, left_on=["pa", "maned"], right_on=["prisomrade", "maned"], how="left").drop(columns="prisomrade")
    print("EGD-dekning i DiD-data:", m.egd_pa.notna().mean().round(3), "| måneder uten EGD:", sorted(m.loc[m.egd_pa.isna(), "maned"].unique()))
    m = m.dropna(subset=["egd_pa"]).copy()
    m["mnd"] = m.maned.str[5:]
    m["bestilt_post"] = m.bestilt * m.post
    m["tidlig_post"] = m.tidlig * m.post
    m["sent_post"] = m.sent * m.post
    m["bestilt_egd"] = m.bestilt * m.egd_pa
    print(f"Klustre (g): {m.g.nunique()} – få klustre; standardfeil er nedadskjeve (kritikk pkt. 9)")

    fit(m, "log_y ~ C(g) + C(pa_t) + bestilt_post", ["bestilt_post"], "D1 gruppe-FE + område×måned-FE", "g", "n_mp")
    fit(m, "log_y ~ C(g) + C(pa_t) + bestilt:C(mnd) + bestilt_post", ["bestilt_post"], "D2 + bestilt×kalendermåned", "g", "n_mp")
    fit(m, "log_y ~ C(g) + C(pa_t) + bestilt_egd + bestilt_post", ["bestilt_post", "bestilt_egd"], "D3 + bestilt×EGD", "g", "n_mp")
    pre = m[m.maned < POST].copy(); pre["bestilt_post"] = pre.bestilt * (pre.maned >= "2024-10")
    fit(pre, "log_y ~ C(g) + C(pa_t) + bestilt_egd + bestilt_post", ["bestilt_post"], "D4 placebo okt. 2024 på D3 (≤ sep. 2025)", "g", "n_mp")
    pre["bestilt_post"] = pre.bestilt * (pre.maned >= "2024-10")
    fit(pre, "log_y ~ C(g) + C(pa_t) + bestilt:C(mnd) + bestilt_post", ["bestilt_post"], "D4b placebo okt. 2024 på D2 (≤ sep. 2025)", "g", "n_mp")
    fit(m, "log_y ~ C(g) + C(pa_t) + bestilt_egd + tidlig_post + sent_post", ["tidlig_post", "sent_post"], "D5 D3, tidlig/sent", "g", "n_mp")
    fit(m, "log_y ~ C(g) + C(pa_t) + bestilt:C(mnd) + tidlig_post + sent_post", ["tidlig_post", "sent_post"], "D5b D2, tidlig/sent", "g", "n_mp")
    for eac in sorted(m.eac.unique()):
        sub = m[m.eac == eac]
        fit(sub, "log_y ~ C(g) + C(pa_t) + bestilt:C(mnd) + bestilt_post", ["bestilt_post"], f"D6 D2 kun {eac}", "g", "n_mp")

    # Sesongjustert event-study (D2-stil): bestilt × kalendermåned fanger bestillernes sesongprofil fra de to
    # årene FØR ordningen; post-koeffisientene er avvik fra denne. Pre-perioden er referanse (ellers rangdefekt).
    post_m = sorted(m.loc[m.post == 1, "maned"].unique())
    out = []
    for navn, var in (("bestilt", "bestilt"), ("tidlig", "tidlig"), ("sent", "sent")):
        d = m.copy(); cols = []
        if navn != "bestilt":                       # sammenlign én bestillergruppe mot ikke-bestilt
            d = d[(d[var] == 1) | (d.bestilt == 0)].copy()
        for mo in post_m:
            c = f"ev_{navn}_" + mo.replace("-", "_"); d[c] = d[var] * (d.maned == mo).astype(int); cols.append(c)
        r = smf.wls(f"log_y ~ C(g) + C(pa_t) + {var}:C(mnd) + " + " + ".join(cols), data=d, weights=d.n_mp).fit(
            cov_type="cluster", cov_kwds={"groups": d.g})
        for c, mo in zip(cols, post_m):
            out.append({"gruppe": navn, "maned": mo, "koef": r.params[c], "se": r.bse[c], "pst": 100 * (np.exp(r.params[c]) - 1)})
    es = pd.DataFrame(out)
    es.to_csv(OUT / "tab_event_study_d2.csv", index=False)
    print("\n  Event-study D2-stil (avvik fra egen sesongprofil 2023-10–2025-09), prosent:")
    print(es.pivot(index="maned", columns="gruppe", values="pst").round(1).to_string())
    print("  se:"); print(es.pivot(index="maned", columns="gruppe", values="se").round(3).to_string())
    _plot_groups(es, OUT / "fig_event_study_d2.png")


def _plot(es, scale, path, title):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 4.5))
    x = pd.PeriodIndex(es.maned, freq="M").to_timestamp()
    y = es.effekt_pst_ved_snittandel
    yerr = (np.exp((es.koef + 1.96 * es.se) * scale) - np.exp((es.koef - 1.96 * es.se) * scale)) / 2 * 100
    ax.errorbar(x, y, yerr=yerr, fmt="o-", ms=3, capsize=2, color="#1f4e79")
    ax.axhline(0, color="grey", lw=0.8); ax.axvline(pd.Timestamp(NORGESPRIS_START), color="#c00", ls="--", lw=1)
    ax.set_ylabel("Effekt på forbruk per målepunkt, prosent"); ax.set_title(title, fontsize=10)
    fig.tight_layout(); fig.savefig(path, dpi=160)


def _plot_groups(es, path):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 4.5))
    for g, col in (("bestilt", "#1f4e79"), ("tidlig", "#2e8b57"), ("sent", "#c0504d")):
        d = es[es.gruppe == g]
        x = pd.PeriodIndex(d.maned, freq="M").to_timestamp()
        ax.errorbar(x, d.pst, yerr=1.96 * d.se * 100, fmt="o-", ms=3, capsize=2, color=col, label=g, alpha=0.9)
    ax.axhline(0, color="grey", lw=0.8); ax.legend()
    ax.set_ylabel("Avvik fra egen sesongprofil, prosent")
    ax.set_title("DiD bestilt vs. ikke bestilt, sesongjustert (bestilt×kalendermåned), post-måneder", fontsize=10)
    fig.tight_layout(); fig.savefig(path, dpi=160)


if __name__ == "__main__":
    mean_share = kommunepanel()
    did()
    t = pd.DataFrame(rows)
    t["pst_effekt"] = np.where(t.term.str.contains("share"), (np.exp(t.koef * mean_share) - 1) * 100, (np.exp(t.koef) - 1) * 100)
    t.loc[t.term.str.contains("spot|egd"), "pst_effekt"] = np.nan
    t.to_csv(OUT / "tab_forbedret.csv", index=False)
    print(f"\nSamlet (prosenteffekt for share-modeller ved målerveid husholdningsandel {mean_share:.3f}):")
    print(t.round(4).to_string(index=False))
