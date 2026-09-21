"""Steg 21: Magasinfylling og utveksling med utlandet – datagrunnlag for påstanden om at lave magasiner
skyldes eksport, ikke forbruk.

Kilder (alle åpne, hentet 21.09.2026):
  NVE magasinstatistikk, offentlig API (ukentlig, 1995–):
    https://biapi.nve.no/magasinstatistikk/api/Magasinstatistikk/HentOffentligData        -> data/raw/nve_magasin_raw.json
    https://biapi.nve.no/magasinstatistikk/api/Magasinstatistikk/HentOffentligDataMinMaxMedian -> data/raw/nve_magasin_minmaxmedian.json
    omrType NO = hele landet (omrnr 0), EL = elspotområde NO1–NO5, VASS = vassdragsområde. Median/min/maks per uke er NVEs
    egne, regnet over referanseperioden NVE bruker (oppgitt i API-et som samlet verdi per uke).
  Statnett driftsdata, nedlasting (time):
    https://driftsdata.statnett.no/restapi/download/productionconsumption/{aar}?fileFormat=csv -> data/raw/statnett/pc{aar}.csv (2021–2026)
    https://driftsdata.statnett.no/restapi/download/physicalflow/{aar}?fileFormat=csv         -> data/raw/statnett/pf{aar}.csv (bare 2025–2026 har innhold;
                                                                                                  2021–2024 er nullrader i kilden)
  SSB 14091 Elektrisitetsbalanse (måned), allerede hentet i s17 -> output/tab_nettoeksport.csv

Utdata:
  data/processed/nve_magasin_uke.parquet, statnett_maned.parquet
  output/tab_magasin_uke37.csv        fyllingsgrad uke 37 per år 2021–2026 mot NVE-median, NO og NO1/NO2/NO5
  output/tab_magasin_avvik_2026.csv   avvik fra median i TWh gjennom 2026, hele landet og Sør-Norge (NO1+NO2+NO5)
  output/tab_elbalanse_aar.csv        produksjon, import, eksport, nettoeksport, bruttoforbruk, husholdning per år og jan–jul
  output/tab_statnett_maned.csv       Statnett produksjon, forbruk, produksjon−forbruk per måned; utveksling 2025–2026
  output/tab_magasin_eksport.md       sammenstilling med kontrolltall
Alle tall til godkjenning.
"""
import json
import io
import pandas as pd
import numpy as np
from config import RAW, PROC, OUT

SOR = [1, 2, 5]
UKE = 37  # siste publiserte uke i NVE-data ved kjøring (kontrolleres under)

# ----------------------------------------------------------------------------- NVE
m = pd.DataFrame(json.loads((RAW / "nve_magasin_raw.json").read_text(encoding="utf-8")))
mm = pd.DataFrame(json.loads((RAW / "nve_magasin_minmaxmedian.json").read_text(encoding="utf-8")))
m = m[m.omrType.isin(["NO", "EL"])].copy()
m["dato"] = pd.to_datetime(m.dato_Id)
m = m.merge(mm[mm.omrType.isin(["NO", "EL"])][["omrType", "omrnr", "iso_uke", "medianFyllingsGrad", "minFyllingsgrad", "maxFyllingsgrad", "medianFylling_TWH"]],
            on=["omrType", "omrnr", "iso_uke"], how="left")
m["avvik_median_pp"] = (m.fyllingsgrad - m.medianFyllingsGrad) * 100
m["avvik_median_TWh"] = m.fylling_TWh - m.medianFyllingsGrad * m.kapasitet_TWh
m = m.sort_values(["omrType", "omrnr", "dato"]).reset_index(drop=True)
m.to_parquet(PROC / "nve_magasin_uke.parquet", index=False)
siste = m[m.omrType == "NO"].dato.max()
siste_uke = int(m[(m.omrType == "NO") & (m.dato == siste)].iso_uke.iloc[0]); siste_aar = int(m[(m.omrType == "NO") & (m.dato == siste)].iso_aar.iloc[0])
UKE = siste_uke

def omr(r):
    return "Hele landet" if r.omrType == "NO" else f"NO{r.omrnr}"

