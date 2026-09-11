"""Steg 5: Etterprøv NRKs 1 429 liter per kWh (vektet energiekvivalent NO1+NO2).

Kilde: NVEs vannkraftdatabase (felt EnEkv i kWh/m³, MidProd_91_20 i GWh/år,
ElspotomraadeNummer). Vi beregner produksjonsveid snitt for NO1+NO2 og for
hvert område, og rapporterer liter per kWh = 1000 / EnEkv.
"""
import requests
import pandas as pd
from config import RAW, OUT, NVE_PLANTS_URL

NRK_LITER_PER_KWH = 1429


def main():
    dest = RAW / "nve_kraftverk.json"
    if not dest.exists():
        r = requests.get(NVE_PLANTS_URL, timeout=120)
        r.raise_for_status()
        dest.write_bytes(r.content)
    df = pd.read_json(dest)
    df = df.dropna(subset=["EnEkv", "MidProd_91_20"])
    df = df[(df.EnEkv > 0) & (df.MidProd_91_20 > 0)]

    def weighted(sub):
        w = sub.MidProd_91_20
        ekv = (sub.EnEkv * w).sum() / w.sum()
        return pd.Series({"n_kraftverk": len(sub), "prod_gwh": w.sum(),
                          "enekv_kwh_m3": ekv, "liter_per_kwh": 1000 / ekv,
                          "enekv_uveid": sub.EnEkv.mean()})

    rows = []
    for name, mask in {"NO1": df.ElspotomraadeNummer == 1,
                       "NO2": df.ElspotomraadeNummer == 2,
                       "NO1+NO2": df.ElspotomraadeNummer.isin([1, 2]),
                       "NO5": df.ElspotomraadeNummer == 5,
                       "Norge": df.ElspotomraadeNummer.notna()}.items():
        s = weighted(df[mask]); s.name = name; rows.append(s)
    res = pd.DataFrame(rows)
    res["avvik_fra_nrk_pst"] = (res.liter_per_kwh / NRK_LITER_PER_KWH - 1) * 100
    print(res.round(3).to_string())
    res.to_csv(OUT / "tab_energiekvivalent.csv")
    print("\nNRK: 1 429 l/kWh ⇔ 0,700 kWh/m³. Merk: veiing med midlere årsproduksjon "
          "(NRK oppgir bare «vektet snitt»; alternativ er veiing med installert effekt).")


if __name__ == "__main__":
    main()
