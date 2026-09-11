"""Steg 8: Eget design – diff-in-diff på Elhubs uttrekk «forbruk etter bestillingsstatus».

Datasettet (okt 2023 – apr 2026, timesnivå) deler målepunktene i NO1/NO2/NO5 etter
bestillingsstatus («Ikke bestilt», «Bestilt tidlig», «Bestilt sent») og etter gruppe
for estimert årsforbruk (EAC). Kolonner verifisert 05.09.2026:
  STARTTID;SLUTTID;PRISOMRÅDE;ESTIMERT_ÅRLIG_FORBRUK_GRUPPE;NORGESPRIS_BESTILLING_STATUS;FORBRUK;ANTALL_MÅLEPUNKT

Vi:
  1. måler nivåforskjellen før oktober 2025 (seleksjon),
  2. tester parallelle trender før,
  3. estimerer effekten etter, innenfor EAC-gruppe, samlet og separat for tidlig/sent,
  4. event-study måned for måned.

Modell: log(kWh per målepunkt)_{g,t} = α_g + λ_{område,t} + β·Bestilt_g·Post_t + ε,
  g = område × status × EAC-gruppe, vektet med antall målepunkt, klustret på g.
"""
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from config import PROC, OUT, NORGESPRIS_START

POST = NORGESPRIS_START[:7]