u = m[(m.iso_uke == UKE) & (m.iso_aar.between(2021, 2026)) & ((m.omrType == "NO") | (m.omrnr.isin(SOR)))].copy()
u["omrade"] = u.apply(omr, axis=1)
t_uke = u.pivot_table(index="omrade", columns="iso_aar", values="fyllingsgrad").mul(100).round(1)
t_uke["median_NVE"] = (u.groupby("omrade").medianFyllingsGrad.first() * 100).round(1)
t_uke["min_NVE"] = (u.groupby("omrade").minFyllingsgrad.first() * 100).round(1)
t_uke["kapasitet_TWh"] = u[u.iso_aar == 2026].set_index("omrade").kapasitet_TWh.round(1)
t_uke.to_csv(OUT / f"tab_magasin_uke{UKE}.csv", encoding="utf-8")

# Sør-Norge samlet (NO1+NO2+NO5): summer fylling og kapasitet per uke, median vektet med kapasitet
s = m[(m.omrType == "EL") & (m.omrnr.isin(SOR))].groupby(["iso_aar", "iso_uke", "dato"]).agg(
    fylling_TWh=("fylling_TWh", "sum"), kapasitet_TWh=("kapasitet_TWh", "sum"),
    median_TWh=("medianFylling_TWH", "sum")).reset_index()
s["fyllingsgrad"] = s.fylling_TWh / s.kapasitet_TWh; s["median_grad"] = s.median_TWh / s.kapasitet_TWh
s["avvik_median_TWh"] = s.fylling_TWh - s.median_TWh
land = m[m.omrType == "NO"][["iso_aar", "iso_uke", "dato", "fylling_TWh", "kapasitet_TWh", "fyllingsgrad", "medianFyllingsGrad", "avvik_median_TWh"]]
a26 = land[land.iso_aar == 2026].merge(s[s.iso_aar == 2026][["iso_uke", "fyllingsgrad", "median_grad", "avvik_median_TWh"]], on="iso_uke", suffixes=("_land", "_sor"))
a26 = a26.rename(columns={"medianFyllingsGrad": "median_grad_land", "median_grad": "median_grad_sor"})
a26[["iso_uke", "dato", "fyllingsgrad_land", "median_grad_land", "avvik_median_TWh_land", "fyllingsgrad_sor", "median_grad_sor", "avvik_median_TWh_sor"]].round(4).to_csv(OUT / "tab_magasin_avvik_2026.csv", index=False, encoding="utf-8")

# Utvikling gjennom det hydrologiske året: fylling uke 37 minus fylling uke 37 året før, per år (TWh), hele landet og Sør
def endring_aar(df, col="fylling_TWh"):
    x = df[df.iso_uke == UKE].set_index("iso_aar")[col]
    return (x - x.shift(1)).dropna()
end_land = endring_aar(land); end_sor = endring_aar(s)

# ----------------------------------------------------------------------------- SSB elbalanse (fra s17)
eb = pd.read_csv(OUT / "tab_nettoeksport.csv")
eb["aar"] = eb.maaned.str[:4].astype(int); eb["mnd"] = eb.maaned.str[5:].astype(int)
siste_mnd_2026 = int(eb[eb.aar == 2026].mnd.max())
cols = ["produksjon_gwh", "import_gwh", "eksport_gwh", "nettoeksport_gwh", "bruttoforbruk_gwh", "husholdningsforbruk_gwh"]
aar = eb.groupby("aar")[cols].sum().div(1000).round(2); aar["mnd_dekket"] = eb.groupby("aar").mnd.count()
jj = eb[eb.mnd <= siste_mnd_2026].groupby("aar")[cols].sum().div(1000).round(2); jj.index = [f"{a} jan–{siste_mnd_2026:02d}" for a in jj.index]
snitt = jj.iloc[:-1].mean().round(2); snitt.name = f"snitt 2021–2025 jan–{siste_mnd_2026:02d}"
diff = (jj.iloc[-1] - snitt).round(2); diff.name = f"2026 minus snitt, jan–{siste_mnd_2026:02d}"
t_aar = pd.concat([aar.drop(columns="mnd_dekket"), jj, snitt.to_frame().T, diff.to_frame().T])
t_aar.to_csv(OUT / "tab_elbalanse_aar.csv", encoding="utf-8")

