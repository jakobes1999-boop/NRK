"""Lager syntetiske «processed»-filer med samme skjema som steg 1–4 produserer,
slik at steg 6–8 kan røyktestes uten nettilgang. Innebygd sann effekt: +8 % forbruk
for målere med Norgespris fra okt. 2025, og seleksjon (bestillere bruker 20 % mer).
Kjør: python tests/make_synthetic.py && python src/s06_build_panel.py && ...
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
import numpy as np, pandas as pd
from config import PROC

rng = np.random.default_rng(1)
months = pd.period_range("2021-12", "2026-06", freq="M").astype(str)
# 60 kommuner: 25 NO1 (fylke 32/33), 20 NO2 (42/11), 15 NO5 (46)
knrs = [f"32{i:02d}" for i in range(1, 26)] + [f"42{i:02d}" for i in range(1, 21)] + [f"46{i:02d}" for i in range(1, 16)]
pa_of = lambda k: {"32": "NO1", "42": "NO2", "46": "NO5"}[k[:2]]
egd_season = {m: 600 * max(np.cos((int(m[5:]) - 1) / 12 * 2 * np.pi), 0) + 40 for m in months}
spot = {("NO1", m): 60 + 40 * np.sin(i / 7) + rng.normal(0, 10) for i, m in enumerate(months)}
spot.update({("NO2", m): spot[("NO1", m)] * 1.1 for m in months})
spot.update({("NO5", m): spot[("NO1", m)] * 0.9 for m in months})

rows, np_rows, egd_rows = [], [], []
for k in knrs:
    n_mp = int(rng.integers(2000, 40000)); fe = rng.normal(0, 0.3)
    share_np = rng.uniform(0.05, 0.5)
    for m in months:
        egd = egd_season[m] * rng.uniform(0.8, 1.2)
        post = m >= "2025-10"
        log_kwh_mp = 5.2 + fe + 0.0019 * egd - 0.0005 * spot[(pa_of(k), m)] + post * 0.08 * share_np + rng.normal(0, 0.03)
        rows.append({"KOMMUNENUMMER": k, "KOMMUNE": f"K{k}", "FORBRUKSGRUPPE": "Privat", "maned": m,
                     "kwh": np.exp(log_kwh_mp) * n_mp, "n_mp": n_mp, "n_rows": 720})
        egd_rows.append({"municipalityId": int(k), "maned": m, "egd": egd, "tmean": 17 - egd / 30, "n_dager": 30})
        if post:
            for d in range(1, 4):
                np_rows.append({"KOMMUNENUMMER": k, "DATO": f"{m}-{d:02d}", "FORBRUKSGRUPPE": "Privat",
                                "ANTALL_MALEPUNKT": int(n_mp * share_np)})
pd.DataFrame(rows).to_parquet(PROC / "elhub_cons_muni_month.parquet", index=False)
pd.DataFrame(np_rows).to_parquet(PROC / "elhub_np_muni_daily.parquet", index=False)
pd.DataFrame(egd_rows).to_parquet(PROC / "egd_kommune_maned.parquet", index=False)
pd.DataFrame({"countyId": [32, 42, 46] * len(months), "maned": np.repeat(months, 3),
              "egd": 300, "tmean": 7}).to_parquet(PROC / "egd_fylke_maned.parquet", index=False)
pd.DataFrame([{"area": a, "maned": m, "spot_nok_kwh": v / 100, "spot_ore_kwh": v, "spot_p90": v * 1.5, "n_timer": 720}
              for (a, m), v in spot.items()]).to_parquet(PROC / "spot_month.parquet", index=False)
yrs = range(2020, 2025)
pd.DataFrame([{"knr": k, "kommune": f"K{k}", "aar": y, "median_innt_etter_skatt": 500000 + 20000 * (y - 2020) + rng.normal(0, 30000),
               "median_samlet_innt": 600000, "n_hushold": 10000} for k in knrs for y in yrs]).to_parquet(PROC / "ssb_inntekt_kommune_aar.parquet", index=False)
pd.DataFrame([{"knr": k, "kommune": f"K{k}", "aar": y, "snitt_bruksareal_m2": 120 + rng.normal(0, 15), "n_boliger_kjent_areal": 5000,
               "andel_over_160m2": 0.3} for k in knrs for y in range(2021, 2027)]).to_parquet(PROC / "ssb_bolig_kommune_aar.parquet", index=False)

# Bestillingsstatus-uttrekk (timesnivå, men vi lager døgnrader for å holde det lite – s08 aggregerer til måned)
st_rows = []
for a in ["NO1", "NO2", "NO5"]:
    for eac in ["0-10000", "10000-20000", "20000+"]:
        base = {"0-10000": 5000, "10000-20000": 15000, "20000+": 25000}[eac] / 8760
        for status, sel, n in [("Bestilt", 1.2, 30000), ("Ikke bestilt", 1.0, 70000)]:
            for m in pd.period_range("2023-10", "2026-04", freq="M").astype(str):
                post = m >= "2025-10"
                for d in range(1, 29, 7):
                    y = base * sel * (1 + 0.5 * egd_season[m] / 600) * (1.08 if (post and status == "Bestilt") else 1) * rng.normal(1, 0.02)
                    st_rows.append({"STARTTID": f"{m}-{d:02d}T00:00:00+01:00", "PRISOMRADE": a, "BESTILLINGSSTATUS": status,
                                    "EAC_GRUPPE": eac, "VOLUM_KWH": y * n * 24, "ANTALL_MALEPUNKT": n})
pd.DataFrame(st_rows).to_parquet(PROC / "elhub_np_status_hour.parquet", index=False)
print("Syntetiske filer skrevet til", PROC)