def main():
    d = pd.read_parquet(PROC / "elhub_np_status_hour.parquet")
    d = d.rename(columns={"PRISOMRADE": "pa", "ESTIMERT_ARLIG_FORBRUK_GRUPPE": "eac",
                          "NORGESPRIS_BESTILLING_STATUS": "status", "FORBRUK": "kwh_h", "ANTALL_MALEPUNKT": "n_h"})
    print("Status:", sorted(d.status.unique()), "| EAC:", sorted(d.eac.unique()), "| områder:", sorted(d.pa.unique()))
    d["t"] = pd.to_datetime(d["STARTTID"], utc=True).dt.tz_convert("Europe/Oslo")
    d["maned"] = d.t.dt.strftime("%Y-%m")
    m = (d.groupby(["pa", "status", "eac", "maned"], as_index=False)
           .agg(kwh=("kwh_h", "sum"), n_mp=("n_h", "mean"), timer=("kwh_h", "size")))
    m = m[(m.n_mp > 0) & (m.kwh > 0)].copy()
    m["kwh_mp"] = m.kwh / m.n_mp
    m["log_y"] = np.log(m.kwh_mp)
    s = m.status.str.lower()
    m["bestilt"] = (~s.str.contains("ikke")).astype(int)
    m["tidlig"] = s.str.contains("tidlig").astype(int)
    m["sent"] = s.str.contains("sent").astype(int)
    m["post"] = (m.maned >= POST).astype(int)
    m["g"] = m.pa + "|" + m.status + "|" + m.eac
    m["pa_t"] = m.pa + "|" + m.maned
    m.to_parquet(PROC / "did_month.parquet", index=False)
    print(f"{len(m)} gruppe-måneder, {m.maned.min()}–{m.maned.max()}")

    # 1. Nivå før, vektet med målepunkt
    pre = m[m.post == 0]
    wavg = lambda x: np.average(x.kwh_mp, weights=x.n_mp)
    lvl = pre.groupby(["pa", "status"]).apply(wavg).unstack()
    lvl["bestilt_alle"] = pre[pre.bestilt == 1].groupby("pa").apply(wavg)
    lvl["forskjell_pst"] = (lvl.bestilt_alle / lvl["Ikke bestilt"] - 1) * 100
    print("\nkWh per målepunkt og måned før okt. 2025:\n", lvl.round(1).to_string())
    lvl.to_csv(OUT / "tab_did_nivaa_foer.csv")
    # samme innenfor EAC-gruppe
    lvl_eac = pre.groupby(["pa", "eac", "status"]).apply(wavg).unstack()
    lvl_eac.round(1).to_csv(OUT / "tab_did_nivaa_foer_eac.csv")
    print("\nInnen EAC-gruppe:\n", lvl_eac.round(1).to_string())
    # antall målepunkt per status (siste måned)
    last = m[m.maned == m.maned.max()].groupby(["pa", "status"]).n_mp.sum().unstack()
    print(f"\nMålepunkt {m.maned.max()}:\n", last.round(0).to_string())
    last.to_csv(OUT / "tab_did_malepunkt.csv")

    # 2–3. DiD
    def did(formula, term_names, label):
        r = smf.wls(formula, data=m, weights=m.n_mp).fit(cov_type="cluster", cov_kwds={"groups": m.g})
        rows = []
        for t in term_names:
            b, se, pv = r.params[t], r.bse[t], r.pvalues[t]
            rows.append({"modell": label, "term": t, "koef": b, "se": se, "p": pv, "pst": 100 * (np.exp(b) - 1), "N": int(r.nobs)})
            print(f"  {label:38s} {t:14s} β={b:.4f} (se {se:.4f}, p={pv:.4f}) → {100*(np.exp(b)-1):+.1f} %")
        return rows

    print("\nDiff-in-diff:")
    res = []
    res += did("log_y ~ bestilt:post + C(g) + C(pa_t)", ["bestilt:post"], "Bestilt (alle) vs ikke")
    res += did("log_y ~ tidlig:post + sent:post + C(g) + C(pa_t)", ["tidlig:post", "sent:post"], "Tidlig / sent vs ikke")
    # område-spesifikk effekt
    for pa in sorted(m.pa.unique()):
        sub = m[m.pa == pa]
        r = smf.wls("log_y ~ bestilt:post + C(g) + C(maned)", data=sub, weights=sub.n_mp).fit(cov_type="cluster", cov_kwds={"groups": sub.g})
        b = r.params["bestilt:post"]
        res.append({"modell": f"Bestilt vs ikke, {pa}", "term": "bestilt:post", "koef": b, "se": r.bse["bestilt:post"],
                    "p": r.pvalues["bestilt:post"], "pst": 100 * (np.exp(b) - 1), "N": int(r.nobs)})
        print(f"  {pa}: β={b:.4f} (se {r.bse['bestilt:post']:.4f}) → {100*(np.exp(b)-1):+.1f} %")
    pd.DataFrame(res).to_csv(OUT / "tab_did.csv", index=False)

    # 4. Event-study, referanse = september 2025
    ref = "2025-09"
    months = sorted(m.maned.unique())
    ev_cols = []
    for mo in months:
        if mo == ref:
            continue
        c = "ev_" + mo.replace("-", "_")
        m[c] = m.bestilt * (m.maned == mo).astype(int)
        ev_cols.append(c)
    es = smf.wls("log_y ~ " + " + ".join(ev_cols) + " + C(g) + C(pa_t)", data=m, weights=m.n_mp).fit(
        cov_type="cluster", cov_kwds={"groups": m.g})
    rows = []
    for mo in months:
        if mo == ref:
            rows.append({"maned": mo, "koef": 0.0, "se": 0.0}); continue
        k = "ev_" + mo.replace("-", "_")
        rows.append({"maned": mo, "koef": es.params[k], "se": es.bse[k]})
    es_t = pd.DataFrame(rows)
    es_t["pst"] = (np.exp(es_t.koef) - 1) * 100
    es_t.to_csv(OUT / "tab_event_study_did.csv", index=False)
    pre_es = es_t[es_t.maned < POST]
    print(f"\nEvent-study: snitt pre-koeff = {pre_es.koef.mean():.4f} (sd {pre_es.koef.std():.4f}); "
          f"snitt post = {es_t[es_t.maned >= POST].koef.mean():.4f}")
    print(es_t.round(4).to_string(index=False))

    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 4.5))
    x = pd.PeriodIndex(es_t.maned, freq="M").to_timestamp()
    ax.errorbar(x, es_t.pst, yerr=1.96 * es_t.se * 100, fmt="o-", ms=3, capsize=2, color="#1f4e79")
    ax.axhline(0, color="grey", lw=0.8); ax.axvline(pd.Timestamp(NORGESPRIS_START), color="#c00", ls="--", lw=1)
    ax.set_ylabel("Forskjell i forbruk per målepunkt, prosent\n(bestilt vs. ikke bestilt, ref. sep. 2025)")
    ax.set_title("Event-study: Norgespris og husholdningsforbruk (Elhub, NO1/NO2/NO5)")
    fig.tight_layout(); fig.savefig(OUT / "fig_event_study_did.png", dpi=160)


if __name__ == "__main__":
    main()