# ----------------------------------------------------------------------------- Statnett
def les_statnett(prefix, cols):
    fr = []
    for f in sorted((RAW / "statnett").glob(f"{prefix}*.csv")):
        d = pd.read_csv(f, encoding="utf-8-sig")
        d.columns = ["tid"] + cols
        d["maned"] = d.tid.str[6:10] + "-" + d.tid.str[3:5]
        fr.append(d)
    return pd.concat(fr, ignore_index=True)
pc = les_statnett("pc", ["produksjon_mw", "forbruk_mw"])
pcm = pc.groupby("maned")[["produksjon_mw", "forbruk_mw"]].sum().div(1000)  # MWh -> GWh (timeverdier i MW = MWh per time)
pcm.columns = ["produksjon_gwh_statnett", "forbruk_gwh_statnett"]; pcm["prod_minus_forbruk_gwh"] = pcm.produksjon_gwh_statnett - pcm.forbruk_gwh_statnett
pf = les_statnett("pf", ["import_mw", "eksport_mw", "flyt_fra_no_mw"])
pfm = pf.groupby("maned")[["import_mw", "eksport_mw", "flyt_fra_no_mw"]].sum().div(1000)
pfm.columns = ["import_gwh_statnett", "eksport_gwh_statnett", "nettoeksport_gwh_statnett"]
st = pcm.join(pfm, how="left").join(eb.set_index("maaned")[["nettoeksport_gwh", "produksjon_gwh"]].rename(columns={"nettoeksport_gwh": "nettoeksport_gwh_ssb", "produksjon_gwh": "produksjon_gwh_ssb"}), how="left")
st = st[st.index >= "2021-01"].round(1)
st.to_parquet(PROC / "statnett_maned.parquet"); st.to_csv(OUT / "tab_statnett_maned.csv", encoding="utf-8")
# kontroll: Statnett produksjon−forbruk mot SSB nettoeksport, og Statnett-flyt mot SSB 2025–
k = st.dropna(subset=["nettoeksport_gwh_ssb"])
korr1 = np.corrcoef(k.prod_minus_forbruk_gwh, k.nettoeksport_gwh_ssb)[0, 1]
k2 = k.dropna(subset=["nettoeksport_gwh_statnett"])
avvik2 = (k2.nettoeksport_gwh_statnett - k2.nettoeksport_gwh_ssb)

# ----------------------------------------------------------------------------- notat
o = io.StringIO(); p = o.write
p(f"# Magasinfylling og utveksling – datagrunnlag (s21)\n\nHentet 21.09.2026. Alle tall til godkjenning. Siste NVE-uke: {UKE} ({siste.date()}).\n\n")
p(f"## Fyllingsgrad uke {UKE}, prosent av kapasitet\n\n"); p(t_uke.to_markdown()); p("\n\n")
p("Median og min er NVEs egne referanseverdier for samme uke.\n\n")
p("## Avvik fra median, TWh, 2026\n\n")
p(a26[["iso_uke", "fyllingsgrad_land", "median_grad_land", "avvik_median_TWh_land", "fyllingsgrad_sor", "median_grad_sor", "avvik_median_TWh_sor"]].round(3).to_markdown(index=False)); p("\n\n")
p(f"## Endring i fylling fra uke {UKE} året før til uke {UKE}, TWh\n\n")
p(pd.DataFrame({"Hele landet": end_land, "Sør-Norge (NO1+NO2+NO5)": end_sor}).round(2).to_markdown()); p("\n\n")
p("## Elektrisitetsbalanse, TWh (SSB 14091, hele landet)\n\n"); p(t_aar.to_markdown()); p("\n\n")
p("## Statnett mot SSB\n\n")
p(f"Korrelasjon Statnett produksjon minus forbruk mot SSB nettoeksport, {len(k)} måneder: {korr1:.3f}. ")
p(f"Statnett utveksling mot SSB nettoeksport 2025–{k2.index.max()}: snitt avvik {avvik2.mean():.0f} GWh/mnd, største {avvik2.abs().max():.0f} GWh.\n\n")
p("Statnetts utvekslingsfil har bare innhold fra 2025; 2021–2024 er nullrader i kilden. SSB 14091 er derfor hovedkilden for import og eksport.\n")
(OUT / "tab_magasin_eksport.md").write_text(o.getvalue(), encoding="utf-8")
print(o.getvalue())
